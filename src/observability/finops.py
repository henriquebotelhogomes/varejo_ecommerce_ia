"""Módulo de FinOps e Auditoria de Custos de Inteligência Artificial.

Calcula custos em tempo real de tokens consumidos pelos modelos eficientes
(Gemini 3.8 Flash, DeepSeek V4.1 Flash) em comparação com o modelo de fronteira de referência (GPT 5.6 Luna).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# Tabela de Preços por 1 Milhão de Tokens (USD)
TOKEN_PRICING_PER_MILLION: dict[str, dict[str, float]] = {
    # Tier de Alta Eficiência / Throughput
    "gemini-3.8-flash": {"prompt": 0.075, "completion": 0.30},
    "deepseek-v4.1-flash": {"prompt": 0.14, "completion": 0.28},
    "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79},
    # Tier de Raciocínio Profundo
    "deepseek-v4-pro": {"prompt": 0.55, "completion": 2.19},
    "gemini-3-pro": {"prompt": 1.25, "completion": 5.00},
    # Modelo de Fronteira de Referência (Benchmark de Economia)
    "gpt-5.6-luna": {"prompt": 2.00, "completion": 8.00},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
}


class FinOpsMetrics(BaseModel):
    """Métricas de custo e auditoria financeira por chamada/sessão."""

    prompt_tokens: int = Field(description="Quantidade de tokens de entrada.")
    completion_tokens: int = Field(description="Quantidade de tokens de saída.")
    total_tokens: int = Field(description="Soma total de tokens.")
    actual_cost_usd: float = Field(description="Custo real incorrido no modelo selecionado.")
    projected_baseline_cost_usd: float = Field(
        description="Custo estimado caso fosse executado no modelo de fronteira baseline (GPT 5.6 Luna)."
    )
    savings_usd: float = Field(description="Economia financeira gerada (Baseline - Custo Real).")
    savings_percentage: float = Field(description="Percentual de economia gerada.")


def calcular_custo_tokens(
    prompt_tokens: int, completion_tokens: int, model: str = "gemini-3.8-flash"
) -> float:
    """Calcula o custo em dólares para um determinado volume de tokens."""
    pricing = TOKEN_PRICING_PER_MILLION.get(
        model.lower(), TOKEN_PRICING_PER_MILLION["gemini-3.8-flash"]
    )
    cost = (prompt_tokens / 1_000_000 * pricing["prompt"]) + (
        completion_tokens / 1_000_000 * pricing["completion"]
    )
    return round(cost, 6)


def auditar_finops(
    prompt_tokens: int, completion_tokens: int, model_utilizado: str = "gemini-3.8-flash"
) -> FinOpsMetrics:
    """Gera auditoria comparativa completa entre o modelo executado e a linha de base GPT 5.6 Luna."""
    actual_cost = calcular_custo_tokens(prompt_tokens, completion_tokens, model_utilizado)
    baseline_cost = calcular_custo_tokens(prompt_tokens, completion_tokens, "gpt-5.6-luna")
    savings = max(0.0, baseline_cost - actual_cost)
    pct = (savings / baseline_cost * 100) if baseline_cost > 0 else 0.0

    return FinOpsMetrics(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        actual_cost_usd=round(actual_cost, 6),
        projected_baseline_cost_usd=round(baseline_cost, 6),
        savings_usd=round(savings, 6),
        savings_percentage=round(pct, 2),
    )
