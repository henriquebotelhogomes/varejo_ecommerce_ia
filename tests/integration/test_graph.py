"""Testes de Integração para o Grafo Multi-Agente (LangGraph)."""

from src.agents.graph import (
    build_retailsense_graph,
    route_guard_decision,
    route_intent_decision,
    sql_guard_node,
)
from src.agents.state import AgentState


def test_graph_compilation():
    """Verifica se o grafo de estados compila sem erros estruturais."""
    graph = build_retailsense_graph()
    assert graph is not None
    # Valida que todos os nós registrados existem no grafo compilado
    expected_nodes = {"router", "nl2sql", "sql_guard", "self_healing", "executor", "synthesizer"}
    assert expected_nodes.issubset(set(graph.nodes.keys()))


def test_route_intent_decision():
    """Valida o roteamento condicional de intenções."""
    state_chat: AgentState = {
        "intent": "CASUAL_CHAT",
        "user_query": "Olá",
        "messages": [],
        "sql_query": None,
        "sql_valid": False,
        "sql_validation_error": None,
        "retry_count": 0,
        "sql_result": None,
        "vector_contexts": [],
        "requires_human_approval": False,
        "is_approved": False,
        "final_response": None,
        "next_best_actions": [],
        "token_usage": {},
        "estimated_cost_usd": 0.0,
    }
    assert route_intent_decision(state_chat) == "synthesizer"

    state_sql: AgentState = {**state_chat, "intent": "QUANTITATIVE_SQL"}
    assert route_intent_decision(state_sql) == "nl2sql"


def test_route_guard_decision_valid():
    """Se a query for válida, deve transicionar diretamente para executor."""
    state: AgentState = {
        "sql_valid": True,
        "retry_count": 0,
        "user_query": "",
        "intent": "QUANTITATIVE_SQL",
        "messages": [],
        "sql_query": "SELECT 1",
        "sql_validation_error": None,
        "sql_result": None,
        "vector_contexts": [],
        "requires_human_approval": False,
        "is_approved": False,
        "final_response": None,
        "next_best_actions": [],
        "token_usage": {},
        "estimated_cost_usd": 0.0,
    }
    assert route_guard_decision(state) == "executor"


def test_route_guard_decision_self_healing():
    """Se a query for inválida e retry_count < 3, deve ir para self_healing."""
    state: AgentState = {
        "sql_valid": False,
        "retry_count": 1,
        "user_query": "",
        "intent": "QUANTITATIVE_SQL",
        "messages": [],
        "sql_query": "DROP TABLE avaliacoes",
        "sql_validation_error": "Operação não autorizada",
        "sql_result": None,
        "vector_contexts": [],
        "requires_human_approval": False,
        "is_approved": False,
        "final_response": None,
        "next_best_actions": [],
        "token_usage": {},
        "estimated_cost_usd": 0.0,
    }
    assert route_guard_decision(state) == "self_healing"


def test_route_guard_decision_abort_after_3_retries():
    """Se retry_count >= 3, aborta o ciclo e vai para synthesizer."""
    state: AgentState = {
        "sql_valid": False,
        "retry_count": 3,
        "user_query": "",
        "intent": "QUANTITATIVE_SQL",
        "messages": [],
        "sql_query": "INVALID QUERY",
        "sql_validation_error": "Erro persistente",
        "sql_result": None,
        "vector_contexts": [],
        "requires_human_approval": False,
        "is_approved": False,
        "final_response": None,
        "next_best_actions": [],
        "token_usage": {},
        "estimated_cost_usd": 0.0,
    }
    assert route_guard_decision(state) == "synthesizer"


def test_sql_guard_node_sanitizes_query():
    """Garante que o nó sql_guard sanitiza e injeta LIMIT."""
    state: AgentState = {
        "sql_query": "SELECT title, text FROM avaliacoes",
        "user_query": "",
        "intent": "QUANTITATIVE_SQL",
        "messages": [],
        "sql_valid": False,
        "sql_validation_error": None,
        "retry_count": 0,
        "sql_result": None,
        "vector_contexts": [],
        "requires_human_approval": False,
        "is_approved": False,
        "final_response": None,
        "next_best_actions": [],
        "token_usage": {},
        "estimated_cost_usd": 0.0,
    }
    update = sql_guard_node(state)
    assert update["sql_valid"] is True
    assert "LIMIT 100" in update["sql_query"].upper()
