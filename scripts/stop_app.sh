#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🛑 Parando serviços..."
docker-compose down
echo "😴 Serviços parados."
