---
documento: Roadmap de Evolução
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 10 — Roadmap de Evolução

> Caminho incremental de **repositório técnico → SaaS sólido**. Cada fase entrega valor demonstrável e eleva a percepção de maturidade de engenharia. **Nenhum big-bang** — cada passo é independentemente valioso para um portfólio.

---

## Visão Geral

```
Fase 0        Fase 1            Fase 2           Fase 3           Fase 4
MVP atual ──► Fundação ──────► SaaS Core ─────► Enterprise ────► Escala & IA+
(Streamlit)   (API + React)    (multi-tenant)   (governança)     (avançado)
```

---

## Fase 0 — MVP Atual (✅ concluído)

**Estado:** protótipo funcional validando a hipótese central.

- Text-to-SQL agêntico (Llama 3.3 via Groq).
- Human-in-the-Loop, Self-Healing, memória conversacional.
- Dashboard de KPIs, FinOps, logs de raciocínio.
- Interface Streamlit.

**Valor de portfólio:** prova que o autor constrói IA aplicada com instinto de segurança e custo.

---

## Fase 1 — Fundação Profissional

**Objetivo:** separar frontend/backend e estabelecer padrões de produção.

| Entregável | Detalhe |
|-----------|---------|
| 🔧 Backend FastAPI | Extrair a lógica do `app.py` para API tipada (OpenAPI). |
| ⚛️ Frontend React | SPA com a tela conversacional (doc 09). |
| 🧪 Testes + CI | `pytest`, lint, type-check, GitHub Actions. |
| 📊 Observabilidade base | Logs estruturados + OTel + métricas básicas. |
| 🐳 Docker + Compose | Ambiente reprodutível local. |
| 🛡️ Guard estático de SQL | Substituir confiança no prompt por parser (`sqlglot`). |

**Marco:** demo executável com FE/BE separados, testes verdes, instrumentado.

---

## Fase 2 — SaaS Core (Multi-Tenant)

**Objetivo:** transformar em produto multi-utilizador.

| Entregável | Detalhe |
|-----------|---------|
| 🔐 Auth + RBAC | OAuth2/OIDC, papéis, organizações. |
| 🏢 Multi-tenancy | Postgres + RLS por `org_id`. |
| 🔌 Fontes de dados | Dataset de exemplo + upload CSV/Parquet. |
| 💰 FinOps por tenant | Orçamento, limites, alertas. |
| 📈 Dashboards Grafana | System health, AI quality, FinOps. |
| 🧠 LLM observability | Langfuse (traces, custo, evals). |

**Marco:** múltiplos tenants isolados, com governança de custo e qualidade de IA medida.

---

## Fase 3 — Enterprise & Governança

**Objetivo:** atributos que fecham contratos maiores.

| Entregável | Detalhe |
|-----------|---------|
| 🔑 SSO (SAML/OIDC) + MFA | Identidade enterprise. |
| 📜 Auditoria completa | AuditEvent imutável, retenção configurável. |
| 🧩 Conectores SQL | Postgres/MySQL/BigQuery (read-only). |
| 🤖 HITL por políticas | Aprovação automática por role/risco. |
| 🧪 Evals de IA no CI | Accuracy de Text-to-SQL como quality gate. |
| ♿ Acessibilidade AA | Auditoria WCAG completa. |

**Marco:** plataforma auditável, segura e conectável a dados reais de clientes.

---

## Fase 4 — Escala & IA Avançada

**Objetivo:** diferenciação técnica de fronteira.

| Entregável | Detalhe |
|-----------|---------|
| ⚡ Semantic cache | Reduzir custo/latência de IA. |
| 🧠 Insights proativos | Detecção automática de anomalias e alertas. |
| 🗣️ CX semântico | Embeddings de reviews: temas, sentimento, clustering. |
| 🔀 Roteamento de modelos | Modelo certo por tarefa; BYO-LLM. |
| 🌐 Multi-região / HA | Escala global, failover. |
| 🧱 Extração de serviços | IA Orchestrator e ingestão como serviços. |

**Marco:** SaaS escalável com diferenciais de IA defensáveis.

---

## Matriz de Priorização (Impacto × Esforço)

```
Impacto
  ▲
A │  Auth+RBAC        Frontend React      Backend FastAPI
L │  Multi-tenancy    Guard SQL estático  Langfuse evals
T │
O │  ────────────────────────────────────────────────
  │  SSO/MFA          Conectores SQL      Semantic cache
M │  Multi-região     CX semântico
É │
D │  ────────────────────────────────────────────────
I │  i18n extra        Storybook          Otimizações finas
O │
  └──────────────────────────────────────────────────►
     BAIXO            MÉDIO              ALTO   Esforço
```

> **Quick wins de portfólio (alto impacto, esforço moderado):** Backend FastAPI + Frontend React + Guard SQL estático + Observabilidade base. Estes quatro já elevam dramaticamente a percepção de senioridade.

---

## Critérios de "pronto para mostrar a recrutadores"

- [ ] FE/BE separados, com README e arquitetura documentada (esta pasta `specs/`).
- [ ] Testes e CI verdes, badges no README.
- [ ] Demo pública (deploy) ou vídeo curto do fluxo conversacional.
- [ ] Observabilidade visível (screenshot de dashboards).
- [ ] ADRs explicando decisões (doc 11).

