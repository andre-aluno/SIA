"""
Controller para Ofertas de Disciplinas.
"""
from flask import Blueprint
from app.services import OfertaService, SemestreLetivoService, DisciplinaService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('ofertas', __name__, url_prefix='/api/ofertas')


class OfertaController(BaseController):
    """Controller para gerenciar Ofertas de Disciplinas."""

    def __init__(self, db):
        self.db = db
        self.service = OfertaService(db)
        self.semestre_service = SemestreLetivoService(db)
        self.disciplina_service = DisciplinaService(db)

    def create(self):
        """POST /api/ofertas - Cria nova oferta."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['semestre_id', 'disciplina_id', 'turma'])
        if error:
            return error

        try:
            semestre_id = int(data['semestre_id'])
            disciplina_id = int(data['disciplina_id'])
        except (ValueError, TypeError):
            return ApiResponse.bad_request("IDs devem ser inteiros")

        oferta, service_error = self.service.create_with_validation(
            semestre_id=semestre_id,
            disciplina_id=disciplina_id,
            turma=data['turma']
        )

        if service_error:
            return ApiResponse.bad_request(service_error)

        result = self.serialize_obj(oferta)
        if oferta.semestre:
            result['semestre'] = self.serialize_obj(oferta.semestre)
        if oferta.disciplina:
            result['disciplina'] = self.serialize_obj(oferta.disciplina)

        return ApiResponse.created(result, f"Oferta criada com sucesso")

    def list_all(self):
        """GET /api/ofertas - Lista todas as ofertas."""
        page, per_page = self.get_pagination_params()

        ofertas = self.service.list_all_ordered()
        total = len(ofertas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = ofertas[start:end]

        result = []
        for oferta in paginated:
            oferta_data = self.serialize_obj(oferta)
            if oferta.semestre:
                oferta_data['semestre'] = self.serialize_obj(oferta.semestre)
            if oferta.disciplina:
                oferta_data['disciplina'] = self.serialize_obj(oferta.disciplina)
            result.append(oferta_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_by_id(self, id: int):
        """GET /api/ofertas/<id> - Obtém oferta pelo ID."""
        oferta = self.service.get_by_id(id)

        if not oferta:
            return ApiResponse.not_found(f"Oferta com ID {id} não encontrada")

        result = self.serialize_obj(oferta)
        if oferta.semestre:
            result['semestre'] = self.serialize_obj(oferta.semestre)
        if oferta.disciplina:
            result['disciplina'] = self.serialize_obj(oferta.disciplina)

        return ApiResponse.success(result)

    def get_by_semestre(self, semestre_id: int):
        """GET /api/ofertas/semestre/<semestre_id> - Ofertas de um semestre."""
        page, per_page = self.get_pagination_params()

        ofertas = self.service.get_by_semestre(semestre_id)
        total = len(ofertas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = ofertas[start:end]

        result = []
        for oferta in paginated:
            oferta_data = self.serialize_obj(oferta)
            if oferta.disciplina:
                oferta_data['disciplina'] = self.serialize_obj(oferta.disciplina)
            result.append(oferta_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_by_semestre_nome(self, semestre_nome: str):
        """GET /api/ofertas/semestre-nome/<nome> - Ofertas por nome do semestre."""
        page, per_page = self.get_pagination_params()

        ofertas = self.service.get_by_semestre_nome(semestre_nome)
        total = len(ofertas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = ofertas[start:end]

        result = []
        for oferta in paginated:
            oferta_data = self.serialize_obj(oferta)
            if oferta.disciplina:
                oferta_data['disciplina'] = self.serialize_obj(oferta.disciplina)
            result.append(oferta_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_by_disciplina(self, disciplina_id: int):
        """GET /api/ofertas/disciplina/<disciplina_id> - Ofertas de uma disciplina."""
        page, per_page = self.get_pagination_params()

        ofertas = self.service.get_by_disciplina(disciplina_id)
        total = len(ofertas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = ofertas[start:end]

        result = []
        for oferta in paginated:
            oferta_data = self.serialize_obj(oferta)
            if oferta.semestre:
                oferta_data['semestre'] = self.serialize_obj(oferta.semestre)
            result.append(oferta_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_nao_alocadas(self, semestre_id: int):
        """GET /api/ofertas/semestre/<id>/nao-alocadas - Ofertas sem alocação."""
        page, per_page = self.get_pagination_params()

        ofertas = self.service.get_ofertas_nao_alocadas(semestre_id)
        total = len(ofertas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = ofertas[start:end]

        result = []
        for oferta in paginated:
            oferta_data = self.serialize_obj(oferta)
            if oferta.disciplina:
                oferta_data['disciplina'] = self.serialize_obj(oferta.disciplina)
            result.append(oferta_data)

        return ApiResponse.list_response(result, total, page, per_page,
                                        message="Ofertas não alocadas")

    def get_nao_alocadas_by_nome(self, semestre_nome: str):
        """GET /api/ofertas/semestre-nome/<nome>/nao-alocadas - Não alocadas por nome."""
        page, per_page = self.get_pagination_params()

        ofertas = self.service.get_ofertas_nao_alocadas_by_semestre_nome(semestre_nome)
        total = len(ofertas)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = ofertas[start:end]

        result = []
        for oferta in paginated:
            oferta_data = self.serialize_obj(oferta)
            if oferta.disciplina:
                oferta_data['disciplina'] = self.serialize_obj(oferta.disciplina)
            result.append(oferta_data)

        return ApiResponse.list_response(result, total, page, per_page,
                                        message="Ofertas não alocadas")

    def get_count_by_semestre(self, semestre_id: int):
        """GET /api/ofertas/semestre/<id>/count - Conta ofertas do semestre."""
        total = self.service.get_count_by_semestre(semestre_id)

        return ApiResponse.success({
            "semestre_id": semestre_id,
            "total_ofertas": total
        })

    def delete(self, id: int):
        """DELETE /api/ofertas/<id> - Deleta oferta."""
        success, error = self.service.delete_with_validation(id)

        if not success:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(None, "Oferta deletada com sucesso")


def register_oferta_routes(app, db):
    """Registra rotas de ofertas."""
    controller = OfertaController(db)

    @bp.route('', methods=['POST'])
    def create_oferta():
        """
        POST /api/ofertas - Cria nova oferta.
        ---
        tags:
          - Ofertas
        summary: Criar nova oferta de disciplina
        description: Cria uma nova oferta de disciplina para um semestre
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                semestre_id:
                  type: integer
                  example: 1
                disciplina_id:
                  type: integer
                  example: 1
                turma:
                  type: string
                  example: "A"
              required:
                - semestre_id
                - disciplina_id
                - turma
        responses:
          201:
            description: Oferta criada com sucesso
          400:
            description: Erro de validação
        """
        return controller.create()

    @bp.route('', methods=['GET'])
    def list_ofertas():
        """
        GET /api/ofertas - Lista todas as ofertas.
        ---
        tags:
          - Ofertas
        summary: Listar ofertas
        description: Lista todas as ofertas de disciplinas cadastradas
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
            description: Lista de ofertas
        """
        return controller.list_all()

    @bp.route('/<int:id>', methods=['GET'])
    def get_oferta(id):
        """
        GET /api/ofertas/{id} - Obtém oferta pelo ID.
        ---
        tags:
          - Ofertas
        summary: Buscar oferta por ID
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da oferta
        responses:
          200:
            description: Dados da oferta
          404:
            description: Oferta não encontrada
        """
        return controller.get_by_id(id)

    @bp.route('/semestre/<int:semestre_id>', methods=['GET'])
    def get_ofertas_by_semestre(semestre_id):
        """
        GET /api/ofertas/semestre/{semestre_id} - Ofertas de um semestre.
        ---
        tags:
          - Ofertas
        summary: Buscar ofertas por semestre
        parameters:
          - name: semestre_id
            in: path
            type: integer
            required: true
            description: ID do semestre letivo
        responses:
          200:
            description: Lista de ofertas do semestre
        """
        return controller.get_by_semestre(semestre_id)

    @bp.route('/semestre-nome/<semestre_nome>', methods=['GET'])
    def get_ofertas_by_semestre_nome(semestre_nome):
        """
        GET /api/ofertas/semestre-nome/{semestre_nome} - Ofertas por nome do semestre.
        ---
        tags:
          - Ofertas
        summary: Buscar ofertas por nome do semestre
        parameters:
          - name: semestre_nome
            in: path
            type: string
            required: true
            description: Nome do semestre (ex. "2024.1")
        responses:
          200:
            description: Lista de ofertas do semestre
        """
        return controller.get_by_semestre_nome(semestre_nome)

    @bp.route('/disciplina/<int:disciplina_id>', methods=['GET'])
    def get_ofertas_by_disciplina(disciplina_id):
        """
        GET /api/ofertas/disciplina/{disciplina_id} - Ofertas de uma disciplina.
        ---
        tags:
          - Ofertas
        summary: Buscar ofertas por disciplina
        parameters:
          - name: disciplina_id
            in: path
            type: integer
            required: true
            description: ID da disciplina
        responses:
          200:
            description: Lista de ofertas da disciplina
        """
        return controller.get_by_disciplina(disciplina_id)

    @bp.route('/semestre/<int:semestre_id>/nao-alocadas', methods=['GET'])
    def get_ofertas_nao_alocadas(semestre_id):
        """
        GET /api/ofertas/semestre/{semestre_id}/nao-alocadas - Ofertas não alocadas.
        ---
        tags:
          - Ofertas
        summary: Buscar ofertas não alocadas de um semestre
        parameters:
          - name: semestre_id
            in: path
            type: integer
            required: true
            description: ID do semestre letivo
        responses:
          200:
            description: Lista de ofertas sem professor alocado
        """
        return controller.get_nao_alocadas(semestre_id)

    @bp.route('/semestre-nome/<semestre_nome>/nao-alocadas', methods=['GET'])
    def get_ofertas_nao_alocadas_by_nome(semestre_nome):
        """
        GET /api/ofertas/semestre-nome/{semestre_nome}/nao-alocadas - Ofertas não alocadas por nome.
        ---
        tags:
          - Ofertas
        summary: Buscar ofertas não alocadas por nome do semestre
        parameters:
          - name: semestre_nome
            in: path
            type: string
            required: true
            description: Nome do semestre
        responses:
          200:
            description: Lista de ofertas sem professor alocado
        """
        return controller.get_nao_alocadas_by_nome(semestre_nome)

    @bp.route('/semestre/<int:semestre_id>/count', methods=['GET'])
    def count_ofertas_by_semestre(semestre_id):
        """
        GET /api/ofertas/semestre/{semestre_id}/count - Conta ofertas do semestre.
        ---
        tags:
          - Ofertas
        summary: Contar ofertas de um semestre
        parameters:
          - name: semestre_id
            in: path
            type: integer
            required: true
            description: ID do semestre letivo
        responses:
          200:
            description: Número total de ofertas do semestre
        """
        return controller.get_count_by_semestre(semestre_id)

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_oferta(id):
        """
        DELETE /api/ofertas/{id} - Deleta oferta.
        ---
        tags:
          - Ofertas
        summary: Excluir oferta
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da oferta
        responses:
          200:
            description: Oferta deletada com sucesso
          400:
            description: Erro de validação
          404:
            description: Oferta não encontrada
        """
        return controller.delete(id)

    app.register_blueprint(bp)
