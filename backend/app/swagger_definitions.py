"""
Documentação Swagger dos endpoints em YAML.
"""

AREAS_SWAGGER = {
    'tags': ['Áreas de Competência'],
    'definitions': {
        'Area': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'nome': {'type': 'string'}
            },
            'required': ['nome']
        }
    }
}

DISCIPLINAS_SWAGGER = {
    'tags': ['Disciplinas'],
    'definitions': {
        'Disciplina': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'nome': {'type': 'string'},
                'carga_horaria': {'type': 'number'},
                'nivel_esperado': {'type': 'integer', 'minimum': 0, 'maximum': 4},
                'area_id': {'type': 'integer'}
            },
            'required': ['nome', 'carga_horaria', 'nivel_esperado', 'area_id']
        }
    }
}

PROFESSORES_SWAGGER = {
    'tags': ['Professores'],
    'definitions': {
        'Professor': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'nome': {'type': 'string'},
                'titulacao': {
                    'type': 'string',
                    'enum': ['Ensino Médio', 'Graduado', 'Especialista', 'Mestre', 'Doutor']
                },
                'nivel': {'type': 'integer', 'minimum': 0, 'maximum': 4},
                'carga_maxima': {'type': 'number'},
                'modelo_contratacao': {'type': 'string', 'enum': ['Mensalista ', 'Horista']},
                'areas': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/Area'}
                }
            },
            'required': ['nome', 'titulacao', 'modelo_contratacao']
        }
    }
}

SEMESTRES_SWAGGER = {
    'tags': ['Semestres Letivos'],
    'definitions': {
        'SemestreLetivo': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'nome': {'type': 'string'},
                'ano': {'type': 'integer'},
                'periodo': {'type': 'string'},
                'data_inicio': {'type': 'string', 'format': 'date'},
                'data_fim': {'type': 'string', 'format': 'date'}
            },
            'required': ['nome', 'ano', 'periodo', 'data_inicio', 'data_fim']
        }
    }
}

OFERTAS_SWAGGER = {
    'tags': ['Ofertas'],
    'definitions': {
        'Oferta': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'semestre_id': {'type': 'integer'},
                'disciplina_id': {'type': 'integer'},
                'turma': {'type': 'string'},
                'semestre': {'$ref': '#/definitions/SemestreLetivo'},
                'disciplina': {'$ref': '#/definitions/Disciplina'}
            },
            'required': ['semestre_id', 'disciplina_id', 'turma']
        }
    }
}

ALOCACOES_SWAGGER = {
    'tags': ['Alocações'],
    'definitions': {
        'Alocacao': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'oferta_id': {'type': 'integer'},
                'professor_id': {'type': 'integer'},
                'oferta': {'$ref': '#/definitions/Oferta'},
                'professor': {'$ref': '#/definitions/Professor'}
            },
            'required': ['oferta_id', 'professor_id']
        }
    }
}

IMPORT_SWAGGER = {
    'tags': ['Importação'],
    'definitions': {
        'ImportResult': {
            'type': 'object',
            'properties': {
                'relatorio': {'type': 'string'},
                'estatisticas': {
                    'type': 'object',
                    'properties': {
                        'areas_criadas': {'type': 'integer'},
                        'professores_criados': {'type': 'integer'},
                        'disciplinas_criadas': {'type': 'integer'},
                        'ofertas_criadas': {'type': 'integer'},
                        'alocacoes_criadas': {'type': 'integer'},
                        'erros': {'type': 'array', 'items': {'type': 'string'}}
                    }
                }
            }
        }
    }
}

AG_SWAGGER = {
    'tags': ['Algoritmo Genético'],
    'definitions': {
        'AGConfig': {
            'type': 'object',
            'properties': {
                'num_geracoes': {'type': 'integer', 'minimum': 1},
                'tamanho_populacao': {'type': 'integer', 'minimum': 2},
                'probabilidade_crossover': {'type': 'number', 'minimum': 0.0, 'maximum': 1.0},
                'probabilidade_mutacao': {'type': 'number', 'minimum': 0.0, 'maximum': 1.0},
                'seed': {'type': 'integer', 'nullable': True},
                'elite_size': {'type': 'integer', 'minimum': 0},
                'torneio_size': {'type': 'integer', 'minimum': 2}
            }
        },
        'AGData': {
            'type': 'object',
            'properties': {
                'semestre': {'type': 'string'},
                'total_professores': {'type': 'integer'},
                'total_ofertas': {'type': 'integer'},
                'professores': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'nome': {'type': 'string'},
                            'areas': {'type': 'array'}
                        }
                    }
                },
                'ofertas': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'disciplina_nome': {'type': 'string'},
                            'carga_horaria': {'type': 'number'}
                        }
                    }
                }
            }
        }
    }
}

# Documentação de respostas comuns
RESPONSE_SUCCESS = {
    'type': 'object',
    'properties': {
        'status': {'type': 'string', 'example': 'success'},
        'message': {'type': 'string'},
        'data': {'type': 'object'}
    }
}

RESPONSE_ERROR = {
    'type': 'object',
    'properties': {
        'status': {'type': 'string', 'example': 'error'},
        'message': {'type': 'string'},
        'errors': {'type': 'array', 'items': {'type': 'string'}}
    }
}

RESPONSE_PAGINATED = {
    'type': 'object',
    'properties': {
        'status': {'type': 'string', 'example': 'success'},
        'message': {'type': 'string'},
        'data': {'type': 'array'},
        'pagination': {
            'type': 'object',
            'properties': {
                'page': {'type': 'integer'},
                'per_page': {'type': 'integer'},
                'total': {'type': 'integer'},
                'pages': {'type': 'integer'}
            }
        }
    }
}

