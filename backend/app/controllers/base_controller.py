"""
Controller base com métodos comuns para todos os controllers.
"""
from typing import Any, Dict, Optional, List, Callable
from flask import request
from app.utils.api_response import ApiResponse


class BaseController:
    """Classe base para controllers com métodos comuns."""

    @staticmethod
    def get_pagination_params() -> tuple:
        """
        Extrai parâmetros de paginação da query string.

        Returns:
            Tupla (page, per_page)
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Validar
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        return page, per_page

    @staticmethod
    def get_json_data() -> Optional[Dict]:
        """
        Obtém e valida JSON do corpo da requisição.

        Returns:
            Dicionário com dados ou None
        """
        try:
            data = request.get_json()
            if data is None:
                return {}
            return data
        except Exception as e:
            return None

    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> Optional[tuple]:
        """
        Valida se todos os campos obrigatórios estão presentes.

        Args:
            data: Dicionário com dados
            required_fields: Lista de campos obrigatórios

        Returns:
            Tupla de erro se houver campos faltando, None caso contrário
        """
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)

        if missing:
            return ApiResponse.bad_request(
                f"Campos obrigatórios faltando: {', '.join(missing)}",
                [f"Campo obrigatório: {f}" for f in missing]
            )

        return None

    @staticmethod
    def serialize_obj(obj: Any, exclude_fields: Optional[List[str]] = None) -> Dict:
        """
        Serializa um objeto SQLAlchemy em dicionário.

        Args:
            obj: Objeto a serializar
            exclude_fields: Campos a excluir

        Returns:
            Dicionário com dados
        """
        if obj is None:
            return {}

        exclude_fields = exclude_fields or []
        result = {}

        for key, value in obj.__dict__.items():
            if key.startswith('_') or key in exclude_fields:
                continue

            # Converter valores especiais
            if value is None:
                result[key] = None
            elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
                # Evitar recursão infinita com objetos relacionados
                result[key] = str(value)
            else:
                result[key] = value

        return result

    @staticmethod
    def serialize_list(objects: List[Any], exclude_fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Serializa uma lista de objetos.

        Args:
            objects: Lista de objetos
            exclude_fields: Campos a excluir

        Returns:
            Lista de dicionários
        """
        return [BaseController.serialize_obj(obj, exclude_fields) for obj in objects]

    @staticmethod
    def handle_service_error(obj: Any, error: Optional[str], success_message: str = "",
                           status_code: int = 200) -> tuple:
        """
        Trata erros retornados pelos services.

        Args:
            obj: Objeto retornado pelo service
            error: Mensagem de erro (se houver)
            success_message: Mensagem de sucesso
            status_code: Código HTTP em caso de sucesso

        Returns:
            Resposta formatada
        """
        if error:
            return ApiResponse.bad_request(error)

        if obj is None:
            return ApiResponse.not_found("Recurso não encontrado")

        return ApiResponse.success(
            BaseController.serialize_obj(obj),
            success_message,
            status_code
        )

    @staticmethod
    def handle_service_list(objects: List[Any], total: int = None,
                           page: int = 1, per_page: int = 10,
                           message: str = "Sucesso") -> tuple:
        """
        Trata listas retornadas pelos services.

        Args:
            objects: Lista de objetos
            total: Total de objetos
            page: Página atual
            per_page: Itens por página
            message: Mensagem

        Returns:
            Resposta formatada com paginação
        """
        if total is None:
            total = len(objects)

        return ApiResponse.list_response(
            BaseController.serialize_list(objects),
            total,
            page,
            per_page,
            message
        )
