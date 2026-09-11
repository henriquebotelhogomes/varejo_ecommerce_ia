---
documento: Especificação Técnica de Alto Nível
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 03 — Especificação Técnica de Alto Nível

Este documento descreve **como** o sistema é construído: stack, contratos, modelo de dados e a pipeline de IA. Decisões detalhadas de topologia estão na [Arquitetura (04)](./04-arquitetura.md).

---

## 1. Visão Geral da Stack

| Camada | Hoje (MVP atual) | Proposta SaaS (alvo) | Por quê |
|--------|------------------|----------------------|---------|
| **Frontend** | Streamlit | **React + TypeScript + Vite** | Controlo total de UX, performance e branding profissional. |
| **UI/Design** | Componentes Streamlit | **Tailwind CSS + shadcn/ui + Radix** | Design system acessível, consistente, moderno. |
| **State/Data fetching** | `st.session_state` | **TanStack Query + Zustand** | Cache, sync e estado previsível. |
| **Backend API** | Lógica embutida no `app.py` | **FastAPI (Python) + Pydantic** | Async, tipado, OpenAPI nativo, ótimo p/ IA. |
| **Orquestração IA** | LangChain/LangGraph ad-hoc | **LangGraph + camada de tools tipadas** | Fluxos agênticos determinísticos e auditáveis. |
| **LLM** | Llama 3.3 70B (Groq) | **Groq (default) + provider abstraction** | Custo baixo + flexibilidade BYO-LLM. |
| **Banco de dados** | SQLite local | **PostgreSQL (metadados) + conectores de dados do tenant** | Multi-tenant, transacional, escalável. |
| **Cache/Fila** | — | **Redis (cache + filas) / Celery ou Arq** | Latência e tarefas assíncronas (self-heal, ingestão). |
| **Observabilidade** | `st.session_state` logs | **OpenTelemetry + Langfuse + Prometheus/Grafana** | Traces de LLM + métricas de sistema. |
| **Infra** | Local | **Docker + IaC (Terraform) + Kubernetes/Cloud Run** | Reprodutível, escalável. |

> **Princípio:** a stack atual é um **protótipo válido**; a stack-alvo é o destino. O roadmap (doc 10) descreve a migração incremental, não um big-bang.

---

## 2. Componentes Lógicos

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend (React/TS SPA)                    │
└───────────────┬──────────────────────────────────────────────┘
                │ HTTPS / JSON / SSE (streaming)
┌───────────────▼──────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                       │
│  Auth · Rate limit · Validation · Routing · OpenAPI            │
└───┬──────────┬───────────┬───────────┬───────────┬───────────┘
    │          │           │           │           │
┌───▼───┐ ┌────▼────┐ ┌────▼─────┐ ┌───▼────┐ ┌────▼─────┐
│ Auth  │ │ Conversa│ │  IA      │ │ Data   │ │ FinOps & │
│ & RBAC│ │ Service │ │ Orchestr.│ │ Connect│ │ Billing  │
└───────┘ └────┬────┘ └────┬─────┘ └───┬────┘ └──────────┘
               │           │           │
        ┌──────▼───┐ ┌─────▼─────┐ ┌───▼─────────┐
        │ Postgres │ │ LLM Prov. │ │ Tenant Data │
        │(metadata)│ │ (Groq...) │ │ (SQL/files) │
        └──────────┘ └───────────┘ └─────────────┘
                          │
                   ┌──────▼──────┐
                   │ Observability│ (OTel → Langfuse/Grafana)
                   └──────────────┘
```

### Responsabilidades
- **Auth & RBAC:** identidade, organizações, permissões.
- **Conversation Service:** sessões, histórico, memória, persistência auditável.
- **IA Orchestrator:** pipeline Text-to-SQL, HITL, Self-Healing, sumarização, Next Best Action.
- **Data Connector:** abstração de fontes (exemplo, upload, conectores), introspecção de schema.
- **FinOps & Billing:** contabilidade de tokens, custo, limites, planos.

---

## 3. Pipeline de IA (núcleo)

A pipeline é modelada como um **grafo de estados (LangGraph)**, tornando cada passo observável e testável.

```
[Pergunta]
   │
   ▼
(1) Recuperar contexto ── schema introspection + memória truncada (janela K)
   │
   ▼
(2) Geração de SQL ───── LLM (temperatura 0) → query candidata
   │
   ▼
(3) Guarda de segurança ─ validação estática: só SELECT, sem DDL/DML, allow-list de tabelas
   │
   ▼
(4) Human-in-the-Loop ── aprovação humana OU política automática (por role/risco)
   │
   ▼
(5) Execução read-only ── conexão isolada por tenant, timeout, LIMIT injetado
   │  └─ erro? ──► (5a) Self-Healing: LLM corrige com schema+erro (até N, backoff)
   ▼
(6) Sumarização ──────── LLM transforma resultado em insight de negócio
   │
   ▼
(7) Next Best Action ─── LLM sugere 3 perguntas de aprofundamento
   │
   ▼
[Insight + Tabela + Gráfico + Sugestões]  ──► trace completo na Observabilidade
```

### Pontos críticos de design
- **Determinismo:** `temperature=0` para geração de SQL.
- **Guard estático antes do LLM-guard:** validação por parser SQL (ex.: `sqlglot`) é mais confiável que confiar no prompt.
- **Idempotência & limites:** todo passo de IA tem timeout, retry bounded e contabilização de tokens.
- **Streaming:** respostas via **SSE** para UX responsiva (token-by-token).

---

## 4. Modelo de Dados (metadados — PostgreSQL)

Esquema conceptual (não-DDL) das entidades de controlo do SaaS:

```
Organization (tenant)
  └── User (role: owner|admin|analyst|viewer)
  └── DataSource (tipo: sample|upload|connector, schema_cache)
  └── Conversation
        └── Message (role, content, created_at)
        └── Query (sql, status, attempts, healed_from)
              └── Execution (rows, duration_ms, error?)
        └── AiCall (model, prompt_tokens, completion_tokens, cost, latency_ms, trace_id)
  └── UsageBudget (limit, period, consumed)
  └── AuditEvent (actor, action, target, metadata, ts)
```

> Os **dados do tenant** (reviews, vendas) vivem **separados** dos metadados — em conectores ou storage isolado por organização (ver Segurança, doc 08).

---

## 5. Contratos de API (amostra — OpenAPI-style)

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/v1/auth/login` | Autenticação (retorna JWT). |
| `GET` | `/v1/datasources` | Lista fontes do tenant. |
| `POST` | `/v1/datasources` | Conecta/upload de fonte. |
| `POST` | `/v1/conversations` | Cria conversa. |
| `POST` | `/v1/conversations/{id}/messages` | Envia pergunta → retorna query proposta (stream SSE). |
| `POST` | `/v1/queries/{id}/approve` | Aprova e executa query (HITL). |
| `POST` | `/v1/queries/{id}/reject` | Rejeita query. |
| `GET` | `/v1/usage` | Métricas de FinOps do tenant. |
| `GET` | `/v1/audit` | Trilha de auditoria (admin). |

**Convenções:** REST + JSON, versionamento por path (`/v1`), erros no formato **RFC 7807 (Problem Details)**, paginação por cursor, `Idempotency-Key` em mutações sensíveis.

---

## 6. Estratégia de Testes

| Nível | Foco | Ferramentas (sugestão) |
|-------|------|------------------------|
| **Unitário** | Guards de SQL, parsing, regras de negócio | `pytest` |
| **Integração** | API + Postgres + conectores | `pytest` + `testcontainers` |
| **Avaliação de IA (Evals)** | Qualidade Text-to-SQL (accuracy em golden set) | dataset de avaliação + Langfuse/Promptfoo |
| **E2E** | Fluxos críticos no frontend | Playwright |
| **Contrato** | Compatibilidade FE/BE | OpenAPI + schema validation |
| **Carga** | SLOs de latência | k6 / Locust |

> **Evals de IA são um diferencial sénior:** medir accuracy de SQL gerado contra um *golden dataset* demonstra rigor de engenharia de IA, não apenas "deu certo no demo".

---

## 7. CI/CD (alto nível)

```
PR ──► Lint + Type-check + Unit ──► Build ──► Integration + Evals ──► Preview Deploy
                                                                          │
                                              Merge main ──► Deploy staging ──► E2E ──► Deploy prod (canary)
```

- **Quality gates:** cobertura mínima, evals de IA acima de threshold, SAST/dependency scan.
- **Feature flags** para releases progressivas.
- **Migrations versionadas** (Alembic).

