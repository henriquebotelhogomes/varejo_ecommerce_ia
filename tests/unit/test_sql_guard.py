"""Suíte de Testes Unitários para o Validador AST de SQL (sql_guard.py)."""

from src.agents.sql_guard import validate_and_sanitize_sql


def test_valid_aggregation_query():
    """Valida query de agregação pura sem injeção forçada de LIMIT."""
    query = "SELECT AVG(rating) AS media, COUNT(*) AS total FROM avaliacoes"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is True
    assert res.is_aggregation is True
    assert "avaliacoes" in res.tables_used
    assert res.error_message is None
    # Como é agregação pura sem agrupamento, não precisa de LIMIT forçado
    assert "LIMIT" not in res.sanitized_sql.upper()


def test_valid_select_injects_limit():
    """Garante que queries abertas sem LIMIT recebam LIMIT 100 automaticamente."""
    query = "SELECT title, text, rating FROM avaliacoes WHERE rating = 1"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is True
    assert res.is_aggregation is False
    assert "LIMIT 100" in res.sanitized_sql.upper()


def test_valid_select_preserves_lower_limit():
    """Garante que limits explícitos menores que max_limit sejam preservados."""
    query = "SELECT parent_asin, rating FROM avaliacoes LIMIT 5"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is True
    assert "LIMIT 5" in res.sanitized_sql.upper()


def test_valid_select_caps_excessive_limit():
    """Garante que limits acima do teto sejam ajustados para o max_limit."""
    query = "SELECT parent_asin, rating FROM avaliacoes LIMIT 500"
    res = validate_and_sanitize_sql(query, max_limit=100)
    assert res.is_valid is True
    assert "LIMIT 100" in res.sanitized_sql.upper()


def test_block_drop_table():
    """Bloqueia expressamente comandos DROP TABLE."""
    query = "DROP TABLE avaliacoes"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is False
    assert (
        "Apenas comandos SELECT são autorizados" in res.error_message or "DROP" in res.error_message
    )


def test_block_delete():
    """Bloqueia comandos DELETE."""
    query = "DELETE FROM avaliacoes WHERE rating = 1"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is False
    assert "Apenas comandos SELECT" in res.error_message or "DELETE" in res.error_message


def test_block_update():
    """Bloqueia comandos UPDATE."""
    query = "UPDATE avaliacoes SET rating = 5 WHERE parent_asin = 'XYZ'"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is False


def test_block_insert():
    """Bloqueia comandos INSERT."""
    query = "INSERT INTO avaliacoes (rating, title) VALUES (5, 'Ótimo')"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is False


def test_block_alter_table():
    """Bloqueia comandos ALTER TABLE."""
    query = "ALTER TABLE avaliacoes ADD COLUMN temp_col TEXT"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is False


def test_block_stacked_queries():
    """Bloqueia ataques com múltiplos comandos separados por ponto e vírgula."""
    query = "SELECT * FROM avaliacoes; DROP TABLE avaliacoes;"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is False
    assert "Múltiplas instruções" in res.error_message


def test_block_unauthorized_table():
    """Bloqueia consultas a tabelas fora da whitelist."""
    query = "SELECT * FROM usuarios_secretos"
    res = validate_and_sanitize_sql(query, allowed_tables={"avaliacoes"})
    assert res.is_valid is False
    assert "não pertence à whitelist" in res.error_message


def test_markdown_cleanup():
    """Valida que blocos markdown do LLM (```sql ... ```) sejam devidamente limpos."""
    query = "```sql\nSELECT COUNT(*) FROM avaliacoes WHERE rating = 5\n```"
    res = validate_and_sanitize_sql(query)
    assert res.is_valid is True
    assert res.is_aggregation is True


def test_empty_query():
    """Rejeita strings vazias."""
    res = validate_and_sanitize_sql("   ")
    assert res.is_valid is False
    assert "vazia" in res.error_message
