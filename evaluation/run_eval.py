
import os
import sys
import asyncio
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.run_config import RunConfig
import logging

# Suppress verbose API logs
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Add backend to path to import RAGService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.services.rag_service import RAGService
from backend.core.config import settings

# Initialize Google LLM for Ragas (Judge)
judge_llm = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0
)

judge_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=settings.GOOGLE_API_KEY
)

async def main():
    print("Loading RAG Service...")
    rag_service = RAGService()
    
    import argparse
    parser = argparse.ArgumentParser(description="Run RAG Evaluation")
    parser.add_argument("--dataset", type=str, default="evaluation/test_dataset.json", help="Path to the test dataset JSON (relative to backend root)")
    args = parser.parse_args()

    print(f"Loading Test Dataset from: {args.dataset}")
    with open(args.dataset, "r") as f:
        data = json.load(f)
    
    questions = []
    ground_truths = []
    answers = []
    contexts = []
    categories = []

    print(f"Starting Evaluation on {len(data)} questions...")
    
    # Generate Answers
    import time
    for i, item in enumerate(data):
        print(f"[{i+1}/{len(data)}] Processing: {item['question']}")
        
        try:
            # Get Answer from Agent
            response = rag_service.get_answer(item['question'])
            
            questions.append(item['question'])
            ground_truths.append(item['ground_truth'])
            categories.append(item['category'])
            answers.append(response['answer'])
            # Use the new context_list we added to RAGService
            contexts.append(response.get('context_list', []))
            
            # Sleep to avoid hitting Gemini Free Tier Rate Limits (15 RPM)
            time.sleep(5)
            
        except Exception as e:
            print(f"Error processing question '{item['question']}': {e}")
            questions.append(item['question'])
            ground_truths.append(item['ground_truth'])
            categories.append(item['category'])
            answers.append("Error generating answer")
            contexts.append([])

    # Create HuggingFace Dataset for Ragas
    dataset_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(dataset_dict)

    print("Running Ragas Metrics (Faithfulness, Relevancy, Precision)...")
    # Using Gemini as the Judge
    # Limit workers to 1 to avoid hitting Gemini Free Tier Rate Limits during evaluation
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
        ],
        llm=judge_llm, 
        embeddings=judge_embeddings,
        raise_exceptions=False,
        #run_config=RunConfig(max_workers=1, timeout=600)
    )

    print("Evaluation Complete!")
    print(results)
    
    # Save CSV
    df = results.to_pandas()
    print(f"Dataframe columns: {df.columns}")
    df['category'] = categories # Add category back to DF
    df.to_csv("evaluation/results.csv", index=False)
    print("Results saved to evaluation/results.csv")

    # Generate Markdown Report for Qualitative Analysis (Thesis Requirement)
    generate_markdown_report(df)

def generate_markdown_report(df):
    report_path = "evaluation/validation_report.md"
    with open(report_path, "w") as f:
        f.write("# Relatório de Validação - Agente Teológico (TCC)\n\n")
        f.write("> **Instruções**: Para cada questão, avalie a resposta do Agente com base nos critérios:\n")
        f.write("> 1. **Precisão Factual/Teológica** (1-5)\n")
        f.write("> 2. **Clareza e Acessibilidade** (1-5)\n")
        f.write("> 3. **Profundidade** (1-5)\n")
        f.write("> 4. **Relevância do Contexto** (1-5)\n\n")
        
        f.write("## Resumo das Métricas Automáticas (RAGAS)\n")
        f.write(f"- **Média Fidelidade (Faithfulness)**: {df['faithfulness'].mean():.2f}\n")
        f.write(f"- **Média Relevância (Answer Relevancy)**: {df['answer_relevancy'].mean():.2f}\n")
        f.write(f"- **Média Precisão Contexto (Context Precision)**: {df['context_precision'].mean():.2f}\n\n")
        
        f.write("---\n\n")
        
        for index, row in df.iterrows():
            f.write(f"### Q{index+1}: {row['user_input']}\n")
            f.write(f"**Categoria**: {row['category']}\n\n")
            
            f.write("#### 🤖 Resposta do Agente:\n")
            f.write(f"{row['response']}\n\n")
            
            f.write("#### 📖 Contexto Recuperado (Principais Trechos):\n")
            for i, ctx in enumerate(row['retrieved_contexts'][:3]): # Limit to top 3 for readability
                f.write(f"> {ctx[:300]}...\n\n")
            
            f.write("#### 📊 Métricas RAGAS:\n")
            f.write(f"- Faithfulness: {row['faithfulness']:.2f}\n")
            f.write(f"- Answer Relevancy: {row['answer_relevancy']:.2f}\n")
            f.write(f"- Context Precision: {row['context_precision']:.2f}\n\n")
            
            f.write("#### 👨‍🏫 Avaliação Qualitativa (Manual):\n")
            f.write("| Critério | Nota (1-5) | Comentários |\n")
            f.write("| :--- | :---: | :--- |\n")
            f.write("| Precisão Factual | | |\n")
            f.write("| Clareza | | |\n")
            f.write("| Profundidade | | |\n")
            f.write("| Relevância Contexto | | |\n\n")
            f.write("---\n\n")
            
    print(f"Report generated at {report_path}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
