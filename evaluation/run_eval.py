import asyncio
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from backend.services.rag_service import RAGService
import os

# Set Env to avoid warnings if possible, though RAGAS needs OpenAI by default usually.
# We will configure it to use Gemini if RAGAS supports it easily, otherwise it defaults to OpenAI.
# For this PoC, we will assume the user might need an OPENAI_KEY for RAGAS *metrics* 
# OR we try to pass the Gemini LLM to RAGAS (advanced).
# For simplicity in this step, let's write the scaffolding.

async def generate_responses(rag_service, questions):
    answers = []
    contexts = []
    
    print(f"Generating answers for {len(questions)} questions...")
    for q in questions:
        # We use the sync-like wrapper or just await the stream
        # Ideally we want the full answer + contexts
        
        # We'll use the 'get_answer' method if available or simulate it
        # Let's inspect RAGService again or add a helper method there.
        # For now, we assume we can get it.
        try:
             # We need a synchronous-like return for evaluation data construction
             # We will re-implement a simple invoke here or use the existing one
             docs = await rag_service.retriever.ainvoke(q)
             context_text = [doc.page_content for doc in docs]
             
             # Generation
             chain = rag_service.qa_prompt | rag_service.llm
             response = await chain.ainvoke({
                 "context": "\n".join(context_text), 
                 "chat_history": [], 
                 "input": q
             })
             
             answers.append(response.content)
             contexts.append(context_text) # Ragas expects list of strings
             print(f"Analyzed: {q[:30]}...")
        except Exception as e:
            print(f"Error on {q}: {e}")
            answers.append("Error")
            contexts.append([])

    return answers, contexts

async def main():
    print("Loading Dataset...")
    with open("evaluation/test_dataset.json", "r") as f:
        data = json.load(f)
        
    questions = [item["question"] for item in data]
    ground_truths = [item["ground_truth"] for item in data] # Ragas expects list of strings for single reference
    
    print("Initializing RAG Service...")
    rag = RAGService()
    
    print("Running Inference...")
    answers, contexts = await generate_responses(rag, questions)
    
    # Prepare Dataset for RAGAS
    eval_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(eval_dict)
    
    print("\n--- Starting RAGAS Evaluation ---")
    print("Note: RAGAS metrics heavily rely on an LLM Judge.")
    print("Using the default LLM (usually OpenAI) or configured Gemini.")
    
    # Configure RAGAS to use Gemini
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    
    # Wrap our Gemini LLM and Embeddings
    ragas_llm = LangchainLLMWrapper(rag.llm)
    ragas_embeddings = LangchainEmbeddingsWrapper(rag.embeddings)
    
    # Inject into metrics
    # New Ragas versions prefer passing llm/embeddings to 'evaluate' or using specific init
    
    try:
        results = evaluate(
            dataset = dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
            ],
            llm=ragas_llm, 
            embeddings=ragas_embeddings 
        )
        
        print("\n\n=== RESULTS ===")
        print(results)
        
        df = results.to_pandas()
        df.to_csv("evaluation/results.csv", index=False)
        print("Detailed results saved to evaluation/results.csv")
        
    except Exception as e:
        print(f"\nEvaluation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
