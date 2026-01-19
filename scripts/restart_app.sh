#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🔄 Atualizando e Reiniciando serviços..."
docker-compose up -d --build
echo "✅ Serviços atualizados e rodando!"
