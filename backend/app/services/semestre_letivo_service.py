"""
Service para gerenciar Semestres Letivos.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from ..models import SemestreLetivo
from .base_service import BaseService


class SemestreLetivoService(BaseService[SemestreLetivo]):
    """Service para operações CRUD de Semestres Letivos."""

    def __init__(self, db: Session):
        super().__init__(SemestreLetivo, db)

    def get_by_nome(self, nome: str) -> Optional[SemestreLetivo]:
        """Busca um semestre pelo nome."""
        try:
            return self.db.query(SemestreLetivo).filter(
                SemestreLetivo.nome == nome
            ).first()
        except Exception as e:
            print(f"Erro ao buscar semestre por nome: {str(e)}")
            return None

    def exists_by_nome(self, nome: str) -> bool:
        """Verifica se um semestre com este nome já existe."""
        return self.get_by_nome(nome) is not None

    def list_all_ordered(self) -> List[SemestreLetivo]:
        """Lista todos os semestres ordenados por nome."""
        try:
            return self.db.query(SemestreLetivo).order_by(
                SemestreLetivo.nome
            ).all()
        except Exception as e:
            print(f"Erro ao listar semestres: {str(e)}")
            return []

    def get_by_ano(self, ano: int) -> List[SemestreLetivo]:
        """Busca semestres de um ano específico."""
        try:
            return self.db.query(SemestreLetivo).filter(
                SemestreLetivo.ano == ano
            ).order_by(SemestreLetivo.nome).all()
        except Exception as e:
            print(f"Erro ao listar semestres por ano: {str(e)}")
            return []

    def create_with_validation(self, nome: str, ano: int, periodo: str,
                              data_inicio: date, data_fim: date) -> tuple[Optional[SemestreLetivo], Optional[str]]:
        """
        Cria um semestre letivo com validações.

        Args:
            nome: Nome do semestre (ex: 2025-1)
            ano: Ano do semestre
            periodo: Período (ex: EAD1, 1)
            data_inicio: Data de início
            data_fim: Data de fim

        Returns:
            Tupla (semestre criado, mensagem de erro ou None)
        """
        # Validar duplicata
        if self.exists_by_nome(nome):
            return None, f"O semestre '{nome}' já existe"

        # Validar datas
        if data_inicio >= data_fim:
            return None, "Data de início deve ser menor que data de fim"

        # Validar ano
        if ano < 1900 or ano > 2100:
            return None, "Ano deve estar entre 1900 e 2100"

        # Validar período
        if not periodo or len(periodo.strip()) == 0:
            return None, "Período não pode estar vazio"

        return self.create(
            nome=nome,
            ano=ano,
            periodo=periodo,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

    def update_with_validation(self, id: int, **kwargs) -> tuple[Optional[SemestreLetivo], Optional[str]]:
        """
        Atualiza um semestre letivo com validações.

        Returns:
            Tupla (semestre atualizado, mensagem de erro ou None)
        """
        sem = self.get_by_id(id)
        if not sem:
            return None, f"Semestre com ID {id} não encontrado"

        # Validar ano se fornecido
        if 'ano' in kwargs:
            if kwargs['ano'] < 1900 or kwargs['ano'] > 2100:
                return None, "Ano deve estar entre 1900 e 2100"

        # Validar período se fornecido
        if 'periodo' in kwargs:
            if not kwargs['periodo'] or len(str(kwargs['periodo']).strip()) == 0:
                return None, "Período não pode estar vazio"

        # Validar datas se fornecidas
        data_inicio = kwargs.get('data_inicio', sem.data_inicio)
        data_fim = kwargs.get('data_fim', sem.data_fim)

        if data_inicio >= data_fim:
            return None, "Data de início deve ser menor que data de fim"

        return self.update(id, **kwargs)

    def get_semestres_ativos(self, reference_date: Optional[date] = None) -> List[SemestreLetivo]:
        """
        Retorna semestres que estão ativos em uma data de referência.
        Se nenhuma data for fornecida, usa a data atual.

        Args:
            reference_date: Data de referência (padrão: hoje)

        Returns:
            Lista de semestres ativos
        """
        try:
            if reference_date is None:
                reference_date = date.today()

            return self.db.query(SemestreLetivo).filter(
                SemestreLetivo.data_inicio <= reference_date,
                SemestreLetivo.data_fim >= reference_date
            ).order_by(SemestreLetivo.nome).all()
        except Exception as e:
            print(f"Erro ao listar semestres ativos: {str(e)}")
            return []

    def get_semestres_futuros(self, reference_date: Optional[date] = None) -> List[SemestreLetivo]:
        """
        Retorna semestres que iniciam após uma data de referência.

        Args:
            reference_date: Data de referência (padrão: hoje)

        Returns:
            Lista de semestres futuros
        """
        try:
            if reference_date is None:
                reference_date = date.today()

            return self.db.query(SemestreLetivo).filter(
                SemestreLetivo.data_inicio > reference_date
            ).order_by(SemestreLetivo.nome).all()
        except Exception as e:
            print(f"Erro ao listar semestres futuros: {str(e)}")
            return []

    def delete_with_validation(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta um semestre letivo com validação de dependências.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        sem = self.get_by_id(id)
        if not sem:
            return False, f"Semestre com ID {id} não encontrado"

        # Verifica se há ofertas vinculadas
        if sem.ofertas:
            return False, "Não é possível deletar um semestre que possui ofertas vinculadas"

        return self.delete(id)

