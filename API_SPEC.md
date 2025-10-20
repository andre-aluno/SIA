# SIA – Sistema de Alocação de Professores

> Documento de especificação para construção de uma API RESTful em Flask que substituirá a prova de conceito atual em Streamlit. Este documento cobre domínio, requisitos funcionais e não funcionais, contratos de endpoints, modelos de dados, fluxos e considerações de implementação.

---
## 1. Objetivos

1. Separar frontend (React) e backend (Flask) em uma arquitetura limpa e escalável.
2. Expor uma API consistente para gestão de: Áreas de Competência, Professores, Disciplinas, Semestres, Ofertas e Alocações.
3. Disponibilizar serviços de importação de dados (Excel), exportação (Excel) e geração automática de alocações via Algoritmo Genético (AG).
4. Garantir integridade dos dados e regras de negócio presentes no protótipo.
5. Facilitar extensões futuras (autenticação, relatórios, dashboards, versionamento de regras de alocação).

---
## 2. Escopo Funcional

### 2.1. Gestão de Áreas de Competência
- Criar, listar, detalhar, editar e remover áreas.
- Impedir duplicidade de nomes.

### 2.2. Gestão de Professores
- CRUD completo.
- Definir titulação e nível (0–4) coerentes.
- Associações N:N com áreas de competência.
- Carga máxima e modelo de contratação (Mensalista / Horista).
- Atualizar áreas associadas (substituição ou adição incremental).

### 2.3. Gestão de Disciplinas
- CRUD completo.
- Associação obrigatória a uma área.
- Nível esperado entre 0–4.

### 2.4. Gestão de Semestres Letivos
- CRUD completo.
- Validação: data_inicio < data_fim.
- Nome único (ex: 2025-1).

### 2.5. Gestão de Ofertas de Disciplina
- Criar oferta (semestre + disciplina + turma).
- Validar unicidade (semestre, disciplina, turma).
- Listar com filtros (por semestre, disciplina, status de alocação).

### 2.6. Gestão de Alocações
- Criar alocação de professor para oferta (1:1 por oferta).
- Impedir alocação duplicada.
- Listar todas ou filtrar por semestre, professor, área, disciplina.
- Remover alocação.

### 2.7. Importação de Dados (Excel)
- Ler planilha enviada pelo usuário (upload multipart/form-data).
- Popular áreas, professores (com áreas), disciplinas, semestres, ofertas e alocações existentes.
- Transação única: rollback em caso de erro.
- Operação idempotente (não cria duplicatas).

### 2.8. Exportação de Alocações (Excel)
- Gerar arquivo Excel estruturado por semestre.
- Incluir status (Alocado/Pendente), carga, níveis, área, professor.

### 2.9. Algoritmo Genético (Otimização)
- Simular alocação automática para ofertas pendentes de um semestre.
- Expor parâmetros (ngen, pop_size, cxpb, mutpb).
- Retornar melhor indivíduo + métricas (fitness, logs de evolução).
- Endpoint para confirmar gravação das sugestões.

### 2.10. Relatórios / Consolidação (MVP opcional)
- Totais de carga por professor e percentual de uso.
- Pendências (ofertas não alocadas) por área.

---
## 3. Fora de Escopo Inicial (Planejar Futuro)
- Autenticação / Autorização (JWT / OAuth2).
- Versionamento de regras de fitness.
- Multi-campus / Multi-unidade.
- Auditoria detalhada (histórico de alterações).
- Internacionalização.

---
## 4. Modelos de Dados (Domínio)

### 4.1. Área de Competência (`AreaCompetencia`)
- id: int
- nome: string (único, obrigatório)

### 4.2. Professor (`Professor`)
- id: int
- nome: string (obrigatório)
- titulacao: string (Enum lógica: 'Ensino Médio', 'Graduado', 'Especialista', 'Mestre', 'Doutor')
- nivel: int (0–4)
- carga_maxima: decimal(6,2)
- modelo_contratacao: string ("Mensalista " ou "Horista")
- areas: N:N -> `AreaCompetencia`

### 4.3. Disciplina (`Disciplina`)
- id: int
- nome: string (obrigatório)
- carga_horaria: decimal(5,2)
- nivel_esperado: int (0–4)
- area_id: FK -> `AreaCompetencia`

### 4.4. Semestre Letivo (`SemestreLetivo`)
- id: int
- nome: string (único, obrigatório) (ex: 2025-1)
- ano: int
- periodo: string (livre ex: "1", "EAD1")
- data_inicio: date
- data_fim: date (validação: início < fim)

### 4.5. Oferta (`Oferta`)
- id: int
- semestre_id: FK -> `SemestreLetivo`
- disciplina_id: FK -> `Disciplina`
- turma: string (obrigatório)
- UNIQUE(semestre_id, disciplina_id, turma)

### 4.6. Alocação (`Alocacao`)
- id: int
- oferta_id: FK -> `Oferta`
- professor_id: FK -> `Professor`
- Regra: apenas uma alocação por oferta (1:1). Impedir segunda inserção.

### 4.7. Associação Professor ↔ Área (`professor_area_competencia`)
- professor_id: FK -> `Professor`
- area_id: FK -> `AreaCompetencia`
- PK composto (professor_id, area_id)

---
## 5. Regras de Negócio

1. Titulação mapeada para nível (Ensino Médio=0, Graduado=1, Especialista=2, Mestre=3, Doutor=4). Persistir ambos.
2. Uma oferta só pode possuir no máximo um professor (modelo atual).
3. Carga do professor calculada como soma das cargas das disciplinas alocadas.
4. Carga não pode exceder `carga_maxima` (para lógica de GA penaliza, mas no CRUD simples pode permitir; decidir política: impedir ou apenas avisar). MVP: permitir, mas retornar alerta.
5. Ao excluir uma área: se ligada a disciplina, bloqueia (ON DELETE RESTRICT na lógica). Professores perdem referência via tabela associativa (cascata controlada).
6. Importação Excel não deve criar duplicatas (checar por nome das entidades).
7. Algoritmo Genético só considera ofertas sem alocação.
8. Atualização de áreas do professor substitui conjunto completo (PUT) ou adiciona/remover (PATCH). Definir dois modos.

---
## 6. Estrutura da API (Organização de Código)

Proposta de pastas (Flask app factory):
```
backend/
  app/
    __init__.py        # create_app()
    config.py          # Config classes (Dev, Prod, Test)
    extensions.py      # db, migrate, cache, cors
    models/            # SQLAlchemy models
    schemas/           # Pydantic ou Marshmallow para (de)serialização
    services/          # Regras de negócio e AG
    repositories/      # Acesso a dados (queries complexas)
    api/
      v1/
        areas.py
        professores.py
        disciplinas.py
        semestres.py
        ofertas.py
        alocacoes.py
        importacao.py
        exportacao.py
        ag.py
    utils/             # Helpers (excel, erros, parsing)
    errors.py          # Mapeamento para HTTP codes
  migrations/          # Alembic
  tests/               # Pytest
  wsgi.py              # Entry point
  requirements.txt
```

---
## 7. Convenções da API

- Versão base: `/api/v1`.
- JSON como formato padrão (`Content-Type: application/json`).
- Pagination: `?page=1&page_size=50` (default page_size=50, max=200).
- Filtragem: múltiplos query params (`?semestre=2025-1&area=Programacao`).
- Ordenação: `?sort=nome,-id`.
- Erros: objeto `{ "error": { "code": "RESOURCE_NOT_FOUND", "message": "..." } }`.
- Sucesso: sempre retorna recurso ou `{ "status": "ok" }` para operações sem corpo.
- Excel Download: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
- Idempotência Importação: chave de deduplicação natural (nome). Não implementado token de operação no MVP.

---
## 8. Endpoints Detalhados

### 8.1. Áreas
| Método | Rota | Descrição | Body | Respostas |
|--------|------|-----------|------|-----------|
| GET | /api/v1/areas | Lista paginada | - | 200 lista |
| GET | /api/v1/areas/{id} | Detalhe | - | 200 / 404 |
| POST | /api/v1/areas | Cria área | {nome} | 201 / 409 duplicata |
| PUT | /api/v1/areas/{id} | Atualiza totalmente | {nome} | 200 / 404 / 409 |
| DELETE | /api/v1/areas/{id} | Remove | - | 204 / 404 / 409 se em uso |

### 8.2. Professores
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/v1/professores | Lista (filtros: area, titulacao, nivel_min, nivel_max) |
| GET | /api/v1/professores/{id} | Detalhe (inclui áreas e carga atual calculada) |
| POST | /api/v1/professores | Cria (nome, titulacao, modelo_contratacao, areas[]) |
| PUT | /api/v1/professores/{id} | Atualiza todos campos + substitui áreas |
| PATCH | /api/v1/professores/{id}/areas | Altera incrementalmente (add/remove) |
| DELETE | /api/v1/professores/{id} | Remove (se sem alocações ativas) |

Carga atual endpoint opcional:
- GET `/api/v1/professores/{id}/carga` -> `{ "total": 96.0, "percentual": 0.75 }`

### 8.3. Disciplinas
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/v1/disciplinas | Filtros: area, nivel_min, nivel_max |
| GET | /api/v1/disciplinas/{id} | Detalhe |
| POST | /api/v1/disciplinas | Cria |
| PUT | /api/v1/disciplinas/{id} | Atualiza |
| DELETE | /api/v1/disciplinas/{id} | Remove (se sem ofertas) |

### 8.4. Semestres
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/v1/semestres | Lista |
| GET | /api/v1/semestres/{id} | Detalhe |
| POST | /api/v1/semestres | Cria |
| PUT | /api/v1/semestres/{id} | Atualiza |
| DELETE | /api/v1/semestres/{id} | Remove (cascata em ofertas e alocações) |

### 8.5. Ofertas
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/v1/ofertas | Filtros: semestre, disciplina, status (pendente/alocado) |
| GET | /api/v1/ofertas/{id} | Detalhe |
| POST | /api/v1/ofertas | Cria |
| PUT | /api/v1/ofertas/{id} | Atualiza (semestre, disciplina, turma) |
| DELETE | /api/v1/ofertas/{id} | Remove (se sem alocação) |

Batch criação opcional:
- POST `/api/v1/ofertas/batch` -> lista de objetos.

### 8.6. Alocações
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/v1/alocacoes | Filtros: semestre, professor, disciplina, area |
| GET | /api/v1/alocacoes/{id} | Detalhe |
| POST | /api/v1/alocacoes | Cria (oferta_id, professor_id) |
| DELETE | /api/v1/alocacoes/{id} | Remove |

Endpoint de pendentes:
- GET `/api/v1/semestres/{nome}/ofertas/pendentes` -> ofertas sem alocação.

### 8.7. Importação Excel
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/v1/importacoes/excel | Upload multipart/form-data campo `file` | Retorna resumo (contagens criadas/ignoradas)

### 8.8. Exportação Excel
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/v1/semestres/{nome}/alocacoes/export | Retorna arquivo Excel (download) |

### 8.9. Algoritmo Genético (AG)
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/v1/semestres/{nome}/alocacoes/ag/simular | Executa AG e retorna plano sugerido |
| POST | /api/v1/semestres/{nome}/alocacoes/ag/confirmar | Persiste sugestões (corpo: lista { oferta_id, professor_id }) |

Parâmetros (simular):
```json
{
  "ngen": 50,
  "pop_size": 100,
  "cxpb": 0.7,
  "mutpb": 0.2
}
```
Resposta (exemplo):
```json
{
  "fitness": 12345.67,
  "sugestoes": [
    {"oferta_id": 10, "disciplina": "Calculo I", "professor_id": 3, "professor": "Maria"},
    {"oferta_id": 11, "disciplina": "Álgebra", "professor_id": 5, "professor": "João"}
  ],
  "estatisticas": {
    "geracoes": 50,
    "max": 13000.0,
    "avg": 11000.2,
    "min": 5000.4
  }
}
```

---
## 9. Schemas (JSON) – Exemplos

### 9.1. Professor (GET)
```json
{
  "id": 1,
  "nome": "Ana Silva",
  "titulacao": "Mestre",
  "nivel": 3,
  "carga_maxima": 128.0,
  "modelo_contratacao": "Mensalista ",
  "areas": [ {"id": 2, "nome": "Programação"} ],
  "carga_atual": 64.0,
  "percentual_carga": 0.5
}
```

### 9.2. Criar Professor (POST)
```json
{
  "nome": "Carlos Pereira",
  "titulacao": "Doutor",
  "modelo_contratacao": "Horista",
  "areas_ids": [1, 2]
}
```
Resposta:
```json
{"id": 12, "nome": "Carlos Pereira"}
```

### 9.3. Erro
```json
{
  "error": {
    "code": "DUPLICATE_RESOURCE",
    "message": "Área já existente"
  }
}
```

---
## 10. Regras de Validação

| Campo | Regra | Erro |
|-------|-------|------|
| nome área | não vazio | 422 INVALID_FIELD |
| titulacao | valor permitido | 422 INVALID_ENUM |
| nivel | 0–4 | 422 OUT_OF_RANGE |
| data_inicio < data_fim | obrigatório | 422 INVALID_DATE_RANGE |
| oferta (unique) | semestre+disciplina+turma | 409 DUPLICATE_RESOURCE |
| alocação única | uma por oferta | 409 CONFLICT |

---
## 11. Estratégia de Persistência

- SQLAlchemy + Alembic para migrações.
- Sessão por request (scoped_session).
- Transações explícitas em operações batch/importação/AG confirm.
- Tratamento de exceções: IntegrityError -> mapeado para 409.

---
## 12. Algoritmo Genético (Integração)

- Módulo `services/ag_service.py`:
  - `load_data(semestre_nome)` retorna professores + ofertas pendentes.
  - `run_ga(params)` executa e devolve indivíduo + log.
  - Conversão do indivíduo (lista de professor_ids ordenada por ofertas) para sugestões.
- Persistência apenas em confirmar.
- Penalidades/Bônus parametrizadas externamente (permitir configuração futura via `config.py`).

---
## 13. Segurança (Futuro)

- CORS restrito ao domínio do frontend.
- Rate limit (Flask-Limiter) para endpoints sensíveis (import/export/AG).
- Autenticação JWT (planejado).
- Sanitização básica de inputs (evitar injection em filtros dinâmicos; usar ORM corretamente).

---
## 14. Logging & Observabilidade

- Logging estruturado (JSON) opcional.
- Nível INFO para fluxo normal; DEBUG para desenvolvimento.
- Métricas (futuro): tempo de execução do AG, número de ofertas pendentes, carga média por professor.

---
## 15. Testes

| Tipo | Escopo |
|------|--------|
| Unit | Services (AG, importação parser, validações) |
| Integration | Endpoints CRUD + DB real (test container) |
| E2E (futuro) | Fluxo completo: criar semestre → criar ofertas → AG → confirmar |

Casos críticos:
- Duplicata de oferta.
- Alocação repetida.
- Importação com linhas inválidas.
- AG sem ofertas pendentes (retornar aviso).

---
## 16. Performance

- Paginação obrigatória em listas grandes.
- Eager loading (joinedload) para evitar N+1 (professores → áreas, ofertas → disciplina → área).
- Indexes: ofertas(semestre_id, disciplina_id), professor_area(area_id), alocacao(oferta_id).
- Possível cache leve (Redis) para métricas agregadas (futuro).

---
## 17. Deploy

- Variáveis de ambiente: `DATABASE_URL`, `FLASK_ENV`, `SECRET_KEY`.
- Gunicorn + gevent/uvicorn workers.
- Dockerfile multi-stage.
- Health check: `GET /api/v1/health` → `{ "status": "ok" }` + opcional verificação DB.

---
## 18. Roadmap de Evolução

| Fase | Itens |
|------|-------|
| MVP | CRUDs + importação + exportação + AG simular + confirmar |
| Fase 2 | Autenticação + relatórios + otimizações AG configuráveis |
| Fase 3 | Auditoria + cache + dashboards carga |
| Fase 4 | Multi-tenant + versionamento de regras |

---
## 19. Glossário
- Oferta: instância de disciplina oferecida em semestre + turma.
- Alocação: vínculo professor ↔ oferta.
- AG: Algoritmo Genético para otimização da distribuição de professores.
- Carga Máxima: limite de horas atribuíveis a um professor no semestre.

---
## 20. Checklist de Implementação (Ordem Sugerida)
1. App factory + config básica.
2. Modelos + migração inicial (Alembic).
3. Schemas (Marshmallow ou Pydantic). 
4. Blueprints CRUD (áreas → professores → disciplinas → semestres → ofertas → alocações).
5. Importação Excel.
6. Exportação Excel.
7. Serviço AG (simular + confirmar).
8. Erros padronizados + testes unitários.
9. Índices e otimizações de query.
10. Health check + logging.

---
## 21. Exemplos de Respostas

### Listar ofertas pendentes
```json
{
  "page": 1,
  "page_size": 50,
  "total": 3,
  "items": [
    {"id": 10, "disciplina": {"id": 5, "nome": "Cálculo I"}, "semestre": "2025-1", "turma": "A", "status": "PENDENTE"},
    {"id": 11, "disciplina": {"id": 7, "nome": "Álgebra"}, "semestre": "2025-1", "turma": "B", "status": "PENDENTE"}
  ]
}
```

### Erro de alocação duplicada
```json
{
  "error": {
    "code": "ALOCACAO_EXISTENTE",
    "message": "Oferta já possui professor alocado"
  }
}
```

---
## 22. Considerações Finais

Este documento consolida os requisitos necessários para migrar o protótipo em Streamlit para uma API robusta em Flask, mantendo integralmente a lógica de negócio já validada e abrindo espaço para evolução incremental. Seguir a ordem sugerida e padronizar respostas garantirá menor atrito na integração com o futuro frontend em React.

Qualquer ajuste adicional (ex: autenticação) deve estender as seções 8 (Endpoints) e 13 (Segurança).

---


