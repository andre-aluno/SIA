"""
Camada de Services - Lógica de negócio e operações CRUD para todas as entidades.
"""
from .base_service import BaseService
from .area_competencia_service import AreaCompetenciaService
from .disciplina_service import DisciplinaService
from .professor_service import ProfessorService
from .semestre_letivo_service import SemestreLetivoService
from .oferta_service import OfertaService
from .alocacao_service import AlocacaoService
from .import_service import ImportService
from .algoritmo_genetico_service import AlgoritmoGeneticoService

__all__ = [
    'BaseService',
    'AreaCompetenciaService',
    'DisciplinaService',
    'ProfessorService',
    'SemestreLetivoService',
    'OfertaService',
    'AlocacaoService',
    'ImportService',
    'AlgoritmoGeneticoService',
]
