import os
import enum
import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Numeric, Date, ForeignKey, Table,
    Enum, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# ---------------------------------------------------------------------
# 1. Conexão e Sessão
# ---------------------------------------------------------------------
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://sia_user:sia_pass@db:5432/sia_db'
)

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL, echo=False)

@st.cache_resource
def get_session():
    SessionLocal = sessionmaker(bind=get_engine())
    return SessionLocal()

# ---------------------------------------------------------------------
# 2. Base ORM
# ---------------------------------------------------------------------
Base = declarative_base()

# ---------------------------------------------------------------------
# 3. Enumerações
# ---------------------------------------------------------------------
class TitulacaoEnum(enum.Enum):
    Ensino_Medio   = 'Ensino Médio'
    Graduado       = 'Graduado'
    Especialista   = 'Especialista'
    Mestre         = 'Mestre'
    Doutor         = 'Doutor'

class ModeloContratacaoEnum(enum.Enum):
    Mensalista = 'Mensalista '
    Horista    = 'Horista'

# ---------------------------------------------------------------------
# 4. Tabela associativa Professor ↔ Área (N:N)
# ---------------------------------------------------------------------
prof_area = Table(
    'professor_area_competencia', Base.metadata,
    Column('professor_id', Integer, ForeignKey('professor.id', ondelete='CASCADE'), primary_key=True),
    Column('area_id',      Integer, ForeignKey('area_competencia.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_prof_area_area_id', 'area_id')
)

# ---------------------------------------------------------------------
# 5. Modelos de Dados
# ---------------------------------------------------------------------
class AreaCompetencia(Base):
    __tablename__ = 'area_competencia'
    id   = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)

    disciplinas = relationship('Disciplina', back_populates='area')
    professores = relationship('Professor', secondary=prof_area, back_populates='areas')

class Professor(Base):
    __tablename__ = 'professor'
    __table_args__ = (
        CheckConstraint('nivel BETWEEN 0 AND 4', name='chk_professor_nivel'),
    )

    id                 = Column(Integer, primary_key=True)
    nome               = Column(String, nullable=False)
    titulacao          = Column(String, nullable=False)
    nivel              = Column(Integer, nullable=False)
    carga_maxima       = Column(Numeric(6,2), nullable=False)
    modelo_contratacao = Column(String, nullable=False)

    areas     = relationship('AreaCompetencia', secondary=prof_area, back_populates='professores')
    alocacoes = relationship('Alocacao', back_populates='professor')

class Disciplina(Base):
    __tablename__ = 'disciplina'
    __table_args__ = (
        CheckConstraint('nivel_esperado BETWEEN 0 AND 4', name='chk_disciplina_nivel'),
    )

    id             = Column(Integer, primary_key=True)
    nome           = Column(String, nullable=False)
    carga_horaria  = Column(Numeric(5,2), nullable=False)
    nivel_esperado = Column(Integer, nullable=False)
    area_id        = Column(Integer, ForeignKey('area_competencia.id', ondelete='RESTRICT'), nullable=False)

    area    = relationship('AreaCompetencia', back_populates='disciplinas')
    ofertas = relationship('Oferta', back_populates='disciplina')

class SemestreLetivo(Base):
    __tablename__ = 'semestre_letivo'
    __table_args__ = (
        CheckConstraint('data_inicio < data_fim', name='chk_semestre_datas'),
    )

    id          = Column(Integer, primary_key=True)
    nome        = Column(String, unique=True, nullable=False)
    ano         = Column(Integer, nullable=False)
    periodo     = Column(String, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim    = Column(Date, nullable=False)

    ofertas = relationship('Oferta', back_populates='semestre')

class Oferta(Base):
    __tablename__ = 'oferta'
    __table_args__ = (
        UniqueConstraint('semestre_id', 'disciplina_id', 'turma', name='uq_oferta_semdisc_turma'),
        Index('ix_oferta_semestre_id', 'semestre_id'),
        Index('ix_oferta_disciplina_id', 'disciplina_id')
    )

    id            = Column(Integer, primary_key=True)
    semestre_id   = Column(Integer, ForeignKey('semestre_letivo.id', ondelete='CASCADE'), nullable=False)
    disciplina_id = Column(Integer, ForeignKey('disciplina.id', ondelete='CASCADE'), nullable=False)
    turma         = Column(String, nullable=False)

    semestre  = relationship('SemestreLetivo', back_populates='ofertas')
    disciplina = relationship('Disciplina', back_populates='ofertas')
    alocacoes = relationship('Alocacao', back_populates='oferta')

class Alocacao(Base):
    __tablename__ = 'alocacao'

    id           = Column(Integer, primary_key=True)
    oferta_id    = Column(Integer, ForeignKey('oferta.id', ondelete='CASCADE'), nullable=False)
    professor_id = Column(Integer, ForeignKey('professor.id', ondelete='CASCADE'), nullable=False)

    oferta    = relationship('Oferta', back_populates='alocacoes')
    professor = relationship('Professor', back_populates='alocacoes')

# ---------------------------------------------------------------------
# 6. Inicialização do banco
# ---------------------------------------------------------------------
def init_db():
    """Cria as tabelas no banco se ainda não existirem."""
    Base.metadata.create_all(bind=get_engine())
