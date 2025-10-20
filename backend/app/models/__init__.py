from .area_competencia import AreaCompetencia
from .professor import Professor, TITULACOES, MODELOS_CONTRATACAO, TITULACAO_NIVEL_MAP
from .disciplina import Disciplina
from .semestre_letivo import SemestreLetivo
from .oferta import Oferta
from .alocacao import Alocacao
from .association import professor_area_competencia

__all__ = [
    'AreaCompetencia',
    'Professor',
    'Disciplina',
    'SemestreLetivo',
    'Oferta',
    'Alocacao',
    'professor_area_competencia',
    'TITULACOES',
    'MODELOS_CONTRATACAO',
    'TITULACAO_NIVEL_MAP'
]

