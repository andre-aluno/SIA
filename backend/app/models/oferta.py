from ..extensions import db
from sqlalchemy import UniqueConstraint, Index

class Oferta(db.Model):
    __tablename__ = 'oferta'
    __table_args__ = (
        UniqueConstraint('semestre_id', 'disciplina_id', 'turma', name='uq_oferta_semdisc_turma'),
        Index('ix_oferta_semestre_id', 'semestre_id'),
        Index('ix_oferta_disciplina_id', 'disciplina_id')
    )

    id = db.Column(db.Integer, primary_key=True)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id', ondelete='CASCADE'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id', ondelete='CASCADE'), nullable=False)
    turma = db.Column(db.String, nullable=False)

    semestre = db.relationship('SemestreLetivo', back_populates='ofertas', lazy='joined')
    disciplina = db.relationship('Disciplina', back_populates='ofertas', lazy='joined')
    alocacoes = db.relationship('Alocacao', back_populates='oferta', lazy='select')

    def __repr__(self):
        return f"<Oferta id={self.id} turma={self.turma!r}>"

