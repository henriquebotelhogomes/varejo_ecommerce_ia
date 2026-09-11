"""Endpoint Conversacional e Analítico com LangGraph (Chat & Text-to-SQL)."""

import asyncio
import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from src.agents.graph import app_graph
from src.agents.state import AgentState
from src.api.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Copilot & Analytics"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Interagir com o Copiloto de Dados",
    description="Envia uma pergunta em linguagem natural para o motor multi-agente LangGraph com persistência de thread.",
)
async def process_chat(payload: ChatRequest) -> ChatResponse:
    """Executa o ciclo completo de orquestração multi-agente sobre a base de dados."""
    thread_id = payload.thread_id or f"thread_{uuid.uuid4().hex[:12]}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state: AgentState = {
        "user_query": payload.query,
        "intent": "QUANTITATIVE_SQL",
        "messages": [HumanMessage(content=payload.query)],
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

    try:
        final_state = await app_graph.ainvoke(initial_state, config=config)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erro durante a orquestração multi-agente: {exc}"
        ) from exc

    return ChatResponse(
        thread_id=thread_id,
        intent=final_state.get("intent", "QUANTITATIVE_SQL"),
        sql_query=final_state.get("sql_query"),
        sql_valid=final_state.get("sql_valid", True),
        data=final_state.get("sql_result"),
        final_response=final_state.get("final_response") or "Consulta processada com sucesso.",
        next_best_actions=final_state.get("next_best_actions") or [],
    )


@router.post(
    "/stream",
    summary="Streaming de Ciclo de Vida e Resposta do Agente (SSE)",
    description="Emite eventos progressivos Server-Sent Events informando os passos de execução do agente e a resposta analítica.",
)
async def process_chat_stream(payload: ChatRequest) -> StreamingResponse:
    """Streaming progressivo de eventos e tokens para renderização em tempo real."""
    thread_id = payload.thread_id or f"thread_{uuid.uuid4().hex[:12]}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state: AgentState = {
        "user_query": payload.query,
        "intent": "QUANTITATIVE_SQL",
        "messages": [HumanMessage(content=payload.query)],
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

    async def event_generator():
        # 1. Evento de Inicialização
        yield f"data: {json.dumps({'type': 'init', 'thread_id': thread_id})}\n\n"
        await asyncio.sleep(0.01)

        try:
            # 2. Executa nós com emissão de progresso via astream
            final_state = dict(initial_state)
            async for chunk in app_graph.astream(initial_state, config=config):
                for node_name, node_output in chunk.items():
                    final_state.update(node_output)

                    step_data: dict[str, Any]
                    if node_name == "router":
                        intent_val = node_output.get("intent", "QUANTITATIVE_SQL")
                        step_data = {
                            "type": "step",
                            "step": "router",
                            "message": f"Intencao identificada: {intent_val}",
                        }
                        yield f"data: {json.dumps(step_data)}\n\n"
                    elif node_name == "nl2sql":
                        step_data = {
                            "type": "step",
                            "step": "nl2sql",
                            "message": "Query SQL analitica gerada com sucesso",
                            "sql": node_output.get("sql_query"),
                        }
                        yield f"data: {json.dumps(step_data)}\n\n"
                    elif node_name == "sql_guard":
                        valido = node_output.get("sql_valid", False)
                        msg = (
                            "Query validada pelo AST Guardrail"
                            if valido
                            else "Query rejeitada, iniciando auto-correcao..."
                        )
                        step_data = {
                            "type": "step",
                            "step": "guard",
                            "message": msg,
                            "valid": valido,
                        }
                        yield f"data: {json.dumps(step_data)}\n\n"
                    elif node_name == "executor":
                        total_rows = len(node_output.get("sql_result") or [])
                        step_data = {
                            "type": "step",
                            "step": "executor",
                            "message": f"{total_rows} registros retornados do motor colunar DuckDB",
                            "rows": total_rows,
                        }
                        yield f"data: {json.dumps(step_data)}\n\n"
                    elif node_name == "self_healing":
                        step_data = {
                            "type": "step",
                            "step": "healing",
                            "message": "Auto-correcao concluida com sucesso",
                        }
                        yield f"data: {json.dumps(step_data)}\n\n"

            # 3. Emissão dos tokens finais e resposta estruturada
            final_resp = final_state.get("final_response") or "Análise concluída com sucesso."
            payload_end = {
                "type": "end",
                "thread_id": thread_id,
                "intent": final_state.get("intent", "QUANTITATIVE_SQL"),
                "sql_query": final_state.get("sql_query"),
                "sql_valid": final_state.get("sql_valid", True),
                "data": final_state.get("sql_result"),
                "final_response": final_resp,
                "next_best_actions": final_state.get("next_best_actions") or [],
            }
            yield f"data: {json.dumps(payload_end)}\n\n"

        except Exception as err:
            err_payload = {"type": "error", "message": f"Erro de processamento no agente: {err}"}
            yield f"data: {json.dumps(err_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
