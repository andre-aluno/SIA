import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from db import Alocacao, Oferta, Professor, SemestreLetivo, Disciplina, get_session

def export_alocacoes_to_excel(db: Session, semestre_nome: str):
    """Gera e retorna um arquivo Excel com as alocações do semestre especificado."""
    try:
        # Buscar todas as ofertas do semestre (com ou sem alocação)
        ofertas_com_alocacao = (
            db.query(Oferta, Alocacao, Professor)
            .join(Oferta.semestre)
            .join(Oferta.disciplina)
            .join(Disciplina.area)
            .outerjoin(Alocacao, Oferta.id == Alocacao.oferta_id)
            .outerjoin(Professor, Alocacao.professor_id == Professor.id)
            .filter(SemestreLetivo.nome == semestre_nome)
            .all()
        )

        if not ofertas_com_alocacao:
            return None, "Não há ofertas para este semestre."

        # Preparar dados para o Excel
        data = []
        for oferta, alocacao, professor in ofertas_com_alocacao:
            data.append({
                "ID_Alocacao": alocacao.id if alocacao else "",
                "Semestre": oferta.semestre.nome,
                "Ano": oferta.semestre.ano,
                "Periodo": oferta.semestre.periodo,
                "Disciplina": oferta.disciplina.nome,
                "Turma": oferta.turma,
                "Carga_Horaria": float(oferta.disciplina.carga_horaria),
                "Nivel_Esperado": oferta.disciplina.nivel_esperado,
                "Area_Competencia": oferta.disciplina.area.nome,
                "Professor": professor.nome if professor else "",
                "Titulacao": professor.titulacao if professor else "",
                "Nivel_Professor": professor.nivel if professor else "",
                "Modelo_Contratacao": professor.modelo_contratacao if professor else "",
                "Carga_Maxima": float(professor.carga_maxima) if professor else "",
                "Status_Alocacao": "Alocado" if alocacao else "Pendente"
            })

        df = pd.DataFrame(data)

        # Criar buffer para o Excel
        output = io.BytesIO()

        # Usar xlsxwriter como engine para ter mais controle sobre formatação
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Alocações', index=False)

            # Obter o workbook e worksheet para formatação
            workbook = writer.book
            worksheet = writer.sheets['Alocações']

            # Definir formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            # Formato para células de ofertas pendentes
            pending_format = workbook.add_format({
                'bg_color': '#FFF2CC',
                'border': 1
            })

            # Aplicar formato ao cabeçalho
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Aplicar formatação condicional para ofertas pendentes
            for row_num, row_data in enumerate(df.itertuples(), start=1):
                if row_data.Status_Alocacao == "Pendente":
                    for col_num in range(len(df.columns)):
                        worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], pending_format)

            # Ajustar largura das colunas
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, min(max_len, 30))

        output.seek(0)
        return output.getvalue(), None

    except Exception as e:
        return None, f"Erro ao gerar Excel: {str(e)}"

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
    st.dataframe(df, use_container_width=True)

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

        if not semestres:
            st.warning("Não há semestres cadastrados.")
            return

        sel_sem = st.selectbox("Semestre", options=[s.nome for s in semestres])
        sem_obj = next(s for s in semestres if s.nome == sel_sem)

        ofertas = db.query(Oferta) \
            .filter_by(semestre_id=sem_obj.id) \
            .join(Oferta.disciplina) \
            .order_by(Disciplina.nome, Oferta.turma) \
            .all()

        if not ofertas:
            st.warning(f"Não há ofertas cadastradas para o semestre {sel_sem}.")
            return

        oferta_labels = [f"{o.disciplina.nome} - Turma {o.turma}" for o in ofertas]
        sel_oferta_label = st.selectbox("Oferta", options=oferta_labels)
        oferta_obj = ofertas[oferta_labels.index(sel_oferta_label)]

        profs = db.query(Professor).order_by(Professor.nome).all()

        if not profs:
            st.warning("Não há professores cadastrados.")
            return

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
                st.rerun()

def page_alocacao():
    """Entry point para a seção de Alocação de Professores."""
    st.title("📊 Alocação de Professores")
    db = get_session()

    # Formulário de criação
    create_alocacao(db)

    # Divisor
    st.divider()

    # Lista de alocações existentes
    st.subheader("📋 Alocações Existentes")
    list_alocacoes(db)

    # Divisor
    st.divider()

    # Seção de exportação
    st.subheader("📤 Exportar Alocações para Excel")

    # Buscar semestres disponíveis
    semestres = db.query(SemestreLetivo).order_by(SemestreLetivo.nome).all()

    if not semestres:
        st.warning("Não há semestres cadastrados.")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        semestre_selecionado = st.selectbox(
            "Selecione o semestre para exportação:",
            options=[s.nome for s in semestres],
            key="export_semestre"
        )

    with col2:
        # Alinhar o botão com o selectbox
        st.write("")  # Espaço para alinhamento com o label
        export_clicked = st.button("📊 Exportar Excel", type="primary", key="btn_export")

    # Processar exportação quando o botão for clicado
    if export_clicked:
        with st.spinner("Gerando arquivo Excel..."):
            excel_data, error = export_alocacoes_to_excel(db, semestre_selecionado)

            if error:
                st.error(error)
            else:
                # Gerar nome do arquivo com timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"alocacoes_{semestre_selecionado.replace('/', '_')}_{timestamp}.xlsx"

                # Mostrar o botão de download imediatamente
                st.success(f"✅ Arquivo Excel gerado com sucesso!")

                # Botão de download mais visível
                st.download_button(
                    label="📥 BAIXAR ARQUIVO EXCEL",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_file",
                    type="primary",
                    use_container_width=True
                )

                st.info("💡 Clique no botão acima para baixar o arquivo para seu computador.")

# Execução da página
page_alocacao()
