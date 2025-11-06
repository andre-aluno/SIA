"""
Controller para Disciplinas.
"""
from flask import Blueprint
from app.services import DisciplinaService, AreaCompetenciaService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('disciplinas', __name__, url_prefix='/api/disciplinas')


class DisciplinaController(BaseController):
    """Controller para gerenciar Disciplinas."""

    def __init__(self, db):
        self.db = db
        self.service = DisciplinaService(db)
        self.area_service = AreaCompetenciaService(db)

    def create(self):
        """POST /api/disciplinas - Cria nova disciplina."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['nome', 'carga_horaria', 'nivel_esperado', 'area_id'])
        if error:
            return error

        try:
            carga_horaria = float(data['carga_horaria'])
            nivel_esperado = int(data['nivel_esperado'])
            area_id = int(data['area_id'])
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Valores numéricos inválidos")

        disc, service_error = self.service.create_with_area(
            nome=data['nome'],
            carga_horaria=carga_horaria,
            nivel_esperado=nivel_esperado,
            area_id=area_id
        )

        if service_error:
            return ApiResponse.bad_request(service_error)

        return ApiResponse.created(
            self.serialize_obj(disc),
            f"Disciplina '{disc.nome}' criada com sucesso"
        )

    def list_all(self):
        """GET /api/disciplinas - Lista todas as disciplinas."""
        page, per_page = self.get_pagination_params()

        disciplinas = self.service.list_all_ordered()
        total = len(disciplinas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = disciplinas[start:end]

        # Serialize disciplinas with proper area objects
        serialized_disciplinas = []
        for disc in paginated:
            data = self.serialize_obj(disc)
            if disc.area:
                data['area'] = self.serialize_obj(disc.area)
            serialized_disciplinas.append(data)

        return ApiResponse.list_response(
            serialized_disciplinas,
            total,
            page,
            per_page,
            "Sucesso"
        )

    def get_by_id(self, id: int):
        """GET /api/disciplinas/<id> - Obtém disciplina pelo ID."""
        disc = self.service.get_by_id(id)

        if not disc:
            return ApiResponse.not_found(f"Disciplina com ID {id} não encontrada")

        data = self.serialize_obj(disc)
        if disc.area:
            data['area'] = self.serialize_obj(disc.area)

        return ApiResponse.success(data)

    def get_by_area(self, area_id: int):
        """GET /api/disciplinas/area/<area_id> - Obtém disciplinas de uma área."""
        page, per_page = self.get_pagination_params()

        disciplinas = self.service.get_by_area(area_id)
        total = len(disciplinas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = disciplinas[start:end]

        # Serialize disciplinas with proper area objects
        serialized_disciplinas = []
        for disc in paginated:
            data = self.serialize_obj(disc)
            if disc.area:
                data['area'] = self.serialize_obj(disc.area)
            serialized_disciplinas.append(data)

        return ApiResponse.list_response(
            serialized_disciplinas,
            total,
            page,
            per_page,
            "Sucesso"
        )

    def update(self, id: int):
        """PUT /api/disciplinas/<id> - Atualiza disciplina."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        if not data:
            return ApiResponse.bad_request("Nenhum dado para atualizar")

        # Converter valores numéricos se fornecidos
        if 'carga_horaria' in data:
            try:
                data['carga_horaria'] = float(data['carga_horaria'])
            except (ValueError, TypeError):
                return ApiResponse.bad_request("Carga horária deve ser numérica")

        if 'nivel_esperado' in data:
            try:
                data['nivel_esperado'] = int(data['nivel_esperado'])
            except (ValueError, TypeError):
                return ApiResponse.bad_request("Nível esperado deve ser inteiro")

        disc, service_error = self.service.update_with_validation(id, **data)

        return self.handle_service_error(disc, service_error, "Disciplina atualizada com sucesso")

    def delete(self, id: int):
        """DELETE /api/disciplinas/<id> - Deleta disciplina."""
        success, error = self.service.delete_with_validation(id)

        if not success:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(None, "Disciplina deletada com sucesso")


def register_disciplina_routes(app, db):
    """Registra rotas de disciplinas."""
    controller = DisciplinaController(db)

    @bp.route('', methods=['POST'])
    def create_disciplina():
        """
        POST /api/disciplinas - Cria nova disciplina.
        ---
        tags:
          - Disciplinas
        summary: Criar nova disciplina
        description: Cria uma nova disciplina no sistema
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
                carga_horaria:
                  type: number
                  example: 64.0
                nivel_esperado:
                  type: integer
                  example: 3
                area_id:
                  type: integer
                  example: 1
              required:
                - nome
                - carga_horaria
                - nivel_esperado
                - area_id
        responses:
          201:
            description: Disciplina criada com sucesso
          400:
            description: Erro de validação
        """
        return controller.create()

    @bp.route('', methods=['GET'])
    def list_disciplinas():
        """
        GET /api/disciplinas - Lista todas as disciplinas.
        ---
        tags:
          - Disciplinas
        summary: Listar disciplinas
        description: Lista todas as disciplinas cadastradas no sistema
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
            description: Itens por página
        responses:
          200:
            description: Lista de disciplinas
        """
        return controller.list_all()

    @bp.route('/<int:id>', methods=['GET'])
    def get_disciplina(id):
        """
        GET /api/disciplinas/{id} - Obtém disciplina pelo ID.
        ---
        tags:
          - Disciplinas
        summary: Buscar disciplina por ID
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da disciplina
        responses:
          200:
            description: Dados da disciplina
          404:
            description: Disciplina não encontrada
        """
        return controller.get_by_id(id)

    @bp.route('/area/<int:area_id>', methods=['GET'])
    def get_disciplinas_by_area(area_id):
        """
        GET /api/disciplinas/area/{area_id} - Obtém disciplinas de uma área.
        ---
        tags:
          - Disciplinas
        summary: Buscar disciplinas por área de competência
        parameters:
          - name: area_id
            in: path
            type: integer
            required: true
            description: ID da área de competência
        responses:
          200:
            description: Lista de disciplinas da área
        """
        return controller.get_by_area(area_id)

    @bp.route('/<int:id>', methods=['PUT'])
    def update_disciplina(id):
        """
        PUT /api/disciplinas/{id} - Atualiza disciplina.
        ---
        tags:
          - Disciplinas
        summary: Atualizar dados da disciplina
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da disciplina
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
                carga_horaria:
                  type: number
                nivel_esperado:
                  type: integer
                area_id:
                  type: integer
        responses:
          200:
            description: Disciplina atualizada com sucesso
          400:
            description: Erro de validação
          404:
            description: Disciplina não encontrada
        """
        return controller.update(id)

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_disciplina(id):
        """
        DELETE /api/disciplinas/{id} - Deleta disciplina.
        ---
        tags:
          - Disciplinas
        summary: Excluir disciplina
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da disciplina
        responses:
          200:
            description: Disciplina deletada com sucesso
          400:
            description: Erro de validação (disciplina pode estar sendo usada)
          404:
            description: Disciplina não encontrada
        """
        return controller.delete(id)

    app.register_blueprint(bp)
