import streamlit as st
import pandas as pd
import altair as alt
import time
from sqlalchemy.orm import Session
from db import get_session, SemestreLetivo
from ag import run_ga, load_data


def page_alocacao_ga():
    st.title("📊 Alocação de Professores (AG)")

    # Seleção de semestre
    db: Session = get_session()
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
                "Professor": prof.nome,
                "Titulacao": prof.titulacao,
                "ModeloContrato": prof.modelo_contratacao,
                "NivelProf": prof.nivel,
                "CargaMax": float(prof.carga_maxima),
                "Disciplina": oferta.disciplina.nome,
                "CH": ch,
                "NivelEsp": oferta.disciplina.nivel_esperado,
                "AreaDisc": oferta.disciplina.area.nome,
                "Match": "✅" if match else "❌"
            })
        df_assign = pd.DataFrame(records)

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

        # Gráfico de barras: Horas Alocada vs Livre por Professor (Livre sobre Alocada)
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
                # 'Alocada' primeiro (embaixo), 'Livre' depois (acima)
                'Tipo:N',
                sort='ascending'
            ),
            tooltip=["Professor", "Tipo", "Horas"]
        )
        st.altair_chart(bar_chart, use_container_width=True)

        # Detalhamento por professor
        st.subheader("Detalhamento por Professor")
        for p in professores:
            prof_df = df_assign[df_assign["Professor"] == p.nome]
            total = carga_total[p.id]
            cap = float(p.carga_maxima)
            label = f"{p.nome} — {total:.0f}/{cap:.0f}h"
            with st.expander(label):
                st.table(prof_df[["Disciplina", "CH", "NivelEsp", "AreaDisc", "Match"]])

        # Pivot table consolidada
        st.subheader("Visão Consolidada (Pivot)")
        pivot = df_assign.pivot_table(
            index="Professor", columns="Disciplina", values="CH", fill_value=0
        )
        st.dataframe(pivot)

# Execução da página
page_alocacao_ga()
