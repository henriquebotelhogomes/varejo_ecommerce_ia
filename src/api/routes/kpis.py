"""Endpoint de Métricas Consolidadas de Catálogo (KPIs em Tempo Real)."""

from fastapi import APIRouter

from src.api.schemas import KPIsResponse
from src.core.database import obter_kpis_detalhados
from src.core.duckdb_engine import obter_kpis_duckdb

router = APIRouter(prefix="/kpis", tags=["Analytics & BI"])


@router.get(
    "",
    response_model=KPIsResponse,
    summary="Obter Indicadores Globais do Catálogo",
    description="Calcula e retorna em tempo real o volume total de avaliações, nota média, distribuição por estrela, série histórica e top produtos via DuckDB OLAP.",
)
async def get_kpis() -> KPIsResponse:
    """Retorna os indicadores executivos do catálogo de produtos."""
    try:
        data = obter_kpis_duckdb()
    except Exception:
        data = obter_kpis_detalhados()

    return KPIsResponse(
        total_reviews=data.get("total_reviews", 0),
        avg_rating=data.get("avg_rating", 0.0),
        five_star_reviews=data.get("five_star_reviews", 0),
        rating_distribution=data.get("rating_distribution", {}),
        yearly_trend=data.get("yearly_trend", []),
        top_products=data.get("top_products", []),
    )
