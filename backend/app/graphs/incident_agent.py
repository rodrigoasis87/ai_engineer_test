from typing import cast
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Importamos los esquemas
from app.schemas.graph_schemas import AgentState, ClassificationOutput
from app.core.config import GOOGLE_API_KEY

# --- Configuración ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)
# Al usar with_structured_output, LangChain intentará devolver un objeto Pydantic
structured_llm = llm.with_structured_output(ClassificationOutput)

# --- Nodos ---

def node_analysis(state: AgentState):
    print("--- 🧠 Nodo Análisis ---")
    
    # PROMPT REAL Y COMPLETO
    system_prompt = """Eres un sistema experto de triaje y clasificación de tickets para una empresa de software.
    Tu trabajo es analizar el mensaje de entrada y asignarle una de las siguientes categorías estrictas:

    1. 'technical-issue': Úsalo cuando el usuario reporte errores de código, fallos del servidor (500, 404), bugs visuales o comportamientos inesperados del software.
    2. 'user-issue': Úsalo cuando el usuario tenga problemas de acceso, olvido de contraseñas, dudas sobre facturación, o preguntas sobre cómo usar una funcionalidad (errores humanos).
    3. 'general': Úsalo para saludos, preguntas irrelevantes, spam o temas que no requieren soporte.

    Tu 'reason' debe ser una frase corta y explicativa en español justificando tu decisión."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input_text}"), 
    ])
    
    chain = prompt | structured_llm
    
    # TRUCO PARA PYLANCE: Forzamos el tipado de la variable 'result'
    response = chain.invoke({"input_text": state["input_text"]})
    result = cast(ClassificationOutput, response)
    
    return {
        "classification": result.category, 
        "reason": result.reason
    }

def node_derivation(state: AgentState):
    # AgentState es un TypedDict, así que AQUÍ usamos CORCHETES ["..."]
    # Si intentas usar state.classification dará error.
    category = state["classification"]
    print(f"--- 🔀 Nodo Derivación: {category} ---")
    
    if category == "technical-issue":
        destination = "COLA_INGENIERIA"
        priority = "ALTA"
    elif category == "user-issue":
        destination = "ATENCION_CLIENTE"
        priority = "MEDIA"
    else:
        destination = "AUTO_RESPUESTA"
        priority = "BAJA"
        
    new_reason = f"{state['reason']} -> Derivado a {destination} ({priority})"
    
    return {"reason": new_reason}

def node_response(state: AgentState):
    print("--- 📝 Nodo Respuesta ---")
    
    # Nuevamente, AgentState usa corchetes
    classification = state["classification"]
    reason = state["reason"]
    
    final_msg = (
        f"🛡️ REPORTE 🛡️\n"
        f"Área: {classification.upper()}\n"
        f"Detalle: {reason}"
    )
    
    return {"final_output": final_msg}

# --- Grafo ---
def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("analisis", node_analysis)
    workflow.add_node("derivacion", node_derivation)
    workflow.add_node("respuesta", node_response)

    workflow.set_entry_point("analisis")
    workflow.add_edge("analisis", "derivacion")
    workflow.add_edge("derivacion", "respuesta")
    workflow.add_edge("respuesta", END)

    return workflow.compile()

incident_graph = build_agent_graph()