import logging
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, SystemMessage, AIMessage 
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import GOOGLE_API_KEY
from app.tools.agent_tools import tools
from app.schemas.react_schemas import ReactState

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Modelo (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)
llm_with_tools = llm.bind_tools(tools)

# 3. Nodos del Grafo
tool_node = ToolNode(tools)

# Nodo para llamar al modelo
def call_model(state: ReactState):
    logging.info("---CALLING THE MODEL---")
    
    system_prompt = (
        "Eres un asistente servicial que debe responder a las preguntas del usuario. "
        "No hagas preguntas de seguimiento si puedes encontrar la información tú mismo usando tus herramientas. "
        "Usa tus herramientas siempre que sea posible. "
        "Regla importante: Si una pregunta involucra un cálculo matemático con una fecha (como 'hoy', 'mañana', etc.), "
        "DEBES usar primero la herramienta `datetime_info` para obtener la fecha, y luego DEBES usar la herramienta `convert_date_to_timestamp` sobre el resultado. "
        "Finalmente, usa la calculadora con el timestamp numérico. No extraigas partes de la fecha manualmente."
    )
    
    messages = [SystemMessage(content=system_prompt), *state["messages"]]
    
    logging.info(f"Messages: {messages}")
    response = llm_with_tools.invoke(messages)
    logging.info(f"Model Response: {response}")
    return {"messages": [response]}

# Nodo para invocar herramientas (con logging)
def call_tool_node(state: ReactState):
    logging.info("---CALLING A TOOL---")
    last_message = state["messages"][-1]
    
    # --- CORRECCIÓN 1: Verificamos tipo antes de acceder a la propiedad ---
    # Si NO es un mensaje de IA, O si SIENDO de IA no tiene herramientas, salimos.
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return state
    
    # Aquí Pylance ya sabe que last_message es AIMessage y tiene tool_calls
    logging.info(f"Tool Calls: {last_message.tool_calls}")
    
    tool_response = tool_node.invoke(state)
    logging.info(f"Tool Response: {tool_response}")
    return tool_response


# 4. Lógica Condicional para decidir qué nodo ejecutar
def should_continue(state: ReactState):
    logging.info("---CHECKING FOR NEXT STEP---")
    last_message = state["messages"][-1]
    
    # --- CORRECCIÓN 2: Verificamos tipo antes de acceder a la propiedad ---
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logging.info("Decision: Call a tool.")
        return "call_tool"
    
    logging.info("Decision: End of execution.")
    return END


# 5. Construcción del Grafo
workflow = StateGraph(ReactState)
workflow.add_node("agent", call_model)
workflow.add_node("call_tool", call_tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "call_tool": "call_tool",
        END: END,
    },
)
workflow.add_edge("call_tool", "agent")

# 6. Memoria
memory = MemorySaver()

# 7. Compilación
react_graph = workflow.compile(checkpointer=memory)