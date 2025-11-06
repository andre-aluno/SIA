"""
Service base com operações CRUD comuns para todas as entidades.
"""
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

T = TypeVar('T')


class BaseService(Generic[T]):
    """Classe base para services com operações CRUD genéricas."""

    def __init__(self, model: Type[T], db: Session):
        """
        Inicializa o service com um modelo e uma sessão do banco.

        Args:
            model: Classe do modelo SQLAlchemy
            db: Sessão do banco de dados
        """
        self.model = model
        self.db = db

    def create(self, **kwargs) -> tuple[T, Optional[str]]:
        """
        Cria um novo registro.

        Returns:
            Tupla (objeto criado, mensagem de erro ou None)
        """
        try:
            obj = self.model(**kwargs)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig) if e.orig else str(e)
            return None, f"Erro de integridade: {error_msg}"
        except SQLAlchemyError as e:
            self.db.rollback()
            return None, f"Erro ao criar {self.model.__name__}: {str(e)}"
        except Exception as e:
            self.db.rollback()
            return None, f"Erro inesperado: {str(e)}"

    def get_by_id(self, id: int) -> Optional[T]:
        """Busca um registro pelo ID."""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            print(f"Erro ao buscar {self.model.__name__} por ID: {str(e)}")
            return None

    def get_all(self) -> List[T]:
        """Busca todos os registros."""
        try:
            return self.db.query(self.model).all()
        except Exception as e:
            print(f"Erro ao listar {self.model.__name__}: {str(e)}")
            return []

    def update(self, id: int, **kwargs) -> tuple[Optional[T], Optional[str]]:
        """
        Atualiza um registro.

        Returns:
            Tupla (objeto atualizado, mensagem de erro ou None)
        """
        try:
            obj = self.get_by_id(id)
            if not obj:
                return None, f"{self.model.__name__} com ID {id} não encontrado"

            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            self.db.commit()
            self.db.refresh(obj)
            return obj, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig) if e.orig else str(e)
            return None, f"Erro de integridade: {error_msg}"
        except SQLAlchemyError as e:
            self.db.rollback()
            return None, f"Erro ao atualizar {self.model.__name__}: {str(e)}"
        except Exception as e:
            self.db.rollback()
            return None, f"Erro inesperado: {str(e)}"

    def delete(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta um registro.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        try:
            obj = self.get_by_id(id)
            if not obj:
                return False, f"{self.model.__name__} com ID {id} não encontrado"

            self.db.delete(obj)
            self.db.commit()
            return True, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig) if e.orig else str(e)
            return False, f"Erro de integridade ao deletar: {error_msg}"
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, f"Erro ao deletar {self.model.__name__}: {str(e)}"
        except Exception as e:
            self.db.rollback()
            return False, f"Erro inesperado: {str(e)}"

    def count(self) -> int:
        """Conta o total de registros."""
        try:
            return self.db.query(self.model).count()
        except Exception as e:
            print(f"Erro ao contar {self.model.__name__}: {str(e)}")
            return 0

