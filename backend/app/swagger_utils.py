"""
Decoradores e utilitários para documentação Swagger.
"""
from functools import wraps


def swagger_doc(**kwargs):
    """Decorador para adicionar documentação Swagger a um endpoint."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **func_kwargs):
            return f(*args, **func_kwargs)

        # Adicionar documentação ao docstring
        if 'description' in kwargs:
            decorated_function.__doc__ = kwargs['description']

        # Adicionar metadados Swagger
        decorated_function.swagger_doc = kwargs
        return decorated_function
    return decorator


def get_swagger_yaml(method, path, description, params=None, request_body=None, responses=None, tags=None):
    """
    Gera YAML Swagger para um endpoint.

    Args:
        method: GET, POST, PUT, DELETE, etc
        path: Caminho do endpoint
        description: Descrição do endpoint
        params: Lista de parâmetros (query, path)
        request_body: Schema do corpo da requisição
        responses: Dicionário de respostas HTTP
        tags: Tags para agrupar endpoints

    Returns:
        String YAML formatada
    """
    yaml = f"""
---
tags:
  {yaml_list(tags or [])}
summary: {description}
description: {description}
parameters:
"""

    if params:
        for param in params:
            yaml += f"""  - name: {param['name']}
    in: {param.get('in', 'query')}
    required: {str(param.get('required', False)).lower()}
    schema:
      type: {param.get('type', 'string')}
"""

    if request_body:
        yaml += f"""requestBody:
  required: true
  content:
    application/json:
      schema:
        {yaml_schema(request_body)}
"""

    yaml += """responses:
"""

    if responses:
        for status, response in responses.items():
            yaml += f"""  '{status}':
    description: {response.get('description', '')}
"""
            if 'schema' in response:
                yaml += f"""    content:
      application/json:
        schema:
          {yaml_schema(response['schema'])}
"""

    return yaml


def yaml_list(items):
    """Formata lista para YAML."""
    if not items:
        return "[]"
    return "\n  ".join([f"- {item}" for item in items])


def yaml_schema(schema):
    """Formata schema para YAML."""
    if isinstance(schema, dict):
        lines = []
        for key, value in schema.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                lines.append(f"  {yaml_schema(value)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    return str(schema)

