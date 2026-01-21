#!/bin/bash

# Script Facilitador para Treinamento do Agente
# Garante que o container esteja de pé e roda o script mestre

echo "========================================="
echo "   SCRIPTURE AI ASSISTANT - TREINAMENTO  "
echo "========================================="

# 1. Garantir que o backend está rodando
echo "Checking backend container..."
docker-compose up -d backend

# 2. Executar o script de treinamento dentro do container
echo "Starting training script (Enrich + Ingest)..."
docker-compose exec backend python backend/data_ingestion/train_agent.py

echo "========================================="
echo "   FIM DO PROCESSO  "
echo "========================================="
