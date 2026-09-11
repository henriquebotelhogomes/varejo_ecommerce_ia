"""Definição do Estado Global do LangGraph (AgentState) e Contratos Pydantic v2.

Padronização de tipos e contratos I/O estruturados para o RetailSense AI.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# =====================================================================
# 1. CONTRATOS PYDANTIC v2 PARA SAÍDAS ESTRUTURADAS (STRUCTURED OUTPUTS)
# =====================================================================


class IntentClassificationOutput(BaseModel):
    """Classificação semântica da requisição do usuário."""

    intent: Literal["QUANTITATIVE_SQL", "QUALITATIVE_RAG", "HYBRID", "CASUAL_CHAT"] = Field(
        description="Categoria primária da dúvida do usuário."
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Nível de confiança na classificação (0.0 a 1.0)."
    )
    reasoning: str = Field(description="Justificativa sucinta para a rota escolhida.")
    extracted_entities: list[str] = Field(
        default_factory=list, description="Termos-chave, categorias ou ASINs identificados."
    )


class SQLGenerationOutput(BaseModel):
    """Estrutura da query gerada pelo modelo."""

    sql_query: str = Field(description="Comando SQL SQLite puro sem blocos markdown.")
    tables_used: list[str] = Field(
        default_factory=list, description="Lista de tabelas referenciadas na consulta."
    )
    is_aggregation: bool = Field(
        default=False,
        description="Indica se a query realiza agregação (COUNT, AVG, SUM, MIN, MAX).",
    )
    explanation: str = Field(description="Explicação breve em português da lógica da query.")


class NextBestActionItem(BaseModel):
    """Pergunta sugerida para aprofundamento analítico investigativo."""

    question: str = Field(
        description="Pergunta em linguagem natural que aprofunda a análise dos dados."
    )
    business_rationale: str = Field(
        description="Por que esta pergunta é valiosa para o gestor de varejo/CX."
    )


class ExecutiveSummaryOutput(BaseModel):
    """Síntese executiva formatada para gestores de varejo e CX."""

    executive_summary: str = Field(
        description="Resposta executiva, objetiva e contextualizada com os dados apurados."
    )
    key_findings: list[str] = Field(
        default_factory=list, description="Bullet points com os achados analíticos mais críticos."
    )
    suggested_actions: list[NextBestActionItem] = Field(
        default_factory=list,
        min_length=3,
        max_length=3,
        description="Exatamente 3 próximas perguntas analíticas recomendadas.",
    )


# =====================================================================
# 2. ESTADO GLOBAL COMPARTILHADO DO LANGGRAPH (AgentState)
# =====================================================================


class AgentState(TypedDict):
    """Estado global compartilhado entre os nós do LangGraph."""

    # Histórico de mensagens com reducer oficial de concatenação delta
    messages: Annotated[list[BaseMessage], add_messages]

    # Entrada do usuário e intenção classificada
    user_query: str
    intent: Literal["QUANTITATIVE_SQL", "QUALITATIVE_RAG", "HYBRID", "CASUAL_CHAT"]

    # Artefatos da Trilha SQL
    sql_query: str | None
    sql_valid: bool
    sql_validation_error: str | None
    retry_count: int
    sql_result: list[dict[str, Any]] | None

    # Artefatos da Trilha Vetorial (RAG Híbrido)
    vector_contexts: list[str]

    # Governança e Human-in-the-Loop
    requires_human_approval: bool
    is_approved: bool

    # Síntese Executiva Final
    final_response: str | None
    next_best_actions: list[str]

    # Auditoria e FinOps
    token_usage: dict[str, int]
    estimated_cost_usd: float
