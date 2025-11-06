FROM python:3.11-slim

WORKDIR /backend

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copiar aplicação
COPY backend/ .

# Criar diretórios necessários
RUN mkdir -p logs uploads

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=main.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Expõe porta
EXPOSE 3001

# Comando para rodar com Gunicorn - usar main.py
CMD ["gunicorn", "--bind", "0.0.0.0:3001", "--workers", "4", "--timeout", "120", "main:create_app()"]
