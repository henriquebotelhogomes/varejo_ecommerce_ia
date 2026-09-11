---
documento: Estratégia de Performance e Escalabilidade
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 07 — Performance & Escalabilidade

> Em SaaS de IA há **duas dimensões de escala**: a de sistema (requisições, dados) e a de **custo de IA**. Escalar bem significa crescer em utilizadores **sem** crescer custo/latência de forma linear.

---

## 1. Estratégia de Caching (multinível)

| Camada | O que cacheia | Tecnologia | Ganho |
|--------|---------------|------------|-------|
| **CDN** | Assets do frontend (SPA, imagens) | CloudFront/Cloudflare | LCP baixo, custo zero de origem |
| **Schema cache** | Introspecção de schema do tenant | Redis | Evita reler metadados a cada pergunta |
| **Semantic query cache** | Perguntas semanticamente equivalentes → resposta/SQL | Redis + embeddings | **Corta chamadas de LLM** e custo |
| **Result cache** | Resultados de queries idênticas (TTL curto) | Redis | Latência ~0 em repetições |
| **LLM provider cache** | Prompts idênticos | Provider/Groq | Reduz tokens faturados |

> O **semantic cache** é um diferencial: perguntas como _"qual a média de notas?"_ e _"média geral das avaliações?"_ resolvem para o mesmo SQL sem nova chamada cara ao LLM.

---

## 2. Escala Horizontal

- **Backend stateless** → réplicas atrás de load balancer, **HPA** por CPU/latência.
- **Estado externo**: Postgres (managed, com réplicas de leitura) + Redis.
- **Workers desacoplados** por fila (Redis/Celery/Arq) → escalam independentemente do request-path.
- **Connection pooling** (PgBouncer) para proteger o Postgres sob carga.

```
            ┌─ API pod ─┐
LB ────────►├─ API pod ─┤──► PgBouncer ──► Postgres (primary + read replicas)
            └─ API pod ─┘            └──► Redis
                  │
            (jobs assíncronos via fila)
                  ▼
            ┌─ Worker ─┐ (autoscale por tamanho da fila)
            └─ Worker ─┘
```

---

## 3. Performance da Pipeline de IA

| Técnica | Efeito |
|---------|--------|
| **Streaming (SSE)** | Reduz *time-to-first-token* — UX percebida muito melhor. |
| **Temperatura 0 + prompts enxutos** | Menos variância, menos tokens. |
| **Janela de memória truncada (K interações)** | Custo previsível, foco contextual (já no MVP). |
| **Limite de linhas enviadas ao LLM para sumarização** | Evita overflow e tokens desnecessários. |
| **Guard estático antes do LLM** | Rejeita queries inválidas sem gastar tokens. |
| **Modelo certo para a tarefa** | Modelo pequeno/rápido para classificação (chat vs SQL), grande só quando necessário. |
| **Batching de evals** | Avaliação de qualidade fora do caminho crítico. |

---

## 4. Escalabilidade de Dados

- **Ingestão assíncrona** para datasets grandes (o MVP já baixa 283K reviews; produção precisa de jobs em background com progresso).
- **Colunar/Parquet** para datasets analíticos grandes; SQLite só para demo.
- **Paginação por cursor** e `LIMIT` injetado para nunca materializar resultados gigantes.
- **Particionamento/índices** apropriados nas fontes consultadas com frequência.
- Para escala analítica real: caminho para **DuckDB / data warehouse** (BigQuery, Snowflake) via conectores.

---

## 5. Gestão de Custo de IA (FinOps técnico)

```
Estratégia de redução de custo (ordem de impacto):
1. Semantic cache .................... evita a chamada inteira
2. Guard estático .................... evita chamadas em queries inválidas
3. Modelo open-source default (Groq) . custo base baixo
4. Truncamento de contexto ........... menos tokens por chamada
5. Roteamento de modelo .............. tarefa simples → modelo barato
6. Limites de orçamento por tenant ... teto de gasto
```

- **Orçamento por tenant** com *circuit breaker* ao atingir limite.
- **Comparação contínua** custo real vs. baseline premium (herdado do MVP).

---

## 6. Resiliência sob Carga

- **Rate limiting** por tenant/utilizador (token bucket).
- **Timeouts e retries com backoff** em LLM e DB.
- **Circuit breakers** para provedores externos (LLM down → fallback ou degradação graciosa).
- **Backpressure** nas filas de ingestão.
- **Graceful degradation**: se a sumarização falhar, ainda se entrega tabela + SQL.

---

## 7. Testes de Performance

- **Load tests** (k6/Locust) validando os SLOs do doc 05.
- **Profiling** de endpoints críticos e da pipeline de IA.
- **Testes de regressão de latência** no CI (alertar se p95 piora).

---

## 8. Roadmap de Escala (resumo)

| Estágio | Carga | Foco técnico |
|---------|-------|--------------|
| MVP SaaS | dezenas de tenants | Monólito modular + Redis + workers |
| Crescimento | centenas de tenants | Read replicas, semantic cache, HPA agressivo |
| Escala | milhares | Extração de serviços (IA Orchestrator), warehouse, multi-região |

