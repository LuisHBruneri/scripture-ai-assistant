#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🧐 Inspecionando o Cérebro (Database)..."
docker-compose exec backend python backend/debug/inspect_db.py
