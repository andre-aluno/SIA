import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db import Oferta, SemestreLetivo, Disciplina, get_session


def list_ofertas(db: Session):
    """Exibe todas as ofertas de disciplinas em uma tabela."""
    ofertas = (
        db.query(Oferta)
          .join(SemestreLetivo, Oferta.semestre)
          .join(Disciplina, Oferta.disciplina)
          .order_by(SemestreLetivo.nome, Disciplina.nome)
          .all()
    )
    data = []
    for o in ofertas:
        data.append({
            "ID": o.id,
            "Semestre": o.semestre.nome,
            "Disciplina": o.disciplina.nome,
            "Turma": o.turma
        })
    df = pd.DataFrame(data)
    st.dataframe(df)


def create_oferta(db: Session):
    """Formulário para criar uma nova oferta de disciplina."""
    with st.form(key="frm_nova_oferta"):
        st.subheader("Nova Oferta de Disciplina")
        semestres = db.query(SemestreLetivo).order_by(SemestreLetivo.nome).all()
        disciplinas = db.query(Disciplina).order_by(Disciplina.nome).all()
        sel_sem = st.selectbox(
            "Semestre",
            options=[s.nome for s in semestres]
        )
        sel_disc = st.selectbox(
            "Disciplina",
            options=[d.nome for d in disciplinas]
        )
        turma = st.text_input("Turma")
        submitted = st.form_submit_button("Salvar")

        if submitted:
            # Verifica duplicata
            sem_obj = next(s for s in semestres if s.nome == sel_sem)
            disc_obj = next(d for d in disciplinas if d.nome == sel_disc)
            exists = (
                db.query(Oferta)
                  .filter_by(semestre_id=sem_obj.id, disciplina_id=disc_obj.id, turma=turma)
                  .first()
            )
            if exists:
                st.warning(f"Oferta da disciplina '{sel_disc}' no semestre '{sel_sem}' e turma '{turma}' já existe.")
            else:
                nova = Oferta(
                    semestre=sem_obj,
                    disciplina=disc_obj,
                    turma=turma
                )
                db.add(nova)
                db.commit()
                st.success(f"Oferta criada: {sel_disc} - {sel_sem} (Turma {turma})")


def page_oferta():
    """Entry point para a seção de Oferta de Disciplina."""
    st.title("📋 Oferta de Disciplina")
    db = get_session()
    create_oferta(db)
    st.markdown("---")
    list_ofertas(db)

page_oferta()
