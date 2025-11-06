"""
Controller para Professores.
"""
from flask import Blueprint
from app.services import ProfessorService, AreaCompetenciaService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('professores', __name__, url_prefix='/api/professores')


class ProfessorController(BaseController):
    """Controller para gerenciar Professores."""

    def __init__(self, db):
        self.db = db
        self.service = ProfessorService(db)
        self.area_service = AreaCompetenciaService(db)

    def create(self):
        """POST /api/professores - Cria novo professor."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['nome', 'titulacao', 'modelo_contratacao'])
        if error:
            return error

        try:
            carga_maxima = float(data.get('carga_maxima', 256.0))
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Carga máxima deve ser numérica")

        area_ids = data.get('area_ids', [])

        prof, service_error = self.service.create_with_areas(
            nome=data['nome'],
            titulacao=data['titulacao'],
            carga_maxima=carga_maxima,
            modelo_contratacao=data['modelo_contratacao'],
            area_ids=area_ids
        )

        if service_error:
            return ApiResponse.bad_request(service_error)

        result = self.serialize_obj(prof)
        if prof.areas:
            result['areas'] = self.serialize_list(prof.areas)

        return ApiResponse.created(result, f"Professor '{prof.nome}' criado com sucesso")

    def list_all(self):
        """GET /api/professores - Lista todos os professores."""
        page, per_page = self.get_pagination_params()

        professores = self.service.list_all_ordered()
        total = len(professores)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = professores[start:end]

        result = []
        for prof in paginated:
            prof_data = self.serialize_obj(prof)
            if prof.areas:
                prof_data['areas'] = self.serialize_list(prof.areas)
            result.append(prof_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_by_id(self, id: int):
        """GET /api/professores/<id> - Obtém professor pelo ID."""
        prof = self.service.get_by_id(id)

        if not prof:
            return ApiResponse.not_found(f"Professor com ID {id} não encontrado")

        data = self.serialize_obj(prof)
        if prof.areas:
            data['areas'] = self.serialize_list(prof.areas)

        # Adicionar informações de carga
        data['carga_total'] = self.service.get_carga_total(id)
        data['carga_livre'] = self.service.get_carga_livre(id)
        data['percentual_carga'] = self.service.get_percentual_carga(id)

        return ApiResponse.success(data)

    def get_by_titulacao(self, titulacao: str):
        """GET /api/professores/titulacao/<titulacao> - Busca por titulação."""
        page, per_page = self.get_pagination_params()

        professores = self.service.get_by_titulacao(titulacao)
        total = len(professores)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = professores[start:end]

        result = []
        for prof in paginated:
            prof_data = self.serialize_obj(prof)
            if prof.areas:
                prof_data['areas'] = self.serialize_list(prof.areas)
            result.append(prof_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_by_area(self, area_id: int):
        """GET /api/professores/area/<area_id> - Professores com competência numa área."""
        page, per_page = self.get_pagination_params()

        professores = self.service.get_by_area(area_id)
        total = len(professores)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = professores[start:end]

        result = []
        for prof in paginated:
            prof_data = self.serialize_obj(prof)
            if prof.areas:
                prof_data['areas'] = self.serialize_list(prof.areas)
            result.append(prof_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def add_area(self, id: int):
        """POST /api/professores/<id>/areas - Adiciona área ao professor."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['area_id'])
        if error:
            return error

        try:
            area_id = int(data['area_id'])
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Area ID deve ser inteiro")

        success, service_error = self.service.add_area(id, area_id)

        if not success:
            return ApiResponse.bad_request(service_error)

        prof = self.service.get_by_id(id)
        result = self.serialize_obj(prof)
        if prof.areas:
            result['areas'] = self.serialize_list(prof.areas)

        return ApiResponse.success(result, "Área adicionada com sucesso")

    def remove_area(self, id: int):
        """DELETE /api/professores/<id>/areas/<area_id> - Remove área do professor."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['area_id'])
        if error:
            return error

        try:
            area_id = int(data['area_id'])
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Area ID deve ser inteiro")

        success, service_error = self.service.remove_area(id, area_id)

        if not success:
            return ApiResponse.bad_request(service_error)

        prof = self.service.get_by_id(id)
        result = self.serialize_obj(prof)
        if prof.areas:
            result['areas'] = self.serialize_list(prof.areas)

        return ApiResponse.success(result, "Área removida com sucesso")

    def get_carga_info(self, id: int):
        """GET /api/professores/<id>/carga - Informações de carga do professor."""
        prof = self.service.get_by_id(id)

        if not prof:
            return ApiResponse.not_found(f"Professor com ID {id} não encontrado")

        data = {
            "professor_id": id,
            "professor_nome": prof.nome,
            "carga_maxima": float(prof.carga_maxima),
            "carga_total": self.service.get_carga_total(id),
            "carga_livre": self.service.get_carga_livre(id),
            "percentual_utilizado": self.service.get_percentual_carga(id)
        }

        return ApiResponse.success(data)

    def update(self, id: int):
        """PUT /api/professores/<id> - Atualiza professor."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        if not data:
            return ApiResponse.bad_request("Nenhum dado para atualizar")

        if 'carga_maxima' in data:
            try:
                data['carga_maxima'] = float(data['carga_maxima'])
            except (ValueError, TypeError):
                return ApiResponse.bad_request("Carga máxima deve ser numérica")

        prof, service_error = self.service.update(id, **data)

        return self.handle_service_error(prof, service_error, "Professor atualizado com sucesso")

    def delete(self, id: int):
        """DELETE /api/professores/<id> - Deleta professor."""
        success, error = self.service.delete_with_validation(id)

        if not success:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(None, "Professor deletado com sucesso")


def register_professor_routes(app, db):
    """Registra rotas de professores."""
    controller = ProfessorController(db)

    @bp.route('', methods=['POST'])
    def create_professor():
        """
        POST /api/professores - Cria novo professor.
        ---
        tags:
          - Professores
        summary: Criar novo professor
        description: Cria um novo professor no sistema
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
                  example: "João Silva"
                titulacao:
                  type: string
                  example: "Doutor"
                carga_maxima:
                  type: number
                  example: 256.0
                modelo_contratacao:
                  type: string
                  example: "CLT"
                area_ids:
                  type: array
                  items:
                    type: integer
                  example: [1, 2]
              required:
                - nome
                - titulacao
                - modelo_contratacao
        responses:
          201:
            description: Professor criado com sucesso
          400:
            description: Erro de validação
        """
        return controller.create()

    @bp.route('', methods=['GET'])
    def list_professores():
        """
        GET /api/professores - Lista todos os professores.
        ---
        tags:
          - Professores
        summary: Listar professores
        description: Lista todos os professores cadastrados no sistema
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
            description: Lista de professores
        """
        return controller.list_all()

    @bp.route('/<int:id>', methods=['GET'])
    def get_professor(id):
        """
        GET /api/professores/{id} - Obtém professor pelo ID.
        ---
        tags:
          - Professores
        summary: Buscar professor por ID
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do professor
        responses:
          200:
            description: Dados do professor
          404:
            description: Professor não encontrado
        """
        return controller.get_by_id(id)

    @bp.route('/titulacao/<titulacao>', methods=['GET'])
    def get_professores_by_titulacao(titulacao):
        """
        GET /api/professores/titulacao/{titulacao} - Busca por titulação.
        ---
        tags:
          - Professores
        summary: Buscar professores por titulação
        parameters:
          - name: titulacao
            in: path
            type: string
            required: true
            description: Titulação do professor
        responses:
          200:
            description: Lista de professores com a titulação especificada
        """
        return controller.get_by_titulacao(titulacao)

    @bp.route('/area/<int:area_id>', methods=['GET'])
    def get_professores_by_area(area_id):
        """
        GET /api/professores/area/{area_id} - Professores com competência numa área.
        ---
        tags:
          - Professores
        summary: Buscar professores por área de competência
        parameters:
          - name: area_id
            in: path
            type: integer
            required: true
            description: ID da área de competência
        responses:
          200:
            description: Lista de professores competentes na área
        """
        return controller.get_by_area(area_id)

    @bp.route('/<int:id>/areas', methods=['POST'])
    def add_area_to_professor(id):
        """
        POST /api/professores/{id}/areas - Adiciona área ao professor.
        ---
        tags:
          - Professores
        summary: Adicionar área de competência ao professor
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do professor
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                area_id:
                  type: integer
                  example: 1
              required:
                - area_id
        responses:
          200:
            description: Área adicionada com sucesso
          400:
            description: Erro de validação
        """
        return controller.add_area(id)

    @bp.route('/<int:id>/areas', methods=['DELETE'])
    def remove_area_from_professor(id):
        """
        DELETE /api/professores/{id}/areas - Remove área do professor.
        ---
        tags:
          - Professores
        summary: Remover área de competência do professor
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do professor
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                area_id:
                  type: integer
                  example: 1
              required:
                - area_id
        responses:
          200:
            description: Área removida com sucesso
          400:
            description: Erro de validação
        """
        return controller.remove_area(id)

    @bp.route('/<int:id>/carga', methods=['GET'])
    def get_professor_carga(id):
        """
        GET /api/professores/{id}/carga - Informações de carga do professor.
        ---
        tags:
          - Professores
        summary: Obter informações de carga horária do professor
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do professor
        responses:
          200:
            description: Informações de carga do professor
          404:
            description: Professor não encontrado
        """
        return controller.get_carga_info(id)

    @bp.route('/<int:id>', methods=['PUT'])
    def update_professor(id):
        """
        PUT /api/professores/{id} - Atualiza professor.
        ---
        tags:
          - Professores
        summary: Atualizar dados do professor
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do professor
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
                titulacao:
                  type: string
                carga_maxima:
                  type: number
                modelo_contratacao:
                  type: string
        responses:
          200:
            description: Professor atualizado com sucesso
          400:
            description: Erro de validação
          404:
            description: Professor não encontrado
        """
        return controller.update(id)

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_professor(id):
        """
        DELETE /api/professores/{id} - Deleta professor.
        ---
        tags:
          - Professores
        summary: Excluir professor
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do professor
        responses:
          200:
            description: Professor deletado com sucesso
          400:
            description: Erro de validação (professor pode estar alocado)
          404:
            description: Professor não encontrado
        """
        return controller.delete(id)

    app.register_blueprint(bp)
