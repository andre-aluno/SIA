"""
Arquivo de configuração para variáveis de ambiente.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuração base."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/alocacao_professor'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


def get_config():
    """Retorna configuração baseada em FLASK_ENV."""
    env = os.getenv('FLASK_ENV', 'development')

    if env == 'testing':
        return TestingConfig
    elif env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig

