#!/usr/bin/env bash
# =====================================================================
# Script de Deploy Automatizado para o Google Cloud Run (Scale-to-Zero)
# Garante custo $0/mês quando a aplicação estiver ociosa.
# =====================================================================

set -euo pipefail

# Variáveis Configuráveis do Projeto
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="retailsense-ai"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "=========================================================="
echo "🚀 Iniciando Deploy do RetailSense AI no Google Cloud Run"
echo "Projeto GCP: ${PROJECT_ID}"
echo "Região:      ${REGION}"
echo "Serviço:     ${SERVICE_NAME}"
echo "=========================================================="

# 1. Build da Imagem Multi-Stage usando o Cloud Build
echo "📦 Construindo imagem conteinerizada via Cloud Build..."
gcloud builds submit --tag "${IMAGE_TAG}" .

# 2. Deploy no Cloud Run com política rígida de Scale-to-Zero
echo "☁️ Realizando deploy no Cloud Run com min-instances=0..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_TAG}" \
    --platform managed \
    --region "${REGION}" \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --set-env-vars="GEMINI_API_KEY=${GEMINI_API_KEY:-},OPENCODE_API_KEY=${OPENCODE_API_KEY:-}"

echo "=========================================================="
echo "✅ Deploy concluído com sucesso!"
echo "URL do serviço:"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)"
echo "Documentação Scalar:"
echo "$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)")/docs"
echo "=========================================================="
