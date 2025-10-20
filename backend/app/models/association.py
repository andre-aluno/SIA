from ..extensions import db
from sqlalchemy import Index

professor_area_competencia = db.Table(
    'professor_area_competencia',
    db.Column('professor_id', db.Integer, db.ForeignKey('professor.id', ondelete='CASCADE'), primary_key=True),
    db.Column('area_id', db.Integer, db.ForeignKey('area_competencia.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_prof_area_area_id', 'area_id')
)

