"""
Controller para Importação de Dados.
"""
from flask import Blueprint, request
from werkzeug.utils import secure_filename
import os
from app.services import ImportService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('import', __name__, url_prefix='/api/import')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ImportController(BaseController):
    """Controller para importação de dados."""

    def __init__(self, db):
        self.db = db
        self.service = ImportService(db)

        # Criar pasta de upload se não existir
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def upload_excel(self):
        """POST /api/import/excel - Importa dados de arquivo Excel."""

        # Validar se arquivo foi enviado
        if 'file' not in request.files:
            return ApiResponse.bad_request("Nenhum arquivo enviado")

        file = request.files['file']

        if file.filename == '':
            return ApiResponse.bad_request("Arquivo não selecionado")

        if not allowed_file(file.filename):
            return ApiResponse.bad_request(
                "Tipo de arquivo não permitido. Use .xlsx ou .xls"
            )

        try:
            # Salvar arquivo temporariamente
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Importar dados
            sucesso, relatorio = self.service.import_from_excel(filepath)

            # Remover arquivo após importação
            if os.path.exists(filepath):
                os.remove(filepath)

            if sucesso:
                stats = self.service.get_stats()
                return ApiResponse.success({
                    "relatorio": relatorio,
                    "estatisticas": stats
                }, "Importação concluída com sucesso", 200)
            else:
                stats = self.service.get_stats()
                return ApiResponse.success({
                    "relatorio": relatorio,
                    "estatisticas": stats,
                    "erros": stats.get('erros', [])
                }, "Importação concluída com erros", 207)

        except Exception as e:
            # Remover arquivo em caso de erro
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)

            return ApiResponse.server_error(f"Erro ao processar arquivo: {str(e)}")

    def get_import_status(self):
        """GET /api/import/status - Retorna última importação realizada."""
        stats = self.service.get_stats()

        return ApiResponse.success({
            "estatisticas": stats
        }, "Status da importação")


def register_import_routes(app, db):
    """Registra rotas de importação."""
    controller = ImportController(db)

    @bp.route('/excel', methods=['POST'])
    def upload_excel():
        """
        POST /api/import/excel - Importa dados de arquivo Excel.
        ---
        tags:
          - Importação de Dados
        summary: Importar dados via Excel
        description: Faz upload e processa arquivo Excel com dados de professores e disciplinas
        consumes:
          - multipart/form-data
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: Arquivo Excel (.xlsx) com os dados
          - name: semestre_nome
            in: formData
            type: string
            required: true
            description: Nome do semestre (ex. "2024.1")
        responses:
          200:
            description: Dados importados com sucesso
          400:
            description: Erro no arquivo ou dados inválidos
        """
        return controller.upload_excel()

    @bp.route('/status', methods=['GET'])
    def import_status():
        """
        GET /api/import/status - Status da última importação.
        ---
        tags:
          - Importação de Dados
        summary: Status da importação
        description: Retorna informações sobre o status da última importação realizada
        responses:
          200:
            description: Status da importação
        """
        return controller.get_import_status()

    app.register_blueprint(bp)
