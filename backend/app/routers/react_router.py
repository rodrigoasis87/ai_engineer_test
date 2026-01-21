import time
from typing import Optional, Any, cast
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
import pytz

from app.graphs.react_agent import react_graph, memory, ReactState
from app.core.settings import settings
from app.schemas.react_schemas import ChatRequest, ChatResponse, TimezoneRequest
from app.utils.rate_limiter import check_rate_limit

router = APIRouter(prefix="/react", tags=["Ejercicio 3: Agente ReAct"])


# --- Endpoints ---

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, req: Request):
    # 1. Rate Limiting
    client_ip = req.client.host if req.client else "unknown"
    check_rate_limit(client_ip)
    
    start_time = time.time()
    
    try:
        # 2. Invocación del Agente
        # Configurable: thread_id permite persistencia por usuario
        config: RunnableConfig = {"configurable": {"thread_id": request.thread_id}}
        
        # El input para el grafo debe ser un diccionario con la clave "messages"
        # y una lista de BaseMessage
        inputs: ReactState = {"messages": [HumanMessage(content=request.question)]}
        
        # Ejecutamos el grafo
        response = react_graph.invoke(inputs, config=config)
        result = cast(ReactState, response)
        
        # 3. Extracción de Respuesta
        last_message = result["messages"][-1]
        
        # Corrección: El contenido de Gemini viene como una lista de partes.
        # Extraemos el texto de la primera parte.
        if isinstance(last_message.content, list):
            # Obtenemos el primer elemento
            first_content = last_message.content[0]
        
            # CORRECCIÓN: Verificamos que sea un diccionario antes de usar .get()
            if isinstance(first_content, dict):
                answer_text = first_content.get("text", "")
            else:
                # Si es un string dentro de una lista (raro, pero posible)
                answer_text = str(first_content)
        else:
            answer_text = last_message.content
        
        # 4. Cálculo de Metadata
        execution_time = time.time() - start_time
        token_usage = last_message.response_metadata.get("token_usage", {})
        
        return {
            "answer": answer_text,
            "metadata": {
                "execution_time_seconds": round(execution_time, 2),
                "tokens": token_usage,
                "model": "gemini-2.5-flash",
                "thread_id": request.thread_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/config/timezone")
async def set_agent_timezone(config: TimezoneRequest):
    """Cambia la zona horaria para la herramienta datetime_info."""
    if config.timezone not in pytz.all_timezones:
        raise HTTPException(status_code=400, detail="Zona horaria inválida. Use formato 'Continent/City'")
    
    settings.set_timezone(config.timezone)
    return {"status": "success", "current_timezone": config.timezone}

@router.get("/context/{thread_id}", response_model=list[dict])
async def get_context(thread_id: str):
    """Obtiene el historial de mensajes para un thread_id específico."""
    try:
        # 1. Definimos config con tipado para que Pylance sea feliz
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        
        # 2. Usamos el método oficial del grafo para obtener el 'Snapshot' del estado
        snapshot = react_graph.get_state(config)
        
        # 3. Accedemos a .values (que es tu ReactState dict)
        if not snapshot.values:
            raise HTTPException(status_code=404, detail="No se encontró contexto para este ID.")
        
        # 4. Iteramos sobre snapshot.values["messages"]
        history = [
            {"type": msg.type, "content": msg.content} 
            for msg in snapshot.values.get("messages", [])
        ]
        return history

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/context/{thread_id}")
async def reset_context(thread_id: str):
    """Reinicia la conversación borrando la memoria del thread."""
    try:
        # CORRECCIÓN: MemorySaver es una clase simple, no tiene 'get_checkpointer'.
        # La forma de borrar en esta clase específica es accediendo a su .storage
        
        # Buscamos todas las claves en memoria que pertenezcan a este thread_id
        keys_to_delete = [
            k for k in memory.storage.keys() 
            if k == thread_id or (isinstance(k, tuple) and k[0] == thread_id)
        ]
        
        if not keys_to_delete:
            return {"status": "warning", "message": "No se encontró contexto para borrar."}

        # Borramos físicamente del diccionario en memoria
        for k in keys_to_delete:
            del memory.storage[k]

        return {"status": "success", "message": f"Contexto para '{thread_id}' eliminado."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))