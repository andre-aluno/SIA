from ..extensions import db
from .association import professor_area_competencia

TITULACOES = (
    'Ensino Médio', 'Graduado', 'Especialista', 'Mestre', 'Doutor'
)
MODELOS_CONTRATACAO = (
    'Mensalista ', 'Horista'
)

TITULACAO_NIVEL_MAP = {
    'Ensino Médio': 0,
    'Graduado': 1,
    'Especialista': 2,
    'Mestre': 3,
    'Doutor': 4
}

class Professor(db.Model):
    __tablename__ = 'professor'
    __table_args__ = (
        db.CheckConstraint('nivel BETWEEN 0 AND 4', name='chk_professor_nivel'),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    titulacao = db.Column(db.String, nullable=False)
    nivel = db.Column(db.Integer, nullable=False)
    carga_maxima = db.Column(db.Numeric(6, 2), nullable=False)
    modelo_contratacao = db.Column(db.String, nullable=False)

    areas = db.relationship('AreaCompetencia', secondary=professor_area_competencia, back_populates='professores', lazy='select')
    alocacoes = db.relationship('Alocacao', back_populates='professor', lazy='select')

    def __repr__(self):
        return f"<Professor id={self.id} nome={self.nome!r}>"

    @property
    def carga_total(self):
        # Soma a carga das disciplinas vinculadas via alocações
        return float(sum(a.oferta.disciplina.carga_horaria for a in self.alocacoes)) if self.alocacoes else 0.0

    @property
    def percentual_carga(self):
        if not self.carga_maxima:
            return 0.0
        return self.carga_total / float(self.carga_maxima)

