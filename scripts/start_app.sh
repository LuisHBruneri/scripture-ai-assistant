#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "🚀 Iniciando Backend e Banco de Dados..."
if docker-compose up -d --build; then
    echo "✅ Sistema online! API disponível em http://localhost:8001"
else
    echo "❌ Falha ao iniciar o sistema."
    exit 1
fi
