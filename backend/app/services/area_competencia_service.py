"""
Service para gerenciar Áreas de Competência.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import AreaCompetencia
from .base_service import BaseService


class AreaCompetenciaService(BaseService[AreaCompetencia]):
    """Service para operações CRUD de Áreas de Competência."""

    def __init__(self, db: Session):
        super().__init__(AreaCompetencia, db)

    def get_by_nome(self, nome: str) -> Optional[AreaCompetencia]:
        """Busca uma área pelo nome."""
        try:
            return self.db.query(AreaCompetencia).filter(
                AreaCompetencia.nome == nome
            ).first()
        except Exception as e:
            print(f"Erro ao buscar área por nome: {str(e)}")
            return None

    def exists_by_nome(self, nome: str) -> bool:
        """Verifica se uma área com este nome já existe."""
        return self.get_by_nome(nome) is not None

    def list_all_ordered(self) -> List[AreaCompetencia]:
        """Lista todas as áreas ordenadas por nome."""
        try:
            return self.db.query(AreaCompetencia).order_by(
                AreaCompetencia.nome
            ).all()
        except Exception as e:
            print(f"Erro ao listar áreas: {str(e)}")
            return []

    def create_if_not_exists(self, nome: str) -> tuple[AreaCompetencia, Optional[str]]:
        """
        Cria uma área apenas se ela não existir.

        Returns:
            Tupla (área, mensagem de erro ou None)
        """
        existing = self.get_by_nome(nome)
        if existing:
            return existing, None

        return self.create(nome=nome)

    def delete_with_validation(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta uma área com validação de dependências.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        area = self.get_by_id(id)
        if not area:
            return False, f"Área com ID {id} não encontrada"

        # Verifica se há disciplinas vinculadas
        if area.disciplinas:
            return False, "Não é possível deletar uma área que possui disciplinas vinculadas"

        # Verifica se há professores vinculados
        if area.professores:
            return False, "Não é possível deletar uma área que possui professores vinculados"

        return self.delete(id)

