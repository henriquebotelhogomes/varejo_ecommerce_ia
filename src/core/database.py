"""Camada de Acesso a Dados e Persistência Otimizada: RetailSense AI.

Gerencia a conexão com o banco de dados relacional (SQLite/PostgreSQL), criação
de índices analíticos e execução segura em modo somente leitura (read-only).
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any

import pandas as pd
from datasets import load_dataset

DB_PATH = "amazon_reviews.db"


def criar_indices_otimizados(conn: sqlite3.Connection) -> None:
    """Garante a criação de índices B-Tree para acelerar consultas analíticas."""
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_avaliacoes_rating ON avaliacoes(rating);",
        "CREATE INDEX IF NOT EXISTS idx_avaliacoes_parent_asin ON avaliacoes(parent_asin);",
        "CREATE INDEX IF NOT EXISTS idx_avaliacoes_timestamp ON avaliacoes(timestamp);",
        "CREATE INDEX IF NOT EXISTS idx_avaliacoes_helpful ON avaliacoes(helpful_vote);",
    ]
    cursor = conn.cursor()
    for sql in indices:
        cursor.execute(sql)
    conn.commit()


def get_connection(read_only: bool = True) -> sqlite3.Connection:
    """Retorna uma conexão com o SQLite.

    Em modo read-only, utiliza a URI do SQLite com mode=ro para impedir qualquer escrita.
    """
    if read_only:
        # Abre conexão em modo estritamente somente leitura
        uri = f"file:{os.path.abspath(DB_PATH)}?mode=ro"
        return sqlite3.connect(uri, uri=True)
    return sqlite3.connect(DB_PATH)


def preparar_banco_amazon(limite_amostra: int | None = None) -> tuple[bool, str]:
    """Ingere o dataset da Amazon do HuggingFace e cria índices de performance.

    Se o banco já existir, garante apenas a presença dos índices.
    """
    if os.path.exists(DB_PATH):
        try:
            conn = get_connection(read_only=False)
            criar_indices_otimizados(conn)
            conn.close()
            return True, f"Banco '{DB_PATH}' pronto e com índices otimizados."
        except Exception as e:
            return False, f"Falha ao validar índices do banco existente: {e}"

    import logging

    logger = logging.getLogger("retail_db")

    try:
        logger.info("Carregando dataset da Amazon do HuggingFace...")
        dataset = load_dataset("minhth2nh/amazon_product_review_283K", split="train")

        if limite_amostra and limite_amostra > 0:
            dataset = dataset.select(range(limite_amostra))

        logger.info("Convertendo registros para DataFrame...")
        df = dataset.to_pandas()

        logger.info("Persistindo tabela no SQLite e gerando indices B-Tree...")
        conn = get_connection(read_only=False)
        df.to_sql("avaliacoes", conn, if_exists="replace", index=False)
        criar_indices_otimizados(conn)
        conn.close()

        return (
            True,
            f"Banco '{DB_PATH}' criado com sucesso com {len(df):,} registros e indices ativos.",
        )
    except Exception as e:
        return False, f"Erro ao preparar banco de dados: {e}"


def obter_schema_avaliacoes() -> str:
    """Retorna a estrutura DDL das colunas e tipos da tabela 'avaliacoes'."""
    if not os.path.exists(DB_PATH):
        return (
            "Tabela 'avaliacoes': rating REAL, title TEXT, text TEXT, "
            "parent_asin TEXT, user_id TEXT, timestamp INTEGER, helpful_vote INTEGER"
        )

    conn = get_connection(read_only=True)
    schema_df = pd.read_sql("PRAGMA table_info(avaliacoes)", conn)
    conn.close()

    linhas = [f"- {row['name']} ({row['type']})" for _, row in schema_df.iterrows()]
    return "Tabela 'avaliacoes':\n" + "\n".join(linhas)


_CACHED_KPIS: dict[str, Any] | None = None


def obter_kpis_gerais() -> dict[str, Any]:
    """Calcula rapidamente as métricas consolidadas do catálogo."""
    if not os.path.exists(DB_PATH):
        return {"total_reviews": 0, "avg_rating": 0.0, "five_star_reviews": 0}

    conn = get_connection(read_only=True)
    try:
        total = pd.read_sql("SELECT COUNT(*) as count FROM avaliacoes", conn).iloc[0]["count"]
        avg = pd.read_sql("SELECT AVG(rating) as avg FROM avaliacoes", conn).iloc[0]["avg"]
        five = pd.read_sql("SELECT COUNT(*) as count FROM avaliacoes WHERE rating = 5", conn).iloc[
            0
        ]["count"]
        return {
            "total_reviews": int(total),
            "avg_rating": float(avg) if avg else 0.0,
            "five_star_reviews": int(five),
        }
    finally:
        conn.close()


def obter_kpis_detalhados() -> dict[str, Any]:
    """Retorna métricas consolidadas, série temporal e top produtos com cache em memória."""
    global _CACHED_KPIS
    if _CACHED_KPIS is not None:
        return _CACHED_KPIS

    if not os.path.exists(DB_PATH):
        return {
            "total_reviews": 0,
            "avg_rating": 0.0,
            "five_star_reviews": 0,
            "rating_distribution": {},
            "yearly_trend": [],
            "top_products": [],
        }

    conn = get_connection(read_only=True)
    try:
        total = pd.read_sql("SELECT COUNT(*) as count FROM avaliacoes", conn).iloc[0]["count"]
        avg = pd.read_sql("SELECT AVG(rating) as avg FROM avaliacoes", conn).iloc[0]["avg"]
        five = pd.read_sql("SELECT COUNT(*) as count FROM avaliacoes WHERE rating = 5", conn).iloc[
            0
        ]["count"]

        # 1. Distribuição de Notas
        df_dist = pd.read_sql(
            "SELECT rating, COUNT(*) as qtd FROM avaliacoes GROUP BY rating ORDER BY rating", conn
        )
        distribution = {
            f"{int(r['rating'])} Estrelas": int(r["qtd"]) for _, r in df_dist.iterrows()
        }

        # 2. Série Temporal Anual (2016 a 2023)
        q_trend = """
        SELECT
          strftime('%Y', datetime(CAST(timestamp AS INTEGER)/1000, 'unixepoch')) as ano,
          COUNT(*) as total,
          ROUND(AVG(CAST(rating AS REAL)), 2) as media_nota
        FROM avaliacoes
        WHERE timestamp IS NOT NULL AND CAST(timestamp AS INTEGER) > 0
        GROUP BY ano
        HAVING CAST(ano AS INTEGER) >= 2016 AND CAST(ano AS INTEGER) <= 2023
        ORDER BY ano ASC
        """
        df_trend = pd.read_sql(q_trend, conn)
        yearly_trend = [
            {"ano": str(r["ano"]), "total": int(r["total"]), "media_nota": float(r["media_nota"])}
            for _, r in df_trend.iterrows()
        ]

        # 3. Top 5 Produtos Mais Avaliados
        q_top = """
        SELECT
          parent_asin,
          COUNT(*) as total_reviews,
          ROUND(AVG(CAST(rating AS REAL)), 2) as media_nota,
          ROUND(100.0 * SUM(CASE WHEN CAST(rating AS REAL) = 5.0 THEN 1 ELSE 0 END) / COUNT(*), 1) as perc_5_estrelas
        FROM avaliacoes
        GROUP BY parent_asin
        ORDER BY total_reviews DESC
        LIMIT 5
        """
        df_top = pd.read_sql(q_top, conn)
        top_products = [
            {
                "parent_asin": str(r["parent_asin"]),
                "total_reviews": int(r["total_reviews"]),
                "media_nota": float(r["media_nota"]),
                "perc_5_estrelas": float(r["perc_5_estrelas"]),
            }
            for _, r in df_top.iterrows()
        ]

        _CACHED_KPIS = {
            "total_reviews": int(total),
            "avg_rating": float(avg) if avg else 0.0,
            "five_star_reviews": int(five),
            "rating_distribution": distribution,
            "yearly_trend": yearly_trend,
            "top_products": top_products,
        }
        return _CACHED_KPIS
    finally:
        conn.close()


def executar_query_read_only(sql_query: str) -> pd.DataFrame:
    """Executa uma query em modo somente leitura com garantia a nível de driver."""
    conn = get_connection(read_only=True)
    try:
        df = pd.read_sql(sql_query, conn)
        return df
    finally:
        conn.close()
