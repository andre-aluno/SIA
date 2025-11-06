"""
Controller para Áreas de Competência.
"""
from flask import Blueprint, request
from app.services import AreaCompetenciaService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController
from app.models import AreaCompetencia

bp = Blueprint('areas', __name__, url_prefix='/api/areas')


class AreaCompetenciaController(BaseController):
    """Controller para gerenciar Áreas de Competência."""

    def __init__(self, db):
        self.db = db
        self.service = AreaCompetenciaService(db)

    def create(self):
        """Cria nova área de competência."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        # Validar campos obrigatórios
        error = self.validate_required_fields(data, ['nome'])
        if error:
            return error

        # Criar área
        area, service_error = self.service.create(nome=data['nome'])

        if service_error:
            return ApiResponse.bad_request(service_error)

        return ApiResponse.created(
            self.serialize_obj(area),
            f"Área '{area.nome}' criada com sucesso"
        )

    def list_all(self):
        """Lista todas as áreas de competência."""
        page, per_page = self.get_pagination_params()

        areas = self.service.list_all_ordered()
        total = len(areas)

        # Aplicar paginação
        start = (page - 1) * per_page
        end = start + per_page
        paginated = areas[start:end]

        return self.handle_service_list(paginated, total, page, per_page)

    def get_by_id(self, id: int):
        """Obtém uma área pelo ID."""
        area = self.service.get_by_id(id)

        if not area:
            return ApiResponse.not_found(f"Área com ID {id} não encontrada")

        return ApiResponse.success(self.serialize_obj(area))

    def get_by_nome(self, nome: str):
        """Obtém uma área pelo nome."""
        area = self.service.get_by_nome(nome)

        if not area:
            return ApiResponse.not_found(f"Área '{nome}' não encontrada")

        return ApiResponse.success(self.serialize_obj(area))

    def update(self, id: int):
        """Atualiza uma área."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        if not data:
            return ApiResponse.bad_request("Nenhum dado para atualizar")

        area, service_error = self.service.update(id, **data)

        return self.handle_service_error(
            area,
            service_error,
            f"Área atualizada com sucesso"
        )

    def delete(self, id: int):
        """Deleta uma área."""
        success, error = self.service.delete_with_validation(id)

        if not success:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(None, "Área deletada com sucesso")

    def count(self):
        """Retorna total de áreas."""
        total = self.service.count()
        return ApiResponse.success({"total": total})


def register_area_routes(app, db):
    """Registra rotas de áreas de competência."""
    controller = AreaCompetenciaController(db)

    @bp.route('', methods=['POST'])
    def create_area():
        """
        POST /api/areas - Cria nova área de competência.
        ---
        tags:
          - Áreas de Competência
        summary: Criar nova área
        description: Cria uma nova área de competência no sistema
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
                  example: "Programação Python"
              required:
                - nome
        responses:
          201:
            description: Área criada com sucesso
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "success"
                message:
                  type: string
                data:
                  type: object
                  properties:
                    id:
                      type: integer
                    nome:
                      type: string
          400:
            description: Erro de validação
        """
        return controller.create()

    @bp.route('', methods=['GET'])
    def list_areas():
        """
        GET /api/areas - Lista todas as áreas de competência.
        ---
        tags:
          - Áreas de Competência
        summary: Listar áreas
        description: Retorna lista paginada de áreas de competência
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
            description: Número da página
          - name: per_page
            in: query
            type: integer
            default: 10
            description: Itens por página (máximo 100)
        responses:
          200:
            description: Lista de áreas
            schema:
              type: object
              properties:
                status:
                  type: string
                message:
                  type: string
                data:
                  type: array
                  items:
                    type: object
                pagination:
                  type: object
                  properties:
                    page:
                      type: integer
                    per_page:
                      type: integer
                    total:
                      type: integer
                    pages:
                      type: integer
        """
        return controller.list_all()

    @bp.route('/<int:id>', methods=['GET'])
    def get_area(id):
        """
        GET /api/areas/{id} - Obtém uma área pelo ID.
        ---
        tags:
          - Áreas de Competência
        summary: Obter área por ID
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da área
        responses:
          200:
            description: Área encontrada
          404:
            description: Área não encontrada
        """
        return controller.get_by_id(id)

    @bp.route('/by-nome/<nome>', methods=['GET'])
    def get_area_by_nome(nome):
        """
        GET /api/areas/by-nome/{nome} - Obtém uma área pelo nome.
        ---
        tags:
          - Áreas de Competência
        summary: Buscar por nome
        parameters:
          - name: nome
            in: path
            type: string
            required: true
            description: Nome da área
        responses:
          200:
            description: Área encontrada
          404:
            description: Área não encontrada
        """
        return controller.get_by_nome(nome)

    @bp.route('/<int:id>', methods=['PUT'])
    def update_area(id):
        """
        PUT /api/areas/{id} - Atualiza uma área.
        ---
        tags:
          - Áreas de Competência
        summary: Atualizar área
        parameters:
          - name: id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
        responses:
          200:
            description: Área atualizada com sucesso
          404:
            description: Área não encontrada
          400:
            description: Erro de validação
        """
        return controller.update(id)

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_area(id):
        """
        DELETE /api/areas/{id} - Deleta uma área.
        ---
        tags:
          - Áreas de Competência
        summary: Deletar área
        parameters:
          - name: id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Área deletada com sucesso
          404:
            description: Área não encontrada
          400:
            description: Não é possível deletar (dependências)
        """
        return controller.delete(id)

    @bp.route('/stats/count', methods=['GET'])
    def count_areas():
        """
        GET /api/areas/stats/count - Retorna total de áreas.
        ---
        tags:
          - Áreas de Competência
        summary: Contar áreas
        description: Retorna o total de áreas de competência cadastradas
        responses:
          200:
            description: Total de áreas
            schema:
              type: object
              properties:
                status:
                  type: string
                data:
                  type: object
                  properties:
                    total:
                      type: integer
        """
        return controller.count()

    app.register_blueprint(bp)
