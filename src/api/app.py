"""Aplicação Principal FastAPI com Documentação Viva via Scalar (RetailSense AI).

Desativa o Swagger UI legado e expõe a documentação interativa moderna no endpoint /docs
utilizando Scalar (padrão obrigatório de governança).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from scalar_fastapi import get_scalar_api_reference

from src.api.routes.chat import router as chat_router
from src.api.routes.health import router as health_router
from src.api.routes.kpis import router as kpis_router
from src.core.database import obter_kpis_gerais


def create_app() -> FastAPI:
    """Instancia e configura a aplicação FastAPI desacoplada com Scalar."""
    api = FastAPI(
        title="RetailSense AI - Enterprise Conversational Analytics",
        description=(
            "API REST de Analytics Conversacional e Text-to-SQL para Varejo e E-commerce. "
            "Combina LangGraph Multi-Agentes, AST Guardrails determinísticos e roteamento FinOps."
        ),
        version="0.2.0",
        # Desativa Swagger UI e ReDoc legados conforme as regras normativas
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    # Middleware CORS para integração segura com Frontends modernos (Next.js / React 19)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registro de Rotas Versionadas (/api/v1)
    api.include_router(health_router, prefix="/api/v1")
    api.include_router(kpis_router, prefix="/api/v1")
    api.include_router(chat_router, prefix="/api/v1")

    # Endpoint de Métricas Prometheus/OpenTelemetry para Observabilidade
    @api.get("/metrics", include_in_schema=False)
    async def metrics_endpoint():
        """Retorna métricas da aplicação no padrão Prometheus / OpenMetrics."""
        kpis = obter_kpis_gerais()
        total = kpis.get("total_reviews", 0)
        avg = kpis.get("avg_rating", 0.0)
        five = kpis.get("five_star_reviews", 0)

        lines = [
            "# HELP retail_reviews_total Volume total de avaliacoes no catalogo",
            "# TYPE retail_reviews_total counter",
            f"retail_reviews_total {total}",
            "# HELP retail_reviews_avg_rating Nota media calculada das avaliacoes",
            "# TYPE retail_reviews_avg_rating gauge",
            f"retail_reviews_avg_rating {avg:.4f}",
            "# HELP retail_reviews_five_star Total de avaliacoes 5 estrelas",
            "# TYPE retail_reviews_five_star counter",
            f"retail_reviews_five_star {five}",
        ]
        return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

    # Documentação Viva com Scalar nos endpoints /docs e /scalar
    @api.get("/docs", include_in_schema=False)
    @api.get("/scalar", include_in_schema=False)
    async def scalar_html():
        return get_scalar_api_reference(
            openapi_url=api.openapi_url,
            title="RetailSense AI - Documentação Interativa",
        )

    # 3. Servir arquivos estáticos do Frontend compilado (React) se existirem
    from pathlib import Path

    from fastapi.staticfiles import StaticFiles

    dist_candidates = [
        Path(__file__).parent / "static",
        Path(__file__).parent.parent.parent / "frontend" / "dist",
    ]
    for dist_dir in dist_candidates:
        if dist_dir.exists() and (dist_dir / "index.html").exists():
            api.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
            break

    return api


app = create_app()
