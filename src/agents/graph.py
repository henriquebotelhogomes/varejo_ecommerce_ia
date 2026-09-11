"""Compilação do Grafo de Estados (StateGraph) do LangGraph: RetailSense AI.

Orquestra a execução multi-agente, transições condicionais, guardrails AST,
ciclo autônomo de Self-Healing e persistência com checkpointing.
"""

from __future__ import annotations

from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.router import intent_router_node
from src.agents.sql_agent import nl2sql_node, self_healing_node
from src.agents.sql_guard import validate_and_sanitize_sql
from src.agents.state import AgentState
from src.agents.synthesizer import synthesizer_node
from src.core.database import executar_query_read_only
from src.core.duckdb_engine import executar_query_duckdb

# =====================================================================
# 1. NÓS INTERMEDIÁRIOS DE SEGURANÇA E EXECUÇÃO
# =====================================================================


def sql_guard_node(state: AgentState) -> dict[str, Any]:
    """Nó que submete a query gerada ao validador determinístico de AST."""
    raw_sql = state.get("sql_query") or ""
    res = validate_and_sanitize_sql(raw_sql)

    if res.is_valid and res.sanitized_sql:
        return {"sql_query": res.sanitized_sql, "sql_valid": True, "sql_validation_error": None}
    return {
        "sql_valid": False,
        "sql_validation_error": res.error_message or "Violação de segurança ou sintaxe no SQL.",
    }


def database_executor_node(state: AgentState) -> dict[str, Any]:
    """Nó executor que roda a query validada primariamente no DuckDB (com fallback SQLite)."""
    sql_to_run = state.get("sql_query")
    if not sql_to_run:
        return {
            "sql_result": None,
            "sql_valid": False,
            "sql_validation_error": "Nenhuma query SQL disponível para execução.",
        }

    # 1. Tentativa primária no motor colunar DuckDB (sub-20ms)
    try:
        duck_records = executar_query_duckdb(sql_to_run)
        return {"sql_result": duck_records, "sql_valid": True, "sql_validation_error": None}
    except Exception:
        pass

    # 2. Fallback de alta disponibilidade no SQLite 3 indexado
    try:
        df = executar_query_read_only(sql_to_run)
        records = df.to_dict(orient="records")
        return {"sql_result": records, "sql_valid": True, "sql_validation_error": None}
    except Exception as exec_err:
        return {
            "sql_result": None,
            "sql_valid": False,
            "sql_validation_error": f"Erro de execução no banco de dados: {exec_err}",
        }


# =====================================================================
# 2. ROTEADORES CONDICIONAIS DE TRANSIÇÃO (EDGES)
# =====================================================================


def route_intent_decision(state: AgentState) -> Literal["synthesizer", "nl2sql"]:
    """Decide se segue para o fluxo SQL ou diretamente para a síntese."""
    if state.get("intent") == "CASUAL_CHAT":
        return "synthesizer"
    return "nl2sql"


def route_guard_decision(state: AgentState) -> Literal["executor", "self_healing", "synthesizer"]:
    """Avalia o resultado da validação AST do SQL."""
    if state.get("sql_valid"):
        return "executor"

    retry_count = state.get("retry_count", 0)
    if retry_count < 3:
        return "self_healing"
    return "synthesizer"


def route_executor_decision(state: AgentState) -> Literal["synthesizer", "self_healing"]:
    """Avalia o resultado da execução física da query no banco de dados."""
    if state.get("sql_result") is not None and not state.get("sql_validation_error"):
        return "synthesizer"

    retry_count = state.get("retry_count", 0)
    if retry_count < 3:
        return "self_healing"
    return "synthesizer"


# =====================================================================
# 3. MONTAGEM E COMPILAÇÃO DO GRAFO (StateGraph)
# =====================================================================


def build_retailsense_graph() -> Any:
    """Constrói e compila o grafo do RetailSense AI com persistência em memória."""
    workflow = StateGraph(AgentState)

    # Registro de Nós
    workflow.add_node("router", intent_router_node)
    workflow.add_node("nl2sql", nl2sql_node)
    workflow.add_node("sql_guard", sql_guard_node)
    workflow.add_node("self_healing", self_healing_node)
    workflow.add_node("executor", database_executor_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Transições Principais
    workflow.add_edge(START, "router")
    workflow.add_conditional_edges("router", route_intent_decision)
    workflow.add_edge("nl2sql", "sql_guard")
    workflow.add_conditional_edges("sql_guard", route_guard_decision)
    workflow.add_edge("self_healing", "sql_guard")
    workflow.add_conditional_edges("executor", route_executor_decision)
    workflow.add_edge("synthesizer", END)

    # Persistência via Checkpointer
    checkpointer = MemorySaver()
    compiled_app = workflow.compile(checkpointer=checkpointer)
    return compiled_app


# Instância singleton compilada pronta para uso
app_graph = build_retailsense_graph()
