---
documento: Estratégia de Segurança
status: Proposta
versão: 1.0
atualizado: 2026-06-22
---

# 08 — Estratégia de Segurança

> O projeto já nasce com uma mentalidade de segurança rara em demos de IA: **Human-in-the-Loop** e **bloqueio de operações destrutivas**. Esta estratégia formaliza e expande isso para padrões enterprise, cobrindo tanto segurança de aplicação (OWASP Top 10) quanto **segurança específica de LLM (OWASP LLM Top 10)**.

---

## 1. Modelo de Ameaças (resumo)

| Ativo | Ameaça | Mitigação principal |
|-------|--------|---------------------|
| Dados do tenant | Vazamento entre tenants | Isolamento + RLS + conexões dedicadas |
| Base de dados | Operação destrutiva via IA | Read-only + guard estático + HITL |
| LLM | Prompt injection | Sanitização + guard de saída + allow-list |
| Credenciais | Roubo de segredos | Secret Manager + rotação |
| API | Abuso / DoS | Rate limit + WAF + autenticação |
| Custo | "Denial of Wallet" (estourar gasto de IA) | Orçamento por tenant + circuit breaker |

---

## 2. Autenticação & Autorização

- **AuthN:** OAuth2/OIDC, suporte a SSO (SAML/OIDC) e MFA opcional. Tokens JWT de curta duração + refresh.
- **AuthZ:** **RBAC** com papéis (`Owner`, `Admin`, `Analyst`, `Viewer`). Permissões verificadas no gateway **e** no serviço (defense in depth).
- **Princípio do menor privilégio** em todas as camadas.

---

## 3. Multi-Tenancy & Isolamento

- **Row-Level Security (RLS)** no Postgres por `org_id` — isolamento aplicado pelo banco, não só pela aplicação.
- **Dados do tenant isolados**: conexões/credenciais separadas por organização; nunca compartilhadas.
- **Validação de `org_id`** em toda requisição (impossível "adivinhar" recursos de outro tenant).
- Opção Enterprise: **isolamento dedicado** (DB/VPC próprio).

---

## 4. Segurança de Dados

- **Em trânsito:** TLS 1.2+ obrigatório.
- **Em repouso:** AES-256 (DB, backups, object storage).
- **Segredos:** Vault/Secret Manager; **nunca** em código ou logs. (O MVP já usa `.env` não-versionado — bom ponto de partida.)
- **Minimização & masking:** PII mascarada em logs/traces; retenção mínima necessária.
- **Backups criptografados** e testes de restore.

---

## 5. Segurança Específica de LLM (OWASP LLM Top 10)

| Risco | Mitigação no RetailSense |
|-------|--------------------------|
| **LLM01 — Prompt Injection** | Separação de instruções/sistema vs. input; allow-list de tabelas; guard de saída valida que o output é só SQL. |
| **LLM02 — Insecure Output Handling** | **Nunca** executar saída do LLM diretamente: parser estático (`sqlglot`) + HITL antes de tocar o DB. |
| **LLM03 — Data Poisoning** | Datasets de origem controlados; conectores autenticados. |
| **LLM06 — Sensitive Info Disclosure** | RLS garante que o SQL só acede dados do tenant; sumarização não vaza schema sensível. |
| **LLM08 — Excessive Agency** | Agente é **read-only**; nenhuma ferramenta de escrita/efeito colateral exposta. |
| **LLM10 — Unbounded Consumption** | Limites de tokens, orçamento por tenant, rate limit, timeouts. |

### A defesa em camadas para Text-to-SQL (joia da coroa)
```
Input do utilizador
  └─► (1) Prompt com instruções rígidas (só SELECT)
        └─► (2) LLM gera SQL candidato
              └─► (3) GUARD ESTÁTICO (parser): rejeita DDL/DML, valida tabelas/colunas (allow-list)
                    └─► (4) HUMAN-IN-THE-LOOP: aprovação humana/política
                          └─► (5) Execução com utilizador de DB READ-ONLY + timeout + LIMIT
```
> Cinco camadas independentes. Mesmo que uma falhe, as outras contêm o risco. **Isto é o que demonstra maturidade de segurança a um recrutador.**

---

## 6. Segurança de Aplicação (OWASP Top 10)

- **Validação de input** (Pydantic) em todas as fronteiras.
- **Output encoding** e proteção XSS no frontend (React escapa por padrão; sanitização extra para markdown gerado por IA).
- **CSRF protection** onde aplicável; SameSite cookies.
- **Headers de segurança**: CSP, HSTS, X-Content-Type-Options, etc.
- **Rate limiting & WAF** contra abuso/DoS.
- **Dependency scanning** (SCA) e **SAST** no CI; alertas de CVE.
- **Idempotency-Key** em mutações sensíveis.

---

## 7. Auditoria & Compliance

- **AuditEvent append-only** para ações sensíveis (login, aprovação/rejeição de query, export, mudança de permissão).
- Trilha **reconstrói a cadeia completa** de cada insight (ver doc 06 §6).
- Caminho para **LGPD/GDPR**: direito à exclusão, DPA, residência de dados, consentimento.
- **SOC 2** como meta de maturidade (controlo de acesso, logging, gestão de mudança).

---

## 8. Gestão de Segredos & Supply Chain

- Rotação automática de chaves de API (LLM, DB).
- **SBOM** (Software Bill of Materials) e verificação de integridade de dependências.
- Imagens de container *scanned* e assinadas; base mínima (distroless).

---

## 9. Resposta a Incidentes

- **Runbooks** para vazamento, abuso de custo e indisponibilidade.
- **Alertas** de anomalia (picos de custo, padrões de acesso suspeitos).
- Processo de **disclosure responsável** e *post-mortems* sem culpa.

---

## 10. Evolução a partir do MVP

| Hoje (MVP) | Alvo |
|------------|------|
| HITL: aprovação manual de SQL | HITL + políticas automáticas por role/risco |
| Bloqueio de UPDATE/DELETE/DROP via prompt | Guard estático por parser (não confia só no prompt) |
| `.env` não versionado | Secret Manager + rotação |
| Sem auth (app local) | OAuth2/OIDC + RBAC + RLS multi-tenant |

> O MVP **já tem o instinto certo de segurança**. Esta estratégia o transforma em garantia verificável.
