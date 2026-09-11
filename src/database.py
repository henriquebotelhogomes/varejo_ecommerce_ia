import os
import sqlite3

from datasets import load_dataset

DB_NAME = "amazon_reviews.db"


def preparar_banco_amazon():
    """
    Descarrega o dataset completo de reviews da Amazon usando o Hugging Face,
    converte para Pandas e guarda num banco de dados SQLite local.
    Retorna uma tupla (sucesso: bool, mensagem: str).
    """
    # Verifica se o banco já existe localmente
    if os.path.exists(DB_NAME):
        return (
            True,
            f"Banco de dados '{DB_NAME}' carregado com sucesso a partir do armazenamento local.",
        )

    try:
        print(
            "⏳ A descarregar o dataset COMPLETO da Amazon (isto pode demorar uns segundos/minutos dependendo da internet)..."
        )
        # Descarrega o dataset inteiro
        dataset = load_dataset("minhth2nh/amazon_product_review_283K", split="train")

        # Converte todo o dataset para Pandas (sem o '.select(range(10000))')
        print("⏳ A converter os dados completos para o formato SQL...")
        df = dataset.to_pandas()

        # Conecta ao SQLite e guarda os dados localmente
        print("⏳ A escrever os dados na base de dados local...")
        conn = sqlite3.connect(DB_NAME)
        df.to_sql("avaliacoes", conn, if_exists="replace", index=False)
        conn.close()

        return True, f"Banco '{DB_NAME}' criado com sucesso com todos os {len(df):,} registos!"
    except Exception as e:
        return False, f"Erro ao preparar o banco de dados: {str(e)}"
