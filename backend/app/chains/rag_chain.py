from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from app.services.rag import rag_service

# Usamos Gemini Flash (rápido y gratis)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

template = """Eres un asistente de soporte técnico.
Responde la pregunta basándote ÚNICAMENTE en el siguiente contexto.
Si el contexto no tiene la respuesta, di explícitamente que no tienes información.

Contexto:
{context}

Pregunta: 
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

def retrieve_context(input_dict):
    return rag_service.search(input_dict["question"])

def route_logic(input_dict):
    """Decide si llamar al LLM o devolver error."""
    if not input_dict.get("context"):
        return "Lo siento, no encuentro información en la base de conocimientos interna sobre este tema."
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(input_dict)

# La cadena final exportable
rag_processing_chain = (
    RunnablePassthrough.assign(context=retrieve_context) 
    | RunnableLambda(route_logic)
)