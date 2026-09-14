# =====================================================================
# Script PowerShell de Deploy Automatizado para o Google Cloud Run
# Garante política mandatória de Scale-to-Zero ($0/mês em ociosidade).
# =====================================================================

$ErrorActionPreference = "Stop"

# Carrega chaves do .env caso não estejam nas variáveis de ambiente da sessão
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $varName = $parts[0].Trim()
            $varVal = $parts[1].Trim()
            if (-not [System.Environment]::GetEnvironmentVariable($varName)) {
                [System.Environment]::SetEnvironmentVariable($varName, $varVal)
                $env:$varName = $varVal
            }
        }
    }
}

$ProjectId = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { (gcloud config get-value project) }
$Region = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$ServiceName = "retailsense-ai"
$ImageTag = "gcr.io/$ProjectId/${ServiceName}:latest"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Iniciando Deploy do RetailSense AI no Google Cloud Run" -ForegroundColor Green
Write-Host "Projeto GCP: $ProjectId"
Write-Host "Região:      $Region"
Write-Host "Serviço:     $ServiceName"
Write-Host "Chave Gemini: $(if ($env:GEMINI_API_KEY) { 'Configurada' } else { 'AUSENTE' })"
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Build da imagem conteinerizada via Cloud Build
Write-Host "Enviando build para o Google Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageTag .

# 2. Deploy no Cloud Run com Scale-to-Zero (min-instances = 0)
Write-Host "Implantando servico com min-instances=0 (Scale-to-Zero)..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $ImageTag `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 3 `
    --set-env-vars="GEMINI_API_KEY=$($env:GEMINI_API_KEY),OPENCODE_API_KEY=$($env:OPENCODE_API_KEY)"

$ServiceUrl = (gcloud run services describe $ServiceName --region $Region --format="value(status.url)")

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green
Write-Host "Aplicacao Web e API: $ServiceUrl" -ForegroundColor Cyan
Write-Host "Documentacao Scalar: $ServiceUrl/docs" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
