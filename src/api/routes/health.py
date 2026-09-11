"""Endpoint de Verificação de Saúde (Liveness & Readiness Probes)."""

from fastapi import APIRouter

from src.api.schemas import HealthResponse
from src.core.database import obter_kpis_gerais

router = APIRouter(prefix="/health", tags=["Health & Status"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Verificação de Saúde do Sistema",
    description="Retorna o status operacional da API e a integridade da conexão com a base de dados.",
)
async def check_health() -> HealthResponse:
    """Retorna o estado de prontidão da API."""
    try:
        kpis = obter_kpis_gerais()
        db_ready = isinstance(kpis, dict)
    except Exception:
        db_ready = False

    return HealthResponse(
        status="healthy" if db_ready else "degraded", version="0.2.0", database_ready=db_ready
    )
