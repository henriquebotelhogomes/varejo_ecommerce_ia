---
documento: Proposta de Frontend e Experiência do Usuário
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 09 — Frontend & Experiência do Usuário

> O frontend é a **primeira impressão** que um recrutador tem do projeto. Um backend impecável com uma UI medíocre subvende o trabalho. A meta aqui é uma interface que pareça saída de uma startup de IA de ponta (Linear, Vercel, Perplexity, Notion AI).

---

## 1. Princípios de Design

1. **Conversa em primeiro lugar** — a interação central é o diálogo; tudo orbita à volta dele.
2. **Confiança visível** — a governança (HITL, custo, raciocínio) é mostrada com elegância, não escondida.
3. **Clareza > densidade** — espaço em branco generoso, hierarquia tipográfica forte.
4. **Resposta percebida rápida** — streaming, skeletons e *optimistic UI*.
5. **Acessível por padrão** — WCAG 2.1 AA, teclado, dark/light.
6. **Delight nos detalhes** — micro-interações, transições suaves, estados vazios bem pensados.

---

## 2. Stack de Frontend (proposta)

| Categoria | Escolha | Justificativa |
|-----------|---------|---------------|
| Framework | **React 18 + TypeScript** | Padrão de mercado, ecossistema, tipagem. |
| Build/Dev | **Vite** | DX excelente, HMR instantâneo. |
| Roteamento | **React Router** (ou TanStack Router) | SPA robusta. |
| Estilo | **Tailwind CSS** | Velocidade + consistência sem CSS solto. |
| Componentes | **shadcn/ui + Radix UI** | Acessíveis, headless, customizáveis, lindos. |
| Data fetching | **TanStack Query** | Cache, retries, sync de servidor. |
| Estado cliente | **Zustand** | Simples, sem boilerplate. |
| Streaming IA | **SSE / fetch streams** | Respostas token-by-token. |
| Gráficos | **Recharts / Visx** | Visualizações declarativas e bonitas. |
| Tabelas | **TanStack Table** | Tabelas performáticas e ricas. |
| Animação | **Framer Motion** | Micro-interações fluidas. |
| Formulários | **React Hook Form + Zod** | Validação tipada ponta a ponta. |
| Testes | **Vitest + Testing Library + Playwright** | Unit + E2E. |
| Qualidade | **ESLint + Prettier + TS estrito** | Consistência. |
| Ícones | **Lucide** | Conjunto coeso e moderno. |

---

## 3. Design System

- **Design tokens** (cores, espaçamento, tipografia, raios, sombras) centralizados e temáveis.
- **Modo claro e escuro** com paleta acessível (contraste AA+).
- **Tipografia:** fonte geométrica/legível (ex.: Inter / Geist) + mono para SQL/código.
- **Componentes-base:** Button, Input, Card, Dialog, Tooltip, Toast, Tabs, Badge, Skeleton — via shadcn/ui.
- **Storybook** para documentar e testar componentes isoladamente (sinal forte de maturidade FE).

---

## 4. Arquitetura de Informação (telas principais)

```
/                    → Landing / marketing (conversão)
/login               → Autenticação / SSO
/app
 ├── /chat           → Workspace conversacional (núcleo)
 ├── /dashboard      → KPIs do tenant (cards + gráficos)
 ├── /sources        → Conectar/gerir fontes de dados
 ├── /insights       → CX: temas, sentimento de reviews
 ├── /finops         → Custos de IA, orçamento, economia
 ├── /audit          → Trilha de auditoria (admin)
 └── /settings       → Org, membros, RBAC, preferências
```

---

## 5. A Tela-Núcleo: Workspace Conversacional

```
┌───────────────────────────────────────────────────────────────────┐
│  RetailSense AI            [⌘K]  Fonte: Amazon Reviews ▾   🌙  👤   │
├──────────────┬────────────────────────────────────────────────────┤
│              │                                                      │
│  Conversas   │   💬 "Quais os produtos com pior avaliação?"        │
│  ───────     │                                                      │
│  • Hoje      │   🤖 Gerei esta consulta para responder:            │
│    - Notas   │   ┌──────────────────────────────────────────────┐  │
│    - Churn   │   │ SELECT parent_asin, AVG(rating) ...           │  │
│  • Ontem     │   │ FROM avaliacoes GROUP BY ... ORDER BY ...     │  │
│              │   └──────────────────────────────────────────────┘  │
│              │   🛡️ Revisão necessária   [✅ Aprovar] [✏️ Editar]   │
│  + Nova      │                            [❌ Recusar]              │
│              │                                                      │
│              │   ⏱️ 1.2s  ·  🔢 320 tokens  ·  💲 $0.0004           │
│              │                                                      │
├──────────────┤   ─────────────────────────────────────────────     │
│  Atalhos     │   [ Pergunte aos seus dados...            ↑ ]        │
└──────────────┴────────────────────────────────────────────────────┘
```

### Elementos-chave de UX
- **Streaming token-by-token** com cursor animado → percepção de velocidade.
- **Card de query proposta** com SQL realçado (syntax highlighting), botões **Aprovar / Editar / Recusar** (HITL elegante).
- **Editor inline de SQL** para o utilizador ajustar antes de aprovar (poder + confiança).
- **Badges de telemetria** discretos por mensagem (latência · tokens · custo) — FinOps visível sem poluir.
- **Self-Healing animado**: quando a IA corrige uma query, mostra-se um stepper ("erro detectado → corrigindo → sucesso").
- **Next Best Action** como *chips* clicáveis abaixo da resposta.
- **Resultados ricos**: alternância Tabela ⇄ Gráfico, export CSV, link compartilhável.
- **Comando ⌘K** (command palette) para navegação e perguntas rápidas.

---

## 6. Visualização de Dados

- **Auto-viz inteligente**: o frontend sugere o gráfico adequado conforme o shape do resultado (categórico → barras, série temporal → linha, distribuição → histograma).
- **Tabelas** com ordenação, filtro e paginação (TanStack Table).
- **Dashboards** com cards de KPI animados (contadores) e gráficos responsivos.
- **Skeleton loaders** durante carregamento → zero "tela em branco".

---

## 7. Estados, Erros e Vazios

- **Empty states** com orientação (ex.: "Conecte uma fonte ou experimente o dataset de exemplo").
- **Erros graciosos**: se a IA falha, oferece-se a tabela/SQL e um caminho de recuperação.
- **Loading com propósito**: skeletons específicos por componente, não spinners genéricos.
- **Optimistic UI** em ações como envio de mensagem.

---

## 8. Performance do Frontend

| Técnica | Efeito |
|---------|--------|
| Code splitting / lazy routes | Bundle inicial pequeno |
| Streaming SSE | TTFB percebido baixo |
| TanStack Query cache | Menos refetch, navegação instantânea |
| Memoização & virtualização de listas | Tabelas/conversas longas fluidas |
| Assets via CDN + imagens otimizadas | LCP < 2.5s |
| Web Vitals monitorados | Qualidade mensurável (RUM) |

---

## 9. Acessibilidade & Internacionalização

- **WCAG 2.1 AA**: navegação por teclado, foco visível, ARIA, contraste.
- **Leitores de tela** testados nos fluxos críticos.
- **i18n** (pt-BR, pt-PT, en) com `react-i18next`; conteúdo da IA respeita o locale.
- **Reduced motion** respeitado.

---

## 10. Por que este frontend impressiona

- Demonstra domínio do **ecossistema React moderno** (TS, Tailwind, shadcn, TanStack, Framer Motion).
- Mostra **sensibilidade de produto e design**, não só de código.
- Transforma features de governança (HITL, FinOps, self-heal) em **momentos de UX memoráveis** — exatamente o tipo de detalhe que diferencia um portfólio sénior.
