import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db import AreaCompetencia, get_session

def list_areas(db: Session):
    """Exibe todas as áreas de competência em uma tabela."""
    try:
        areas = db.query(AreaCompetencia).order_by(AreaCompetencia.nome).all()
        data = [{"ID": a.id, "Nome": a.nome} for a in areas]
        df = pd.DataFrame(data)
        st.dataframe(df)
    except Exception as e:
        db.rollback()
        st.error(f"Erro ao carregar áreas: {e}")

def create_area(db: Session):
    """Formulário para criar uma nova área de competência."""
    with st.form(key="frm_nova_area"):
        st.subheader("Nova Área de Competência")
        nome = st.text_input("Nome da Área")
        submitted = st.form_submit_button("Salvar")
        if submitted:
            # Verifica duplicata
            exists = db.query(AreaCompetencia).filter_by(nome=nome).first()
            if exists:
                st.warning(f"A área '{nome}' já existe.")
            else:
                nova = AreaCompetencia(nome=nome)
                db.add(nova)
                db.commit()
                st.success(f"Área '{nome}' criada com sucesso!")

def page_area_competencia():
    """Entry point para a seção de Áreas de Competência."""
    st.title("🏷️ Áreas de Competência")
    db = get_session()
    create_area(db)
    st.markdown("---")
    list_areas(db)

page_area_competencia()