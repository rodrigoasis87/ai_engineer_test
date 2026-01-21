import os
import streamlit as st
import requests
import json

# --- Configuración de la Página ---
st.set_page_config(
    page_title="AI Agent Monitor",
    page_icon="🤖",
    layout="wide"
)

DEFAULT_API_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# --- Configuración Lateral (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    # Nota: Si usas Docker interno, la URL por defecto suele ser http://backend:8000
    API_URL = st.text_input("URL del Backend", DEFAULT_API_URL)
    USER_ID = st.text_input("ID de Usuario / Thread", "default_user")
    
    st.divider()
    st.markdown("### Estado del Sistema")
    if st.button("Verificar Conexión"):
        try:
            r = requests.get(f"{API_URL}/docs")
            if r.status_code == 200:
                st.success("Backend Online 🟢")
            else:
                st.error(f"Error: {r.status_code}")
        except:
            st.error("Backend Offline 🔴")

st.title("🤖 AI Engineer Challenge: Panel de Control")
st.markdown("Interfaz unificada para interactuar con los 3 ejercicios del challenge.")

# --- Pestañas Principales ---
tab1, tab2, tab3 = st.tabs(["📚 RAG (Documental)", "🚨 Triaje (Incidentes)", "🧠 Agente ReAct (Math)"])

# ==========================================
# TAB 1: RAG (Ejercicio 1)
# ==========================================
with tab1:
    st.header("Consulta Documental Técnica")
    st.info("Este agente busca información en manuales técnicos indexados.")
    
    query_rag = st.text_input("Tu pregunta técnica:", "Cómo configuro la conexión wifi?")
    
    if st.button("Consultar RAG", type="primary"):
        with st.spinner("Buscando en vector store..."):
            try:
                payload = {"question": query_rag}
                response = requests.post(f"{API_URL}/rag/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Respuesta Generada:")
                    st.write(data["answer"])
                    
                    with st.expander("Ver Fuentes y Metadata"):
                        st.json(data)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# ==========================================
# TAB 2: Incident Agent (Ejercicio 2) - CORREGIDO
# ==========================================
with tab2:
    st.header("Clasificación y Triaje Automático")
    st.info("Este agente analiza tickets y determina si son Técnicos, de Usuario o Generales.")
    
    incident_text = st.text_area("Descripción del incidente:", "No puedo entrar a mi cuenta, me olvidé la clave")
    
    if st.button("Analizar Incidente", type="primary"):
        with st.spinner("Analizando y clasificando..."):
            try:
                payload = {"text": incident_text}
                response = requests.post(f"{API_URL}/agent/process", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Análisis Completado")

                    # --- ZONA SEGURA DE RENDERIZADO (FIX) ---
                    # 1. Primero mostramos el JSON crudo en un expander para asegurar que los datos llegaron
                    with st.expander("Ver Respuesta Técnica (JSON Completo)", expanded=False):
                        st.json(data)

                    # 2. Intentamos extraer los datos para la vista bonita con manejo de errores
                    try:
                        # Extraemos valores con valores por defecto por seguridad
                        clasificacion = data.get("classification", "Desconocido")
                        respuesta_texto = data.get("final_response", str(data))

                        # Métricas visuales
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Clasificación", str(clasificacion).upper())
                        with col2:
                            accion = "Derivar a Soporte" if str(clasificacion).lower() != "general" else "Responder Auto"
                            st.metric("Acción Sugerida", accion)
                        
                        # Texto de respuesta (Convertido a string para evitar crash de React)
                        st.subheader("Respuesta Sugerida:")
                        if isinstance(respuesta_texto, (dict, list)):
                            st.info(json.dumps(respuesta_texto, indent=2, ensure_ascii=False))
                        else:
                            st.info(str(respuesta_texto))

                    except Exception as parse_error:
                        st.warning(f"Datos recibidos pero hubo un error visualizando los detalles: {parse_error}")
                    # ----------------------------------------

                else:
                    st.error(f"Error del Servidor {response.status_code}")
                    st.write(response.text)

            except Exception as e:
                st.error(f"Error de conexión o ejecución: {e}")

# ==========================================
# TAB 3: ReAct Agent (Ejercicio 3)
# ==========================================
with tab3:
    st.header("Agente Conversacional con Herramientas")
    st.info(f"Agente matemático con memoria y acceso a herramientas. Thread ID: **{USER_ID}**")
    
    # 1. Botón para borrar memoria
    col_del, col_space = st.columns([1, 4])
    with col_del:
        if st.button("🗑️ Borrar Memoria"):
            try:
                requests.delete(f"{API_URL}/react/context/{USER_ID}")
                st.session_state.messages = [] # Limpiar UI también
                st.success("Memoria reiniciada.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al borrar: {e}")

    # 2. Inicializar historial de chat en Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Intentar cargar historial del backend al inicio
        try:
            hist_resp = requests.get(f"{API_URL}/react/context/{USER_ID}")
            if hist_resp.status_code == 200:
                history_data = hist_resp.json()
                for msg in history_data:
                    # Adaptar formato de LangGraph al de Streamlit
                    if msg.get("type") == "human":
                        role = "user"
                    elif msg.get("type") == "ai":
                        role = "assistant"
                    else:
                        continue # Ignorar mensajes de sistema o herramientas por ahora
                        
                    st.session_state.messages.append({"role": role, "content": msg["content"]})
        except:
            pass # Si falla (ej. 404), empezamos vacío

    # 3. Mostrar mensajes del historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. Input del Chat
    if prompt := st.chat_input("Escribe tu consulta (ej: Calcula logaritmo de hoy)..."):
        # Mostrar mensaje usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Llamar al backend
        with st.chat_message("assistant"):
            with st.spinner("Pensando y calculando..."):
                try:
                    payload = {"question": prompt, "thread_id": USER_ID}
                    response = requests.post(f"{API_URL}/react/chat", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        
                        # Mostrar respuesta
                        st.markdown(answer)
                        
                        # Guardar en historial local
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Mostrar metadata técnica (Tokens, tiempo)
                        with st.expander("Detalles Técnicos (Traza)"):
                            st.json(data.get("metadata", {}))
                    else:
                        st.error(f"Error {response.status_code}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")