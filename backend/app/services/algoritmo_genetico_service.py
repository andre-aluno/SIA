"""
Service para Alocação usando Algoritmo Genético.
Replica a funcionalidade da página ag_page.py do Streamlit.
"""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from ..models import Professor, Oferta, SemestreLetivo, Disciplina, AreaCompetencia
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
            areas_necessarias.add(oferta.disciplina.area.id)

        for professor in professores:
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

    def calculate_fitness_metrics(self, alocacao: List[int],
                                 professores: List[Professor],
                                 ofertas: List[Oferta]) -> Dict[str, float]:
        """
        Calcula métricas de qualidade de uma alocação.

        Args:
            alocacao: Lista onde índice é oferta_id e valor é professor_id
            professores: Lista de professores
            ofertas: Lista de ofertas

        Returns:
            Dicionário com métricas
        """
        prof_map = {p.id: p for p in professores}

        # Penalidades (quanto maior o valor, pior a solução)
        penalidade_incompetencia = 0.0
        penalidade_sobrecarga = 0.0
        penalidade_desbalanceamento = 0.0

        carga_por_professor = {p.id: 0.0 for p in professores}

        for idx, prof_id in enumerate(alocacao):
            if prof_id >= len(professores):
                continue

            prof = professores[prof_id]
            oferta = ofertas[idx]

            # Verificar competência
            tem_competencia = any(a.id == oferta.disciplina.area.id for a in prof.areas)
            if not tem_competencia:
                penalidade_incompetencia += 50.0  # Grande penalidade

            # Atualizar carga
            carga_por_professor[prof.id] += float(oferta.disciplina.carga_horaria)

        # Verificar sobrecarga
        for prof_id, carga in carga_por_professor.items():
            prof = prof_map.get(prof_id)
            if prof:
                carga_max = float(prof.carga_maxima)
                if carga > carga_max:
                    penalidade_sobrecarga += (carga - carga_max) * 10.0

        # Penalizar desbalanceamento (favorecer distribuição uniforme)
        if professores:
            carga_media = sum(carga_por_professor.values()) / len(professores)
            for carga in carga_por_professor.values():
                desv = abs(carga - carga_media)
                penalidade_desbalanceamento += desv * 0.5

        # Fitness = penalidades totais (queremos minimizar)
        fitness = penalidade_incompetencia + penalidade_sobrecarga + penalidade_desbalanceamento

        return {
            "fitness_total": fitness,
            "penalidade_incompetencia": penalidade_incompetencia,
            "penalidade_sobrecarga": penalidade_sobrecarga,
            "penalidade_desbalanceamento": penalidade_desbalanceamento,
            "carga_por_professor": carga_por_professor
        }

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
            if prof_id >= len(professores):
                continue

            prof = professores[prof_id]
            oferta = ofertas[idx]
            ch = float(oferta.disciplina.carga_horaria)

            # Verificar match de competência
            match = oferta.disciplina.area.id in {a.id for a in prof.areas}

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

        # Calcular estatísticas
        matches_positivos = sum(1 for r in self.format_alocacao_result(alocacao, professores, ofertas)
                                if r['match'] == "✅")
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
        if config.get('num_geracoes', 0) < 1:
            return False, "Número de gerações deve ser >= 1"

        if config.get('tamanho_populacao', 0) < 2:
            return False, "Tamanho da população deve ser >= 2"

        cxpb = config.get('probabilidade_crossover', 0)
        if not (0.0 <= cxpb <= 1.0):
            return False, "Probabilidade de crossover deve estar entre 0.0 e 1.0"

        mutpb = config.get('probabilidade_mutacao', 0)
        if not (0.0 <= mutpb <= 1.0):
            return False, "Probabilidade de mutação deve estar entre 0.0 e 1.0"

        elite = config.get('elite_size', 0)
        if elite < 0 or elite >= config.get('tamanho_populacao', 0):
            return False, "Elite size deve estar entre 0 e tamanho da população"

        return True, None

