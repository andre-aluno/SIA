import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db import Disciplina, AreaCompetencia, get_session


def list_disciplinas(db: Session):
    """Exibe todas as disciplinas em uma tabela."""
    discs = db.query(Disciplina).order_by(Disciplina.nome).all()
    data = []
    for d in discs:
        area = d.area.nome if d.area else ""
        data.append({
            "ID": d.id,
            "Nome": d.nome,
            "Carga Horária": float(d.carga_horaria),
            "Nível Esperado": d.nivel_esperado,
            "Área de Competência": area
        })
    df = pd.DataFrame(data)
    st.dataframe(df)


def create_disciplina(db: Session):
    """Formulário para criar uma nova disciplina."""
    with st.form(key="frm_nova_disciplina"):
        st.subheader("Nova Disciplina")
        nome = st.text_input("Nome da Disciplina")
        carga = st.number_input("Carga Horária", min_value=0.0, step=1.0)
        nivel = st.selectbox(
            "Nível Esperado",
            options=[0,1,2,3,4],
            format_func=lambda x: {0:'Ensino Médio',1:'Graduado',2:'Especialista',3:'Mestre',4:'Doutor'}[x]
        )
        # Seleção de área única
        todas_areas = db.query(AreaCompetencia).order_by(AreaCompetencia.nome).all()
        sel_area = st.selectbox(
            "Área de Competência",
            options=[a.nome for a in todas_areas]
        )
        submitted = st.form_submit_button("Salvar")

        if submitted:
            # checar duplicidade
            exists = db.query(Disciplina).filter_by(nome=nome).first()
            if exists:
                st.warning(f"A disciplina '{nome}' já existe.")
            else:
                area_obj = next(a for a in todas_areas if a.nome == sel_area)
                nova = Disciplina(
                    nome=nome,
                    carga_horaria=carga,
                    nivel_esperado=nivel,
                    area=area_obj
                )
                db.add(nova)
                db.commit()
                st.success(f"Disciplina '{nome}' criada com sucesso!")


def page_disciplina():
    """Entry point para a seção de Disciplinas."""
    st.title("📚 Disciplinas")
    db = get_session()
    create_disciplina(db)
    st.markdown("---")
    list_disciplinas(db)

page_disciplina()