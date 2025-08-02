from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import json
import logging
from datetime import datetime
import asyncio

# Import our custom modules
from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_processor import LLMProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackRx 6.0 - Intelligent Query Retrieval System",
    description="LLM-Powered Document Processing and Query System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStore()
llm_processor = LLMProcessor()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]
    processing_time: float
    confidence_scores: List[float]
    sources: List[str]

async def verify_token(authorization: str = Header(None)):
    """Verify the Bearer token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    expected_token = "667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8"
    
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

@app.get("/")
async def root():
    return {
        "message": "HackRx 6.0 - Intelligent Query Retrieval System",
        "status": "running",
        "endpoint": "/hackrx/run",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "components": {
            "document_processor": "ready",
            "vector_store": "ready",
            "llm_processor": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """
    Main endpoint for processing document queries
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing {len(request.questions)} questions for document: {request.documents}")
        
        # Step 1: Process the document
        logger.info("Step 1: Processing document...")
        document_chunks = await document_processor.process_document(request.documents)
        
        # Step 2: Store in vector database
        logger.info("Step 2: Storing in vector database...")
        await vector_store.store_documents(document_chunks)
        
        # Step 3: Process each question
        logger.info("Step 3: Processing questions...")
        answers = []
        confidence_scores = []
        sources = []
        
        for i, question in enumerate(request.questions):
            logger.info(f"Processing question {i+1}/{len(request.questions)}: {question[:50]}...")
            
            # Retrieve relevant chunks
            relevant_chunks = await vector_store.search(question, top_k=5)
            
            # Generate answer using LLM
            answer, confidence, source = await llm_processor.generate_answer(
                question, relevant_chunks, document_chunks
            )
            
            answers.append(answer)
            confidence_scores.append(confidence)
            sources.append(source)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        return QueryResponse(
            answers=answers,
            processing_time=processing_time,
            confidence_scores=confidence_scores,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def api_v1_process_queries(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """
    Alternative endpoint for API v1 compatibility
    """
    return await process_queries(request, token)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 