#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "🔄 Atualizando e Reiniciando serviços..."
if docker-compose up -d --build; then
    echo "✅ Serviços atualizados e rodando!"
else
    echo "❌ Falha ao reiniciar serviços."
    exit 1
fi
