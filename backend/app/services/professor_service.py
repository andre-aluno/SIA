"""
Service para gerenciar Professores.
"""
from typing import List, Optional, Set
from sqlalchemy.orm import Session
from ..models import Professor, AreaCompetencia, TITULACAO_NIVEL_MAP
from .base_service import BaseService


class ProfessorService(BaseService[Professor]):
    """Service para operações CRUD de Professores."""

    def __init__(self, db: Session):
        super().__init__(Professor, db)

    def get_by_nome(self, nome: str) -> Optional[Professor]:
        """Busca um professor pelo nome."""
        try:
            return self.db.query(Professor).filter(
                Professor.nome == nome
            ).first()
        except Exception as e:
            print(f"Erro ao buscar professor por nome: {str(e)}")
            return None

    def exists_by_nome(self, nome: str) -> bool:
        """Verifica se um professor com este nome já existe."""
        return self.get_by_nome(nome) is not None

    def list_all_ordered(self) -> List[Professor]:
        """Lista todos os professores ordenados por nome."""
        try:
            return self.db.query(Professor).order_by(
                Professor.nome
            ).all()
        except Exception as e:
            print(f"Erro ao listar professores: {str(e)}")
            return []

    def get_by_titulacao(self, titulacao: str) -> List[Professor]:
        """Busca professores por titulação."""
        try:
            return self.db.query(Professor).filter(
                Professor.titulacao == titulacao
            ).order_by(Professor.nome).all()
        except Exception as e:
            print(f"Erro ao listar professores por titulação: {str(e)}")
            return []

    def get_by_area(self, area_id: int) -> List[Professor]:
        """Busca professores que possuem competência em uma área específica."""
        try:
            return self.db.query(Professor).join(
                Professor.areas
            ).filter(
                AreaCompetencia.id == area_id
            ).order_by(Professor.nome).all()
        except Exception as e:
            print(f"Erro ao listar professores por área: {str(e)}")
            return []

    def create_with_areas(self, nome: str, titulacao: str, carga_maxima: float,
                         modelo_contratacao: str, area_ids: List[int] = None) -> tuple[Optional[Professor], Optional[str]]:
        """
        Cria um professor com validações e áreas de competência.

        Args:
            nome: Nome do professor
            titulacao: Titulação (deve estar em TITULACAO_NIVEL_MAP)
            carga_maxima: Carga horária máxima
            modelo_contratacao: Modelo de contratação (Mensalista ou Horista)
            area_ids: Lista de IDs de áreas de competência

        Returns:
            Tupla (professor criado, mensagem de erro ou None)
        """
        # Validar titulação
        if titulacao not in TITULACAO_NIVEL_MAP:
            valid_titulacoes = ", ".join(TITULACAO_NIVEL_MAP.keys())
            return None, f"Titulação inválida. Válidas: {valid_titulacoes}"

        # Validar carga máxima
        if carga_maxima <= 0:
            return None, "Carga máxima deve ser maior que zero"

        # Validar modelo de contratação
        valid_modelos = ["Mensalista ", "Horista"]
        if modelo_contratacao not in valid_modelos:
            return None, f"Modelo de contratação inválido. Válidos: {', '.join(valid_modelos)}"

        # Obter nível da titulação
        nivel = TITULACAO_NIVEL_MAP[titulacao]

        # Criar professor
        prof, error = self.create(
            nome=nome,
            titulacao=titulacao,
            nivel=nivel,
            carga_maxima=carga_maxima,
            modelo_contratacao=modelo_contratacao
        )

        if error:
            return None, error

        # Adicionar áreas se fornecidas
        if area_ids:
            try:
                for area_id in area_ids:
                    area = self.db.query(AreaCompetencia).filter(
                        AreaCompetencia.id == area_id
                    ).first()
                    if not area:
                        return None, f"Área de competência com ID {area_id} não encontrada"
                    if area not in prof.areas:
                        prof.areas.append(area)

                self.db.commit()
                self.db.refresh(prof)
            except Exception as e:
                self.db.rollback()
                return None, f"Erro ao adicionar áreas: {str(e)}"

        return prof, None

    def add_area(self, professor_id: int, area_id: int) -> tuple[bool, Optional[str]]:
        """
        Adiciona uma área de competência a um professor.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        try:
            prof = self.get_by_id(professor_id)
            if not prof:
                return False, f"Professor com ID {professor_id} não encontrado"

            area = self.db.query(AreaCompetencia).filter(
                AreaCompetencia.id == area_id
            ).first()
            if not area:
                return False, f"Área de competência com ID {area_id} não encontrada"

            if area in prof.areas:
                return False, "Professor já possui esta competência"

            prof.areas.append(area)
            self.db.commit()
            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao adicionar área: {str(e)}"

    def remove_area(self, professor_id: int, area_id: int) -> tuple[bool, Optional[str]]:
        """
        Remove uma área de competência de um professor.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        try:
            prof = self.get_by_id(professor_id)
            if not prof:
                return False, f"Professor com ID {professor_id} não encontrado"

            area = self.db.query(AreaCompetencia).filter(
                AreaCompetencia.id == area_id
            ).first()
            if not area:
                return False, f"Área de competência com ID {area_id} não encontrada"

            if area not in prof.areas:
                return False, "Professor não possui esta competência"

            prof.areas.remove(area)
            self.db.commit()
            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao remover área: {str(e)}"

    def get_areas(self, professor_id: int) -> List[AreaCompetencia]:
        """Retorna as áreas de competência de um professor."""
        try:
            prof = self.get_by_id(professor_id)
            if not prof:
                return []
            return prof.areas
        except Exception as e:
            print(f"Erro ao listar áreas do professor: {str(e)}")
            return []

    def has_area_competence(self, professor_id: int, area_id: int) -> bool:
        """Verifica se um professor tem competência em uma área."""
        try:
            prof = self.get_by_id(professor_id)
            if not prof:
                return False
            return any(a.id == area_id for a in prof.areas)
        except Exception as e:
            print(f"Erro ao verificar competência: {str(e)}")
            return False

    def get_carga_total(self, professor_id: int) -> float:
        """Retorna a carga horária total alocada de um professor."""
        try:
            prof = self.get_by_id(professor_id)
            if not prof or not prof.alocacoes:
                return 0.0
            return float(sum(
                a.oferta.disciplina.carga_horaria
                for a in prof.alocacoes
                if a.oferta and a.oferta.disciplina
            ))
        except Exception as e:
            print(f"Erro ao calcular carga total: {str(e)}")
            return 0.0

    def get_carga_livre(self, professor_id: int) -> float:
        """Retorna a carga horária livre (máxima - alocada) de um professor."""
        try:
            prof = self.get_by_id(professor_id)
            if not prof:
                return 0.0
            carga_max = float(prof.carga_maxima)
            carga_total = self.get_carga_total(professor_id)
            return max(0.0, carga_max - carga_total)
        except Exception as e:
            print(f"Erro ao calcular carga livre: {str(e)}")
            return 0.0

    def get_percentual_carga(self, professor_id: int) -> float:
        """Retorna o percentual de carga utilizada (0.0 a 1.0)."""
        try:
            prof = self.get_by_id(professor_id)
            if not prof or float(prof.carga_maxima) == 0:
                return 0.0
            carga_total = self.get_carga_total(professor_id)
            return carga_total / float(prof.carga_maxima)
        except Exception as e:
            print(f"Erro ao calcular percentual de carga: {str(e)}")
            return 0.0

    def delete_with_validation(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta um professor com validação de dependências.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        prof = self.get_by_id(id)
        if not prof:
            return False, f"Professor com ID {id} não encontrado"

        # Verifica se há alocações vinculadas
        if prof.alocacoes:
            return False, "Não é possível deletar um professor que possui alocações"

        return self.delete(id)

