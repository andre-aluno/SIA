from ..extensions import db

class Disciplina(db.Model):
    __tablename__ = 'disciplina'
    __table_args__ = (
        db.CheckConstraint('nivel_esperado BETWEEN 0 AND 4', name='chk_disciplina_nivel'),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    carga_horaria = db.Column(db.Numeric(5, 2), nullable=False)
    nivel_esperado = db.Column(db.Integer, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area_competencia.id', ondelete='RESTRICT'), nullable=False)

    area = db.relationship('AreaCompetencia', back_populates='disciplinas', lazy='joined')
    ofertas = db.relationship('Oferta', back_populates='disciplina', lazy='select')

    def __repr__(self):
        return f"<Disciplina id={self.id} nome={self.nome!r}>"

