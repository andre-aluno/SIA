import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
import numpy as np
from db import (
    get_engine,
    AreaCompetencia,
    SemestreLetivo,
    Professor,
    Disciplina,
    Oferta,
    Alocacao
)

# Cria um factory de sessão a partir do engine
SessionLocal = sessionmaker(bind=get_engine())


def import_from_excel():
    st.title("📥 Importar Dados do Excel")
    st.markdown("Faça upload do arquivo Excel para popular o banco de dados.")
    uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
    if not uploaded_file:
        return

    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        # Converter datas para datetime
        df['DT INCIO DISCIPLINA'] = pd.to_datetime(
            df['DT INCIO DISCIPLINA'], dayfirst=True, errors='coerce'
        )
        df['DT FIM DISCIPLINA'] = pd.to_datetime(
            df['DT FIM DISCIPLINA'], dayfirst=True, errors='coerce'
        )
    except Exception as e:
        st.error(f"Erro ao ler Excel: {e}")
        return

    # A tabela já possui coluna 'nivel_esperado'
    db = SessionLocal()
    try:
        with db.begin():
            # 1. Áreas de competência
            for nome in df['area_competencia'].dropna().unique():
                if not db.query(AreaCompetencia).filter_by(nome=nome).first():
                    db.add(AreaCompetencia(nome=nome))

            # 2. Semestres
            sem_data = df[['PERIODO_LETIVO', 'DT INCIO DISCIPLINA', 'DT FIM DISCIPLINA']]
            sem_data = sem_data.dropna().drop_duplicates()
            for _, row in sem_data.iterrows():
                nome_sem = row['PERIODO_LETIVO']
                ano = int(nome_sem[:4])
                periodo = nome_sem[4:]
                dt_i = row['DT INCIO DISCIPLINA']
                dt_f = row['DT FIM DISCIPLINA']
                if not db.query(SemestreLetivo).filter_by(nome=nome_sem).first():
                    db.add(SemestreLetivo(
                        nome=nome_sem,
                        ano=ano,
                        periodo=periodo,
                        data_inicio=dt_i,
                        data_fim=dt_f
                    ))

            # 3. Professores com titulação, nível e áreas
            prof_data = df[['PROFESSOR', 'TITULACAO_PROFESSOR', 'nivel_professor', 'area_competencia', 'Horas Máximas Sala/Semestre', 'Modelo de Contratação']]
            prof_data = prof_data.dropna(subset=['PROFESSOR']).drop_duplicates()
            for _, row in prof_data.iterrows():
                nome_prof = row['PROFESSOR']
                titul = row['TITULACAO_PROFESSOR']
                nivel = int(row['nivel_professor'])
                area_nome = row['area_competencia']
                modelo_contratacao = row['Modelo de Contratação']
                carga_maxima = 256.0 if modelo_contratacao == 'Mensalista ' else 128.0
                prof = db.query(Professor).filter_by(nome=nome_prof).first()
                if not prof:
                    prof = Professor(
                        nome=nome_prof,
                        titulacao=titul,
                        nivel=nivel,
                        carga_maxima=carga_maxima,
                        modelo_contratacao=modelo_contratacao
                    )
                    db.add(prof)
                    db.flush()
                area = db.query(AreaCompetencia).filter_by(nome=area_nome).first()
                if area and area not in prof.areas:
                    prof.areas.append(area)

            # 4. Disciplinas (uma única vez), usando 'nivel_esperado' existente
            disc_data = df[['DISCIPLINA', 'area_competencia', 'CH_DISCIPLINA', 'nivel_esperado']]
            disc_data = disc_data.dropna(subset=['DISCIPLINA']).drop_duplicates(subset=['DISCIPLINA'])
            for _, row in disc_data.iterrows():
                d_name = row['DISCIPLINA']
                area_nome = row['area_competencia']
                carga = float(row['CH_DISCIPLINA'])
                nivel_esp = int(row['nivel_esperado']) if not pd.isna(row['nivel_esperado']) else None
                if not db.query(Disciplina).filter_by(nome=d_name).first():
                    area = db.query(AreaCompetencia).filter_by(nome=area_nome).first()
                    db.add(Disciplina(
                        nome=d_name,
                        carga_horaria=carga,
                        nivel_esperado=nivel_esp,
                        area=area
                    ))

            # 5. Ofertas
            oferta_data = df[['PERIODO_LETIVO', 'DISCIPLINA', 'CH_DISCIPLINA']]
            oferta_data = oferta_data.dropna().drop_duplicates()
            for _, row in oferta_data.iterrows():
                sem_nome = row['PERIODO_LETIVO']
                d_nome = row['DISCIPLINA']
                carga = float(row['CH_DISCIPLINA'])
                sem = db.query(SemestreLetivo).filter_by(nome=sem_nome).first()
                disc = db.query(Disciplina).filter_by(nome=d_nome).first()
                if sem and disc and not db.query(Oferta).filter_by(
                    semestre_id=sem.id,
                    disciplina_id=disc.id
                ).first():
                    db.add(Oferta(
                        semestre=sem,
                        disciplina=disc
                    ))

            # 6. Alocações: vincula cada professor à sua oferta
            alloc_data = df[['PERIODO_LETIVO', 'DISCIPLINA', 'PROFESSOR']] \
                .dropna().drop_duplicates()
            for _, row in alloc_data.iterrows():
                sem_nome = row['PERIODO_LETIVO']
                d_nome = row['DISCIPLINA']
                prof_nome = row['PROFESSOR']

                sem = db.query(SemestreLetivo).filter_by(nome=sem_nome).first()
                disc = db.query(Disciplina).filter_by(nome=d_nome).first()
                prof = db.query(Professor).filter_by(nome=prof_nome).first()

                if sem and disc and prof:
                    oferta = db.query(Oferta).filter_by(
                        semestre_id=sem.id,
                        disciplina_id=disc.id
                    ).first()

                    if oferta:
                        # só adiciona se ainda não existir
                        existe = db.query(Alocacao).filter_by(
                            oferta_id=oferta.id,
                            professor_id=prof.id
                        ).first()
                        if not existe:
                            db.add(Alocacao(
                                oferta_id=oferta.id,
                                professor_id=prof.id
                            ))
        st.success("Importação concluída com sucesso!")
    except Exception as e:
        st.error(f"Falha na importação, nenhuma alteração foi feita: {e}")


def page_import():
    import_from_excel()

page_import()