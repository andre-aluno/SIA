"""
Utilidades para resposta padrão da API.
"""
from typing import Any, Dict, Optional, List
from flask import jsonify


class ApiResponse:
    """Classe para padronizar respostas da API."""

    @staticmethod
    def success(data: Any = None, message: str = "Sucesso", code: int = 200) -> tuple:
        """
        Retorna resposta de sucesso.

        Args:
            data: Dados a retornar
            message: Mensagem de sucesso
            code: Código HTTP

        Returns:
            Tupla (json, código HTTP)
        """
        response = {
            "status": "success",
            "message": message,
            "data": data
        }
        return jsonify(response), code

    @staticmethod
    def error(message: str, code: int = 400, errors: Optional[List[str]] = None) -> tuple:
        """
        Retorna resposta de erro.

        Args:
            message: Mensagem de erro
            code: Código HTTP
            errors: Lista de erros detalhados

        Returns:
            Tupla (json, código HTTP)
        """
        response = {
            "status": "error",
            "message": message,
            "errors": errors or []
        }
        return jsonify(response), code

    @staticmethod
    def created(data: Any, message: str = "Criado com sucesso") -> tuple:
        """Retorna resposta 201 Created."""
        return ApiResponse.success(data, message, 201)

    @staticmethod
    def not_found(message: str = "Recurso não encontrado") -> tuple:
        """Retorna resposta 404 Not Found."""
        return ApiResponse.error(message, 404)

    @staticmethod
    def bad_request(message: str = "Requisição inválida", errors: Optional[List[str]] = None) -> tuple:
        """Retorna resposta 400 Bad Request."""
        return ApiResponse.error(message, 400, errors)

    @staticmethod
    def server_error(message: str = "Erro interno do servidor") -> tuple:
        """Retorna resposta 500 Internal Server Error."""
        return ApiResponse.error(message, 500)

    @staticmethod
    def list_response(items: List[Any], total: int, page: int = 1,
                     per_page: int = 10, message: str = "Sucesso") -> tuple:
        """
        Retorna resposta paginada.

        Args:
            items: Lista de itens
            total: Total de itens
            page: Página atual
            per_page: Itens por página
            message: Mensagem

        Returns:
            Tupla (json, código HTTP)
        """
        response = {
            "status": "success",
            "message": message,
            "data": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
        return jsonify(response), 200

