"""
Configuração do Swagger/OpenAPI com Flasgger.
"""

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Sistema de Alocação de Professores",
        "description": "API REST para gerenciar alocação de professores a disciplinas usando Algoritmo Genético",
        "version": "1.0.0",
        "contact": {
            "name": "CDIA",
            "email": "contato@cdia.com"
        }
    },
    "host": "localhost:3001",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header"
        }
    }
}

