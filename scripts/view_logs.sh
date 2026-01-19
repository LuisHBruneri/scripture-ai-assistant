#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "📋 Exibindo logs do Backend (Ctrl+C para sair)..."
docker-compose logs -f backend
