# 📚 Especificações do Produto — RetailSense AI

> **Documentação de arquitetura, produto e engenharia** para a evolução do projeto de um repositório técnico para um **SaaS de Analytics Conversacional para Varejo & E-commerce**.

Esta pasta `specs/` contém a documentação viva que guia a próxima fase de evolução do projeto. Ela **não contém código** — é o blueprint estratégico e técnico que deve ser lido antes de qualquer implementação.

---

## 🎯 O que é este projeto hoje

Um **Copiloto de Dados (Agentic Text-to-SQL)** construído em Streamlit, que permite a utilizadores de negócio conversarem em linguagem natural com uma base de 283 mil avaliações de produtos da Amazon. O sistema traduz perguntas para SQL, exige aprovação humana antes de executar (Human-in-the-Loop), corrige automaticamente queries com erro (Self-Healing) e audita o custo de tokens (FinOps).

## 🚀 O que ele pode tornar-se

**RetailSense AI** — uma plataforma SaaS multi-tenant onde retalhistas conectam as suas próprias fontes de dados (e-commerce, ERP, reviews, suporte) e obtêm insights de Customer Experience e performance de produto via conversação natural, com governança, segurança e observabilidade de nível enterprise.

---

## 🗂️ Índice da Documentação

| # | Documento | Descrição | Persona-alvo |
|---|-----------|-----------|--------------|
| 01 | [`01-visao-produto.md`](./01-visao-produto.md) | Visão, proposta de valor, público-alvo, posicionamento e modelo de negócio | Produto / Liderança |
| 02 | [`02-especificacao-funcional.md`](./02-especificacao-funcional.md) | Funcionalidades, user stories, fluxos e regras de negócio | Produto / Eng. |
| 03 | [`03-especificacao-tecnica.md`](./03-especificacao-tecnica.md) | Stack, contratos de API, modelo de dados, pipeline de IA | Engenharia |
| 04 | [`04-arquitetura.md`](./04-arquitetura.md) | Arquitetura de referência, componentes, diagramas C4 | Arquitetura |
| 05 | [`05-requisitos-nao-funcionais.md`](./05-requisitos-nao-funcionais.md) | SLAs, SLOs, NFRs e Definition of Done | Eng. / SRE |
| 06 | [`06-observabilidade-rastreabilidade.md`](./06-observabilidade-rastreabilidade.md) | Logs, métricas, traces, LLM observability | SRE / Eng. |
| 07 | [`07-performance-escalabilidade.md`](./07-performance-escalabilidade.md) | Caching, scaling, estratégia de custos de IA | Arquitetura / SRE |
| 08 | [`08-seguranca.md`](./08-seguranca.md) | AuthN/Z, multi-tenancy, LLM security, compliance | Segurança |
| 09 | [`09-frontend-experiencia.md`](./09-frontend-experiencia.md) | Proposta de frontend React, design system e UX | Frontend / Design |
| 10 | [`10-roadmap.md`](./10-roadmap.md) | Evolução faseada do MVP ao SaaS maduro | Produto / Eng. |
| 11 | [`11-riscos-premissas-decisoes.md`](./11-riscos-premissas-decisoes.md) | Riscos, premissas e ADRs (Architecture Decision Records) | Arquitetura |

---

## 🧭 Como ler esta documentação

- **Recrutador / avaliador técnico:** comece pelo `01` (visão) e `04` (arquitetura), depois `09` (frontend) e `11` (decisões).
- **Engenheiro implementando:** `03` → `04` → `05` → `06`/`07`/`08`.
- **Product Manager:** `01` → `02` → `10`.

## 📌 Princípios que guiam este projeto

1. **Trust by design** — IA que age sobre dados precisa de governança, auditabilidade e controlo humano.
2. **Cost-aware AI** — cada token tem custo; observabilidade financeira é uma feature de primeira classe.
3. **Production-grade desde o dia 1** — observabilidade, testes e segurança não são "fase 2".
4. **Developer & Recruiter experience** — o repositório deve ser autoexplicativo e demonstrar maturidade de engenharia.

---

> _Convenção de versionamento desta documentação: cada arquivo declara `status` e `versão` no topo. Mudanças relevantes de arquitetura devem virar um ADR no documento 11._

