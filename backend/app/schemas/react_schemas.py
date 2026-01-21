from typing import TypedDict, Annotated, Sequence, Any
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# --- 1. Estado del Grafo (Internal State) ---
# Esto es lo que viaja dentro de LangGraph
class ReactState(TypedDict):
    # 'add_messages' es vital: le dice al grafo "no sobrescribas la lista, agrega el nuevo mensaje al final"
    messages: Annotated[Sequence[BaseMessage], add_messages]

# --- 2. Modelos de la API (External Contract) ---
# Esto es lo que valida FastAPI
class ChatRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "Calcula el logaritmo del día de hoy"})
    thread_id: str = Field(default="default_user", description="ID de sesión")

class TimezoneRequest(BaseModel):
    timezone: str = Field(..., json_schema_extra={"example": "America/Argentina/Cordoba"})

class ChatResponse(BaseModel):
    answer: str
    metadata: dict[str, Any]