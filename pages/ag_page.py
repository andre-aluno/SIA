import streamlit as st
import pandas as pd
import altair as alt
import time
from db import get_session, SemestreLetivo, Alocacao
from ag import run_ga, load_data


def salvar_alocacao(oferta_id, professor_id):
    """Salva uma alocação no banco de dados"""
    session = get_session()
    try:
        # Verifica se já existe alocação para esta oferta
        existing = session.query(Alocacao).filter_by(oferta_id=oferta_id).first()
        if existing:
            return False, "Esta oferta já possui uma alocação."

        # Cria nova alocação
        nova_alocacao = Alocacao(oferta_id=oferta_id, professor_id=professor_id)
        session.add(nova_alocacao)
        session.commit()
        return True, "Alocação salva com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao salvar alocação: {str(e)}"
    finally:
        session.close()


def page_alocacao_ga():
    st.title("📊 Alocação de Professores (AG)")

    # Seleção de semestre
    db = get_session()
    semestres = db.query(SemestreLetivo).order_by(SemestreLetivo.nome).all()
    sem_options = [""] + [s.nome for s in semestres]
    semestre = st.selectbox("Selecione o semestre letivo", sem_options, index=0)

    # Parâmetros do AG em expander
    with st.expander("Parâmetros do Algoritmo Genético"):
        ngen = st.number_input("Número de gerações", value=50, min_value=1, step=1)
        pop_size = st.number_input("Tamanho da população", value=100, min_value=1, step=1)
        cxpb = st.slider("Probabilidade de crossover", 0.0, 1.0, 0.7)
        mutpb = st.slider("Probabilidade de mutação", 0.0, 1.0, 0.2)

    # Botão de gerar alocação
    generate = st.button("Gerar alocação", disabled=(semestre == ""))

    if generate:
        # Carrega dados e filtra apenas ofertas ainda não alocadas
        professores, ofertas = load_data(semestre)
        if not ofertas:
            st.error("Não há disciplinas pendentes para alocação neste semestre.")
            return

        # Verificar se há professores com competência para todas as disciplinas
        areas_necessarias = set()
        areas_disponiveis = set()

        for oferta in ofertas:
            areas_necessarias.add(oferta.disciplina.area.id)

        for professor in professores:
            for area in professor.areas:
                areas_disponiveis.add(area.id)

        areas_sem_professor = areas_necessarias - areas_disponiveis

        if areas_sem_professor:
            st.warning("⚠️ **Atenção: Há disciplinas sem professores com competência adequada:**")

            # Buscar nomes das áreas e disciplinas problemáticas
            disciplinas_problematicas = []
            for oferta in ofertas:
                if oferta.disciplina.area.id in areas_sem_professor:
                    disciplinas_problematicas.append({
                        "Disciplina": oferta.disciplina.nome,
                        "Turma": oferta.turma,
                        "Área": oferta.disciplina.area.nome,
                        "CH": float(oferta.disciplina.carga_horaria)
                    })

            df_problemas = pd.DataFrame(disciplinas_problematicas)
            st.dataframe(df_problemas, use_container_width=True)

            st.info("💡 O algoritmo genético tentará alocar essas disciplinas mesmo sem match de competência, mas com penalização no fitness.")

        with st.spinner("Executando alocação..."):
            start_time = time.time()
            best, log = run_ga(
                semestre_nome=semestre,
                ngen=int(ngen),
                pop_size=int(pop_size),
                cxpb=float(cxpb),
                mutpb=float(mutpb)
            )
            duration = time.time() - start_time

        # Mapeamento rápido para lookup por ID
        prof_map = {p.id: p for p in professores}

        # Montar DataFrame de alocações
        records = []
        carga_total = {p.id: 0.0 for p in professores}
        for idx, prof_id in enumerate(best):
            prof = prof_map.get(prof_id)
            oferta = ofertas[idx]
            ch = float(oferta.disciplina.carga_horaria)
            carga_total[prof.id] += ch
            match = oferta.disciplina.area.id in {a.id for a in prof.areas}
            records.append({
                "idx": idx,
                "oferta_id": oferta.id,
                "professor_id": prof_id,
                "Professor": prof.nome,
                "Titulacao": prof.titulacao,
                "ModeloContrato": prof.modelo_contratacao,
                "NivelProf": prof.nivel,
                "CargaMax": float(prof.carga_maxima),
                "Disciplina": oferta.disciplina.nome,
                "Turma": oferta.turma,
                "CH": ch,
                "NivelEsp": oferta.disciplina.nivel_esperado,
                "AreaDisc": oferta.disciplina.area.nome,
                "Match": "✅" if match else "❌"
            })
        df_assign = pd.DataFrame(records)

        # Armazenar dados na sessão para persistir entre interações
        st.session_state['df_assign'] = df_assign
        st.session_state['ofertas'] = ofertas
        st.session_state['professores'] = professores
        st.session_state['carga_total'] = carga_total
        st.session_state['best'] = best
        st.session_state['log'] = log
        st.session_state['duration'] = duration

    # Se existem dados na sessão, mostrar resultados
    if 'df_assign' in st.session_state:
        df_assign = st.session_state['df_assign']
        ofertas = st.session_state['ofertas']
        professores = st.session_state['professores']
        carga_total = st.session_state['carga_total']
        best = st.session_state['best']
        log = st.session_state['log']
        duration = st.session_state['duration']

        # Resumo rápido
        st.subheader("Resumo")
        st.markdown(f"**Melhor fitness:** `{best.fitness.values[0]:.2f}`")
        gens = log.select("gen")[-1] if hasattr(log, 'select') else len(log)
        st.markdown(f"**Gerações executadas:** {gens}")
        st.markdown(f"**Tempo de execução:** {duration:.1f} s")

        # Evolução do Fitness
        df_log = pd.DataFrame({
            'Geração': log.select('gen'),
            'MaxFitness': log.select('max'),
            'AvgFitness': log.select('avg'),
            'MinFitness': log.select('min'),
        })
        df_melt = df_log.melt(id_vars=['Geração'],
                              value_vars=['MaxFitness', 'AvgFitness', 'MinFitness'],
                              var_name='Tipo', value_name='Fitness')
        fitness_chart = alt.Chart(df_melt).mark_line(point=True).encode(
            x='Geração:Q',
            y='Fitness:Q',
            color='Tipo:N',
            tooltip=['Geração', 'Tipo', 'Fitness']
        ).interactive()
        st.altair_chart(fitness_chart, use_container_width=True)

        # Gráfico de barras: Horas Alocada vs Livre por Professor
        df_summary = pd.DataFrame([
            {"Professor": p.nome,
             "Alocada": carga_total[p.id],
             "Livre": max(0.0, float(p.carga_maxima) - carga_total[p.id])}
            for p in professores
        ])
        mdf = df_summary.melt(
            id_vars=["Professor"],
            value_vars=["Alocada", "Livre"],
            var_name="Tipo", value_name="Horas"
        )
        bar_chart = alt.Chart(mdf).mark_bar().encode(
            x=alt.X("Professor:N", sort=None),
            y=alt.Y("Horas:Q"),
            color=alt.Color("Tipo:N", scale=alt.Scale(domain=["Alocada", "Livre"])),
            order=alt.Order(
                'Tipo:N',
                sort='ascending'
            ),
            tooltip=["Professor", "Tipo", "Horas"]
        )
        st.altair_chart(bar_chart, use_container_width=True)

        # Detalhamento por professor
        st.subheader("👨‍🏫 Detalhamento por Professor")
        for p in professores:
            prof_df = df_assign[df_assign["Professor"] == p.nome]
            if not prof_df.empty:
                total = carga_total[p.id]
                cap = float(p.carga_maxima)
                label = f"{p.nome} — {total:.0f}/{cap:.0f}h"
                with st.expander(label):
                    st.table(prof_df[["Disciplina", "Turma", "CH", "NivelEsp", "AreaDisc", "Match"]])

        # Tabela de seleção com checkboxes
        st.subheader("☑️ Seleção de Alocações")
        st.markdown("Marque as alocações que deseja confirmar e clique em **Alocar Selecionadas**:")

        # Inicializar estado dos checkboxes se não existir
        if 'selected_allocations' not in st.session_state:
            st.session_state['selected_allocations'] = {}

        # Criar um container para a tabela
        with st.container():
            # Cabeçalho da tabela
            header_cols = st.columns([0.5, 2, 2, 1, 1, 1, 1])
            with header_cols[0]:
                st.write("**Sel.**")
            with header_cols[1]:
                st.write("**Disciplina**")
            with header_cols[2]:
                st.write("**Professor**")
            with header_cols[3]:
                st.write("**CH**")
            with header_cols[4]:
                st.write("**Nível**")
            with header_cols[5]:
                st.write("**Match**")
            with header_cols[6]:
                st.write("**Área**")

            st.divider()

            # Linhas da tabela com checkboxes
            for idx, row in df_assign.iterrows():
                cols = st.columns([0.5, 2, 2, 1, 1, 1, 1])

                with cols[0]:
                    checkbox_key = f"select_{row['oferta_id']}_{row['professor_id']}"
                    # Usar o valor atual sem atualizar automaticamente o session_state
                    current_value = st.session_state['selected_allocations'].get(checkbox_key, False)
                    selected = st.checkbox(
                        "",
                        key=checkbox_key,
                        value=current_value
                    )
                    # Só atualizar se mudou
                    if selected != current_value:
                        st.session_state['selected_allocations'][checkbox_key] = selected

                with cols[1]:
                    st.write(f"{row['Disciplina']} - {row['Turma']}")

                with cols[2]:
                    st.write(f"{row['Professor']}")
                    st.caption(f"{row['Titulacao']} - Nível {row['NivelProf']}")

                with cols[3]:
                    st.write(f"{row['CH']:.0f}h")

                with cols[4]:
                    st.write(f"{row['NivelEsp']}")

                with cols[5]:
                    st.write(row['Match'])

                with cols[6]:
                    st.caption(f"{row['AreaDisc']}")

        st.divider()

        # Botões para ações em lote na seleção
        selection_cols = st.columns([1, 1, 1, 2])

        # Contar selecionadas uma única vez
        selected_count = sum(1 for key, value in st.session_state['selected_allocations'].items()
                           if value and key.startswith('select_'))

        with selection_cols[0]:
            if st.button("☑️ Selecionar Todas", key="select_all"):
                for idx, row in df_assign.iterrows():
                    checkbox_key = f"select_{row['oferta_id']}_{row['professor_id']}"
                    st.session_state['selected_allocations'][checkbox_key] = True
                st.rerun()

        with selection_cols[1]:
            if st.button("☐ Desmarcar Todas", key="deselect_all"):
                for idx, row in df_assign.iterrows():
                    checkbox_key = f"select_{row['oferta_id']}_{row['professor_id']}"
                    st.session_state['selected_allocations'][checkbox_key] = False
                st.rerun()

        with selection_cols[2]:
            st.metric("Selecionadas", selected_count)

        with selection_cols[3]:
            if st.button("🎯 Alocar Selecionadas", type="primary", disabled=selected_count == 0, key="allocate_selected"):
                success_count = 0
                error_count = 0
                errors = []
                allocated_keys = []

                # Processar apenas as alocações selecionadas
                for idx, row in df_assign.iterrows():
                    checkbox_key = f"select_{row['oferta_id']}_{row['professor_id']}"
                    if st.session_state['selected_allocations'].get(checkbox_key, False):
                        success, message = salvar_alocacao(row['oferta_id'], row['professor_id'])
                        if success:
                            success_count += 1
                            allocated_keys.append(checkbox_key)
                        else:
                            error_count += 1
                            errors.append(f"{row['Disciplina']} - {row['Turma']}: {message}")

                # Feedback
                if success_count > 0:
                    st.success(f"✅ {success_count} alocações salvas com sucesso!")
                if error_count > 0:
                    st.error(f"❌ {error_count} alocações falharam:")
                    for error in errors:
                        st.error(error)

                # Remover alocações bem-sucedidas
                if success_count > 0:
                    # Filtrar o dataframe removendo as alocações bem-sucedidas
                    remaining_indices = []
                    for idx, row in df_assign.iterrows():
                        checkbox_key = f"select_{row['oferta_id']}_{row['professor_id']}"
                        if checkbox_key not in allocated_keys:
                            remaining_indices.append(idx)

                    if remaining_indices:
                        df_assign_updated = df_assign.loc[remaining_indices].reset_index(drop=True)
                        st.session_state['df_assign'] = df_assign_updated

                        # Limpar checkboxes das alocações removidas
                        for key in allocated_keys:
                            if key in st.session_state['selected_allocations']:
                                del st.session_state['selected_allocations'][key]
                    else:
                        # Se não sobrou nenhuma alocação, limpar tudo
                        for key in ['df_assign', 'ofertas', 'professores', 'carga_total', 'best', 'log', 'duration']:
                            if key in st.session_state:
                                del st.session_state[key]
                        if 'selected_allocations' in st.session_state:
                            del st.session_state['selected_allocations']

                    st.rerun()

# Execução da página
page_alocacao_ga()
