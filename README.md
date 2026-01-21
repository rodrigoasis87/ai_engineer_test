# 🤖 AI Agent Orchestrator (Microservices Architecture)

Este proyecto es una prueba técnica de ingeniería de IA que implementa una arquitectura de microservicios dockerizada para orquestar múltiples agentes inteligentes.

## 🚀 Funcionalidades

El sistema consta de 3 agentes especializados orquestados con **LangGraph**:

1.  **RAG Documental (Ejercicio 1):**
    * Ingesta y búsqueda semántica en documentos técnicos PDF.
    * Stack: LangChain, ChromaDB/FAISS (Vector Store), Google Gemini Embeddings.
2.  **Agente de Triaje de Incidentes (Ejercicio 2):**
    * Clasificación automática de tickets (Técnico, Usuario, General) usando LLMs estructurados.
    * Generación de respuestas automáticas o JSON de derivación.
3.  **Agente ReAct Conversacional (Ejercicio 3):**
    * Agente con capacidad de razonamiento y uso de herramientas (Calculadora, Datetime).
    * **Persistencia de Memoria:** Mantiene el contexto de la conversación por usuario (`thread_id`).

## 🛠️ Tech Stack

* **Backend:** Python 3.11, FastAPI, LangGraph, LangChain.
* **LLM:** Google Gemini 2.5 Flash & Flash-Lite via Google GenAI SDK.
* **Frontend:** Streamlit (Interfaz reactiva con gestión de estado).
* **Infraestructura:** Docker & Docker Compose (Hot-reloading activado para desarrollo).
* **Package Manager:** `uv` (para gestión eficiente de dependencias).

## 📋 Pre-requisitos

* Docker & Docker Compose instalados.
* Una API Key de Google Gemini (`GOOGLE_API_KEY`).

## ⚡ Cómo ejecutar

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/ai-agent-orchestrator.git](https://github.com/tu-usuario/ai-agent-orchestrator.git)
    cd ai-agent-orchestrator
    ```

2.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` dentro de la carpeta `backend/`:
    ```bash
    # backend/.env
    GOOGLE_API_KEY=tu_api_key_aqui
    ```

3.  **Levantar los servicios:**
    ```bash
    docker compose up --build
    ```

4.  **Acceder a la aplicación:**
    * **Frontend (Streamlit):** [http://localhost:8501](http://localhost:8501)
    * **Backend Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📂 Estructura del Proyecto

```text
├── backend/            # API FastAPI & Lógica de Agentes (LangGraph)
│   ├── app/graphs/     # Definición de Grafos (ReAct, State Machines)
│   ├── app/routers/    # Endpoints REST
│   └── Dockerfile
├── frontend/           # Interfaz de Usuario (Streamlit)
│   └── Dockerfile
└── docker-compose.yml  # Orquestación de servicios