"""Esquemas Pydantic v2 de Requisição e Resposta para a API REST."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload de entrada para o copiloto de dados."""

    query: str = Field(
        min_length=1,
        max_length=1000,
        description="Pergunta em linguagem natural do usuário.",
        examples=["Qual é a nota média geral das avaliações?"],
    )
    thread_id: str | None = Field(
        default=None,
        description="Identificador único da sessão/conversa para persistência de histórico.",
        examples=["thread-cx-1234"],
    )


class ChatResponse(BaseModel):
    """Payload de resposta estruturada do copiloto."""

    thread_id: str = Field(description="Identificador da sessão persistida pelo checkpointer.")
    intent: str = Field(description="Intenção classificada pelo IntentRouter.")
    sql_query: str | None = Field(
        default=None, description="Query SQL gerada e validada pelo AST Guardrail."
    )
    sql_valid: bool = Field(
        default=True, description="Indica se o SQL passou na validação sintática e de segurança."
    )
    data: list[dict[str, Any]] | None = Field(
        default=None,
        description="Registros tabulares retornados pelo banco de dados (amostra formatada).",
    )
    final_response: str = Field(
        description="Síntese executiva formatada em Markdown com insights para CX/Varejo."
    )
    next_best_actions: list[str] = Field(
        default_factory=list,
        description="Lista com 3 perguntas analíticas preditivas recomendadas.",
    )


class KPIsResponse(BaseModel):
    """Indicadores-chave de desempenho (KPIs) em tempo real da base de dados."""

    total_reviews: int = Field(description="Total de avaliações processadas no catálogo.")
    avg_rating: float = Field(description="Nota média ponderada de todas as avaliações.")
    five_star_reviews: int = Field(
        description="Quantidade total de avaliações com nota máxima (5 estrelas)."
    )
    rating_distribution: dict[str, int] = Field(
        default_factory=dict, description="Distribuição quantitativa de notas de 1 a 5 estrelas."
    )
    yearly_trend: list[dict[str, Any]] = Field(
        default_factory=list, description="Série temporal de volume e nota média anual (2016-2023)."
    )
    top_products: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Ranking dos produtos mais avaliados com rating e proporção 5 estrelas.",
    )


class HealthResponse(BaseModel):
    """Diagnóstico de saúde e prontidão do serviço."""

    status: str = Field(default="healthy", description="Status operacional da API.")
    version: str = Field(default="0.2.0", description="Versão atual do backend RetailSense AI.")
    database_ready: bool = Field(
        description="Indica se a conexão com o banco de dados SQLite/Postgres está ativa."
    )
