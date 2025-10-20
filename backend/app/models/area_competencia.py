from ..extensions import db

class AreaCompetencia(db.Model):
    __tablename__ = 'area_competencia'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True, nullable=False)

    disciplinas = db.relationship('Disciplina', back_populates='area', lazy='select')
    professores = db.relationship('Professor', secondary='professor_area_competencia', back_populates='areas', lazy='select')

    def __repr__(self):
        return f"<AreaCompetencia id={self.id} nome={self.nome!r}>"

