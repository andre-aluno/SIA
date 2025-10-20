from ..extensions import db

class SemestreLetivo(db.Model):
    __tablename__ = 'semestre_letivo'
    __table_args__ = (
        db.CheckConstraint('data_inicio < data_fim', name='chk_semestre_datas'),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    periodo = db.Column(db.String, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)

    ofertas = db.relationship('Oferta', back_populates='semestre', lazy='select')

    def __repr__(self):
        return f"<SemestreLetivo id={self.id} nome={self.nome!r}>"

