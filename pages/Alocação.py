import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from db import Alocacao, Oferta, Professor, SemestreLetivo, Disciplina, get_session

def list_alocacoes(db: Session):
    """Exibe todas as alocações de professores em uma tabela."""
    allocs = (
        db.query(Alocacao)
        .join(Alocacao.oferta)
        .join(Alocacao.professor)
        .join(Oferta.semestre)
        .join(Oferta.disciplina)
        .all()
    )
    data = []
    for a in allocs:
        data.append({
            "ID": a.id,
            "Semestre": a.oferta.semestre.nome,
            "Disciplina": a.oferta.disciplina.nome,
            "Turma": a.oferta.turma,
            "Professor": a.professor.nome
        })
    df = pd.DataFrame(data)
    st.dataframe(df)

def load_data(db: Session, semestre_nome: str):
    """
    Retorna:
      - professores: lista de objetos Professor (com .areas carregado)
      - ofertas: lista de objetos Oferta (com .disciplina e .disciplina.area carregados)
    Filtra apenas as ofertas do semestre `semestre_nome`.
    """
    # 1. Todos os professores, carregando também as áreas de competência
    professores = (
        db.query(Professor)
               .options(joinedload(Professor.areas))
               .all()
    )

    # 2. Ofertas apenas do semestre selecionado, com disciplina e área
    ofertas = (
        db.query(Oferta)
               .join(Oferta.semestre)
               .options(
                   joinedload(Oferta.disciplina)
                     .joinedload(lambda d: d.area)  # carrega disciplina.area
               )
               .filter(SemestreLetivo.nome == semestre_nome)
               .all()
    )

    return professores, ofertas


def create_alocacao(db: Session):
    """Formulário para criar nova alocação de professor a uma oferta."""
    with st.form(key="frm_nova_alocacao"):
        st.subheader("Nova Alocação de Professor")
        semestres = db.query(SemestreLetivo).order_by(SemestreLetivo.nome).all()
        sel_sem = st.selectbox("Semestre", options=[s.nome for s in semestres])
        sem_obj = next(s for s in semestres if s.nome == sel_sem)

        ofertas = db.query(Oferta) \
            .filter_by(semestre_id=sem_obj.id) \
            .join(Oferta.disciplina) \
            .order_by(Disciplina.nome, Oferta.turma) \
            .all()
        oferta_labels = [f"{o.disciplina.nome} - Turma {o.turma}" for o in ofertas]
        sel_oferta_label = st.selectbox("Oferta", options=oferta_labels)
        oferta_obj = ofertas[oferta_labels.index(sel_oferta_label)]

        profs = db.query(Professor).order_by(Professor.nome).all()
        sel_prof = st.selectbox("Professor", options=[p.nome for p in profs])
        prof_obj = next(p for p in profs if p.nome == sel_prof)

        submitted = st.form_submit_button("Salvar")
        if submitted:
            exists = db.query(Alocacao).filter_by(
                oferta_id=oferta_obj.id,
                professor_id=prof_obj.id
            ).first()
            if exists:
                st.warning(f"Professor '{prof_obj.nome}' já está alocado para '{sel_oferta_label}'.")
            else:
                nova = Alocacao(
                    oferta_id=oferta_obj.id,
                    professor_id=prof_obj.id
                )
                db.add(nova)
                db.commit()
                st.success(f"Alocação criada: {prof_obj.nome} → {sel_oferta_label}")


def page_alocacao():
    """Entry point para a seção de Alocação de Professores."""
    st.title("📊 Alocação de Professores")
    db = get_session()
    create_alocacao(db)
    st.markdown("---")
    list_alocacoes(db)


page_alocacao()
