import random
import math
from deap import base, creator, tools, algorithms
from sqlalchemy.orm import joinedload
from db import get_session, Professor, Oferta, SemestreLetivo, Disciplina


from sqlalchemy.orm import joinedload
from db import get_session, Professor, Oferta, SemestreLetivo, Disciplina

def load_data(semestre_nome: str):
    session = get_session()
    try:
        professores = (
            session.query(Professor)
                   .options(joinedload(Professor.areas))
                   .all()
        )
        ofertas = (
            session.query(Oferta)
                   .join(Oferta.semestre)
                   .options(
                       joinedload(Oferta.disciplina)
                         .joinedload(Disciplina.area)
                   )
                   .filter(
                       SemestreLetivo.nome == semestre_nome,
                       # filtra apenas ofertas que não tenham nenhuma alocação
                       ~Oferta.alocacoes.any()
                   )
                   .all()
        )
        return professores, ofertas
    finally:
        session.close()


def evaluate_fitness(individual, professores, ofertas):
    P_c, B_c = 1000, 200
    B_n = 50
    P_h = 5000
    P_u = 500
    B_b = 100

    # Map de carga e áreas por professor
    prof_map = {p.id: p for p in professores}
    carga = {p.id: 0.0 for p in professores}
    prof_areas = {p.id: {a.id for a in p.areas} for p in professores}

    total = 0.0
    # 1 e 2: competência, nível e acumulação de carga
    for idx, prof_id in enumerate(individual):
        prof = prof_map.get(prof_id)
        oferta = ofertas[idx]
        # Cobertura de competência
        if oferta.disciplina.area.id not in prof_areas[prof_id]:
            total -= P_c
        else:
            total += B_c
        # Nível de titulação
        if prof.nivel >= oferta.disciplina.nivel_esperado:
            total += B_n
        # Soma carga
        carga[prof_id] += float(oferta.disciplina.carga_horaria)

    # 3: respeito à carga máxima
    for p in professores:
        C = carga[p.id]
        # TODO considerar as alocações já existentes
        max_load = float(p.carga_maxima)
        if C > max_load:
            total -= P_h * (C - max_load)

    # 4: utilização do corpo docente
    M = len(professores)
    U = sum(1 for v in carga.values() if v > 0)
    total -= P_u * (M - U) ** 2

    # 5: balanceamento relativo de carga
    ratios = [(carga[p.id] / float(p.carga_maxima)) if p.carga_maxima > 0 else 0.0 for p in professores]
    mean_r = sum(ratios) / len(ratios)
    variance = sum((r - mean_r) ** 2 for r in ratios) / len(ratios)
    sigma_r = math.sqrt(variance)
    total += B_b * (1 - min(max(sigma_r, 0.0), 1.0))

    return (total,)


def setup_representation(professores, ofertas):
    # Cria classes de Fitness e Individual apenas uma vez
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)

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
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)

    # Avaliação com binding por nome para manter ordem de parâmetros
    toolbox.register(
        "evaluate",
        evaluate_fitness,
        professores=professores,
        ofertas=ofertas
    )

    return toolbox, N_OFFERS, len(professores)


def run_ga(semestre_nome, ngen=50, pop_size=100, cxpb=0.7, mutpb=0.2):
    professores, ofertas = load_data(semestre_nome)
    toolbox, N_OFFERS, N_PROFS = setup_representation(professores, ofertas)

    random.seed()
    pop = toolbox.population(n=pop_size)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda fits: sum(f[0] for f in fits) / len(fits))
    stats.register("min", lambda fits: min(f[0] for f in fits))
    stats.register("max", lambda fits: max(f[0] for f in fits))

    pop, log = algorithms.eaSimple(
        population=pop,
        toolbox=toolbox,
        cxpb=cxpb,
        mutpb=mutpb,
        ngen=ngen,
        stats=stats,
        verbose=True
    )

    best = tools.selBest(pop, 1)[0]
    return best, log
