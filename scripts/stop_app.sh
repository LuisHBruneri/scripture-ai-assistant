#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "🛑 Parando serviços..."
if docker-compose down; then
    echo "😴 Serviços parados."
else
    echo "❌ Falha ao parar serviços."
    exit 1
fi
