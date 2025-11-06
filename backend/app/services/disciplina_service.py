"""
Service para gerenciar Disciplinas.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Disciplina, AreaCompetencia
from .base_service import BaseService


class DisciplinaService(BaseService[Disciplina]):
    """Service para operações CRUD de Disciplinas."""

    def __init__(self, db: Session):
        super().__init__(Disciplina, db)

    def get_by_nome(self, nome: str) -> Optional[Disciplina]:
        """Busca uma disciplina pelo nome."""
        try:
            return self.db.query(Disciplina).filter(
                Disciplina.nome == nome
            ).first()
        except Exception as e:
            print(f"Erro ao buscar disciplina por nome: {str(e)}")
            return None

    def exists_by_nome(self, nome: str) -> bool:
        """Verifica se uma disciplina com este nome já existe."""
        return self.get_by_nome(nome) is not None

    def list_all_ordered(self) -> List[Disciplina]:
        """Lista todas as disciplinas ordenadas por nome."""
        try:
            return self.db.query(Disciplina).order_by(
                Disciplina.nome
            ).all()
        except Exception as e:
            print(f"Erro ao listar disciplinas: {str(e)}")
            return []

    def get_by_area(self, area_id: int) -> List[Disciplina]:
        """Busca todas as disciplinas de uma área específica."""
        try:
            return self.db.query(Disciplina).filter(
                Disciplina.area_id == area_id
            ).order_by(Disciplina.nome).all()
        except Exception as e:
            print(f"Erro ao listar disciplinas por área: {str(e)}")
            return []

    def create_with_area(self, nome: str, carga_horaria: float,
                        nivel_esperado: int, area_id: int) -> tuple[Optional[Disciplina], Optional[str]]:
        """
        Cria uma disciplina com validações.

        Args:
            nome: Nome da disciplina
            carga_horaria: Carga horária em horas
            nivel_esperado: Nível esperado (0-4)
            area_id: ID da área de competência

        Returns:
            Tupla (disciplina criada, mensagem de erro ou None)
        """
        # Validar duplicata
        if self.exists_by_nome(nome):
            return None, f"A disciplina '{nome}' já existe"

        # Validar nível
        if not (0 <= nivel_esperado <= 4):
            return None, "Nível esperado deve estar entre 0 e 4"

        # Validar carga horária
        if carga_horaria <= 0:
            return None, "Carga horária deve ser maior que zero"

        # Validar área
        try:
            area = self.db.query(AreaCompetencia).filter(
                AreaCompetencia.id == area_id
            ).first()
            if not area:
                return None, f"Área de competência com ID {area_id} não encontrada"
        except Exception as e:
            return None, f"Erro ao validar área: {str(e)}"

        return self.create(
            nome=nome,
            carga_horaria=carga_horaria,
            nivel_esperado=nivel_esperado,
            area_id=area_id
        )

    def update_with_validation(self, id: int, **kwargs) -> tuple[Optional[Disciplina], Optional[str]]:
        """
        Atualiza uma disciplina com validações.

        Returns:
            Tupla (disciplina atualizada, mensagem de erro ou None)
        """
        disc = self.get_by_id(id)
        if not disc:
            return None, f"Disciplina com ID {id} não encontrada"

        # Validar nível se fornecido
        if 'nivel_esperado' in kwargs:
            if not (0 <= kwargs['nivel_esperado'] <= 4):
                return None, "Nível esperado deve estar entre 0 e 4"

        # Validar carga horária se fornecida
        if 'carga_horaria' in kwargs:
            if kwargs['carga_horaria'] <= 0:
                return None, "Carga horária deve ser maior que zero"

        # Validar área se fornecida
        if 'area_id' in kwargs:
            try:
                area = self.db.query(AreaCompetencia).filter(
                    AreaCompetencia.id == kwargs['area_id']
                ).first()
                if not area:
                    return None, f"Área de competência com ID {kwargs['area_id']} não encontrada"
            except Exception as e:
                return None, f"Erro ao validar área: {str(e)}"

        return self.update(id, **kwargs)

    def delete_with_validation(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta uma disciplina com validação de dependências.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        disc = self.get_by_id(id)
        if not disc:
            return False, f"Disciplina com ID {id} não encontrada"

        # Verifica se há ofertas vinculadas
        if disc.ofertas:
            return False, "Não é possível deletar uma disciplina que possui ofertas vinculadas"

        return self.delete(id)

