from pydantic import BaseModel, Field
from typing import List

class RAGQueryRequest(BaseModel):
    question: str = Field(..., description="La pregunta técnica del usuario")

class RAGResponse(BaseModel):
    answer: str = Field(..., description="Respuesta generada por el LLM o mensaje de fallback")
    context_found: bool = Field(..., description="Indica si se encontró información relevante en los docs")
    sources: List[str] = Field(default=[], description="Fuentes utilizadas")