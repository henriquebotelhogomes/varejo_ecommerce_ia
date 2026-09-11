---
documento: Riscos, Premissas e Decisões Arquiteturais (ADRs)
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 11 — Riscos, Premissas & Decisões Arquiteturais

---

## Parte A — Premissas

| ID | Premissa | Impacto se falsa |
|----|----------|------------------|
| P-01 | Modelos open-source via Groq são "bons o suficiente" para Text-to-SQL de qualidade. | Necessário roteamento p/ modelo premium → custo maior. |
| P-02 | Utilizadores aceitam o passo de aprovação (HITL) como valor, não fricção. | Rever UX p/ auto-aprovação por política. |
| P-03 | A maioria das perguntas resolve-se com `SELECT` sobre dados estruturados. | Ampliar p/ análise semântica/RAG. |
| P-04 | Tenants de médio porte toleram latência de 2–5s para insights complexos. | Investir mais em cache/streaming. |
| P-05 | Custo de IA por insight pode ser mantido baixo com cache + truncamento. | Margens pressionadas; rever pricing. |
| P-06 | Datasets cabem em Postgres/DuckDB nesta fase (não exigem warehouse já). | Antecipar conectores de warehouse. |

---

## Parte B — Riscos

### Legenda: P (Probabilidade) × I (Impacto) — Baixo / Médio / Alto

| ID | Risco | P | I | Mitigação |
|----|-------|---|---|-----------|
| R-01 | **Alucinação de SQL** (query plausível mas errada). | M | A | Guard estático + HITL + evals contra golden set + exibição da query. |
| R-02 | **Prompt injection** via dados/pergunta. | M | A | Separação de instruções, allow-list de tabelas, guard de saída (só SELECT). |
| R-03 | **Explosão de custo de IA** ("denial of wallet"). | M | A | Orçamento por tenant, circuit breaker, semantic cache, rate limit. |
| R-04 | **Vazamento entre tenants**. | B | A | RLS no Postgres, conexões isoladas, testes de isolamento. |
| R-05 | **Lock-in num provedor de LLM**. | M | M | Abstração `LLMProvider`, suporte BYO-LLM. |
| R-06 | **Latência alta degrada UX**. | M | M | Streaming SSE, cache multinível, modelo rápido p/ tarefas simples. |
| R-07 | **Complexidade prematura** (over-engineering). | M | M | Começar como modular monolith; extrair serviços só quando justificado. |
| R-08 | **Qualidade de Text-to-SQL regride** após mudança de prompt/modelo. | M | A | Evals no CI como quality gate, versionamento de prompts. |
| R-09 | **Dados sensíveis em logs**. | B | A | Redaction/masking automático, revisão de logging. |
| R-10 | **Self-Healing entra em loop / custo descontrolado**. | B | M | Limite de N tentativas com backoff (já no MVP), contabilização de tokens. |
| R-11 | **Scope creep** desviando o foco de portfólio. | A | M | Roadmap faseado, "quick wins" priorizados (doc 10). |

---

## Parte C — Architecture Decision Records (ADRs)

> Formato resumido. Cada ADR registra contexto, decisão, consequências e alternativas.

### ADR-001 — Modular Monolith antes de Microserviços
- **Contexto:** projeto de portfólio / produto inicial, equipa pequena.
- **Decisão:** iniciar como **monólito modular** (FastAPI) com bounded contexts claros; extrair serviços só sob necessidade real.
- **Consequências:** ✅ menor complexidade operacional, deploy simples, evolução rápida. ⚠️ exige disciplina de fronteiras internas.
- **Alternativa rejeitada:** microserviços desde o início (complexidade prematura, R-07).

### ADR-002 — Frontend React/TS substituindo Streamlit
- **Contexto:** Streamlit é ótimo p/ prototipar, mas limita UX, branding e performance.
- **Decisão:** migrar para **React + TypeScript + Tailwind + shadcn/ui**.
- **Consequências:** ✅ UX profissional, controlo total, valor de portfólio FE. ⚠️ mais esforço inicial; exige API separada.
- **Alternativa rejeitada:** manter Streamlit (teto de qualidade de UI).

### ADR-003 — Guard estático de SQL (parser) além do prompt
- **Contexto:** o MVP bloqueia DML/DDL via instrução no prompt — frágil contra injection.
- **Decisão:** adicionar **validação por parser (`sqlglot`)** + allow-list de tabelas antes de qualquer execução.
- **Consequências:** ✅ segurança verificável, não depende do "bom comportamento" do LLM. ⚠️ manter o parser atualizado.
- **Alternativa rejeitada:** confiar só no prompt (R-02).

### ADR-004 — Abstração de provedor de LLM (BYO-LLM)
- **Contexto:** risco de lock-in e necessidade de roteamento de custo/qualidade.
- **Decisão:** interface `LLMProvider`; **Groq como default**, com suporte a outros provedores.
- **Consequências:** ✅ flexibilidade, FinOps, resiliência (fallback). ⚠️ camada de abstração a manter.
- **Alternativa rejeitada:** acoplar diretamente a um SDK (R-05).

### ADR-005 — Human-in-the-Loop como política, não só botão
- **Contexto:** HITL manual é seguro mas pode ser fricção em escala.
- **Decisão:** manter HITL como **núcleo de confiança**, evoluindo para **aprovação por política** (por role/risco da query) na Fase 3.
- **Consequências:** ✅ equilíbrio segurança/UX. ⚠️ definir bem as regras de risco.
- **Alternativa rejeitada:** auto-execução sem revisão (inaceitável p/ trust by design).

### ADR-006 — Observabilidade de LLM com Langfuse + OTel
- **Contexto:** logs caseiros (como no MVP) não escalam nem medem qualidade.
- **Decisão:** **OpenTelemetry** (sistema) + **Langfuse** (LLM: traces, custo, evals).
- **Consequências:** ✅ qualidade e custo mensuráveis, detecção de regressão. ⚠️ infra adicional.
- **Alternativa rejeitada:** logging manual em sessão (não auditável, não escala).

### ADR-007 — Multi-tenancy com RLS no Postgres
- **Contexto:** isolamento de dados entre organizações é crítico.
- **Decisão:** **shared DB + Row-Level Security** por `org_id` p/ metadados; isolamento físico/lógico p/ dados do tenant.
- **Consequências:** ✅ isolamento aplicado pelo banco, custo razoável. ⚠️ RLS exige rigor; opção dedicada p/ Enterprise.
- **Alternativa rejeitada:** isolamento só na aplicação (R-04).

### ADR-008 — Streaming via SSE para respostas de IA
- **Contexto:** latência de LLM prejudica UX se a resposta vier "de uma vez".
- **Decisão:** **Server-Sent Events** para entrega token-by-token.
- **Consequências:** ✅ time-to-first-token baixo, UX percebida superior. ⚠️ gestão de conexões/timeout.
- **Alternativa rejeitada:** request/response bloqueante (UX inferior).

---

## Parte D — Itens em Aberto (a decidir)

| # | Questão | Quando decidir |
|---|---------|----------------|
| Q1 | Cloud-alvo (AWS / GCP / Cloud Run vs. Kubernetes)? | Antes da Fase 2 |
| Q2 | Pricing exato (seats vs. usage vs. híbrido)? | Antes do go-to-market |
| Q3 | Embeddings/vector store para CX semântico (pgvector vs. dedicado)? | Fase 4 |
| Q4 | Estratégia de warehouse (DuckDB vs. BigQuery/Snowflake)? | Quando surgir tenant com dados grandes |

---

> **Nota de manutenção:** novas decisões arquiteturais relevantes devem ser adicionadas como `ADR-00N` aqui, com data e status (Proposto / Aceito / Substituído).
