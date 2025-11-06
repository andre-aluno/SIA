"""
Controller para Semestres Letivos.
"""
from flask import Blueprint
from datetime import datetime
from app.services import SemestreLetivoService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('semestres', __name__, url_prefix='/api/semestres')


class SemestreLetivoController(BaseController):
    """Controller para gerenciar Semestres Letivos."""

    def __init__(self, db):
        self.db = db
        self.service = SemestreLetivoService(db)

    def create(self):
        """POST /api/semestres - Cria novo semestre letivo."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['nome', 'ano', 'periodo', 'data_inicio', 'data_fim'])
        if error:
            return error

        try:
            ano = int(data['ano'])
            # Parse datas (formato: YYYY-MM-DD ou DD/MM/YYYY)
            data_inicio = self._parse_date(data['data_inicio'])
            data_fim = self._parse_date(data['data_fim'])

            if not data_inicio or not data_fim:
                return ApiResponse.bad_request("Datas em formato inválido. Use YYYY-MM-DD ou DD/MM/YYYY")
        except (ValueError, TypeError) as e:
            return ApiResponse.bad_request(f"Erro ao processar dados: {str(e)}")

        sem, service_error = self.service.create_with_validation(
            nome=data['nome'],
            ano=ano,
            periodo=data['periodo'],
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        if service_error:
            return ApiResponse.bad_request(service_error)

        return ApiResponse.created(
            self.serialize_obj(sem),
            f"Semestre '{sem.nome}' criado com sucesso"
        )

    def list_all(self):
        """GET /api/semestres - Lista todos os semestres."""
        page, per_page = self.get_pagination_params()

        semestres = self.service.list_all_ordered()
        total = len(semestres)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = semestres[start:end]

        return self.handle_service_list(paginated, total, page, per_page)

    def get_by_id(self, id: int):
        """GET /api/semestres/<id> - Obtém semestre pelo ID."""
        sem = self.service.get_by_id(id)

        if not sem:
            return ApiResponse.not_found(f"Semestre com ID {id} não encontrado")

        return ApiResponse.success(self.serialize_obj(sem))

    def get_by_ano(self, ano: int):
        """GET /api/semestres/ano/<ano> - Obtém semestres de um ano."""
        page, per_page = self.get_pagination_params()

        semestres = self.service.get_by_ano(ano)
        total = len(semestres)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = semestres[start:end]

        return self.handle_service_list(paginated, total, page, per_page)

    def get_ativos(self):
        """GET /api/semestres/ativos - Retorna semestres ativos."""
        semestres = self.service.get_semestres_ativos()

        return ApiResponse.success(
            self.serialize_list(semestres),
            message="Semestres ativos"
        )

    def get_futuros(self):
        """GET /api/semestres/futuros - Retorna semestres futuros."""
        semestres = self.service.get_semestres_futuros()

        return ApiResponse.success(
            self.serialize_list(semestres),
            message="Semestres futuros"
        )

    def update(self, id: int):
        """PUT /api/semestres/<id> - Atualiza semestre."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        if not data:
            return ApiResponse.bad_request("Nenhum dado para atualizar")

        # Converter datas se fornecidas
        if 'data_inicio' in data:
            data_inicio = self._parse_date(data['data_inicio'])
            if not data_inicio:
                return ApiResponse.bad_request("Data de início em formato inválido")
            data['data_inicio'] = data_inicio

        if 'data_fim' in data:
            data_fim = self._parse_date(data['data_fim'])
            if not data_fim:
                return ApiResponse.bad_request("Data de fim em formato inválido")
            data['data_fim'] = data_fim

        if 'ano' in data:
            try:
                data['ano'] = int(data['ano'])
            except (ValueError, TypeError):
                return ApiResponse.bad_request("Ano deve ser inteiro")

        sem, service_error = self.service.update_with_validation(id, **data)

        return self.handle_service_error(sem, service_error, "Semestre atualizado com sucesso")

    def delete(self, id: int):
        """DELETE /api/semestres/<id> - Deleta semestre."""
        success, error = self.service.delete_with_validation(id)

        if not success:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(None, "Semestre deletado com sucesso")

    @staticmethod
    def _parse_date(date_str):
        """Parse data em múltiplos formatos."""
        if not date_str:
            return None

        # Tenta YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            pass

        # Tenta DD/MM/YYYY
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except:
            pass

        return None


def register_semestre_routes(app, db):
    """Registra rotas de semestres letivos."""
    controller = SemestreLetivoController(db)

    @bp.route('', methods=['POST'])
    def create_semestre():
        """
        POST /api/semestres - Cria novo semestre letivo.
        ---
        tags:
          - Semestres Letivos
        summary: Criar novo semestre letivo
        description: Cria um novo semestre letivo no sistema
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
                  example: "2024.1"
                ano:
                  type: integer
                  example: 2024
                periodo:
                  type: integer
                  example: 1
                data_inicio:
                  type: string
                  format: date
                  example: "2024-02-01"
                data_fim:
                  type: string
                  format: date
                  example: "2024-06-30"
              required:
                - nome
                - ano
                - periodo
        responses:
          201:
            description: Semestre criado com sucesso
          400:
            description: Erro de validação
        """
        return controller.create()

    @bp.route('', methods=['GET'])
    def list_semestres():
        """
        GET /api/semestres - Lista todos os semestres letivos.
        ---
        tags:
          - Semestres Letivos
        summary: Listar semestres letivos
        description: Lista todos os semestres letivos cadastrados
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
            description: Lista de semestres letivos
        """
        return controller.list_all()

    @bp.route('/<int:id>', methods=['GET'])
    def get_semestre(id):
        """
        GET /api/semestres/{id} - Obtém semestre pelo ID.
        ---
        tags:
          - Semestres Letivos
        summary: Buscar semestre por ID
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do semestre letivo
        responses:
          200:
            description: Dados do semestre letivo
          404:
            description: Semestre não encontrado
        """
        return controller.get_by_id(id)

    @bp.route('/ano/<int:ano>', methods=['GET'])
    def get_semestres_by_ano(ano):
        """
        GET /api/semestres/ano/{ano} - Semestres de um ano específico.
        ---
        tags:
          - Semestres Letivos
        summary: Buscar semestres por ano
        parameters:
          - name: ano
            in: path
            type: integer
            required: true
            description: Ano do semestre (ex. 2024)
        responses:
          200:
            description: Lista de semestres do ano
        """
        return controller.get_by_ano(ano)

    @bp.route('/ativos', methods=['GET'])
    def get_semestres_ativos():
        """
        GET /api/semestres/ativos - Semestres atualmente ativos.
        ---
        tags:
          - Semestres Letivos
        summary: Obter semestres ativos
        description: Lista semestres letivos que estão atualmente em andamento
        responses:
          200:
            description: Lista de semestres ativos
        """
        return controller.get_ativos()

    @bp.route('/futuros', methods=['GET'])
    def get_semestres_futuros():
        """
        GET /api/semestres/futuros - Semestres futuros.
        ---
        tags:
          - Semestres Letivos
        summary: Obter semestres futuros
        description: Lista semestres letivos que ainda não começaram
        responses:
          200:
            description: Lista de semestres futuros
        """
        return controller.get_futuros()

    @bp.route('/<int:id>', methods=['PUT'])
    def update_semestre(id):
        """
        PUT /api/semestres/{id} - Atualiza semestre letivo.
        ---
        tags:
          - Semestres Letivos
        summary: Atualizar dados do semestre letivo
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do semestre letivo
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nome:
                  type: string
                ano:
                  type: integer
                periodo:
                  type: integer
                data_inicio:
                  type: string
                  format: date
                data_fim:
                  type: string
                  format: date
        responses:
          200:
            description: Semestre atualizado com sucesso
          400:
            description: Erro de validação
          404:
            description: Semestre não encontrado
        """
        return controller.update(id)

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_semestre(id):
        """
        DELETE /api/semestres/{id} - Deleta semestre letivo.
        ---
        tags:
          - Semestres Letivos
        summary: Excluir semestre letivo
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID do semestre letivo
        responses:
          200:
            description: Semestre deletado com sucesso
          400:
            description: Erro de validação (semestre pode ter ofertas)
          404:
            description: Semestre não encontrado
        """
        return controller.delete(id)

    app.register_blueprint(bp)
