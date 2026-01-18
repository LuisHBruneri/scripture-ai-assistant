from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.services.rag_service import RAGService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Theological AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

# Initialize RAG Service (Lazy loading or at startup)
rag_service = None

@app.on_event("startup")
async def startup_event():
    global rag_service
    try:
        rag_service = RAGService()
        logger.info("RAG Service initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Service: {e}")
        # In a real app, you might want to stop startup or retry

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    if not rag_service:
         raise HTTPException(status_code=503, detail="RAG Service not initialized")
    
    try:
        result = rag_service.get_answer(request.query)
        return QueryResponse(answer=result["answer"], sources=result["source_documents"])
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/health")
def health_check():
    return {"status": "ok"}
