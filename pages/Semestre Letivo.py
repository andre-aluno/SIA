import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db import SemestreLetivo, get_session


def list_semestres(db: Session):
    """Exibe todos os semestres letivos em uma tabela."""
    sems = db.query(SemestreLetivo).order_by(SemestreLetivo.nome).all()
    data = []
    for s in sems:
        data.append({
            "ID": s.id,
            "Nome": s.nome,
            "Ano": s.ano,
            "Período": s.periodo,
            "Data Início": s.data_inicio,
            "Data Fim": s.data_fim
        })
    df = pd.DataFrame(data)
    st.dataframe(df)


def create_semestre(db: Session):
    """Formulário para criar um novo semestre letivo."""
    with st.form(key="frm_novo_semestre"):
        st.subheader("Novo Semestre Letivo")
        nome = st.text_input("Nome do Semestre (ex: 2025-1)")
        ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2025, step=1)
        periodo = st.text_input("Período (ex: EAD1, 1", max_chars=10)
        data_inicio = st.date_input("Data de Início")
        data_fim = st.date_input("Data de Fim")
        submitted = st.form_submit_button("Salvar")

        if submitted:
            # checar duplicidade
            exists = db.query(SemestreLetivo).filter_by(nome=nome).first()
            if exists:
                st.warning(f"O semestre '{nome}' já existe.")
            else:
                novo = SemestreLetivo(
                    nome=nome,
                    ano=ano,
                    periodo=periodo,
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )
                db.add(novo)
                db.commit()
                st.success(f"Semestre '{nome}' criado com sucesso!")


def page_semestre():
    """Entry point para a seção de Semestre Letivo."""
    st.title("📅 Semestres Letivos")
    db = get_session()
    create_semestre(db)
    st.markdown("---")
    list_semestres(db)

page_semestre()
