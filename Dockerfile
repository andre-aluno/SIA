# Base com Python
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos
COPY . /app

# Instala dependências
RUN pip install streamlit pygad plotly sqlalchemy psycopg2-binary openpyxl deap xlsxwriter

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
