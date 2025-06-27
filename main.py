import streamlit as st

# Layout da página
st.set_page_config(
    page_title="SIA – Sistema de Alocação",
    layout="wide",
    initial_sidebar_state="expanded"
)

from db import init_db, get_engine, get_session
from pages.professor import page_professor

# inicializa o esquema
init_db()

# obtém engine e sessão (já cacheados no get_engine/get_session)
engine = get_engine()
db = get_session()

st.success("Banco de dados pronto e conectado!")