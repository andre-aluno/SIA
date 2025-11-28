"""
Service para Alocação usando Algoritmo Genético.
Replica a funcionalidade da página ag_page.py do Streamlit.
"""
from typing import List, Optional, Tuple, Dict, Any
import random
import math
import time
from sqlalchemy.orm import Session
from deap import base, creator, tools, algorithms
from ..models import Professor, Oferta
from .oferta_service import OfertaService
from .professor_service import ProfessorService


class AlgoritmoGeneticoService:
    """Service para otimização de alocação usando Algoritmo Genético."""

    def __init__(self, db: Session):
        self.db = db
        self.oferta_service = OfertaService(db)
        self.professor_service = ProfessorService(db)

    def load_data_for_semestre(self, semestre_nome: str) -> Tuple[List[Professor], List[Oferta]]:
        """
        Carrega dados necessários para executar o AG.

        Args:
            semestre_nome: Nome do semestre letivo

        Returns:
            Tupla (professores, ofertas não alocadas)
        """
        try:
            # Buscar professores com suas áreas de competência
            professores = self.db.query(Professor).order_by(Professor.nome).all()

            # Buscar ofertas não alocadas do semestre
            ofertas = self.oferta_service.get_ofertas_nao_alocadas_by_semestre_nome(semestre_nome)

            return professores, ofertas
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")
            return [], []

    def validate_feasibility(self, professores: List[Professor],
                            ofertas: List[Oferta]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Valida se é possível alocar todas as disciplinas.

        Args:
            professores: Lista de professores disponíveis
            ofertas: Lista de ofertas a alocar

        Returns:
            Tupla (viável, lista de problemas encontrados)
        """
        problemas = []

        if not ofertas:
            return True, []

        if not professores:
            return False, [{"tipo": "sem_professores", "mensagem": "Não há professores cadastrados"}]

        # Verificar áreas disponíveis vs necessárias
        areas_necessarias = set()
        areas_disponiveis = set()

        for oferta in ofertas:
            if oferta.disciplina and oferta.disciplina.area:
                areas_necessarias.add(oferta.disciplina.area.id)

        for professor in professores:
            if professor.areas:
                for area in professor.areas:
                    areas_disponiveis.add(area.id)

        areas_sem_professor = areas_necessarias - areas_disponiveis

        if areas_sem_professor:
            # Listar disciplinas problemáticas
            for oferta in ofertas:
                if oferta.disciplina.area.id in areas_sem_professor:
                    problemas.append({
                        "tipo": "sem_competencia",
                        "disciplina": oferta.disciplina.nome,
                        "turma": oferta.turma,
                        "area": oferta.disciplina.area.nome,
                        "carga_horaria": float(oferta.disciplina.carga_horaria),
                        "mensagem": f"Nenhum professor tem competência em {oferta.disciplina.area.nome}"
                    })

        # Verificar carga horária total vs disponível
        carga_total_disciplinas = sum(float(o.disciplina.carga_horaria) for o in ofertas)
        carga_total_professores = sum(float(p.carga_maxima) for p in professores)

        if carga_total_disciplinas > carga_total_professores:
            problemas.append({
                "tipo": "carga_insuficiente",
                "mensagem": (
                    f"Carga horária total das disciplinas ({carga_total_disciplinas}h) "
                    f"excede a capacidade dos professores ({carga_total_professores}h)"
                )
            })

        return len(areas_sem_professor) == 0, problemas

    def calculate_fitness_metrics(self, individual: List[int],
                                 professores: List[Professor],
                                 ofertas: List[Oferta],
                                 carga_existente: Dict[int, float]) -> Tuple[float,]:
        """
        Calcula o fitness de uma solução (menor é melhor).

        Args:
            individual: Lista onde índice é oferta_id e valor é professor_id
            professores: Lista de professores
            ofertas: Lista de ofertas
            carga_existente: Carga horária já existente para os professores

        Returns:
            Tupla com o valor de fitness (penalidade total)
        """
        P_c, B_c = 1000, 200  # Penalidade e bonus de competência
        B_n = 50              # Bonus de nível
        P_h = 5000            # Penalidade de sobrecarga
        P_u = 500             # Penalidade de subutilização
        B_b = 100             # Bonus de balanceamento

        prof_map = {p.id: p for p in professores}
        carga = {p.id: carga_existente.get(p.id, 0.0) for p in professores}
        prof_areas = {p.id: {a.id for a in p.areas} if p.areas else set() for p in professores}

        score = 0.0

        # Critério 1 e 2: Competência e Nível
        for idx, prof_id in enumerate(individual):
            if idx >= len(ofertas):
                # Proteção contra índice fora do range
                score += P_c * 10
                continue

            prof = prof_map.get(prof_id)
            if not prof:
                score += P_c * 10  # Penalidade alta para professor inválido
                continue

            oferta = ofertas[idx]

            if oferta.disciplina.area.id not in prof_areas[prof_id]:
                score += P_c
            else:
                score -= B_c

            if prof.nivel >= oferta.disciplina.nivel_esperado:
                score -= B_n

            carga[prof_id] += float(oferta.disciplina.carga_horaria)

        # Critério 3: Respeito à carga máxima
        for p in professores:
            C = carga[p.id]
            max_load = float(p.carga_maxima)
            if C > max_load:
                score += P_h * (C - max_load)

        # Critério 4: Utilização do corpo docente
        M = len(professores)
        U = sum(1 for v in carga.values() if v > 0)
        score += P_u * (M - U) ** 2

        # Critério 5: Balanceamento relativo de carga
        ratios = [
            (carga[p.id] / float(p.carga_maxima)) if p.carga_maxima > 0 else 0.0
            for p in professores
        ]
        if ratios and len(ratios) > 0:
            mean_r = sum(ratios) / len(ratios)
            variance = sum((r - mean_r) ** 2 for r in ratios) / len(ratios)
            sigma_r = math.sqrt(variance)
            score -= B_b * (1 - min(max(sigma_r, 0.0), 1.0))

        return (score,)

    def format_alocacao_result(self, alocacao: List[int],
                              professores: List[Professor],
                              ofertas: List[Oferta]) -> List[Dict[str, Any]]:
        """
        Formata resultado da alocação para visualização.

        Args:
            alocacao: Solução do AG
            professores: Lista de professores
            ofertas: Lista de ofertas

        Returns:
            Lista de dicionários com alocações formatadas
        """
        prof_map = {p.id: p for p in professores}
        records = []

        for idx, prof_id in enumerate(alocacao):
            # Proteção contra índice fora do range
            if idx >= len(ofertas):
                print(f"[WARNING] Índice {idx} excede o número de ofertas ({len(ofertas)})")
                continue

            # Buscar professor pelo ID (não por índice)
            prof = prof_map.get(prof_id)
            if not prof:
                # Se o professor não existe, pular (não deveria acontecer)
                print(f"[WARNING] Professor com ID {prof_id} não encontrado na lista de professores")
                continue

            oferta = ofertas[idx]
            ch = float(oferta.disciplina.carga_horaria)

            # Verificar match de competência (proteção contra areas None)
            prof_areas = {a.id for a in prof.areas} if prof.areas else set()
            match = oferta.disciplina.area.id in prof_areas

            records.append({
                "idx": idx,
                "oferta_id": oferta.id,
                "professor_id": prof.id,
                "professor_nome": prof.nome,
                "titulacao": prof.titulacao,
                "modelo_contratacao": prof.modelo_contratacao,
                "nivel_professor": prof.nivel,
                "carga_maxima": float(prof.carga_maxima),
                "disciplina_nome": oferta.disciplina.nome,
                "turma": oferta.turma,
                "carga_horaria": ch,
                "nivel_esperado": oferta.disciplina.nivel_esperado,
                "area_disciplina": oferta.disciplina.area.nome,
                "match": "✅" if match else "❌",
                "tem_competencia": match
            })

        return records

    def get_resumo_alocacao(self, alocacao: List[int],
                           professores: List[Professor],
                           ofertas: List[Oferta],
                           metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Gera resumo executivo da alocação.

        Args:
            alocacao: Solução do AG
            professores: Lista de professores
            ofertas: Lista de ofertas
            metrics: Métricas de fitness calculadas

        Returns:
            Dicionário com resumo
        """
        carga_por_prof = metrics.get('carga_por_professor', {})
        prof_map = {p.id: p for p in professores}

        # Calcular estatísticas - SEM recalcular format_alocacao_result
        matches_positivos = 0
        for idx, prof_id in enumerate(alocacao):
            if idx >= len(ofertas):
                continue
            prof = prof_map.get(prof_id)
            if not prof:
                continue
            oferta = ofertas[idx]
            prof_areas = {a.id for a in prof.areas} if prof.areas else set()
            if oferta.disciplina.area.id in prof_areas:
                matches_positivos += 1

        matches_negativos = len(ofertas) - matches_positivos

        # Distribuição de carga
        cargas = []
        for prof in professores:
            carga = carga_por_prof.get(prof.id, 0.0)
            carga_max = float(prof.carga_maxima)
            percentual = (carga / carga_max * 100) if carga_max > 0 else 0.0
            cargas.append({
                "professor": prof.nome,
                "carga_alocada": carga,
                "carga_maxima": carga_max,
                "carga_livre": max(0.0, carga_max - carga),
                "percentual_utilizado": percentual
            })

        return {
            "ofertas_totais": len(ofertas),
            "ofertas_com_match": matches_positivos,
            "ofertas_sem_match": matches_negativos,
            "percentual_compatibilidade": (matches_positivos / len(ofertas) * 100) if ofertas else 0.0,
            "fitness_total": metrics.get('fitness_total', 0.0),
            "distribuicao_carga": cargas,
            "professores_utilizados": sum(1 for c in cargas if c['carga_alocada'] > 0),
            "total_professores": len(professores)
        }

    def get_config_defaults(self) -> Dict[str, Any]:
        """
        Retorna configurações padrão para o AG.

        Returns:
            Dicionário com parâmetros recomendados
        """
        return {
            "num_geracoes": 50,
            "tamanho_populacao": 100,
            "probabilidade_crossover": 0.7,
            "probabilidade_mutacao": 0.2,
            "seed": None,  # None = aleatório
            "elite_size": 5,  # Tamanho da elite preservada
            "torneio_size": 3,  # Tamanho do torneio para seleção
        }

    def get_config_validation(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida parâmetros de configuração do AG.

        Args:
            config: Dicionário com configurações

        Returns:
            Tupla (válido, mensagem de erro ou None)
        """
        num_gen = config.get('num_geracoes', 0)
        if num_gen < 1:
            return False, "Número de gerações deve ser >= 1"

        tam_pop = config.get('tamanho_populacao', 0)
        if tam_pop < 2:
            return False, "Tamanho da população deve ser >= 2"

        cxpb = config.get('probabilidade_crossover', 0)
        if not (0.0 <= cxpb <= 1.0):
            return False, "Probabilidade de crossover deve estar entre 0.0 e 1.0"

        mutpb = config.get('probabilidade_mutacao', 0)
        if not (0.0 <= mutpb <= 1.0):
            return False, "Probabilidade de mutação deve estar entre 0.0 e 1.0"

        elite = config.get('elite_size', 0)
        if elite < 0 or elite > tam_pop:
            return False, f"Elite size deve estar entre 0 e {tam_pop} (tamanho da população)"

        return True, None

    def _setup_ga(self, professores: List[Professor],
                  ofertas: List[Oferta],
                  carga_existente: Dict[int, float]) -> Tuple[base.Toolbox, int, int]:
        """
        Configura o ambiente de execução do AG (DEAP).

        Args:
            professores: Lista de professores
            ofertas: Lista de ofertas
            carga_existente: Dict com carga já alocada por professor no semestre

        Returns:
            Tupla (toolbox, num_ofertas, num_professores)
        """
        # Limpar classes anteriores se existirem
        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "Individual"):
            del creator.Individual

        # Criar classes de Fitness e Individual (MINIMIZANDO)
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        prof_ids = [p.id for p in professores]
        N_OFFERS = len(ofertas)

        toolbox = base.Toolbox()
        toolbox.register("attr_professor", random.choice, prof_ids)
        toolbox.register(
            "individual",
            tools.initRepeat,
            creator.Individual,
            toolbox.attr_professor,
            n=N_OFFERS
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("mate", tools.cxOnePoint)

        # CORRIGIDO: Usar mutação adequada que troca valores (professor_ids), não embaralha posições
        def mutate_professor(individual, indpb, prof_ids):
            """Mutação que troca o professor alocado em cada posição."""
            for i in range(len(individual)):
                if random.random() < indpb:
                    individual[i] = random.choice(prof_ids)
            return individual,

        toolbox.register("mutate", mutate_professor, indpb=0.2, prof_ids=prof_ids)

        # Registrar função de avaliação com binding
        toolbox.register(
            "evaluate",
            self.calculate_fitness_metrics,
            professores=professores,
            ofertas=ofertas,
            carga_existente=carga_existente
        )

        return toolbox, N_OFFERS, len(professores)

    def execute_ga(self, semestre_nome: str,
                  num_geracoes: int = 50,
                  tamanho_populacao: int = 100,
                  probabilidade_crossover: float = 0.7,
                  probabilidade_mutacao: float = 0.2) -> Dict[str, Any]:
        """
        Executa o Algoritmo Genético para alocar professores às ofertas.

        Este é o método principal que orquestra todo o processo.

        Args:
            semestre_nome: Nome do semestre letivo
            num_geracoes: Número de gerações para executar
            tamanho_populacao: Tamanho da população por geração
            probabilidade_crossover: Probabilidade de crossover (0.0 a 1.0)
            probabilidade_mutacao: Probabilidade de mutação (0.0 a 1.0)

        Returns:
            Dicionário com os resultados da execução contendo:
                - alocacao: Lista de professor_ids para cada oferta
                - alocacao_formatada: Detalhes completos de cada alocação
                - metrics: Métricas de fitness
                - resumo: Resumo executivo
                - tempo_execucao: Tempo gasto em segundos
        """
        start_time = time.time()

        try:
            print(f"[AG] Iniciando carregamento de dados para semestre: {semestre_nome}")

            # 1. Carregar dados
            professores, ofertas = self.load_data_for_semestre(semestre_nome)
            print(f"[AG] Dados carregados: {len(professores)} professores, {len(ofertas)} ofertas")

            if not ofertas:
                print(f"[AG] Nenhuma oferta não alocada encontrada")
                return {
                    "sucesso": False,
                    "erro": f"Nenhuma oferta não alocada encontrada para o semestre '{semestre_nome}'",
                    "alocacao": None,
                    "alocacao_formatada": [],
                    "metrics": None,
                    "resumo": None,
                    "tempo_execucao": time.time() - start_time
                }

            if not professores:
                print(f"[AG] Nenhum professor cadastrado")
                return {
                    "sucesso": False,
                    "erro": "Nenhum professor cadastrado no sistema",
                    "alocacao": None,
                    "alocacao_formatada": [],
                    "metrics": None,
                    "resumo": None,
                    "tempo_execucao": time.time() - start_time
                }

            # 2. Validar viabilidade
            print(f"[AG] Validando viabilidade...")
            viavel, problemas = self.validate_feasibility(professores, ofertas)
            print(f"[AG] Viabilidade: {viavel}, Problemas: {len(problemas)}")

            # 3. Configurar AG
            print(f"[AG] Carregando carga existente do semestre...")
            carga_existente = self._get_carga_existente_por_semestre(semestre_nome)
            print(f"[AG] Carga existente carregada: {len(carga_existente)} professores com alocação")

            print(f"[AG] Configurando AG...")
            toolbox, N_OFFERS, N_PROFS = self._setup_ga(professores, ofertas, carga_existente)
            print(f"[AG] AG configurado com {N_OFFERS} ofertas e {N_PROFS} professores")

            # 4. Executar AG
            print(f"[AG] Criando população inicial de {tamanho_populacao} indivíduos...")
            random.seed()
            pop = toolbox.population(n=tamanho_populacao)
            print(f"[AG] População criada com sucesso")

            print(f"[AG] Configurando estatísticas...")
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", lambda fits: sum(f[0] for f in fits) / len(fits) if fits else 0)
            stats.register("std", lambda fits: (
                (sum((f[0] - sum(f[0] for f in fits) / len(fits)) ** 2
                 for f in fits) / len(fits)) ** 0.5
            ) if fits else 0)
            stats.register("min", lambda fits: min(f[0] for f in fits) if fits else 0)
            stats.register("max", lambda fits: max(f[0] for f in fits) if fits else 0)

            print(f"[AG] Iniciando evolução com {num_geracoes} gerações...")
            pop, logbook = algorithms.eaSimple(
                population=pop,
                toolbox=toolbox,
                cxpb=probabilidade_crossover,
                mutpb=probabilidade_mutacao,
                ngen=num_geracoes,
                stats=stats,
                verbose=False
            )
            print(f"[AG] Evolução concluída com sucesso")

            # 5. Extrair melhor solução
            print(f"[AG] Extraindo melhor solução...")
            best_individual = tools.selBest(pop, 1)[0]
            best_alocacao = list(best_individual)
            print(f"[AG] Melhor fitness: {best_individual.fitness.values[0]}")

            # 6. A alocacao já contém IDs reais de professores (não índices)
            alocacao_real = best_alocacao

            # 7. Calcular métricas
            print(f"[AG] Calculando métricas...")
            fitness_value = best_individual.fitness.values[0]
            metrics = self._calculate_detailed_metrics(best_alocacao, professores, ofertas, carga_existente)
            metrics['fitness_total'] = fitness_value
            print(f"[AG] Métricas calculadas")

            # 8. Formatar resultado
            print(f"[AG] Formatando resultado...")
            alocacao_formatada = self.format_alocacao_result(best_alocacao, professores, ofertas)
            print(f"[AG] Resultado formatado: {len(alocacao_formatada)} alocações")

            # 9. Gerar resumo
            print(f"[AG] Gerando resumo...")
            resumo = self.get_resumo_alocacao(best_alocacao, professores, ofertas, metrics)
            print(f"[AG] Resumo gerado")

            # Converter logbook para dicionário (proteção contra logbook vazio)
            log_dict = {
                "geracoes": logbook.select("gen") if logbook else [],
                "media": logbook.select("avg") if logbook else [],
                "desvio": logbook.select("std") if logbook else [],
                "minimo": logbook.select("min") if logbook else [],
                "maximo": logbook.select("max") if logbook else []
            }

            tempo_execucao = time.time() - start_time
            print(f"[AG] Execução concluída em {tempo_execucao:.2f} segundos")

            return {
                "sucesso": True,
                "semestre": semestre_nome,
                "viavel": viavel,
                "problemas_viabilidade": problemas,
                "alocacao": alocacao_real,
                "alocacao_formatada": alocacao_formatada,
                "metrics": metrics,
                "resumo": resumo,
                "evolucao": log_dict,
                "tempo_execucao": tempo_execucao,
                "parametros": {
                    "num_geracoes": num_geracoes,
                    "tamanho_populacao": tamanho_populacao,
                    "probabilidade_crossover": probabilidade_crossover,
                    "probabilidade_mutacao": probabilidade_mutacao
                }
            }

        except Exception as e:
            import traceback
            import errno

            error_trace = traceback.format_exc()
            error_type = type(e).__name__
            error_msg = str(e)

            if hasattr(e, 'errno'):
                errno_val = e.errno
                print(f"[AG ERROR] Errno: {errno_val}")
                if errno_val == 9:
                    print(f"[AG ERROR] Erro 9: Bad file descriptor - possível problema com banco de dados ou sessão")

            print(f"[AG ERROR] Tipo de erro: {error_type}")
            print(f"[AG ERROR] Mensagem: {error_msg}")
            print(f"[AG ERROR] Traceback:\n{error_trace}")

            return {
                "sucesso": False,
                "erro": f"Erro ao executar AG: {error_type} - {error_msg}",
                "erro_tipo": error_type,
                "erro_detalhado": error_trace,
                "alocacao": None,
                "alocacao_formatada": [],
                "metrics": None,
                "resumo": None,
                "tempo_execucao": time.time() - start_time
            }

    def _get_carga_existente_por_semestre(self, semestre_nome: str) -> Dict[int, float]:
        """
        Calcula a carga horária JÁ ALOCADA para cada professor NO SEMESTRE INFORMADO.

        Busca apenas as alocações confirmadas do semestre específico.

        Args:
            semestre_nome: Nome do semestre letivo

        Returns:
            Dicionário {professor_id: carga_alocada}
        """
        try:
            # Buscar todas as ofertas alocadas do semestre
            ofertas_alocadas = self.db.query(Oferta).join(
                Oferta.semestre
            ).filter(
                Oferta.alocacoes.any(),  # Tem pelo menos uma alocação
                Oferta.semestre.has(nome=semestre_nome)
            ).all()

            carga_por_professor = {}

            # Somar carga de cada professor por suas alocações no semestre
            for oferta in ofertas_alocadas:
                if not oferta.alocacoes:
                    continue

                for alocacao in oferta.alocacoes:
                    professor_id = alocacao.professor_id
                    carga_horaria = float(oferta.disciplina.carga_horaria)

                    if professor_id not in carga_por_professor:
                        carga_por_professor[professor_id] = 0.0

                    carga_por_professor[professor_id] += carga_horaria

            return carga_por_professor
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Erro ao calcular carga existente no semestre '{semestre_nome}': {str(e)}")
            print(f"Traceback: {error_trace}")
            # Retornar vazio em caso de erro para não quebrar o fluxo
            return {}

    def _calculate_detailed_metrics(self, individual: List[int],
                                   professores: List[Professor],
                                   ofertas: List[Oferta],
                                   carga_existente: Dict[int, float]) -> Dict[str, Any]:
        """
        Calcula métricas detalhadas de uma solução para fins de relatório.
        Esta função é separada da de fitness para não impactar a performance do AG.
        """
        prof_map = {p.id: p for p in professores}
        carga = {p.id: carga_existente.get(p.id, 0.0) for p in professores}

        penalidade_incompetencia = 0.0
        penalidade_sobrecarga = 0.0
        penalidade_desbalanceamento = 0.0

        for idx, prof_id in enumerate(individual):
            if idx >= len(ofertas):
                continue

            prof = prof_map.get(prof_id)
            if not prof:
                continue

            oferta = ofertas[idx]

            # Acumula carga da solução atual
            carga[prof.id] += float(oferta.disciplina.carga_horaria)

            # Verifica competência (proteção contra areas None)
            prof_areas = {a.id for a in prof.areas} if prof.areas else set()
            if oferta.disciplina.area.id not in prof_areas:
                penalidade_incompetencia += 1

        # Calcula sobrecarga
        for p in professores:
            if carga[p.id] > float(p.carga_maxima):
                penalidade_sobrecarga += (carga[p.id] - float(p.carga_maxima))

        # Calcula desbalanceamento (proteção contra divisão por zero)
        ratios = [
            (carga[p.id] / float(p.carga_maxima)) if p.carga_maxima > 0 else 0.0
            for p in professores
        ]
        if ratios and len(ratios) > 0:
            mean_r = sum(ratios) / len(ratios)
            variance = sum((r - mean_r) ** 2 for r in ratios) / len(ratios)
            sigma_r = math.sqrt(variance)
            penalidade_desbalanceamento = sigma_r

        return {
            "penalidade_incompetencia": penalidade_incompetencia,
            "penalidade_sobrecarga": penalidade_sobrecarga,
            "penalidade_desbalanceamento": penalidade_desbalanceamento,
            "carga_por_professor": carga
        }
