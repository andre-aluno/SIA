"""
Aplicação Flask - Entry point do backend.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Flasgger
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Imports locais
from app.extensions import db
from app.controllers import register_all_routes
from app.utils.api_response import ApiResponse
from app.swagger_config import SWAGGER_CONFIG, SWAGGER_TEMPLATE


def create_app():
    """Factory function para criar a aplicação Flask."""

    app = Flask(__name__)

    # Configurações
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # Banco de dados
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://alocacao:senha_segura_123@db:5432/alocacao_professor')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensões
    db.init_app(app)
    CORS(app)

    # Inicializar Swagger/Flasgger
    Flasgger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # Criar tabelas apenas se necessário, com proteção contra concorrência
    with app.app_context():
        try:
            # Verificar se as tabelas já existem antes de tentar criar
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            if not existing_tables:
                print("Criando tabelas do banco de dados...")
                db.create_all()
                print("Tabelas criadas com sucesso!")
            else:
                print(f"Tabelas já existem no banco: {existing_tables}")

        except Exception as e:
            print(f"Aviso: Erro ao verificar/criar tabelas: {e}")
            # Tentar criar tabelas mesmo assim, ignorando erros de duplicação
            try:
                db.create_all()
            except:
                pass  # Se falhar, continua sem interromper a aplicação

    # Registrar blueprints de rotas
    register_all_routes(app, db.session)

    # Rota de health check
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Verifica saúde da API.
        ---
        tags:
          - Health
        responses:
          200:
            description: API está operacional
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "success"
                message:
                  type: string
                  example: "API está operacional"
                data:
                  type: object
                  properties:
                    status:
                      type: string
                      example: "online"
                    version:
                      type: string
                      example: "1.0.0"
        """
        return ApiResponse.success({
            "status": "online",
            "version": "1.0.0"
        }, "API está operacional")

    # Rota raiz
    @app.route('/', methods=['GET'])
    def index():
        """
        Página inicial da API.
        ---
        tags:
          - Info
        responses:
          200:
            description: Informações da API
        """
        return ApiResponse.success({
            "nome": "Sistema de Alocação de Professores",
            "versao": "1.0.0",
            "endpoints": {
                "areas": "/api/areas",
                "disciplinas": "/api/disciplinas",
                "professores": "/api/professores",
                "semestres": "/api/semestres",
                "ofertas": "/api/ofertas",
                "alocacoes": "/api/alocacoes",
                "importacao": "/api/import",
                "algoritmo_genetico": "/api/ag",
                "health": "/health",
                "swagger": "/api/docs"
            }
        }, "Sistema de Alocação de Professores")

    # Tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        """Trata erros 404."""
        return ApiResponse.not_found("Endpoint não encontrado")

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Trata erros 405."""
        return ApiResponse.error("Método HTTP não permitido", 405)

    @app.errorhandler(500)
    def internal_error(error):
        """Trata erros 500."""
        return ApiResponse.server_error("Erro interno do servidor")

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Trata exceções genéricas."""
        return ApiResponse.server_error(f"Erro: {str(error)}")

    return app


def main():
    """Entry point para executar a aplicação."""
    app = create_app()

    # Configurações de ambiente
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 3001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"\n{'='*70}")
    print(f"🚀 Iniciando Sistema de Alocação de Professores")
    print(f"{'='*70}")
    print(f"🌐 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📚 Documentação Swagger: http://{host}:{port}/api/docs")
    print(f"💚 Health Check: http://{host}:{port}/health")
    print(f"{'='*70}\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
