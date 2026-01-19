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
    session_id: str = "default_session"

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

import json
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    if not rag_service:
         raise HTTPException(status_code=503, detail="RAG Service not initialized")
    
    async def event_generator():
        try:
            # Pass session_id to get_answer_stream
            async for chunk in rag_service.get_answer_stream(request.query, request.session_id):
                # Send as Server-Sent Events (SSE) data: JSON\n\n
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error(f"Error in stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "ok"}
