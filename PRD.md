# 📄 Product Requirements Document (PRD): RetailSense AI v2.0

---

## 1. Visão Geral do Produto

**RetailSense AI v2.0** é uma plataforma analítica conversacional governada de padrão internacional (*Global Scale-up Enterprise Conversational Analytics*), desenhada para transformar equipes de e-commerce e varejo (CX, Merchandising, Produto, Operações) em operadores orientados a dados sem intermediários técnicos e sem filas de espera de BI.

Diferente de soluções legadas e chatbots frágeis, o RetailSense AI combina:
1. **Motor Analítico Colunar de Alta Performance (DuckDB):** Vetorização SIMD local e leitura de formatos abertos (Apache Parquet) sobre 204.382 avaliações reais de compras verificadas da Amazon, garantindo agregações sub-milissegundo com **custo zero de infraestrutura ($0.00/mês)**.
2. **Tri-Tiering Agnóstico de Modelos (Gemini Pro + OpenCode Go + OpenRouter):** Roteamento inteligente entre **Google Gemini Pro** (Gemini 3.8 Flash e embeddings semânticos), **OpenCode Go** (DeepSeek V4.1 Flash com cota de 26k req/5h, Qwen 3.8 Max) e **OpenRouter** (modelos de 550B parâmetros gratuitos para avaliação independente com Ragas).
3. **Camada Semântica de Métricas (Metric Layer):** Blindagem matemática de fórmulas de negócio (CSAT Proxy, NPS Proxy, % 5 Estrelas) como código, eliminando alucinações de métricas.
4. **Streaming Progressivo em Tempo Real (SSE):** Feedback de execução passo-a-passo e streaming de tokens com Time-to-First-Token $\le 500\text{ms}$.
5. **Governança & Human-in-the-Loop (HITL):** Validação sintática determinística via AST (`sqlglot`), blindagem contra comandos destrutivos (somente `SELECT`), checkpoints resilientes e modo estrito de leitura.

---

## 2. Público-Alvo e Personas (ICP)

### Perfil de Cliente Ideal (ICP)
* **Empresas:** E-commerces B2C, marketplaces omnichannel e marcas de varejo com mais de 50.000 avaliações de produtos ou pedidos/mês.
* **Tamanho:** Médio a grande porte (50 a 2.000 colaboradores) com gargalo na equipa central de dados/BI.

### Personas

| Persona | Papel / Função | Dor Principal | Benefício RetailSense AI v2.0 |
| :--- | :--- | :--- | :--- |
| **Marina (CX Lead)** | Head de Customer Experience | Recebe centenas de milhares de reviews e não consegue minerar motivos reais de insatisfação em tempo útil. | Descoberta semântica instantânea de causas-raiz de detratores e tendências temporais em segundos. |
| **Rafael (Product Manager)** | Gerente de Produto E-commerce | Depende de sprints de BI para validar hipóteses de catálogo, devoluções e churn de produtos. | Consultas ad-hoc em linguagem natural com geração de queries DuckDB auditáveis e seguras. |
| **Carla (CTO / Head de Dados)** | Liderança Técnica & Segurança | Teme alucinações de métricas, injeções de SQL acidentais, custos astronômicos de LLMs e perda de governança. | Validação AST estrita, Camada Semântica, aprovação humana pré-execução e telemetria FinOps integrada. |
| **Diego (Analista de BI)** | BI / Analytics Engineer | Afogado em tickets repetitivos de "extração de CSV" e "qual a média de estrelas da categoria X". | Deflecção de pedidos triviais de rotina através de autoatendimento assistido com Next Best Action. |

---

## 3. Problema de Negócio & Dores Mapeadas

1. **Gargalo Operacional em BI:** O tempo médio para responder a uma pergunta analítica varia de 3 a 7 dias úteis via tickets de dados tradicionais.
2. **Subutilização de Dados de Avaliações:** Mais de 80% do feedback dos clientes (títulos e corpos de avaliações) fica dormente por falta de ferramentas de NLP integradas ao dado transacional.
3. **Alucinação de Fórmulas Matemáticas:** LLMs sem camada semântica inventam definições de métricas (ex: calculam NPS somando notas de forma errônea).
4. **Percepção de Lentidão em Interfaces de IA:** Esperas síncronas de 10 a 15 segundos geram abandono do usuário no painel.

---

## 4. Requisitos Funcionais (RF)

### RF01: Roteamento Inteligente & Regex Fast-Path
* Perguntas analíticas canônicas devem ser resolvidas via **Regex Fast-Path** com latência $\le 10\text{ms}$ e custo zero de tokens.
* Perguntas complexas devem ser roteadas pelo `IntentRouter` para o modelo ideal do Tri-Tier (DeepSeek V4.1 Flash, Gemini 3.8 Flash ou Qwen 3.8 Max).

### RF02: Motor Analítico Colunar DuckDB
* O sistema deve utilizar **DuckDB** como motor analítico nativo sobre a base consolidada de 204.382 registros em formato Parquet / DuckDB local.
* Agregações de séries temporais, notas médias e rankings devem executar em $\le 20\text{ms}$ em memória.

### RF03: Camada Semântica Centralizada (Metric Layer)
* As fórmulas analíticas de negócio (CSAT Proxy, Taxa de Promotores, Taxa de Detratores, Índice de Votos Úteis) devem ser codificadas em contratos canônicos consumidos pelo gerador SQL, impedindo fórmulas divergentes.

### RF04: Validação de Segurança & AST Guardrails (`sqlglot`)
* Validação sintática obrigatória impedindo qualquer comando de mutação (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`). Somente declarações do tipo `SELECT` são aceitas.
* Injeção forçada de cláusula `LIMIT 100` em consultas tabulares abertas.
* Conexão com o banco estritamente em modo de leitura (`read-only`).

### RF05: Streaming Server-Sent Events (SSE)
* O endpoint de chat deve suportar streaming em tempo real emitindo eventos de ciclo de vida (`intent_detected`, `sql_generated`, `sql_validated`, `db_executed`) e streaming token-a-token da síntese executiva.

### RF06: Síntese Executiva & Next Best Action Interativo
* Síntese direta com números-chave e destaques executivos.
* Geração de exatamente 3 perguntas acionáveis ("Next Best Action").
* Ao clicar na sugestão, o texto deve ser inserido no campo de entrada da UI com foco imediato, sem auto-envio acidental.

### RF07: RAG Híbrido Qualitativo sobre Reviews
* Cruzamento das métricas numéricas com busca semântica no corpo dos reviews utilizando embeddings `text-embedding-004` da Google e re-ranking contextual.

### RF08: Observabilidade FinOps & Telemetria Prometheus
* Registro detalhado de tokens de entrada e saída, tempo de execução por nó do grafo e custo estimado em USD.
* Exposição do endpoint oficial `/metrics` no formato Prometheus/OpenMetrics.

---

## 5. Requisitos Não-Funcionais (RNF)

* **RNF01 — Performance & SLAs:**
  - Fast-Path de Roteamento: $\le 10\text{ms}$ (0.00s verificado).
  - Time to First Token (TTFT) via Streaming SSE: $\le 500\text{ms}$.
  - Agregação Analítica DuckDB: $\le 25\text{ms}$.
* **RNF02 — Arquitetura Fullstack Desacoplada:**
  - Backend: **FastAPI 0.111+** com tipagem estrita Pydantic v2 e documentação **Scalar** em `/docs`.
  - Frontend: **React 19 + TypeScript + Vite + Tailwind CSS + Recharts**. 100% tema claro corporativo (padrão Stripe/Linear). **Proibição absoluta de Streamlit**.
* **RNF03 — Avaliação Contínua no CI/CD:**
  - Avaliação automatizada com **Ragas** utilizando modelos independentes do OpenRouter (NVIDIA Nemotron 3 Ultra 550B / Gemma 4) como Juiz imparcial:
    - *Faithfulness* $\ge 0.85$
    - *Answer Relevancy* $\ge 0.80$
* **RNF04 — FinOps & Custo Zero de Infraestrutura:**
  - Banco colunar embutido (DuckDB) com custo de infraestrutura de **\$0.00/mês**.
  - Aproveitamento integral dos créditos do **Azure for Students** para deploy de containers e das assinaturas ativas (**Google Gemini Pro** e **OpenCode Go**).

---

## 6. Métricas de Sucesso (KPIs & SLAs)

1. **Taxa de Sucesso de Queries (Pass@1):** $\ge 90\%$.
2. **Taxa de Sucesso com Self-Healing (Pass@3):** $\ge 98\%$.
3. **Assertividade de Negócio (Ragas Faithfulness):** $\ge 0.85$.
4. **Time to First Token (TTFT):** $\le 500\text{ms}$.
5. **Custo Médio por Sessão Analítica:** $\le \$0.002$.
6. **Zero Incidentes de Segurança:** Zero comandos de alteração executados.
