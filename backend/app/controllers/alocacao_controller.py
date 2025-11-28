"""
Controller para Alocações de Professores.
"""
from flask import Blueprint
from app.services import AlocacaoService, OfertaService, ProfessorService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('alocacoes', __name__, url_prefix='/api/alocacoes')


class AlocacaoController(BaseController):
    """Controller para gerenciar Alocações de Professores."""

    def __init__(self, db):
        self.db = db
        self.service = AlocacaoService(db)
        self.oferta_service = OfertaService(db)
        self.professor_service = ProfessorService(db)

    def create(self):
        """POST /api/alocacoes - Cria nova alocação."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['oferta_id', 'professor_id'])
        if error:
            return error

        try:
            oferta_id = int(data['oferta_id'])
            professor_id = int(data['professor_id'])
        except (ValueError, TypeError):
            return ApiResponse.bad_request("IDs devem ser inteiros")

        alocacao, service_error = self.service.create_with_validation(
            oferta_id=oferta_id,
            professor_id=professor_id
        )

        if service_error:
            return ApiResponse.bad_request(service_error)

        result = self.serialize_obj(alocacao)
        if alocacao.oferta:
            result['oferta'] = self.serialize_obj(alocacao.oferta)
        if alocacao.professor:
            result['professor'] = self.serialize_obj(alocacao.professor)

        return ApiResponse.created(result, "Alocação criada com sucesso")

    def list_all(self):
        """GET /api/alocacoes - Lista todas as alocações."""
        page, per_page = self.get_pagination_params()

        alocacoes = self.service.list_all_ordered()
        total = len(alocacoes)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = alocacoes[start:end]

        result = []
        for aloc in paginated:
            aloc_data = self.serialize_obj(aloc)
            if aloc.oferta:
                aloc_data['oferta'] = self.serialize_obj(aloc.oferta)
            if aloc.professor:
                aloc_data['professor'] = self.serialize_obj(aloc.professor)
            result.append(aloc_data)

        return ApiResponse.list_response(result, total, page, per_page)

    def get_by_id(self, id: int):
        """GET /api/alocacoes/<id> - Obtém alocação pelo ID."""
        alocacao = self.service.get_by_id(id)

        if not alocacao:
            return ApiResponse.not_found(f"Alocação com ID {id} não encontrada")

        result = self.serialize_obj(alocacao)
        if alocacao.oferta:
            result['oferta'] = self.serialize_obj(alocacao.oferta)
        if alocacao.professor:
            result['professor'] = self.serialize_obj(alocacao.professor)

        return ApiResponse.success(result)

    def get_by_oferta(self, oferta_id: int):
        """GET /api/alocacoes/oferta/<oferta_id> - Alocação de uma oferta."""
        alocacao = self.service.get_by_oferta(oferta_id)

        if not alocacao:
            return ApiResponse.success(None, message="Oferta não possui alocação")

        result = self.serialize_obj(alocacao)
        if alocacao.professor:
            result['professor'] = self.serialize_obj(alocacao.professor)

        return ApiResponse.success(result)

    def get_by_professor(self, professor_id: int):
        """GET /api/alocacoes/professor/<professor_id> - Alocações de um professor."""
        page, per_page = self.get_pagination_params()

        alocacoes = self.service.get_by_professor(professor_id)
        total = len(alocacoes)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = alocacoes[start:end]

        result = []
        for aloc in paginated:
            aloc_data = self.serialize_obj(aloc)
            if aloc.oferta:
                aloc_data['oferta'] = self.serialize_obj(aloc.oferta)
            result.append(aloc_data)

        return ApiResponse.list_response(result, total, page, per_page,
                                        message="Alocações do professor")

    def get_by_semestre(self, semestre_id: int):
        """GET /api/alocacoes/semestre/<semestre_id> - Alocações de um semestre."""
        page, per_page = self.get_pagination_params()

        alocacoes = self.service.get_by_semestre(semestre_id)
        total = len(alocacoes)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = alocacoes[start:end]

        result = []
        for aloc in paginated:
            aloc_data = self.serialize_obj(aloc)
            if aloc.oferta:
                aloc_data['oferta'] = self.serialize_obj(aloc.oferta)
            if aloc.professor:
                aloc_data['professor'] = self.serialize_obj(aloc.professor)
            result.append(aloc_data)

        return ApiResponse.list_response(result, total, page, per_page,
                                        message="Alocações do semestre")

    def get_by_semestre_nome(self, semestre_nome: str):
        """GET /api/alocacoes/semestre-nome/<nome> - Alocações por nome do semestre."""
        page, per_page = self.get_pagination_params()

        alocacoes = self.service.get_by_semestre_nome(semestre_nome)
        total = len(alocacoes)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = alocacoes[start:end]

        result = []
        for aloc in paginated:
            aloc_data = self.serialize_obj(aloc)
            if aloc.oferta:
                aloc_data['oferta'] = self.serialize_obj(aloc.oferta)
            if aloc.professor:
                aloc_data['professor'] = self.serialize_obj(aloc.professor)
            result.append(aloc_data)

        return ApiResponse.list_response(result, total, page, per_page,
                                        message="Alocações do semestre")

    def get_resumo_professor_semestre(self, professor_id: int, semestre_id: int):
        """GET /api/alocacoes/resumo/professor/<prof_id>/semestre/<sem_id>"""
        resumo = self.service.get_resumo_professor_semestre(professor_id, semestre_id)

        if not resumo:
            return ApiResponse.not_found("Dados não encontrados")

        return ApiResponse.success(resumo, message="Resumo de alocações")

    def get_resumo_oferta_semestre(self, semestre_id: int):
        """GET /api/alocacoes/resumo/semestre/<sem_id>"""
        resumo = self.service.get_resumo_oferta_semestre(semestre_id)

        if not resumo:
            return ApiResponse.not_found("Dados não encontrados")

        return ApiResponse.success(resumo, message="Resumo de ofertas")

    def get_formatado_semestre(self, semestre_nome: str):
        """GET /api/alocacoes/semestre-nome/<nome>/formatado - Alocações formatadas."""
        alocacoes = self.service.get_alocacoes_by_semestre_formatted(semestre_nome)

        return ApiResponse.success(
            alocacoes,
            message="Alocações formatadas para exportação"
        )

    def bulk_create(self):
        """POST /api/alocacoes/bulk - Cria múltiplas alocações."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        if 'alocacoes' not in data or not isinstance(data['alocacoes'], list):
            return ApiResponse.bad_request("Campo 'alocacoes' deve ser uma lista")

        alocacoes, erros = self.service.bulk_create(data['alocacoes'])

        response = {
            "total_processadas": len(data['alocacoes']),
            "criadas_com_sucesso": len(alocacoes),
            "total_erros": len(erros),
            "erros": erros
        }

        if erros:
            response['alocacoes'] = [self.serialize_obj(a) for a in alocacoes]
            return ApiResponse.success(response, "Erro ao gerar alocações", 400)
        else:
            response['alocacoes'] = [self.serialize_obj(a) for a in alocacoes]
            return ApiResponse.success(response, "Todas as alocações criadas com sucesso", 201)

    def delete(self, id: int):
        """DELETE /api/alocacoes/<id> - Deleta alocação."""
        success, error = self.service.delete_with_feedback(id)

        if not success:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(None, "Alocação deletada com sucesso")


def register_alocacao_routes(app, db):
    """Registra rotas de alocações."""
    controller = AlocacaoController(db)

    @bp.route('', methods=['POST'])
    def create_alocacao():
        """
        POST /api/alocacoes - Cria nova alocação.
        ---
        tags:
          - Alocações
        summary: Criar nova alocação
        description: Cria uma nova alocação de professor para uma oferta de disciplina
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                oferta_id:
                  type: integer
                  example: 1
                professor_id:
                  type: integer
                  example: 1
              required:
                - oferta_id
                - professor_id
        responses:
          201:
            description: Alocação criada com sucesso
          400:
            description: Erro de validação
        """
        return controller.create()

    @bp.route('', methods=['GET'])
    def list_alocacoes():
        """
        GET /api/alocacoes - Lista todas as alocações.
        ---
        tags:
          - Alocações
        summary: Listar alocações
        description: Lista todas as alocações de professores
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
            description: Lista de alocações
        """
        return controller.list_all()

    @bp.route('/bulk', methods=['POST'])
    def bulk_create_alocacoes():
        """
        POST /api/alocacoes/bulk - Cria múltiplas alocações.
        ---
        tags:
          - Alocações
        summary: Criar alocações em lote
        description: Cria múltiplas alocações de uma vez
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                alocacoes:
                  type: array
                  items:
                    type: object
                    properties:
                      oferta_id:
                        type: integer
                      professor_id:
                        type: integer
              required:
                - alocacoes
        responses:
          201:
            description: Alocações criadas com sucesso
          400:
            description: Erro de validação
        """
        return controller.bulk_create()

    @bp.route('/<int:id>', methods=['GET'])
    def get_alocacao(id):
        """
        GET /api/alocacoes/{id} - Obtém alocação pelo ID.
        ---
        tags:
          - Alocações
        summary: Buscar alocação por ID
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID da alocação
        responses:
          200:
            description: Dados da alocação
          404:
            description: Alocação não encontrada
        """
        return controller.get_by_id(id)

    @bp.route('/oferta/<int:oferta_id>', methods=['GET'])
    def get_alocacao_by_oferta(oferta_id):
        """
        GET /api/alocacoes/oferta/{oferta_id} - Alocação de uma oferta.
        ---
        tags:
          - Alocações
        summary: Buscar alocação por oferta
        parameters:
          - name: oferta_id
            in: path
            type: integer
            required: true
            description: ID da oferta
        responses:
          200:
            description: Alocação da oferta
          404:
            description: Alocação não encontrada
        """
        return controller.get_by_oferta(oferta_id)

    @bp.route('/professor/<int:professor_id>', methods=['GET'])
    def get_alocacoes_by_professor(professor_id):
        """
        GET /api/alocacoes/professor/{professor_id} - Alocações de um professor.
        ---
        tags:
          - Alocações
        summary: Buscar alocações por professor
        parameters:
          - name: professor_id
            in: path
            type: integer
            required: true
            description: ID do professor
        responses:
          200:
            description: Lista de alocações do professor
        """
        return controller.get_by_professor(professor_id)

    @bp.route('/semestre/<int:semestre_id>', methods=['GET'])
    def get_alocacoes_by_semestre(semestre_id):
        """
        GET /api/alocacoes/semestre/{semestre_id} - Alocações de um semestre.
        ---
        tags:
          - Alocações
        summary: Buscar alocações por semestre
        parameters:
          - name: semestre_id
            in: path
            type: integer
            required: true
            description: ID do semestre
        responses:
          200:
            description: Lista de alocações do semestre
        """
        return controller.get_by_semestre(semestre_id)

    @bp.route('/semestre-nome/<semestre_nome>', methods=['GET'])
    def get_alocacoes_by_semestre_nome(semestre_nome):
        """
        GET /api/alocacoes/semestre-nome/{semestre_nome} - Alocações por nome do semestre.
        ---
        tags:
          - Alocações
        summary: Buscar alocações por nome do semestre
        parameters:
          - name: semestre_nome
            in: path
            type: string
            required: true
            description: Nome do semestre
        responses:
          200:
            description: Lista de alocações do semestre
        """
        return controller.get_by_semestre_nome(semestre_nome)

    @bp.route('/resumo/professor/<int:professor_id>/semestre/<int:semestre_id>', methods=['GET'])
    def resumo_professor_semestre(professor_id, semestre_id):
        """
        GET /api/alocacoes/resumo/professor/{professor_id}/semestre/{semestre_id} - Resumo do professor no semestre.
        ---
        tags:
          - Alocações
        summary: Resumo de alocações de professor no semestre
        parameters:
          - name: professor_id
            in: path
            type: integer
            required: true
            description: ID do professor
          - name: semestre_id
            in: path
            type: integer
            required: true
            description: ID do semestre
        responses:
          200:
            description: Resumo das alocações do professor
        """
        return controller.get_resumo_professor_semestre(professor_id, semestre_id)

    @bp.route('/resumo/semestre/<int:semestre_id>', methods=['GET'])
    def resumo_oferta_semestre(semestre_id):
        """
        GET /api/alocacoes/resumo/semestre/{semestre_id} - Resumo de ofertas do semestre.
        ---
        tags:
          - Alocações
        summary: Resumo de alocações do semestre
        parameters:
          - name: semestre_id
            in: path
            type: integer
            required: true
            description: ID do semestre
        responses:
          200:
            description: Resumo das ofertas e alocações do semestre
        """
        return controller.get_resumo_oferta_semestre(semestre_id)

    @bp.route('/semestre-nome/<semestre_nome>/formatado', methods=['GET'])
    def alocacoes_formatadas(semestre_nome):
        """
        GET /api/alocacoes/semestre-nome/{semestre_nome}/formatado - Alocações formatadas.
        ---
        tags:
          - Alocações
        summary: Obter alocações em formato estruturado
        parameters:
          - name: semestre_nome
            in: path
            type: string
            required: true
            description: Nome do semestre
        responses:
          200:
            description: Alocações em formato estruturado para visualização
        """
        return controller.get_formatado_semestre(semestre_nome)

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_alocacao(id):
        """DELETE /api/alocacoes/<id> - Deleta alocação."""
        return controller.delete(id)

    app.register_blueprint(bp)
