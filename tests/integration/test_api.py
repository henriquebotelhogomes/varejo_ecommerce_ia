"""Testes de Integração para a API REST FastAPI e Documentação Scalar."""

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_health_endpoint():
    """Valida a rota de liveness/readiness probe."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.2.0"
    assert "status" in data
    assert "database_ready" in data


def test_kpis_endpoint():
    """Valida a rota analítica de KPIs do catálogo."""
    response = client.get("/api/v1/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "avg_rating" in data
    assert "five_star_reviews" in data
    assert "rating_distribution" in data


def test_scalar_docs_endpoint():
    """Garante que a documentação interativa viva do Scalar é servida em /docs."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    # Verifica que a referência ao script do Scalar está presente
    assert "@scalar/api-reference" in response.text or "scalar" in response.text.lower()


def test_openapi_schema_endpoint():
    """Garante que o schema OpenAPI está disponível em /openapi.json."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/api/v1/chat" in data["paths"]
    assert "/api/v1/kpis" in data["paths"]
    assert "/api/v1/health" in data["paths"]


def test_chat_casual_endpoint():
    """Testa a interação de chat informal com o copiloto."""
    payload = {"query": "Olá! Quem é você?"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "CASUAL_CHAT"
    assert "RetailSense AI" in data["final_response"]
    assert len(data["next_best_actions"]) == 3
    assert data["thread_id"].startswith("thread_")


def test_chat_quantitative_endpoint():
    """Testa a interação analítica quantitativa Text-to-SQL."""
    payload = {"query": "Qual é a média de notas dos produtos?", "thread_id": "test_thread_001"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["thread_id"] == "test_thread_001"
    assert data["final_response"] is not None
    assert len(data["next_best_actions"]) >= 1


def test_chat_stream_endpoint():
    """Valida o endpoint de streaming progressivo via Server-Sent Events (SSE)."""
    payload = {"query": "Qual é a nota média geral?", "thread_id": "test_stream_001"}
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    content = response.text
    assert "data: " in content
    assert '"type": "init"' in content
    assert '"type": "end"' in content
