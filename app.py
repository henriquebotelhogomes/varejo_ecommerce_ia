"""Ponto de Entrada Principal: RetailSense AI Backend.

Executa o servidor FastAPI com documentação viva interativa Scalar (/docs)
e arquivos estáticos do frontend compilado na raiz.
"""

import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()


def main():
    """Inicia o servidor de aplicação Uvicorn."""
    # Porta padrão 8080 para evitar conflito com serviços Docker/WSL na porta 8000
    port = int(os.getenv("PORT", 8080))
    print("=" * 65)
    print("🚀 Iniciando RetailSense — Analytics & Customer Experience")
    print(f"👉 Interface Web & API: http://127.0.0.1:{port} (ou http://localhost:{port})")
    print(f"👉 Documentação Scalar: http://127.0.0.1:{port}/docs")
    print(f"👉 Métricas Prometheus: http://127.0.0.1:{port}/metrics")
    print("=" * 65)

    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
