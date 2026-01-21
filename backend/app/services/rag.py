import logging
from typing import Optional, List
from app.core.config import GOOGLE_API_KEY
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
# NUEVO: Importamos el splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.45 

class RAGService:
    def __init__(self):
        self.vectorstore = None
        
        if not GOOGLE_API_KEY:
            logger.error("Falta la API Key")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="text-embedding-004",
            task_type="retrieval_document" 
        )
        
        # NUEVO: Configuración del Splitter
        # Chunk size: Tamaño del fragmento (caracteres).
        # Chunk overlap: Solapamiento para no perder contexto entre cortes.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Simula la carga y procesamiento de documentos reales."""
        logger.info("Inicializando RAG Avanzado con Gemini...")
        
        # Simulamos documentos "largos" (Raw Text)
        raw_documents = [
            Document(
                page_content="""TITULO: ERROR 503 EN SERVICIOS DE PAGOS.
                Este error suele ocurrir durante eventos de alto tráfico como CyberMonday.
                Causa Principal: Sobrecarga en el balanceador de carga 'LB-Main-01'.
                Diagnóstico: Revisar métricas de latencia en CloudWatch. Si la latencia supera 2s, es bloqueo.
                Solución Protocolar: El protocolo indica escalar horizontalmente los pods de 'payment-service'.
                Se requiere un mínimo de 5 réplicas para soportar la carga base.
                Comando de ejecución: kubectl scale deployment payment-service --replicas=5.
                Una vez estabilizado, monitorear por 30 minutos antes de reducir.""",
                metadata={"source": "manual_incidencias.pdf", "section": "Pagos"}
            ),
            Document(
                page_content="""TITULO: POLITICA DE ROTACIÓN DE API KEYS.
                La seguridad es prioridad en Ithreex.
                Vigencia: Las keys de servicios de terceros (Stripe, SendGrid, AWS) tienen una vida útil máxima de 90 días.
                Procedimiento de Rotación:
                1. Generar nueva key en el dashboard del proveedor.
                2. Actualizar el valor en AWS Secrets Manager (nunca en variables de entorno locales).
                3. Reiniciar los servicios afectados (Rolling Update).
                Alerta: Si una key es commiteada a Git, debe ser revocada inmediatamente.""",
                metadata={"source": "politicas_seguridad.docx", "section": "Credenciales"}
            ),
            Document(
                page_content="""TITULO: CONFIGURACIÓN DE REINTENTOS (RETRIES).
                Para garantizar resiliencia en microservicios distribuídos.
                Estándar: Todos los clientes HTTP internos deben implementar 'Exponential Backoff'.
                Configuración Recomendada: 
                - Max retries: 3 intentos.
                - Base delay: 100ms.
                - Max delay: 2 segundos.
                - Jitter: Habilitado para evitar el problema de 'thundering herd'.
                Librerías: Usar 'Tenacity' en Python o 'Resilience4j' en Java.""",
                metadata={"source": "arquitectura_referencia.md", "section": "Resiliencia"}
            )
        ]

        # PASO CRÍTICO: Splitting
        # Aquí convertimos 3 documentos largos en quizás 5 o 6 chunks manejables
        logger.info("🔪 Fragmentando documentos...")
        split_docs = self.text_splitter.split_documents(raw_documents)
        
        logger.info(f"Generados {len(split_docs)} chunks a partir de {len(raw_documents)} documentos originales.")

        try:
            # Indexamos los fragmentos (chunks), no los documentos enteros
            self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
            logger.info("✅ VectorStore listo.")
        except Exception as e:
            logger.error(f"🔥 Error FAISS: {e}")
            self.vectorstore = None

    def search(self, query: str) -> Optional[str]:
        if not self.vectorstore: return None

        self.embeddings.task_type = "retrieval_query"
        
        # Ahora al buscar, recuperamos fragmentos específicos
        results = self.vectorstore.similarity_search_with_relevance_scores(query, k=2)
        
        valid_docs = []
        for doc, score in results:
            if score >= SIMILARITY_THRESHOLD:
                # Podemos usar la metadata para enriquecer la respuesta si quisiéramos
                source = doc.metadata.get('source', 'desconocido')
                logger.info(f"✅ Match en '{source}' (Score: {score:.3f})")
                valid_docs.append(doc.page_content)
        
        return "\n\n".join(valid_docs) if valid_docs else None

rag_service = RAGService()