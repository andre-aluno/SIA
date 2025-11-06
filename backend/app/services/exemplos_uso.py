"""
Exemplos de uso da camada de Services.
Este arquivo documenta como usar os services para operações comuns.
"""

from sqlalchemy.orm import Session
from app.services import (
    AreaCompetenciaService,
    DisciplinaService,
    ProfessorService,
    SemestreLetivoService,
    OfertaService,
    AlocacaoService,
    ImportService,
    AlgoritmoGeneticoService,
)
from datetime import date


# =============================================================================
# 1. EXEMPLO: Gerenciar Áreas de Competência
# =============================================================================

def exemplo_areas_competencia(db: Session):
    """Demonstra operações com áreas de competência."""
    service = AreaCompetenciaService(db)

    # Criar uma nova área
    area, error = service.create(nome="Programação Python")
    if error:
        print(f"Erro ao criar área: {error}")
    else:
        print(f"Área criada: {area.nome}")

    # Buscar por nome
    area = service.get_by_nome("Programação Python")
    print(f"Área encontrada: {area}")

    # Listar todas ordenadas
    areas = service.list_all_ordered()
    print(f"Total de áreas: {len(areas)}")

    # Atualizar
    area, error = service.update(area.id, nome="Python Avançado")

    # Deletar (com validação)
    sucesso, error = service.delete_with_validation(area.id)
    if not sucesso:
        print(f"Não foi possível deletar: {error}")


# =============================================================================
# 2. EXEMPLO: Gerenciar Disciplinas
# =============================================================================

def exemplo_disciplinas(db: Session):
    """Demonstra operações com disciplinas."""
    service = DisciplinaService(db)
    area_service = AreaCompetenciaService(db)

    # Obter ou criar uma área
    area = area_service.get_by_nome("Programação Python")
    if not area:
        area, _ = area_service.create(nome="Programação Python")

    # Criar disciplina com validação
    disc, error = service.create_with_area(
        nome="Python Fundamentals",
        carga_horaria=80.0,
        nivel_esperado=1,  # Graduado
        area_id=area.id
    )

    if error:
        print(f"Erro: {error}")
    else:
        print(f"Disciplina criada: {disc.nome}")

    # Listar disciplinas de uma área
    disciplinas = service.get_by_area(area.id)
    print(f"Disciplinas na área: {len(disciplinas)}")

    # Atualizar com validação
    disc, error = service.update_with_validation(
        disc.id,
        carga_horaria=90.0
    )


# =============================================================================
# 3. EXEMPLO: Gerenciar Professores
# =============================================================================

def exemplo_professores(db: Session):
    """Demonstra operações com professores."""
    service = ProfessorService(db)
    area_service = AreaCompetenciaService(db)

    # Obter áreas
    areas = area_service.list_all_ordered()
    area_ids = [a.id for a in areas[:2]]  # Usar 2 primeiras áreas

    # Criar professor com áreas
    prof, error = service.create_with_areas(
        nome="Dr. João Silva",
        titulacao="Doutor",
        carga_maxima=256.0,
        modelo_contratacao="Mensalista ",
        area_ids=area_ids
    )

    if error:
        print(f"Erro: {error}")
    else:
        print(f"Professor criado: {prof.nome}")

    # Listar professores
    professores = service.list_all_ordered()
    print(f"Total de professores: {len(professores)}")

    # Adicionar área ao professor
    if areas:
        sucesso, error = service.add_area(prof.id, areas[-1].id)
        if sucesso:
            print(f"Área adicionada ao professor")

    # Verificar competência
    tem_competencia = service.has_area_competence(prof.id, area_ids[0])
    print(f"Tem competência: {tem_competencia}")

    # Obter carga horária
    carga_total = service.get_carga_total(prof.id)
    carga_livre = service.get_carga_livre(prof.id)
    percentual = service.get_percentual_carga(prof.id)

    print(f"Carga total: {carga_total}h")
    print(f"Carga livre: {carga_livre}h")
    print(f"Percentual: {percentual*100:.1f}%")


# =============================================================================
# 4. EXEMPLO: Gerenciar Semestres Letivos
# =============================================================================

def exemplo_semestres(db: Session):
    """Demonstra operações com semestres letivos."""
    service = SemestreLetivoService(db)

    # Criar semestre
    sem, error = service.create_with_validation(
        nome="2025-1",
        ano=2025,
        periodo="1",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 6, 30)
    )

    if error:
        print(f"Erro: {error}")
    else:
        print(f"Semestre criado: {sem.nome}")

    # Listar semestres ordenados
    semestres = service.list_all_ordered()
    print(f"Total de semestres: {len(semestres)}")

    # Buscar semestres ativos
    semestres_ativos = service.get_semestres_ativos()
    print(f"Semestres ativos hoje: {len(semestres_ativos)}")

    # Buscar semestres futuros
    semestres_futuros = service.get_semestres_futuros()
    print(f"Semestres futuros: {len(semestres_futuros)}")


# =============================================================================
# 5. EXEMPLO: Gerenciar Ofertas
# =============================================================================

def exemplo_ofertas(db: Session):
    """Demonstra operações com ofertas de disciplinas."""
    service = OfertaService(db)
    semestre_service = SemestreLetivoService(db)
    disciplina_service = DisciplinaService(db)

    # Obter semestre e disciplina
    semestres = semestre_service.list_all_ordered()
    disciplinas = disciplina_service.list_all_ordered()

    if semestres and disciplinas:
        # Criar oferta
        oferta, error = service.create_with_validation(
            semestre_id=semestres[0].id,
            disciplina_id=disciplinas[0].id,
            turma="A"
        )

        if error:
            print(f"Erro: {error}")
        else:
            print(f"Oferta criada: {oferta.disciplina.nome} - Turma {oferta.turma}")

        # Buscar ofertas por semestre
        ofertas = service.get_by_semestre(semestres[0].id)
        print(f"Ofertas no semestre: {len(ofertas)}")

        # Buscar ofertas não alocadas
        ofertas_nao_alocadas = service.get_ofertas_nao_alocadas(semestres[0].id)
        print(f"Ofertas não alocadas: {len(ofertas_nao_alocadas)}")


# =============================================================================
# 6. EXEMPLO: Gerenciar Alocações
# =============================================================================

def exemplo_alocacoes(db: Session):
    """Demonstra operações com alocações."""
    service = AlocacaoService(db)
    oferta_service = OfertaService(db)
    professor_service = ProfessorService(db)

    # Obter uma oferta não alocada e um professor
    ofertas = oferta_service.get_all()
    professores = professor_service.list_all_ordered()

    if ofertas and professores:
        oferta_nao_alocada = None
        for oferta in ofertas:
            if not oferta.alocacoes:
                oferta_nao_alocada = oferta
                break

        if oferta_nao_alocada:
            # Criar alocação com validação
            alocacao, error = service.create_with_validation(
                oferta_id=oferta_nao_alocada.id,
                professor_id=professores[0].id
            )

            if error:
                print(f"Erro ao alocar: {error}")
            else:
                print(f"Alocação criada: {alocacao.professor.nome} → {alocacao.oferta.disciplina.nome}")

        # Buscar alocações por professor
        alocacoes = service.get_by_professor(professores[0].id)
        print(f"Alocações do professor: {len(alocacoes)}")

        # Resumo de professor no semestre
        if alocacoes:
            resumo = service.get_resumo_professor_semestre(
                professores[0].id,
                alocacoes[0].oferta.semestre_id
            )
            print(f"Resumo: {resumo}")


# =============================================================================
# 7. EXEMPLO: Importar Dados do Excel
# =============================================================================

def exemplo_importacao(db: Session, arquivo_excel: str):
    """Demonstra importação de dados em massa."""
    service = ImportService(db)

    # Importar do Excel
    sucesso, relatorio = service.import_from_excel(arquivo_excel)

    print(relatorio)

    if sucesso:
        stats = service.get_stats()
        print(f"Estatísticas: {stats}")


# =============================================================================
# 8. EXEMPLO: Algoritmo Genético para Alocação
# =============================================================================

def exemplo_algoritmo_genetico(db: Session, semestre_nome: str):
    """Demonstra uso do AG para otimizar alocação."""
    service = AlgoritmoGeneticoService(db)

    # Carregar dados
    professores, ofertas = service.load_data_for_semestre(semestre_nome)
    print(f"Professores: {len(professores)}, Ofertas: {len(ofertas)}")

    # Validar viabilidade
    viavel, problemas = service.validate_feasibility(professores, ofertas)

    if not viavel:
        print(f"Problema de viabilidade: {problemas}")
        return

    # Obter configuração padrão
    config = service.get_config_defaults()

    # Validar configuração (exemplo de modificação)
    config['num_geracoes'] = 100
    config['tamanho_populacao'] = 200

    valid, error = service.get_config_validation(config)
    if not valid:
        print(f"Configuração inválida: {error}")
        return

    print(f"Configuração validada: {config}")

    # Aqui você chamaria o AG real (ex: usando DEAP)
    # alocacao_solucao = run_ag(professores, ofertas, config)

    # Exemplo de cálculo de fitness (simulado)
    # alocacao_exemplo = list(range(len(ofertas)))  # Simples round-robin
    # metrics = service.calculate_fitness_metrics(alocacao_exemplo, professores, ofertas)

    # Formatar resultado
    # resultado = service.format_alocacao_result(alocacao_exemplo, professores, ofertas)

    # Resumo
    # resumo = service.get_resumo_alocacao(alocacao_exemplo, professores, ofertas, metrics)
    # print(f"Resumo: {resumo}")


# =============================================================================
# 9. EXEMPLO: Fluxo Completo
# =============================================================================

def exemplo_fluxo_completo(db: Session):
    """Demonstra um fluxo completo de uso do sistema."""
    print("\n" + "="*70)
    print("EXEMPLO: FLUXO COMPLETO DO SISTEMA")
    print("="*70 + "\n")

    # 1. Criar áreas
    print("1. Criando áreas de competência...")
    area_service = AreaCompetenciaService(db)
    areas_nomes = ["Programação Python", "Banco de Dados", "Web Development"]
    areas = []
    for nome in areas_nomes:
        area, _ = area_service.create_if_not_exists(nome=nome)
        areas.append(area)
    print(f"   ✓ {len(areas)} áreas criadas\n")

    # 2. Criar semestre
    print("2. Criando semestre letivo...")
    sem_service = SemestreLetivoService(db)
    semestre, _ = sem_service.create_with_validation(
        nome="2025-1",
        ano=2025,
        periodo="1",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 6, 30)
    )
    print(f"   ✓ Semestre '{semestre.nome}' criado\n")

    # 3. Criar professores
    print("3. Criando professores...")
    prof_service = ProfessorService(db)
    profs_data = [
        ("Dr. João Silva", "Doutor", [areas[0].id, areas[1].id]),
        ("Profa. Maria Santos", "Mestre", [areas[1].id, areas[2].id]),
        ("Prof. Pedro Costa", "Especialista", [areas[0].id]),
    ]

    professores = []
    for nome, titul, area_ids in profs_data:
        prof, _ = prof_service.create_with_areas(
            nome=nome,
            titulacao=titul,
            carga_maxima=256.0,
            modelo_contratacao="Mensalista ",
            area_ids=area_ids
        )
        professores.append(prof)
    print(f"   ✓ {len(professores)} professores criados\n")

    # 4. Criar disciplinas
    print("4. Criando disciplinas...")
    disc_service = DisciplinaService(db)
    discs_data = [
        ("Python Fundamentals", 80.0, 1, areas[0].id),
        ("SQL Avançado", 60.0, 2, areas[1].id),
        ("React Basics", 100.0, 1, areas[2].id),
    ]

    disciplinas = []
    for nome, carga, nivel, area_id in discs_data:
        disc, _ = disc_service.create_with_area(
            nome=nome,
            carga_horaria=carga,
            nivel_esperado=nivel,
            area_id=area_id
        )
        disciplinas.append(disc)
    print(f"   ✓ {len(disciplinas)} disciplinas criadas\n")

    # 5. Criar ofertas
    print("5. Criando ofertas...")
    oferta_service = OfertaService(db)
    ofertas = []
    for disc in disciplinas:
        oferta, _ = oferta_service.create_with_validation(
            semestre_id=semestre.id,
            disciplina_id=disc.id,
            turma="A"
        )
        ofertas.append(oferta)
    print(f"   ✓ {len(ofertas)} ofertas criadas\n")

    # 6. Criar alocações
    print("6. Criando alocações...")
    aloc_service = AlocacaoService(db)
    alocacoes = []
    for idx, oferta in enumerate(ofertas):
        prof = professores[idx % len(professores)]
        aloc, error = aloc_service.create_with_validation(
            oferta_id=oferta.id,
            professor_id=prof.id
        )
        if aloc:
            alocacoes.append(aloc)
    print(f"   ✓ {len(alocacoes)} alocações criadas\n")

    # 7. Resumo final
    print("7. Resumo final:")
    print(f"   - Áreas: {len(areas)}")
    print(f"   - Semestre: {semestre.nome}")
    print(f"   - Professores: {len(professores)}")
    print(f"   - Disciplinas: {len(disciplinas)}")
    print(f"   - Ofertas: {len(ofertas)}")
    print(f"   - Alocações: {len(alocacoes)}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("Este arquivo contém exemplos de uso dos services.")
    print("Para usar, importe as funções e passe uma sessão do banco de dados.")

