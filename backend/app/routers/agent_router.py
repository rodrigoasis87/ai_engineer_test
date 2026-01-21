from typing import cast
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graphs.incident_agent import incident_graph
from app.schemas.graph_schemas import AgentState, AgentInput


# Definimos el Router
router = APIRouter(prefix="/agent", tags=["Ejercicio 2"])

@router.post("/process")
async def process_incident(request: AgentInput):
    try:
        # Invocamos el Grafo con el texto del usuario
        # CORRECCIÓN: Inicializamos TODAS las claves del AgentState para que Pylance no se queje.
        # Al ser un TypedDict, espera que la estructura esté completa desde el inicio.
        initial_state: AgentState = {
            "input_text": request.text,
            "classification": "",  # Placeholder vacío
            "reason": "",          # Placeholder vacío
            "final_output": ""     # Placeholder vacío
        }
        
        # .invoke ejecuta todo el flujo (Análisis -> Derivación -> Respuesta)
        # Ahora 'initial_state' cumple perfectamente con el contrato de AgentState
        response = incident_graph.invoke(initial_state)
        result = cast(AgentState, response)
        
        # Devolvemos solo lo que nos interesa del estado final
        return {
            "input": result["input_text"],
            "classification": result["classification"],
            "final_response": result["final_output"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))