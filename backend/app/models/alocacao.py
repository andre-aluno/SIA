from ..extensions import db
from sqlalchemy import UniqueConstraint

class Alocacao(db.Model):
    __tablename__ = 'alocacao'
    __table_args__ = (
        # Garante apenas uma alocação por oferta (modelo atual)
        UniqueConstraint('oferta_id', name='uq_alocacao_oferta_unique'),
    )

    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.id', ondelete='CASCADE'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id', ondelete='CASCADE'), nullable=False)

    oferta = db.relationship('Oferta', back_populates='alocacoes', lazy='joined')
    professor = db.relationship('Professor', back_populates='alocacoes', lazy='joined')

    def __repr__(self):
        return f"<Alocacao id={self.id} oferta_id={self.oferta_id} professor_id={self.professor_id}>"

