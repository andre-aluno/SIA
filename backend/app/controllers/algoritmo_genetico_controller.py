"""
Controller para Algoritmo Genético e Otimização de Alocação.
"""
from flask import Blueprint
from app.services import AlgoritmoGeneticoService
from app.utils.api_response import ApiResponse
from .base_controller import BaseController

bp = Blueprint('ag', __name__, url_prefix='/api/ag')


class AlgoritmoGeneticoController(BaseController):
    """Controller para otimização com Algoritmo Genético."""

    def __init__(self, db):
        self.db = db
        self.service = AlgoritmoGeneticoService(db)

    def load_data(self, semestre_nome: str):
        """GET /api/ag/semestre/<nome>/dados - Carrega dados para AG."""
        professores, ofertas = self.service.load_data_for_semestre(semestre_nome)

        if not ofertas:
            return ApiResponse.bad_request(
                f"Nenhuma oferta não alocada encontrada para o semestre '{semestre_nome}'"
            )

        data = {
            "semestre": semestre_nome,
            "total_professores": len(professores),
            "total_ofertas": len(ofertas),
            "professores": [
                {
                    "id": p.id,
                    "nome": p.nome,
                    "titulacao": p.titulacao,
                    "nivel": p.nivel,
                    "carga_maxima": float(p.carga_maxima),
                    "areas": [{"id": a.id, "nome": a.nome} for a in p.areas]
                }
                for p in professores
            ],
            "ofertas": [
                {
                    "id": o.id,
                    "disciplina_nome": o.disciplina.nome,
                    "turma": o.turma,
                    "carga_horaria": float(o.disciplina.carga_horaria),
                    "nivel_esperado": o.disciplina.nivel_esperado,
                    "area": {
                        "id": o.disciplina.area.id,
                        "nome": o.disciplina.area.nome
                    }
                }
                for o in ofertas
            ]
        }

        return ApiResponse.success(data, "Dados carregados com sucesso")

    def validate_feasibility(self):
        """POST /api/ag/validar - Valida viabilidade da alocação."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['semestre_nome'])
        if error:
            return error

        semestre_nome = data['semestre_nome']

        professores, ofertas = self.service.load_data_for_semestre(semestre_nome)

        viavel, problemas = self.service.validate_feasibility(professores, ofertas)

        response = {
            "viavel": viavel,
            "total_professores": len(professores),
            "total_ofertas": len(ofertas),
            "problemas": problemas
        }

        if viavel:
            return ApiResponse.success(response, "Alocação é viável")
        else:
            return ApiResponse.success(response, "Existem problemas de viabilidade", 207)

    def get_config_defaults(self):
        """GET /api/ag/config/defaults - Retorna configuração padrão."""
        config = self.service.get_config_defaults()

        return ApiResponse.success(config, "Configuração padrão do AG")

    def validate_config(self):
        """POST /api/ag/config/validar - Valida configuração do AG."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        valid, error = self.service.get_config_validation(data)

        if not valid:
            return ApiResponse.bad_request(error)

        return ApiResponse.success(data, "Configuração válida")

    def calculate_fitness(self):
        """POST /api/ag/fitness - Calcula fitness de uma alocação."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['semestre_nome', 'alocacao'])
        if error:
            return error

        semestre_nome = data['semestre_nome']
        alocacao = data['alocacao']  # Lista onde índice = oferta, valor = professor_id

        if not isinstance(alocacao, list):
            return ApiResponse.bad_request("'alocacao' deve ser uma lista")

        try:
            alocacao = [int(x) for x in alocacao]
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Valores de 'alocacao' devem ser inteiros")

        professores, ofertas = self.service.load_data_for_semestre(semestre_nome)

        if len(alocacao) != len(ofertas):
            return ApiResponse.bad_request(
                f"Tamanho da alocação ({len(alocacao)}) não bate com total de ofertas ({len(ofertas)})"
            )

        metrics = self.service.calculate_fitness_metrics(alocacao, professores, ofertas)

        return ApiResponse.success(metrics, "Fitness calculado")

    def format_result(self):
        """POST /api/ag/formatar - Formata resultado da alocação."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['semestre_nome', 'alocacao'])
        if error:
            return error

        semestre_nome = data['semestre_nome']
        alocacao = data['alocacao']

        if not isinstance(alocacao, list):
            return ApiResponse.bad_request("'alocacao' deve ser uma lista")

        try:
            alocacao = [int(x) for x in alocacao]
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Valores de 'alocacao' devem ser inteiros")

        professores, ofertas = self.service.load_data_for_semestre(semestre_nome)

        if len(alocacao) != len(ofertas):
            return ApiResponse.bad_request(
                f"Tamanho da alocação ({len(alocacao)}) não bate com total de ofertas ({len(ofertas)})"
            )

        resultado = self.service.format_alocacao_result(alocacao, professores, ofertas)

        return ApiResponse.success(resultado, "Alocação formatada")

    def get_resumo(self):
        """POST /api/ag/resumo - Gera resumo executivo da alocação."""
        data = self.get_json_data()

        if data is None:
            return ApiResponse.bad_request("JSON inválido")

        error = self.validate_required_fields(data, ['semestre_nome', 'alocacao', 'metrics'])
        if error:
            return error

        semestre_nome = data['semestre_nome']
        alocacao = data['alocacao']
        metrics = data['metrics']

        if not isinstance(alocacao, list):
            return ApiResponse.bad_request("'alocacao' deve ser uma lista")

        try:
            alocacao = [int(x) for x in alocacao]
        except (ValueError, TypeError):
            return ApiResponse.bad_request("Valores de 'alocacao' devem ser inteiros")

        if not isinstance(metrics, dict):
            return ApiResponse.bad_request("'metrics' deve ser um dicionário")

        professores, ofertas = self.service.load_data_for_semestre(semestre_nome)

        if len(alocacao) != len(ofertas):
            return ApiResponse.bad_request(
                f"Tamanho da alocação ({len(alocacao)}) não bate com total de ofertas ({len(ofertas)})"
            )

        resumo = self.service.get_resumo_alocacao(alocacao, professores, ofertas, metrics)

        return ApiResponse.success(resumo, "Resumo da alocação")

    def get_info_semestre(self, semestre_nome: str):
        """GET /api/ag/semestre/<nome>/info - Informações gerais do semestre."""
        professores, ofertas = self.service.load_data_for_semestre(semestre_nome)

        viavel, problemas = self.service.validate_feasibility(professores, ofertas)

        carga_total_ofertas = sum(float(o.disciplina.carga_horaria) for o in ofertas)
        carga_total_professores = sum(float(p.carga_maxima) for p in professores)

        areas_necessarias = set(o.disciplina.area.id for o in ofertas)
        areas_disponiveis = set()
        for p in professores:
            for a in p.areas:
                areas_disponiveis.add(a.id)

        info = {
            "semestre": semestre_nome,
            "viavel": viavel,
            "problemas_encontrados": len(problemas),
            "professores": {
                "total": len(professores),
                "com_competencia": sum(1 for p in professores if p.areas)
            },
            "ofertas": {
                "total": len(ofertas),
                "carga_total_horas": carga_total_ofertas
            },
            "areas": {
                "necessarias": len(areas_necessarias),
                "disponiveis": len(areas_disponiveis),
                "cobertura": len(areas_necessarias & areas_disponiveis) / len(areas_necessarias) if areas_necessarias else 1.0
            },
            "capacidade": {
                "carga_total_professores": carga_total_professores,
                "carga_total_ofertas": carga_total_ofertas,
                "margem": carga_total_professores - carga_total_ofertas,
                "suficiente": carga_total_professores >= carga_total_ofertas
            }
        }

        return ApiResponse.success(info, "Informações do semestre")


def register_ag_routes(app, db):
    """Registra rotas do Algoritmo Genético."""
    controller = AlgoritmoGeneticoController(db)

    @bp.route('/semestre/<semestre_nome>/dados', methods=['GET'])
    def load_ag_data(semestre_nome):
        """
        GET /api/ag/semestre/{semestre_nome}/dados - Carrega dados para o algoritmo genético.
        ---
        tags:
          - Algoritmo Genético
        summary: Carregar dados do semestre
        description: Carrega professores e ofertas de um semestre para processamento pelo algoritmo genético
        parameters:
          - name: semestre_nome
            in: path
            type: string
            required: true
            description: Nome do semestre (ex. "2024.1")
        responses:
          200:
            description: Dados carregados com sucesso
          404:
            description: Semestre não encontrado
        """
        return controller.load_data(semestre_nome)

    @bp.route('/validar', methods=['POST'])
    def validate_feasibility():
        """
        POST /api/ag/validar - Valida viabilidade dos dados.
        ---
        tags:
          - Algoritmo Genético
        summary: Validar viabilidade dos dados
        description: Verifica se é possível alocar professores às ofertas com os dados fornecidos
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                professores:
                  type: array
                  items:
                    type: object
                ofertas:
                  type: array
                  items:
                    type: object
        responses:
          200:
            description: Validação concluída
          400:
            description: Dados inválidos
        """
        return controller.validate_feasibility()

    @bp.route('/config/defaults', methods=['GET'])
    def get_defaults():
        """
        GET /api/ag/config/defaults - Obtém configurações padrão do algoritmo.
        ---
        tags:
          - Algoritmo Genético
        summary: Obter configurações padrão
        description: Retorna as configurações padrão do algoritmo genético
        responses:
          200:
            description: Configurações padrão
        """
        return controller.get_config_defaults()

    @bp.route('/config/validar', methods=['POST'])
    def validate_configuration():
        """
        POST /api/ag/config/validar - Valida configuração do algoritmo.
        ---
        tags:
          - Algoritmo Genético
        summary: Validar configuração
        description: Valida os parâmetros de configuração do algoritmo genético
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                populacao:
                  type: integer
                  example: 50
                geracoes:
                  type: integer
                  example: 100
                taxa_mutacao:
                  type: number
                  example: 0.1
                taxa_crossover:
                  type: number
                  example: 0.8
        responses:
          200:
            description: Configuração válida
          400:
            description: Configuração inválida
        """
        return controller.validate_config()

    @bp.route('/fitness', methods=['POST'])
    def calculate_fitness():
        """
        POST /api/ag/fitness - Calcula fitness de uma solução.
        ---
        tags:
          - Algoritmo Genético
        summary: Calcular fitness
        description: Calcula o valor de fitness de uma solução de alocação
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                alocacao:
                  type: array
                  items:
                    type: object
                    properties:
                      oferta_id:
                        type: integer
                      professor_id:
                        type: integer
        responses:
          200:
            description: Fitness calculado
          400:
            description: Dados inválidos
        """
        return controller.calculate_fitness()

    @bp.route('/formatar', methods=['POST'])
    def format_result():
        """
        POST /api/ag/formatar - Formata resultado do algoritmo.
        ---
        tags:
          - Algoritmo Genético
        summary: Formatar resultado
        description: Formata o resultado do algoritmo genético para visualização
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                resultado:
                  type: object
                  description: Resultado bruto do algoritmo genético
        responses:
          200:
            description: Resultado formatado
          400:
            description: Dados inválidos
        """
        return controller.format_result()

    @bp.route('/resumo', methods=['POST'])
    def get_resumo():
        """
        POST /api/ag/resumo - Obtém resumo da execução.
        ---
        tags:
          - Algoritmo Genético
        summary: Obter resumo da execução
        description: Gera resumo estatístico da execução do algoritmo genético
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                resultado:
                  type: object
                  description: Resultado da execução do algoritmo
        responses:
          200:
            description: Resumo gerado
          400:
            description: Dados inválidos
        """
        return controller.get_resumo()

    @bp.route('/semestre/<semestre_nome>/info', methods=['GET'])
    def info_semestre(semestre_nome):
        """
        GET /api/ag/semestre/{semestre_nome}/info - Informações do semestre.
        ---
        tags:
          - Algoritmo Genético
        summary: Obter informações do semestre
        description: Retorna informações estatísticas sobre professores e ofertas do semestre
        parameters:
          - name: semestre_nome
            in: path
            type: string
            required: true
            description: Nome do semestre
        responses:
          200:
            description: Informações do semestre
          404:
            description: Semestre não encontrado
        """
        return controller.get_info_semestre(semestre_nome)

    app.register_blueprint(bp)
