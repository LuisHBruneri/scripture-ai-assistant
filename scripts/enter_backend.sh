#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🐚 Entrando no container do backend..."
docker-compose exec backend bash
