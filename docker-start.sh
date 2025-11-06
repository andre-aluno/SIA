#!/bin/bash
# Script para iniciar a aplicação com Docker Compose

set -e

echo "========================================================================"
echo "🐳 Sistema de Alocação de Professores - Docker"
echo "========================================================================"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Verificar Docker
echo ""
echo "1️⃣  Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker não encontrado. Instale Docker em https://www.docker.com"
    exit 1
fi
print_status "Docker $(docker --version | cut -d' ' -f3 | cut -d',' -f1) encontrado"

# 2. Verificar Docker Compose
echo ""
echo "2️⃣  Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não encontrado"
    exit 1
fi
print_status "Docker Compose $(docker-compose --version | cut -d' ' -f4 | cut -d',' -f1) encontrado"

# 3. Preparar arquivo .env
echo ""
echo "3️⃣  Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    if [ -f ".env.docker" ]; then
        print_warning ".env não encontrado. Usando .env.docker como template"
        cp .env.docker .env
        print_status ".env criado"
    else
        print_error ".env.docker não encontrado"
        exit 1
    fi
else
    print_status ".env já existe"
fi

# 4. Build e start
echo ""
echo "4️⃣  Iniciando containers..."
docker-compose build --no-cache
docker-compose up -d

# 5. Aguardar serviços ficarem saudáveis
echo ""
echo "5️⃣  Aguardando serviços ficarem saudáveis..."
for i in {1..60}; do
    if docker-compose ps | grep -q "backend.*healthy"; then
        print_status "Backend está saudável"
        break
    fi
    if [ $i -eq 60 ]; then
        print_warning "Timeout aguardando backend. Verifique os logs com: docker-compose logs backend"
    fi
    echo -n "."
    sleep 1
done

# 6. Info final
echo ""
echo "========================================================================"
echo "✅ Aplicação iniciada com sucesso!"
echo "========================================================================"
echo ""
echo "📍 Acesse:"
echo "  🌐 API:     http://localhost:3001"
echo "  📚 Swagger: http://localhost:3001/api/docs"
echo "  💚 Health:  http://localhost:3001/health"
echo ""
echo "🔍 Comandos úteis:"
echo "  Ver status:     docker-compose ps"
echo "  Ver logs:       docker-compose logs -f backend"
echo "  Parar:          docker-compose stop"
echo "  Remover:        docker-compose down"
echo ""
echo "========================================================================"
echo ""

