"""Nós de Tradução NL2SQL e Auto-Correção (Self-Healing).

Traduz a intenção do usuário em queries SQLite válidas e corrige erros sintáticos
ou de identificadores de forma autônoma (até 3 tentativas).
"""

from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.semantic_layer import get_semantic_layer_prompt_context
from src.agents.state import AgentState, SQLGenerationOutput
from src.core.database import obter_schema_avaliacoes
from src.core.llm_provider import get_chat_model

SYSTEM_NL2SQL_PROMPT = """Você é um Engenheiro de Analytics especialista em Varejo/E-commerce e dialeto SQL DuckDB/SQLite.
Sua missão é traduzir com máxima precisão a dúvida do usuário em uma query SQL analítica válida.

{schema}

{metric_context}

DIRETRIZES TÉCNICAS E DE NEGÓCIO:
1. Gere RIGOROSAMENTE consultas iniciadas pelo comando 'SELECT'.
2. NUNCA gere estruturas JSON, dicionários ({{...}}), objetos STRUCT ou comandos DDL/DML.
3. Para buscas textuais, use LOWER(coluna) LIKE '%termo%' para garantir insensibilidade a maiúsculas/minúsculas.
4. Para agrupamentos ou rankings, inclua cláusula ORDER BY descendente ou ascendente coerente com a pergunta.
5. Limite o retorno com LIMIT 100 caso não seja uma agregação pura de linha única."""


def nl2sql_node(state: AgentState) -> dict[str, Any]:
    """Nó do LangGraph responsável por gerar a query SQL a partir da linguagem natural."""
    user_query = state.get("user_query") or ""
    schema = obter_schema_avaliacoes()
    metric_context = get_semantic_layer_prompt_context()

    llm = get_chat_model(tier="fast", temperature=0.0)

    formatted_sys = SYSTEM_NL2SQL_PROMPT.format(schema=schema, metric_context=metric_context)
    prompt_messages = [
        SystemMessage(content=formatted_sys),
        HumanMessage(content=f"Pergunta do usuário: {user_query}"),
    ]

    try:
        structured_llm = llm.with_structured_output(SQLGenerationOutput)
        res: SQLGenerationOutput = structured_llm.invoke(prompt_messages)
        generated_sql = res.sql_query
    except Exception:
        # Fallback de parsing resiliente
        raw_res = llm.invoke(prompt_messages)
        content = raw_res.content if hasattr(raw_res, "content") else str(raw_res)
        # Extrai SQL limpo de eventual markdown
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
        generated_sql = match.group(1).strip() if match else content.strip()

    # Tratamento caso a saída venha encapsulada em JSON ou STRUCT
    if generated_sql.startswith("{") and generated_sql.endswith("}"):
        try:
            import json

            parsed = json.loads(generated_sql)
            if isinstance(parsed, dict) and "sql_query" in parsed:
                generated_sql = parsed["sql_query"].strip()
        except Exception:
            pass

    return {"sql_query": generated_sql, "sql_valid": False, "sql_validation_error": None}


def self_healing_node(state: AgentState) -> dict[str, Any]:
    """Nó de auto-correção autônoma que analisa mensagens de erro e corrige o SQL."""
    current_retry = state.get("retry_count", 0) + 1
    failed_sql = state.get("sql_query", "")
    error_msg = state.get("sql_validation_error", "Erro sintático ou de execução desconhecido")
    schema = obter_schema_avaliacoes()

    llm = get_chat_model(tier="reasoning", temperature=0.0)

    fix_prompt = f"""A seguinte query SQL falhou durante a validação ou execução:
Query Inválida: {failed_sql}
Mensagem de Erro: {error_msg}

{schema}

Tarefa: Corrija a query para o dialeto SQLite 3, ajustando os identificadores ou operadores necessários.
Retorne rigorosamente a estrutura SQL válida."""

    prompt_messages = [
        SystemMessage(content="Você é um especialista em reparo e debug de queries SQL SQLite."),
        HumanMessage(content=fix_prompt),
    ]

    try:
        structured_llm = llm.with_structured_output(SQLGenerationOutput)
        res: SQLGenerationOutput = structured_llm.invoke(prompt_messages)
        fixed_sql = res.sql_query
    except Exception:
        raw_res = llm.invoke(prompt_messages)
        content = raw_res.content if hasattr(raw_res, "content") else str(raw_res)
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
        fixed_sql = match.group(1).strip() if match else content.strip()

    return {"sql_query": fixed_sql, "retry_count": current_retry, "sql_validation_error": None}
