---
documento: Estratégia de Observabilidade e Rastreabilidade
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 06 — Observabilidade & Rastreabilidade

> Em sistemas de IA, **observabilidade não é luxo — é o que separa um demo de um produto**. Não basta saber que respondeu; é preciso saber _como_, _quanto custou_ e se a resposta foi _confiável_.

Esta estratégia evolui o que o MVP já faz (logs de raciocínio na aba "Caixa Preta" + contagem de tokens FinOps) para uma plataforma de observabilidade de produção.

---

## 1. Os Três Pilares + o Quarto (IA)

```
┌──────────────┬──────────────┬──────────────┬───────────────────┐
│    LOGS      │   MÉTRICAS   │    TRACES    │  LLM OBSERVABILITY │
│ (o que       │ (tendências  │ (jornada de  │ (qualidade, custo, │
│  aconteceu)  │  agregadas)  │  uma req)    │  prompts, evals)   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
        Loki         Prometheus    OpenTelemetry      Langfuse
                     + Grafana     + Jaeger/Tempo
```

---

## 2. Logs Estruturados

- **Formato JSON** com campos padronizados: `timestamp`, `level`, `service`, `trace_id`, `org_id`, `user_id`, `event`, `duration_ms`.
- **Sem PII** em logs (mascaramento/redaction automático).
- **Níveis** disciplinados (DEBUG/INFO/WARN/ERROR) e correlação por `trace_id`.
- Centralizados em **Loki** (ou equivalente), pesquisáveis no Grafana.

## 3. Métricas (Prometheus + Grafana)

### Métricas de sistema (RED + USE)
- **Rate / Errors / Duration** por endpoint.
- Saturação de CPU/memória/conexões DB/fila Redis.

### Métricas de produto & IA
| Métrica | Tipo | Por quê |
|---------|------|---------|
| `ai_tokens_total{type,model,org}` | counter | FinOps |
| `ai_cost_usd_total{model,org}` | counter | FinOps |
| `ai_latency_seconds{step}` | histogram | Performance da pipeline |
| `sql_generation_success_ratio` | gauge | Qualidade Text-to-SQL |
| `self_heal_attempts` / `self_heal_success_ratio` | histogram/gauge | Robustez |
| `hitl_approval_ratio` | gauge | Confiança do utilizador na IA |
| `query_execution_seconds` | histogram | Performance de dados |

## 4. Tracing Distribuído (OpenTelemetry)

- **Trace ID propagado** do frontend → API → orquestrador → LLM → DB.
- Cada **nó do grafo LangGraph** vira um *span* (geração, guard, HITL, execução, self-heal, sumarização).
- Spans de LLM anexam atributos: `model`, `prompt_tokens`, `completion_tokens`, `cost`, `temperature`.
- Exportado para **Jaeger/Tempo**; correlacionado com logs e métricas no Grafana.

## 5. LLM Observability (Langfuse) — o diferencial

A camada que recrutadores de empresas de IA procuram:

- **Traces de cada chamada**: prompt completo, resposta, tokens, custo, latência, versão do prompt.
- **Avaliação de qualidade (Evals)**: accuracy do SQL gerado contra *golden dataset*, scores de relevância da sumarização.
- **Prompt management & versionamento**: prompts como artefactos versionados, com A/B e rollback.
- **Detecção de regressão**: alertas quando a qualidade do Text-to-SQL cai após mudança de prompt/modelo.
- **Dataset de feedback**: thumbs up/down do utilizador alimentam o conjunto de avaliação.

## 6. Rastreabilidade & Auditoria

Para cada insight entregue, é possível reconstruir a **cadeia completa**:

```
Pergunta do utilizador
   → prompt enviado (versão X)
   → query SQL proposta
   → decisão HITL (quem aprovou, quando)
   → tentativas de self-heal (se houve)
   → query final executada
   → resultado (linhas, duração)
   → insight gerado
   → tokens e custo
```

- **AuditEvent imutável** (append-only) para ações sensíveis (login, aprovação de query, mudança de permissão, export de dados).
- Retenção **configurável por plano** (compliance Enterprise).
- Auditoria **isolada por tenant**.

## 7. Alertas & SLOs

- **Error budgets** baseados nos SLOs do doc 05.
- Alertas (PagerDuty/Slack) para: queda de disponibilidade, explosão de custo de IA, queda de accuracy de SQL, fila de ingestão atrasada.
- **Runbooks** ligados a cada alerta.

## 8. Dashboards (Grafana — propostos)

1. **System Health** — RED/USE, latências, erros.
2. **AI Quality** — accuracy de SQL, taxa de self-heal, HITL approval.
3. **FinOps** — tokens, custo por tenant, economia vs. baseline.
4. **Tenant Usage** — engajamento, queries por utilizador, ativação.

---

## 9. Evolução a partir do MVP atual

| Hoje (MVP) | Alvo |
|------------|------|
| Logs de raciocínio em `st.session_state` | Logs estruturados em Loki + traces OTel |
| Contagem de tokens manual | Métricas Prometheus + Langfuse automáticos |
| "Caixa preta" exibida na aba Logs | Mesma transparência, agora persistida e auditável |
| Custo estimado vs. GPT 5.6 Luna | Dashboard FinOps por tenant com alertas |

> A **filosofia de transparência já existe no MVP** — esta estratégia apenas a leva a um padrão de produção.
