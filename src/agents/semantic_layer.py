"""Camada Semântica Centralizada (Metric Layer) do RetailSense AI.

Codifica definições matemáticas e canônicas de métricas de negócio para varejo/e-commerce,
garantindo consistência absoluta de cálculo entre o BI, o NL2SQL e as sínteses executivas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MetricDefinition(BaseModel):
    """Contrato de especificação formal de uma métrica analítica de negócio."""

    metric_id: str = Field(description="Identificador único em snake_case da métrica.")
    name: str = Field(description="Nome de exibição executivo da métrica.")
    formula: str = Field(description="Expressão matemática compatível com dialeto DuckDB.")
    business_context: str = Field(description="Definição de negócio e regra de interpretação.")
    canonical_sql_snippet: str = Field(description="Fragmento de query canônica recomendada.")


METRIC_CATALOG: dict[str, MetricDefinition] = {
    "csat_proxy": MetricDefinition(
        metric_id="csat_proxy",
        name="Índice de Satisfação do Cliente (CSAT Proxy)",
        formula="ROUND((COUNT(CASE WHEN rating >= 4.0 THEN 1 END) * 100.0) / COUNT(*), 1)",
        business_context="Percentual de clientes que avaliaram positivamente (4 ou 5 estrelas) sobre o total.",
        canonical_sql_snippet="SELECT ROUND((COUNT(CASE WHEN rating >= 4.0 THEN 1 END) * 100.0) / COUNT(*), 1) AS csat_proxy FROM avaliacoes",
    ),
    "promoter_rate": MetricDefinition(
        metric_id="promoter_rate",
        name="Taxa de Promotores (Promoter Share)",
        formula="ROUND((COUNT(CASE WHEN rating >= 4.0 THEN 1 END) * 100.0) / COUNT(*), 1)",
        business_context="Parcela de compras com alta recomendação e fidelidade no catálogo.",
        canonical_sql_snippet="SELECT ROUND((COUNT(CASE WHEN rating >= 4.0 THEN 1 END) * 100.0) / COUNT(*), 1) AS promoter_rate FROM avaliacoes",
    ),
    "detractor_rate": MetricDefinition(
        metric_id="detractor_rate",
        name="Taxa de Detratores (Detractor Share)",
        formula="ROUND((COUNT(CASE WHEN rating <= 2.0 THEN 1 END) * 100.0) / COUNT(*), 1)",
        business_context="Parcela de avaliações insatisfeitas (1 e 2 estrelas) que indicam atrito operacional ou defeito.",
        canonical_sql_snippet="SELECT ROUND((COUNT(CASE WHEN rating <= 2.0 THEN 1 END) * 100.0) / COUNT(*), 1) AS detractor_rate FROM avaliacoes",
    ),
    "net_sentiment_score": MetricDefinition(
        metric_id="net_sentiment_score",
        name="Net Customer Sentiment Score (NPS Proxy)",
        formula="ROUND(((COUNT(CASE WHEN rating >= 4.0 THEN 1 END) - COUNT(CASE WHEN rating <= 2.0 THEN 1 END)) * 100.0) / COUNT(*), 1)",
        business_context="Diferença percentual entre promotores (>=4) e detratores (<=2). Varia de -100 a +100.",
        canonical_sql_snippet="SELECT ROUND(((COUNT(CASE WHEN rating >= 4.0 THEN 1 END) - COUNT(CASE WHEN rating <= 2.0 THEN 1 END)) * 100.0) / COUNT(*), 1) AS net_sentiment_score FROM avaliacoes",
    ),
    "top_products_volume": MetricDefinition(
        metric_id="top_products_volume",
        name="Ranking de Produtos por Volume de Avaliações",
        formula="COUNT(*)",
        business_context="Identifica os SKUs mais relevantes (líderes de tráfego) e sua nota média.",
        canonical_sql_snippet="SELECT parent_asin, COUNT(*) AS total_avaliacoes, ROUND(AVG(rating), 2) AS media_nota FROM avaliacoes GROUP BY parent_asin ORDER BY total_avaliacoes DESC LIMIT 5",
    ),
    "yearly_trend": MetricDefinition(
        metric_id="yearly_trend",
        name="Evolução Temporal Anual de Volume e Satisfação",
        formula="strftime(epoch_ms(timestamp), '%Y')",
        business_context="Série histórica consolidando volume de reviews e evolução da nota por ano de compra.",
        canonical_sql_snippet="SELECT strftime(epoch_ms(timestamp), '%Y') AS ano, COUNT(*) AS total, ROUND(AVG(rating), 2) AS media_nota FROM avaliacoes WHERE timestamp IS NOT NULL GROUP BY ano ORDER BY ano ASC",
    ),
}


def get_metric_definition(metric_id: str) -> MetricDefinition | None:
    """Recupera a definição canônica de uma métrica pelo seu identificador."""
    return METRIC_CATALOG.get(metric_id.lower())


def get_semantic_layer_prompt_context() -> str:
    """Gera bloco de regras de cálculo semântico para injeção no NL2SQLGenerator."""
    lines = [
        "CAMADA SEMÂNTICA DE MÉRICAS DE NEGÓCIO (METRIC LAYER OFICIAL):",
        "Quando o usuário solicitar métricas de negócio, utilize OBRIGATORIAMENTE as seguintes fórmulas canônicas:",
    ]
    for m in METRIC_CATALOG.values():
        lines.append(f"- **{m.name}** (`{m.metric_id}`):")
        lines.append(f"  Regra: {m.business_context}")
        lines.append(f"  Fórmula: `{m.formula}`")
        lines.append(f"  Exemplo: `{m.canonical_sql_snippet}`")
    lines.append("")
    lines.append("IMPORTANTE: NUNCA crie fórmulas ad-hoc diferentes das especificadas acima.")
    return "\n".join(lines)
