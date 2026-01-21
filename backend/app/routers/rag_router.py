from fastapi import APIRouter, HTTPException
from app.schemas.rag_schemas import RAGQueryRequest, RAGResponse
from app.chains.rag_chain import rag_processing_chain
import logging

router = APIRouter(prefix="/rag", tags=["Ejercicio 1"])
logger = logging.getLogger(__name__)

@router.post("/query", response_model=RAGResponse)
async def query_technical_docs(request: RAGQueryRequest):
    try:
        # Ejecutamos la cadena
        result_text = rag_processing_chain.invoke({"question": request.question})
        
        # Detectamos si fue un fallback simple
        is_fallback = "no encuentro información" in result_text
        
        return RAGResponse(
            answer=result_text,
            context_found=not is_fallback,
            sources=["Manual Interno"] if not is_fallback else []
        )

    except Exception as e:
        logger.error(f"Error RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))