"""
Inicialização dos controllers e registro de rotas.
"""
from app.controllers.area_competencia_controller import register_area_routes
from app.controllers.disciplina_controller import register_disciplina_routes
from app.controllers.professor_controller import register_professor_routes
from app.controllers.semestre_letivo_controller import register_semestre_routes
from app.controllers.oferta_controller import register_oferta_routes
from app.controllers.alocacao_controller import register_alocacao_routes
from app.controllers.import_controller import register_import_routes
from app.controllers.algoritmo_genetico_controller import register_ag_routes


def register_all_routes(app, db):
    """Registra todas as rotas da aplicação."""
    register_area_routes(app, db)
    register_disciplina_routes(app, db)
    register_professor_routes(app, db)
    register_semestre_routes(app, db)
    register_oferta_routes(app, db)
    register_alocacao_routes(app, db)
    register_import_routes(app, db)
    register_ag_routes(app, db)
