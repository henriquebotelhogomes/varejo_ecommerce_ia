from src.agents.semantic_layer import (
    METRIC_CATALOG,
    get_metric_definition,
    get_semantic_layer_prompt_context,
)
from src.core.duckdb_engine import executar_query_duckdb, obter_kpis_duckdb


def test_duckdb_engine_connectivity():
    res = executar_query_duckdb("SELECT 1 AS alive")
    assert len(res) == 1
    assert res[0]["alive"] == 1


def test_duckdb_table_avaliacoes():
    res = executar_query_duckdb("SELECT count(rating) AS total FROM avaliacoes")
    assert len(res) == 1
    assert res[0]["total"] > 200000


def test_duckdb_kpi_summary():
    kpis = obter_kpis_duckdb(force_refresh=True)
    assert kpis["total_reviews"] > 200000
    assert 1.0 <= kpis["avg_rating"] <= 5.0
    assert "duckdb" in kpis.get("engine", "").lower()


def test_semantic_layer_catalog():
    assert len(METRIC_CATALOG) >= 6
    assert "csat_proxy" in METRIC_CATALOG
    assert "promoter_rate" in METRIC_CATALOG
    assert "detractor_rate" in METRIC_CATALOG
    assert "net_sentiment_score" in METRIC_CATALOG


def test_semantic_layer_lookup():
    csat = get_metric_definition("csat_proxy")
    assert csat is not None
    assert "rating >= 4.0" in csat.formula
    assert csat.metric_id == "csat_proxy"


def test_semantic_layer_prompt_context():
    ctx = get_semantic_layer_prompt_context()
    assert "CAMADA SEMÂNTICA" in ctx
    assert "csat_proxy" in ctx
