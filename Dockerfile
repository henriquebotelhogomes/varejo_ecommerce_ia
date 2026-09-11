# =====================================================================
# ESTÁGIO 1: BUILD DO FRONTEND REACT (VITE + TYPESCRIPT)
# =====================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Instala dependências com cache de camadas
COPY frontend/package*.json ./
RUN npm install

# Copia o código fonte e gera o build estático em /app/frontend/dist
COPY frontend/ ./
RUN npm run build

# =====================================================================
# ESTÁGIO 2: RUNTIME PYTHON / FASTAPI (GOOGLE CLOUD RUN READY)
# =====================================================================
FROM python:3.12-slim AS runner

# Configurações de ambiente de alta performance para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Instala utilitários do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python do projeto
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copia a aplicação do Backend e os dados analíticos (DuckDB / Parquet / SQLite)
COPY src/ ./src/
COPY data/ ./data/
COPY amazon_reviews.db ./amazon_reviews.db

# Copia os arquivos estáticos compilados do Frontend para servir na raiz do FastAPI
COPY --from=frontend-builder /app/frontend/dist ./src/api/static

# Porta padrão de execução do Google Cloud Run
EXPOSE 8080

# Execução assíncrona com Uvicorn
CMD exec uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT}
