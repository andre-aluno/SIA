import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db import Professor, AreaCompetencia, get_session

def list_professores(db: Session):
    """Exibe todos os professores em uma tabela."""
    profs = db.query(Professor).all()
    data = []
    for p in profs:
        areas = ", ".join([a.nome for a in p.areas])
        data.append({
            "ID": p.id,
            "Nome": p.nome,
            "Titulação": p.titulacao,
            "Carga Máxima": p.carga_maxima,
            "Modelo de Contratação": p.modelo_contratacao,
            "Nível": p.nivel,
            "Áreas de Competência": areas
        })
    df = pd.DataFrame(data)
    st.dataframe(df)

def create_professor(db: Session):
    """Formulário para criar um novo professor."""
    with st.form("frm_novo_prof"):
        st.subheader("Novo Professor")
        nome = st.text_input("Nome")
        titul = st.selectbox(
            "Titulação",
            ["Ensino Médio","Graduado","Especialista","Mestre","Doutor"]
        )
        modelo_contratacao = st.selectbox(
            "Modelo de Contratação",
            ["Mensalista ", "Horista"]
        )
        carga = 128.0 if modelo_contratacao == 'Mensalista ' else 256.0
        todas_areas = db.query(AreaCompetencia).order_by(AreaCompetencia.nome).all()
        sel_areas = st.multiselect(
            "Áreas de Competência",
            options=[a.nome for a in todas_areas]
        )
        submitted = st.form_submit_button("Salvar")
        if submitted:
            nivel_map = {
                "Ensino Médio":0,
                "Graduado":1,
                "Especialista":2,
                "Mestre":3,
                "Doutor":4
            }
            novo = Professor(
                nome=nome,
                titulacao=titul,
                nivel=nivel_map[titul],
                carga_maxima=carga,
                modelo_contratacao=modelo_contratacao,
            )
            for nome_area in sel_areas:
                area_obj = next(a for a in todas_areas if a.nome == nome_area)
                novo.areas.append(area_obj)
            db.add(novo)
            db.commit()
            st.success(f"Professor **{nome}** criado com sucesso!")

def page_professor():
    """O entry point chamado em app.py para a seção 'Professor'."""
    st.title("👨‍🏫 Professores")
    db = get_session()
    create_professor(db)
    st.markdown("---")
    list_professores(db)

page_professor()
