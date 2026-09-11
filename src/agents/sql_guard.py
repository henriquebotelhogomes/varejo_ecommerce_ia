"""Módulo de Validação e Sanitização Determinística de SQL (AST Guardrail).

Utiliza o parser AST do sqlglot para avaliar sintaxe, segurança e limites de queries
geradas por LLMs antes da execução no banco de dados.
"""

from __future__ import annotations

import ast
import json
import re

import sqlglot
from pydantic import BaseModel, Field
from sqlglot import exp


class SQLValidationResult(BaseModel):
    """Resultado da análise determinística de segurança do SQL."""

    is_valid: bool = Field(
        description="Indica se a query foi considerada segura e compatível com as regras."
    )
    sanitized_sql: str | None = Field(
        default=None,
        description="Query SQL sanitizada, formatada e com injeção de limites de segurança.",
    )
    is_aggregation: bool = Field(
        default=False,
        description="Indica se a query realiza agregação (COUNT, AVG, SUM, etc.).",
    )
    tables_used: list[str] = Field(
        default_factory=list, description="Lista de tabelas identificadas na consulta."
    )
    error_message: str | None = Field(
        default=None, description="Mensagem de erro detalhada em caso de rejeição da query."
    )


# Lista restrita de expressões expressamente proibidas
FORBIDDEN_EXPRESSIONS: tuple[type[exp.Expression], ...] = (
    exp.Drop,
    exp.Delete,
    exp.Update,
    exp.Insert,
    exp.Alter,
    exp.TruncateTable,
    exp.Create,
)

# Funções analíticas e agregadas autorizadas
AGGREGATE_FUNCTIONS: tuple[type[exp.Expression], ...] = (
    exp.Count,
    exp.Avg,
    exp.Sum,
    exp.Min,
    exp.Max,
)

# Tabela padrão autorizada no contexto do dataset
DEFAULT_ALLOWED_TABLES: set[str] = {"avaliacoes"}


def _clean_markdown(query: str) -> str:
    """Remove eventuais blocos de código markdown residuais ou JSON/dict envolto."""
    cleaned = query.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:sql|json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Se a string recebida for um JSON ou dicionário Python contendo 'sql_query'
    if cleaned.startswith("{") and cleaned.endswith("}"):
        try:
            data = json.loads(cleaned)
            if (
                isinstance(data, dict)
                and "sql_query" in data
                and isinstance(data["sql_query"], str)
            ):
                return data["sql_query"].strip()
        except Exception:
            pass

        try:
            data_py = ast.literal_eval(cleaned)
            if (
                isinstance(data_py, dict)
                and "sql_query" in data_py
                and isinstance(data_py["sql_query"], str)
            ):
                return data_py["sql_query"].strip()
        except Exception:
            pass

        # Regex fallback para extração de campo sql_query
        match = re.search(
            r"['\"]sql_query['\"]\s*:\s*['\"](.*?)['\"](?:\s*,\s*['\"]|\s*})",
            cleaned,
            re.DOTALL,
        )
        if match:
            return match.group(1).strip()

    return cleaned.strip()


def validate_and_sanitize_sql(
    sql_query: str,
    dialect: str = "duckdb",
    allowed_tables: set[str] | None = None,
    max_limit: int = 100,
) -> SQLValidationResult:
    """Analisa a AST da query SQL e retorna se ela é segura, além de aplicar sanitização.

    Args:
        sql_query: Query SQL bruta gerada pelo agente ou usuário.
        dialect: Dialeto SQL alvo (padrão: 'duckdb').
        allowed_tables: Whitelist de tabelas permitidas (se None, usa DEFAULT_ALLOWED_TABLES).
        max_limit: Limite máximo de registros injetado quando ausente em selects abertos.

    Returns:
        SQLValidationResult com status, query sanitizada e diagnósticos.
    """
    if not sql_query or not sql_query.strip():
        return SQLValidationResult(
            is_valid=False, error_message="A query SQL fornecida está vazia."
        )

    clean_sql = _clean_markdown(sql_query)
    tables_whitelist = {t.lower() for t in (allowed_tables or DEFAULT_ALLOWED_TABLES)}

    # 1. Parsing da AST
    try:
        parsed_statements = sqlglot.parse(clean_sql, read=dialect)
    except Exception as parse_err:
        return SQLValidationResult(
            is_valid=False, error_message=f"Erro sintático no parsing do SQL: {parse_err}"
        )

    if not parsed_statements or parsed_statements[0] is None:
        return SQLValidationResult(
            is_valid=False, error_message="Nenhum comando SQL válido foi interpretado."
        )

    # 2. Bloqueio de múltiplos statements (Stacked Queries)
    if len(parsed_statements) > 1:
        return SQLValidationResult(
            is_valid=False,
            error_message="Múltiplas instruções SQL detectadas. Apenas uma consulta por requisição é permitida.",
        )

    root_ast = parsed_statements[0]

    # Se porventura o parser DuckDB interpretou como exp.Struct (dicionário), desempacota o campo sql_query
    if isinstance(root_ast, exp.Struct):
        for prop in root_ast.expressions:
            if (
                isinstance(prop, exp.PropertyEQ)
                and isinstance(prop.this, exp.Identifier)
                and prop.this.this.lower() == "sql_query"
                and isinstance(prop.expression, exp.Literal)
            ):
                inner_sql = prop.expression.this
                try:
                    inner_stmts = sqlglot.parse(inner_sql, read=dialect)
                    if inner_stmts and inner_stmts[0] is not None:
                        root_ast = inner_stmts[0]
                        clean_sql = inner_sql
                        break
                except Exception:
                    pass

    # 3. Validar se o comando raiz é estritamente uma seleção
    if not isinstance(root_ast, exp.Select | exp.Union):
        detected = "STRUCT" if isinstance(root_ast, exp.Struct) else root_ast.key.upper()
        return SQLValidationResult(
            is_valid=False,
            error_message=f"Operação não permitida: Apenas comandos SELECT são autorizados. Detectado: {detected}.",
        )

    # 4. Varredura profunda por nós proibidos
    for forbidden_cls in FORBIDDEN_EXPRESSIONS:
        found_forbidden = list(root_ast.find_all(forbidden_cls))
        if found_forbidden:
            op_name = forbidden_cls.__name__.upper().replace("EXP", "")
            return SQLValidationResult(
                is_valid=False,
                error_message=f"Violação de segurança: Instrução perigosa detectada ({op_name}).",
            )

    # 5. Whitelist de Tabelas
    tables_found: set[str] = set()
    for table_expr in root_ast.find_all(exp.Table):
        t_name = table_expr.name.lower()
        if t_name:
            tables_found.add(t_name)
            if tables_whitelist and t_name not in tables_whitelist:
                return SQLValidationResult(
                    is_valid=False,
                    error_message=f"Acesso negado: A tabela '{t_name}' não pertence à whitelist de dados autorizados.",
                )

    # 6. Detecção de Funções Agregadoras
    is_aggregation = False
    for agg_cls in AGGREGATE_FUNCTIONS:
        if root_ast.find(agg_cls) is not None:
            is_aggregation = True
            break

    # 7. Garantia e Injeção de LIMIT de Segurança
    limit_node = root_ast.find(exp.Limit)
    if limit_node is None:
        # Se for uma consulta não puramente agregada (ou mesmo se selecionar linhas), injeta o LIMIT
        if not (is_aggregation and not root_ast.find(exp.Group)):
            root_ast = root_ast.limit(max_limit)
    else:
        # Se já tiver limit, garante que não ultrapasse o max_limit
        try:
            current_limit = int(limit_node.expression.this)
            if current_limit > max_limit:
                root_ast = root_ast.limit(max_limit)
        except (ValueError, AttributeError):
            # Se a expressão do limit não for inteiro simples, força max_limit
            root_ast = root_ast.limit(max_limit)

    # 8. Geração da query sanitizada final
    sanitized = root_ast.sql(dialect=dialect)

    return SQLValidationResult(
        is_valid=True,
        sanitized_sql=sanitized,
        is_aggregation=is_aggregation,
        tables_used=sorted(tables_found),
        error_message=None,
    )
