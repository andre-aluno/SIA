"""
Extensões do Flask (SQLAlchemy, etc).
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()


def create_app():
    """Factory function para criar app com banco de dados."""
    from flask import Flask

    app = Flask(__name__)
    db.init_app(app)

    return app

