# 📋 Backlog de Implementação & Tarefas: RetailSense AI

---

## Legenda de Status
- [ ] A Fazer / Pendente
- [/] Em Andamento
- [x] Concluído

---

## Fase 1: Governança, Arquitetura & Qualidade Pré-Commit
- [x] **1.1.** Atualizar documento global de regras `C:\Users\henri\.gemini\GEMINI.md` (regras de frontend, modelos Gemini 3.8 Flash e catálogo OpenCode Go).
- [x] **1.2.** Criar `PRD.md` com visão de produto, personas, requisitos funcionais e não-funcionais.
- [x] **1.3.** Criar `PROJECT_SPEC.md` com topologia C4, diagramas Mermaid, ADRs e stack tecnológica.
- [x] **1.4.** Criar `AGENTS.md` com contratos Pydantic v2, `AgentState`, nós do LangGraph e guardrails.
- [x] **1.5.** Criar `TASKS.md` estruturado em fases ordenadas.
- [x] **1.6.** Criar `.pre-commit-config.yaml` com `ruff` (lint + format), `mypy`, `gitleaks` e validadores de syntax.
- [x] **1.7.** Criar `pyproject.toml` com gerenciamento moderno de dependências (`uv`/pip) e configurações das ferramentas.
- [x] **1.8.** Atualizar `README.md` com hero executivo, badges de status, arquitetura C4 e quickstart oficial.

---

## Fase 2: Camada de Dados, Segurança e Validador AST (`sqlglot`)
- [x] **2.1.** Modularizar ingestão de dados em `src/core/database.py` garantindo índices otimizados no SQLite (`idx_parent_asin`, `idx_rating`).
- [x] **2.2.** Implementar módulo `src/agents/sql_guard.py` com parser determinístico via `sqlglot`:
  - [x] Validar que apenas nós `exp.Select` são permitidos.
  - [x] Bloquear comandos de alteração/exclusão (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`).
  - [x] Garantir/Injetar cláusula de `LIMIT 100` em consultas não agregadas.
- [x] **2.3.** Criar suíte de testes unitários para o validador AST em `tests/unit/test_sql_guard.py`.

---

## Fase 3: Multi-Agentes com LangGraph e Checkpointing
- [x] **3.1.** Implementar contratos Pydantic v2 e estado tipado em `src/agents/state.py` (`AgentState`).
- [x] **3.2.** Implementar provedor de LLM agnóstico em `src/core/llm_provider.py` com suporte primário a **Gemini 3.8 Flash** e **OpenCode Go** (DeepSeek V4.1 Flash/Pro).
- [x] **3.3.** Implementar nó `IntentRouter` em `src/agents/router.py`.
- [x] **3.4.** Implementar nó `NL2SQLGenerator` com injeção de schema dinâmico em `src/agents/sql_agent.py`.
- [x] **3.5.** Implementar nó `SynthesizerAgent` com saída estruturada e Next Best Action em `src/agents/synthesizer.py`.
- [x] **3.6.** Implementar nó e transições de `Self-Healing` no `StateGraph` (limite de 3 tentativas).
- [x] **3.7.** Configurar persistência com `MemorySaver`/`SqliteSaver` e Human-in-the-Loop nativo via `interrupt()`.
- [x] **3.8.** Compilar e testar o grafo completo em `src/agents/graph.py`.

---

## Fase 4: Backend REST Assíncrono com FastAPI e Documentação Scalar
- [x] **4.1.** Estruturar a aplicação FastAPI em `src/api/app.py`.
- [x] **4.2.** Desativar Swagger UI clássico e configurar a documentação interativa viva **Scalar** (`scalar-fastapi`) nos endpoints `/docs` e `/scalar`.
- [x] **4.3.** Implementar rotas analíticas em `src/api/routes/`:
  - [x] `POST /api/v1/chat` com execução de grafo LangGraph e suporte a persistência por `thread_id`.
  - [x] `GET /api/v1/health` para probes de liveness e readiness.
  - [x] `GET /api/v1/kpis` para métricas consolidadas em tempo real do catálogo.
- [x] **4.4.** Criar testes de integração da API em `tests/integration/test_api.py`.

---

## Fase 5: Observabilidade (Langfuse/LangSmith) e Evals com Ragas
- [x] **5.1.** Integrar callbacks de observabilidade em `src/observability/callbacks.py` rastreando latência por nó, árvore de decisão e contagem exata de tokens.
- [x] **5.2.** Configurar painel FinOps unificado comparando custos reais (Gemini/DeepSeek) vs modelos legados.
- [x] **5.3.** Construir dataset padrão de avaliação em `tests/evals/test_dataset.json` com perguntas analíticas reais de e-commerce.
- [x] **5.4.** Implementar suíte de testes automatizados com **Ragas** em `tests/evals/test_ragas.py`:
  - [x] Avaliar *Faithfulness* (meta $\ge 0.85$).
  - [x] Avaliar *Answer Relevancy* (meta $\ge 0.80$).

---

## Fase 6: Frontend Moderno Desacoplado (Padrão Startup Global)
- [x] **6.1.** Inicializar aplicação frontend moderna desacoplada em `frontend/` com React + TypeScript estrito, Vite e Tailwind CSS.
- [x] **6.2.** Instalar e configurar componentes **Shadcn UI** (Button, Card, Badge, Input, Lucide Icons).
- [x] **6.3.** Implementar cliente de chat tipado com Zustand consumindo o backend FastAPI.
- [x] **6.4.** Implementar visualização de SQL auditável com AST Guardrail e exportação de CSV.
- [x] **6.5.** Implementar visualizações analíticas de dados e gráficos com Recharts para as respostas tabulares e KPIs.

---

## Fase 7: Conteinerização, CI/CD e Deploy Cloud Run
- [x] **7.1.** Criar `Dockerfile` multi-stage otimizado unificando Frontend React e Backend FastAPI.
- [x] **7.2.** Criar pipeline de GitHub Actions em `.github/workflows/ci.yml` executando `pre-commit`, `pytest`, `ragas` e build de TypeScript.
- [x] **7.3.** Configurar script e parâmetros de deploy no **Google Cloud Run** com política de Scale-to-Zero ($0 de custo em ociosidade).

---

## Fase 8: Evolução Enterprise v2.0 (DuckDB, Tri-Tiering de LLMs, Streaming SSE & Camada Semântica)
- [x] **8.1. Motor Analítico Colunar DuckDB ($0.00/mês):**
  - [x] Adicionar dependência `duckdb` ao `pyproject.toml`.
  - [x] Criar módulo `src/core/duckdb_engine.py` convertendo a base SQLite em `.duckdb` e gerando arquivo colunar `amazon_reviews.parquet`.
  - [x] Adaptar queries analíticas de agregação (`obter_kpis_detalhados`) para o motor DuckDB com vetorização SIMD.
- [x] **8.2. Camada Semântica Centralizada (Metric Layer):**
  - [x] Criar `src/agents/semantic_layer.py` codificando as fórmulas matemáticas de negócio (CSAT Proxy, Taxa de Promotores, Taxa de Detratores, Índice de Votos Úteis).
  - [x] Injetar as definições semânticas no prompt do `NL2SQLGenerator` para blindar fórmulas matemáticas contra alucinações.
- [x] **8.3. Tri-Tiering Agnóstico de LLMs (Gemini Pro + OpenCode Go + OpenRouter):**
  - [x] Atualizar `src/core/llm_provider.py` para suportar configuração dinâmica via `.env`:
    - Tier Primário: **Google Gemini 3.8 Flash**
    - Tier Código/SQL: **OpenCode Go** (`DeepSeek V4.1 Flash` com 26k req/5h e `Qwen 3.8 Max`)
    - Tier Avaliação Evals: **OpenRouter Free** (`NVIDIA Nemotron 3 Ultra 550B` / `Gemma 4 31B`)
- [x] **8.4. Streaming Progressivo em Tempo Real (Server-Sent Events - SSE):**
  - [x] Implementar endpoint `POST /api/v1/chat/stream` com streaming de eventos de ciclo de vida e tokens de síntese executiva.
  - [x] Atualizar o frontend (`ChatView.tsx` e `api.ts`) para renderização progressiva com Time-to-First-Token $\le 500\text{ms}$.
- [ ] **8.5. RAG Híbrido Qualitativo (LanceDB / Qdrant Embutido):**
  - [ ] Gerar embeddings das 204k avaliações com o modelo oficial `text-embedding-004` da Google.
  - [ ] Integrar busca híbrida (vetores densos + BM25 esparso) no nó `SemanticReviewRetriever`.
- [x] **8.6. Empacotamento e Deploy Serverless no Google Cloud Run ($0.00/mês):**
  - [x] Compilar imagem conteinerizada multi-stage unificada no **Google Cloud Build** (`gcr.io/retainiq-prod/retailsense-ai:latest`).
  - [x] Publicar no **Google Cloud Run** com política de Scale-to-Zero (`min-instances=0`, `max-instances=2`, `memory=1Gi`).
  - [x] Ativar HTTPS e domínio oficial em produção: `https://retailsense-ai-197215016090.us-central1.run.app`.
