from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field

# Modelo de entrada simple
class AgentInput(BaseModel):
    text: str = Field(..., description="Descripción del incidente reportado por el usuario")

# --- 1. Lo que Gemini nos va a responder (Structured Output) ---
class ClassificationOutput(BaseModel):
    """Estructura estricta para la clasificación del incidente."""
    category: Literal['general', 'technical-issue', 'user-issue'] = Field(
        ..., 
        description="Categoría obligatoria del incidente: 'general', 'technical-issue' o 'user-issue'."
    )
    reason: str = Field(
        ..., 
        description="Justificación breve de la clasificación."
    )

# --- 2. La 'Mochila' del Grafo (State) ---
# Estos son los datos que viajarán a través de los nodos: Análisis -> Derivación -> Respuesta
class AgentState(TypedDict):
    input_text: str          # El mensaje original del usuario
    classification: str      # La categoría detectada ('technical-issue', etc.)
    reason: str              # El motivo detectado
    final_output: str        # La respuesta final que mostraremos al usuario