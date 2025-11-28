# 🎯 Backend Flask - Sistema de Alocação de Professores

## 📁 Estrutura do Projeto

```
backend/
├── app.py                          # Entry point da aplicação
├── config.py                       # Configurações (dev, test, prod)
├── API_DOCUMENTATION.md            # Documentação completa da API
├── requirements.txt                # Dependências Python
│
├── app/
│   ├── __init__.py
│   ├── extensions.py               # Extensões Flask (SQLAlchemy, CORS)
│   │
│   ├── models/                     # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── area_competencia.py
│   │   ├── professor.py
│   │   ├── disciplina.py
│   │   ├── semestre_letivo.py
│   │   ├── oferta.py
│   │   ├── alocacao.py
│   │   ├── association.py
│   │   └── README.md
│   │
│   ├── services/                   # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── base_service.py         # Classe base genérica CRUD
│   │   ├── area_competencia_service.py
│   │   ├── disciplina_service.py
│   │   ├── professor_service.py
│   │   ├── semestre_letivo_service.py
│   │   ├── oferta_service.py
│   │   ├── alocacao_service.py
│   │   ├── import_service.py       # Importação Excel
│   │   ├── algoritmo_genetico_service.py
│   │   ├── exemplos_uso.py
│   │   ├── test_services.py
│   │   └── README.md
│   │
│   ├── controllers/                # Controllers REST (NOVO)
│   │   ├── __init__.py             # Registro de todas as rotas
│   │   ├── base_controller.py      # Classe base com métodos comuns
│   │   ├── area_competencia_controller.py
│   │   ├── disciplina_controller.py
│   │   ├── professor_controller.py
│   │   ├── semestre_letivo_controller.py
│   │   ├── oferta_controller.py
│   │   ├── alocacao_controller.py
│   │   ├── import_controller.py
│   │   └── algoritmo_genetico_controller.py
│   │
│   ├── utils/                      # Utilitários
│   │   ├── __init__.py
│   │   └── api_response.py         # Formatação de respostas da API
│   │
│   └── uploads/                    # Pasta para uploads temporários
│       └── .gitkeep
```

---

## 🚀 Como Iniciar

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do backend:

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=3001

# Banco de dados
DATABASE_URL=postgresql://user:password@localhost:5432/alocacao_professor
# Ou para SQLite (desenvolvimento):
# DATABASE_URL=sqlite:///alocacao_professor.db

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. Executar a Aplicação

```bash
python app.py
```

**Saída esperada:**
```
======================================================================
🚀 Iniciando Sistema de Alocação de Professores
======================================================================
🌐 Host: 0.0.0.0
🔌 Porta: 3001
🐛 Debug: True
📚 Documentação: http://0.0.0.0:3001/api/docs
💚 Health Check: http://0.0.0.0:3001/health
======================================================================
```

### 4. Testar Health Check

```bash
curl http://localhost:3001/health
```

---

## 🏗️ Arquitetura em Camadas

### 1️⃣ **Models** (SQLAlchemy)
Define a estrutura dos dados e relacionamentos

### 2️⃣ **Services** (Lógica de Negócio)
Encapsula regras de negócio, validações e operações

### 3️⃣ **Controllers** (Rotas REST)
Expõe os services como endpoints HTTP

### 4️⃣ **API Response** (Formatação)
Padroniza respostas JSON

```
Request HTTP
    ↓
Router (Flask Blueprint)
    ↓
Controller (recebe e valida JSON)
    ↓
Service (processa lógica)
    ↓
Model (interage com BD)
    ↓
Response JSON padronizado
```

---

## 📚 Rotas Principais

### Áreas de Competência
```
POST   /api/areas                 Criar
GET    /api/areas                 Listar
GET    /api/areas/<id>            Obter
PUT    /api/areas/<id>            Atualizar
DELETE /api/areas/<id>            Deletar
```

### Disciplinas
```
POST   /api/disciplinas           Criar
GET    /api/disciplinas           Listar
GET    /api/disciplinas/<id>      Obter
GET    /api/disciplinas/area/<id> Por área
PUT    /api/disciplinas/<id>      Atualizar
DELETE /api/disciplinas/<id>      Deletar
```

### Professores
```
POST   /api/professores           Criar
GET    /api/professores           Listar
GET    /api/professores/<id>      Obter
GET    /api/professores/<id>/carga Info carga
POST   /api/professores/<id>/areas Adicionar área
DELETE /api/professores/<id>/areas Remover área
PUT    /api/professores/<id>      Atualizar
DELETE /api/professores/<id>      Deletar
```

### Semestres Letivos
```
POST   /api/semestres             Criar
GET    /api/semestres             Listar
GET    /api/semestres/ativos      Ativos
GET    /api/semestres/futuros     Futuros
PUT    /api/semestres/<id>        Atualizar
DELETE /api/semestres/<id>        Deletar
```

### Ofertas
```
POST   /api/ofertas               Criar
GET    /api/ofertas               Listar
GET    /api/ofertas/semestre-nome/<nome>/nao-alocadas
PUT    /api/ofertas/<id>          Atualizar
DELETE /api/ofertas/<id>          Deletar
```

### Alocações
```
POST   /api/alocacoes             Criar
POST   /api/alocacoes/bulk        Criar múltiplas
GET    /api/alocacoes             Listar
GET    /api/alocacoes/professor/<id> Do professor
GET    /api/alocacoes/semestre-nome/<nome>/formatado
DELETE /api/alocacoes/<id>        Deletar
```

### Importação
```
POST   /api/import/excel          Upload Excel
GET    /api/import/status         Status
```

### Algoritmo Genético
```
GET    /api/ag/semestre/<nome>/dados       Carregar dados
POST   /api/ag/validar                      Validar viabilidade
GET    /api/ag/config/defaults              Config padrão
POST   /api/ag/fitness                      Calcular fitness
POST   /api/ag/formatar                     Formatar resultado
POST   /api/ag/resumo                       Gerar resumo
```

---

## 🔍 Exemplo de Fluxo API

### 1. Criar Área de Competência

```bash
curl -X POST http://localhost:3001/api/areas \
  -H "Content-Type: application/json" \
  -d '{"nome": "Programação Python"}'
```

**Resposta (201 Created):**
```json
{
  "status": "success",
  "message": "Área 'Programação Python' criada com sucesso",
  "data": {
    "id": 1,
    "nome": "Programação Python"
  }
}
```

### 2. Criar Disciplina

```bash
curl -X POST http://localhost:3001/api/disciplinas \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Python Fundamentals",
    "carga_horaria": 80,
    "nivel_esperado": 1,
    "area_id": 1
  }'
```

### 3. Criar Professor

```bash
curl -X POST http://localhost:3001/api/professores \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Dr. João Silva",
    "titulacao": "Doutor",
    "carga_maxima": 256,
    "modelo_contratacao": "Mensalista ",
    "area_ids": [1]
  }'
```

### 4. Criar Semestre

```bash
curl -X POST http://localhost:3001/api/semestres \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "2025-1",
    "ano": 2025,
    "periodo": "1",
    "data_inicio": "2025-01-15",
    "data_fim": "2025-06-30"
  }'
```

### 5. Criar Oferta

```bash
curl -X POST http://localhost:3001/api/ofertas \
  -H "Content-Type: application/json" \
  -d '{
    "semestre_id": 1,
    "disciplina_id": 1,
    "turma": "A"
  }'
```

### 6. Criar Alocação

```bash
curl -X POST http://localhost:3001/api/alocacoes \
  -H "Content-Type: application/json" \
  -d '{
    "oferta_id": 1,
    "professor_id": 1
  }'
```

---

## 📊 Padrão de Resposta

Todas as respostas seguem o padrão:

### ✅ Sucesso
```json
{
  "status": "success",
  "message": "Descrição da ação",
  "data": { ... }
}
```

### ❌ Erro
```json
{
  "status": "error",
  "message": "Descrição do erro",
  "errors": ["Erro 1", "Erro 2"]
}
```

### 📋 Lista Paginada
```json
{
  "status": "success",
  "message": "Sucesso",
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 50,
    "pages": 5
  }
}
```

---

## 🧪 Testes

### Testar Services

```python
from app.services import AreaCompetenciaService
from app import create_app

app = create_app()
with app.app_context():
    from app.extensions import db
    db.create_all()
    
    service = AreaCompetenciaService(db.session)
    area, error = service.create(nome="Test Area")
    print(f"Area criada: {area.nome}")
```

### Testar Controllers (com pytest)

```bash
pytest tests/test_controllers.py -v
```

---

## 🔧 Configuração do Banco de Dados

### PostgreSQL (Recomendado)

```bash
# Instalar PostgreSQL
brew install postgresql

# Criar banco
createdb alocacao_professor

# Conectar
psql alocacao_professor
```

### SQLite (Desenvolvimento)

```python
# No .env:
DATABASE_URL=sqlite:///alocacao_professor.db
```

---

## 📦 Dependências Principais

```
Flask==2.3.0
Flask-SQLAlchemy==3.0.0
Flask-CORS==4.0.0
SQLAlchemy==2.0.0
psycopg2-binary==2.9.0  # Para PostgreSQL
pandas==1.5.0           # Para importação Excel
openpyxl==3.10.0        # Para leitura Excel
deap==1.4.0             # Para Algoritmo Genético
python-dotenv==1.0.0
```

Veja `requirements.txt` para versões exatas.

---

## 🚀 Deploy em Produção

### 1. Usar Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3001 app:create_app()
```

### 3. Variáveis de Ambiente para Produção

```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:password@prod-db:5432/alocacao_professor
SECRET_KEY=sua_chave_secreta_muito_complexa
```

---

## 🛡️ Segurança (TODO)

- [ ] Autenticação JWT
- [ ] Rate limiting
- [ ] HTTPS/SSL
- [ ] Validação de input mais rigorosa
- [ ] CORS específico por domínio
- [ ] Logging e auditoria
- [ ] Backup automático do BD
- [ ] Monitoramento de performance

---

## 📝 Próximos Passos

1. ✅ **Modelos SQLAlchemy** - COMPLETO
2. ✅ **Services com lógica de negócio** - COMPLETO
3. ✅ **Controllers REST** - COMPLETO
4. 🔄 **Implementar AG real** (usar DEAP)
5. ⏳ **Testes unitários**
6. ⏳ **Documentação Swagger/OpenAPI**
7. ⏳ **Frontend React/Vue**

---

## 🐛 Troubleshooting

### Erro: "database does not exist"
```bash
createdb alocacao_professor
```

### Erro: "connection refused"
Verifique se PostgreSQL está rodando:
```bash
brew services list  # macOS
sudo service postgresql status  # Linux
```

### Erro: "No module named 'app'"
```bash
export PYTHONPATH="${PYTHONPATH}:/Users/andreos/dev/cdia/alocacao-professor/backend"
```

---

## 📞 Suporte

- **Documentação API:** `API_DOCUMENTATION.md`
- **Documentação Services:** `app/services/README.md`
- **Documentação Models:** `app/models/README.md`
- **Exemplos:** `app/services/exemplos_uso.py`

---

## 📄 Licença

MIT License - veja LICENSE para detalhes

---

**Última atualização:** Novembro 2025
**Versão:** 1.0.0

