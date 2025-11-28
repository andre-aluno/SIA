"""
Service para gerenciar Ofertas de Disciplinas.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Oferta, SemestreLetivo, Disciplina
from .base_service import BaseService


class OfertaService(BaseService[Oferta]):
    """Service para operações CRUD de Ofertas de Disciplinas."""

    def __init__(self, db: Session):
        super().__init__(Oferta, db)

    def list_all_ordered(self) -> List[Oferta]:
        """Lista todas as ofertas ordenadas por semestre e disciplina."""
        try:
            return self.db.query(Oferta).join(
                Oferta.semestre
            ).join(
                Oferta.disciplina
            ).order_by(
                SemestreLetivo.nome,
                Disciplina.nome
            ).all()
        except Exception as e:
            print(f"Erro ao listar ofertas: {str(e)}")
            return []

    def get_by_semestre(self, semestre_id: int) -> List[Oferta]:
        """Busca todas as ofertas de um semestre específico."""
        try:
            return self.db.query(Oferta).filter(
                Oferta.semestre_id == semestre_id
            ).join(
                Oferta.disciplina
            ).order_by(
                Disciplina.nome,
                Oferta.turma
            ).all()
        except Exception as e:
            print(f"Erro ao listar ofertas por semestre: {str(e)}")
            return []

    def get_by_semestre_nome(self, semestre_nome: str) -> List[Oferta]:
        """Busca ofertas por nome do semestre."""
        try:
            return self.db.query(Oferta).join(
                Oferta.semestre
            ).filter(
                SemestreLetivo.nome == semestre_nome
            ).join(
                Oferta.disciplina
            ).order_by(
                Disciplina.nome,
                Oferta.turma
            ).all()
        except Exception as e:
            print(f"Erro ao listar ofertas por semestre: {str(e)}")
            return []

    def get_by_disciplina(self, disciplina_id: int) -> List[Oferta]:
        """Busca todas as ofertas de uma disciplina específica."""
        try:
            return self.db.query(Oferta).filter(
                Oferta.disciplina_id == disciplina_id
            ).join(
                Oferta.semestre
            ).order_by(
                SemestreLetivo.nome,
                Oferta.turma
            ).all()
        except Exception as e:
            print(f"Erro ao listar ofertas por disciplina: {str(e)}")
            return []

    def exists_duplicate(self, semestre_id: int, disciplina_id: int, turma: str) -> bool:
        """Verifica se uma oferta (semestre, disciplina, turma) já existe."""
        try:
            return self.db.query(Oferta).filter(
                Oferta.semestre_id == semestre_id,
                Oferta.disciplina_id == disciplina_id,
                Oferta.turma == turma
            ).first() is not None
        except Exception as e:
            print(f"Erro ao verificar duplicata: {str(e)}")
            return False

    def create_with_validation(self, semestre_id: int, disciplina_id: int,
                              turma: str) -> tuple[Optional[Oferta], Optional[str]]:
        """
        Cria uma oferta com validações.

        Args:
            semestre_id: ID do semestre
            disciplina_id: ID da disciplina
            turma: Identificação da turma (ex: A, B, 01, etc)

        Returns:
            Tupla (oferta criada, mensagem de erro ou None)
        """
        # Validar turma
        if not turma or len(turma.strip()) == 0:
            return None, "Turma não pode estar vazia"

        # Validar semestre
        try:
            semestre = self.db.query(SemestreLetivo).filter(
                SemestreLetivo.id == semestre_id
            ).first()
            if not semestre:
                return None, f"Semestre com ID {semestre_id} não encontrado"
        except Exception as e:
            return None, f"Erro ao validar semestre: {str(e)}"

        # Validar disciplina
        try:
            disciplina = self.db.query(Disciplina).filter(
                Disciplina.id == disciplina_id
            ).first()
            if not disciplina:
                return None, f"Disciplina com ID {disciplina_id} não encontrada"
        except Exception as e:
            return None, f"Erro ao validar disciplina: {str(e)}"

        # Validar duplicata
        if self.exists_duplicate(semestre_id, disciplina_id, turma):
            return None, f"Oferta da disciplina '{disciplina.nome}' no semestre '{semestre.nome}' e turma '{turma}' já existe"

        return self.create(
            semestre_id=semestre_id,
            disciplina_id=disciplina_id,
            turma=turma
        )

    def get_ofertas_nao_alocadas(self, semestre_id: int) -> List[Oferta]:
        """
        Retorna ofertas de um semestre que ainda não possuem alocação.

        Args:
            semestre_id: ID do semestre

        Returns:
            Lista de ofertas sem alocação
        """
        try:
            return self.db.query(Oferta).filter(
                Oferta.semestre_id == semestre_id
            ).join(
                Oferta.disciplina
            ).filter(
                ~Oferta.alocacoes.any()
            ).order_by(
                Disciplina.nome,
                Oferta.turma
            ).all()
        except Exception as e:
            print(f"Erro ao listar ofertas não alocadas: {str(e)}")
            return []

    def get_ofertas_nao_alocadas_by_semestre_nome(self, semestre_nome: str) -> List[Oferta]:
        """
        Retorna ofertas de um semestre (por nome) que ainda não possuem alocação.

        Args:
            semestre_nome: Nome do semestre

        Returns:
            Lista de ofertas sem alocação
        """
        try:
            return self.db.query(Oferta).join(
                Oferta.semestre
            ).filter(
                SemestreLetivo.nome == semestre_nome
            ).join(
                Oferta.disciplina
            ).filter(
                ~Oferta.alocacoes.any()
            ).order_by(
                Disciplina.nome,
                Oferta.turma
            ).all()
        except Exception as e:
            print(f"Erro ao listar ofertas não alocadas: {str(e)}")
            return []

    def get_count_by_semestre(self, semestre_id: int) -> int:
        """Conta total de ofertas em um semestre."""
        try:
            return self.db.query(Oferta).filter(
                Oferta.semestre_id == semestre_id
            ).count()
        except Exception as e:
            print(f"Erro ao contar ofertas: {str(e)}")
            return 0

    def delete_with_validation(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta uma oferta com validação de dependências.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        oferta = self.get_by_id(id)
        if not oferta:
            return False, f"Oferta com ID {id} não encontrada"

        # Verifica se há alocações vinculadas
        if oferta.alocacoes:
            return False, "Não é possível deletar uma oferta que possui alocações"

        return self.delete(id)
