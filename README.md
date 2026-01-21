# 🤖 AI Agent Orchestrator

Este proyecto es una prueba técnica de ingeniería de IA que implementa una arquitectura de microservicios dockerizada para orquestar múltiples agentes inteligentes. El sistema demuestra la integración de LLMs modernos con lógica de negocio compleja, persistencia de estado y herramientas externas.

## 🚀 Funcionalidades

El sistema consta de 3 agentes especializados orquestados con **LangGraph** y expuestos vía **FastAPI**:

1.  **RAG Documental (Ejercicio 1):**
    * Ingesta y búsqueda semántica eficiente.
    * **Stack:** LangChain, FAISS (Local Vector Store), Google Gemini Embeddings.
    * *Capacidad:* Recuperación precisa de información técnica desde documentos indexados.

2.  **Agente de Triaje de Incidentes (Ejercicio 2):**
    * Clasificación inteligente de tickets (Técnico, Usuario, General) mediante LLMs con salida estructurada (Pydantic).
    * Generación de JSON para derivación automática o respuestas finales al usuario.

3.  **Agente ReAct Conversacional (Ejercicio 3):**
    * Agente autónomo con razonamiento y uso de herramientas (*Tool Calling*).
    * **Herramientas:** Calculadora matemática y Consulta de Fecha/Hora actual.
    * **Persistencia:** Memoria conversacional por sesión (`thread_id`) utilizando `MemorySaver` (Checkpointer).

## 🛠️ Tech Stack

* **Backend:** Python 3.11, FastAPI, LangGraph, LangChain Core.
* **LLM:** Google Gemini 2.5 Flash & Flash-Lite (vía `google-genai` SDK).
* **Frontend:** Streamlit (Interfaz reactiva con gestión de estado de sesión).
* **Infraestructura:** Docker & Docker Compose (Configurado con volúmenes para Hot-Reloading).
* **Gestión de Dependencias:** `uv` (Astral) para entornos virtuales rápidos y reproducibles.

## 📋 Pre-requisitos

* Docker & Docker Compose instalados.
* Una API Key de Google Gemini (`GOOGLE_API_KEY`).

## ⚡ Cómo ejecutar

Sigue estos pasos desde la terminal:

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/rodrigoasis87/ai_engineer_test.git
    cd ai-agent-orchestrator
    ```

2.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` dentro de la carpeta `backend/` con tu clave de API:
    ```bash
    # backend/.env
    GOOGLE_API_KEY=tu_api_key_aqui_sin_comillas
    ```

3.  **Levantar los servicios:**
    Asegúrate de estar en la **carpeta raíz** del proyecto (donde está el `docker-compose.yml`) y ejecuta:
    ```bash
    docker compose up --build
    ```

4.  **Acceder a la aplicación:**
    Una vez que los contenedores estén corriendo:
    * 🖥️ **Frontend (Interfaz Gráfica):** [http://localhost:8501](http://localhost:8501)
    * ⚙️ **Backend (Swagger API Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📂 Estructura del Proyecto

```text
ai-agent-orchestrator/
├── backend/                # Microservicio API (FastAPI)
│   ├── app/
│   │   ├── chains/         # Cadenas de procesamiento (LangChain/LCEL)
│   │   ├── core/           # Configuración (API Keys, Settings)
│   │   ├── graphs/         # Lógica de Agentes (LangGraph)
│   │   ├── routers/        # Endpoints de la API
│   │   ├── schemas/        # Modelos Pydantic (Input/Output)
│   │   ├── services/       # Lógica de RAG y Embeddings
│   │   ├── tools/          # Herramientas personalizadas (Calc, Time)
│   │   └── utils/          # Utilidades (Rate Limiter, Helpers)
│   ├── Dockerfile          # Definición de imagen Backend
│   ├── pyproject.toml      # Definición del proyecto uv
│   └── requirements.txt    # Dependencias congeladas
│
├── frontend/               # Microservicio UI (Streamlit)
│   ├── app.py              # Código de la aplicación web
│   ├── Dockerfile          # Definición de imagen Frontend
│   └── requirements.txt    # Dependencias congeladas
│
├── docker-compose.yml      # Orquestación y Redes
└── README.md               # Documentación
```

## 🛡️ Notas de Seguridad y Desarrollo

* **Hot-Reloading:** El entorno Docker está configurado con *Bind Mounts*. Cualquier cambio que hagas en el código local (backend o frontend) se reflejará inmediatamente en el contenedor sin necesidad de reconstruir.
* **API Keys:** Las claves no se "queman" en la imagen de Docker; se inyectan en tiempo de ejecución desde el archivo `.env` local para mayor seguridad.