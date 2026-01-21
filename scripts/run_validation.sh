#!/bin/bash
echo "=================================================="
echo "   Validation for Theological AI Agent (MBA)      "
echo "=================================================="

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit

echo "1. Ensuring Backend is Running..."
docker-compose up -d backend

echo "2. Starting Evaluation (30 Questions)..."
echo "   NOTE: This may take ~45-60 minutes due to rate limits."
echo "   Logs will be shown below."
echo "=================================================="

docker-compose exec backend python evaluation/run_eval.py "$@"

##Example : ./run_validation.sh --dataset evaluation/test_dataset_poc.json