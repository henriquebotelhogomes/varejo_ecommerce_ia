---
documento: Requisitos Não Funcionais (NFRs)
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 05 — Requisitos Não Funcionais

Os NFRs definem os **atributos de qualidade** do sistema. Cada um tem alvo mensurável (SLO) sempre que possível.

---

## 1. Performance & Latência

| Métrica | SLO alvo |
|---------|----------|
| Latência API (p95, endpoints não-IA) | < 300 ms |
| Time-to-first-token (resposta IA, streaming) | < 1.5 s |
| Geração de SQL (p95) | < 3 s |
| Execução de query analítica (p95) | < 5 s |
| Carregamento inicial do frontend (LCP) | < 2.5 s |

## 2. Disponibilidade & Confiabilidade

| Métrica | SLO alvo |
|---------|----------|
| Disponibilidade da API | 99.9% mensal |
| Taxa de erro (5xx) | < 0.1% das requisições |
| RPO (perda de dados) | ≤ 5 min |
| RTO (recuperação) | ≤ 30 min |
| Sucesso de Self-Healing | > 70% das queries com erro corrigidas em ≤ 3 tentativas |

## 3. Escalabilidade

- Suportar **crescimento horizontal** sem reescrita (stateless + filas).
- Alvo inicial: **100 tenants / 1.000 utilizadores ativos** sem degradação de SLO.
- Ingestão de datasets até **dezenas de milhões de linhas** via processamento assíncrono.
- Detalhes em [`07-performance-escalabilidade.md`](./07-performance-escalabilidade.md).

## 4. Segurança

- Autenticação forte (OAuth2/OIDC, MFA opcional), RBAC, isolamento multi-tenant.
- Criptografia em trânsito (TLS 1.2+) e em repouso (AES-256).
- Conformidade com OWASP Top 10 e OWASP LLM Top 10.
- Detalhes em [`08-seguranca.md`](./08-seguranca.md).

## 5. Observabilidade

- 100% das requisições com **trace ID** propagado.
- 100% das chamadas a LLM com **trace de tokens/custo/latência/qualidade**.
- Detalhes em [`06-observabilidade-rastreabilidade.md`](./06-observabilidade-rastreabilidade.md).

## 6. Manutenibilidade

| Critério | Alvo |
|----------|------|
| Cobertura de testes (core) | ≥ 80% |
| Lint/format obrigatórios | `ruff` + `black` (BE), ESLint + Prettier (FE) |
| Tipagem | `mypy`/Pydantic (BE), TypeScript estrito (FE) |
| Documentação | OpenAPI sempre atualizado; ADRs para decisões relevantes |
| Acoplamento | Módulos por domínio, dependências unidirecionais |
| Dívida técnica | Registada e priorizada (não invisível) |

## 7. Custo (FinOps)

- Custo de IA por insight **medido e visível** por tenant.
- Modelo open-source (Groq/Llama) como **default de baixo custo**; premium opt-in.
- Alertas automáticos ao ultrapassar % do orçamento.

## 8. Acessibilidade & Usabilidade

- **WCAG 2.1 AA** mínimo.
- Suporte a teclado completo, leitores de tela, dark/light mode.
- i18n (pt-BR, pt-PT, en).

## 9. Portabilidade & Infra

- Tudo **containerizado** e reprodutível via IaC.
- Sem lock-in crítico: provedor de LLM e cloud abstraídos.
- Ambientes idênticos (dev/staging/prod).

## 10. Privacidade & Compliance

- Princípio de **minimização de dados** e isolamento por tenant.
- Trilha de auditoria imutável com retenção configurável.
- Caminho para **LGPD/GDPR** (direito de exclusão, DPA, residência de dados).

---

## ✅ Definition of Done (transversal)

Uma funcionalidade só está "pronta" quando:

- [ ] Código revisado, tipado e com testes (unit + integração relevantes).
- [ ] Instrumentada (logs/métricas/traces) com IDs de correlação.
- [ ] Contrato OpenAPI atualizado e validado.
- [ ] Considerações de segurança e multi-tenancy verificadas.
- [ ] Custo de IA (se aplicável) contabilizado no FinOps.
- [ ] Acessibilidade (FE) verificada.
- [ ] Documentação/ADR atualizada quando há decisão arquitetural.
- [ ] Feature flag e plano de rollback definidos.
