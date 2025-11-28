#!/bin/bash
# Script de inicialização do Backend Flask

set -e

echo "========================================================================"
echo "🚀 Sistema de Alocação de Professores - Backend Flask"
echo "========================================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Verificar Python
echo ""
echo "1️⃣  Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python $PYTHON_VERSION encontrado"

# 2. Verificar/Criar ambiente virtual
echo ""
echo "2️⃣  Configurando ambiente virtual..."
if [ ! -d "venv" ]; then
    print_warning "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    print_status "Ambiente virtual criado"
fi

# 3. Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

# 4. Atualizar pip
echo ""
echo "3️⃣  Atualizando pip..."
pip install --upgrade pip -q
print_status "pip atualizado"

# 5. Instalar dependências
echo ""
echo "4️⃣  Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    print_status "Dependências instaladas"
else
    print_error "requirements.txt não encontrado"
    exit 1
fi

# 6. Verificar .env
echo ""
echo "5️⃣  Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env não encontrado. Usando .env.example como template"
        cp .env.example .env
        print_status ".env criado (edite as variáveis conforme necessário)"
    else
        print_error ".env.example não encontrado"
        exit 1
    fi
else
    print_status ".env encontrado"
fi

# 7. Criar pastas necessárias
echo ""
echo "6️⃣  Criando diretórios..."
mkdir -p logs uploads
print_status "Diretórios criados"

# 8. Info final
echo ""
echo "========================================================================"
echo "✅ Ambiente pronto para inicialização!"
echo "========================================================================"
echo ""
echo "Para iniciar o servidor, execute:"
echo ""
echo -e "  ${GREEN}python app.py${NC}"
echo ""
echo "A API estará disponível em:"
echo "  🌐 http://localhost:3001"
echo "  📚 Documentação Swagger: http://localhost:3001/api/docs"
echo "  💚 Health Check: http://localhost:3001/health"
echo ""
echo "========================================================================"
echo ""

