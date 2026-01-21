import os
from dotenv import load_dotenv

# Carga el .env que está en la misma carpeta backend/
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validación opcional (Muy recomendada)
if not GOOGLE_API_KEY:
    print("⚠️ ADVERTENCIA: No se encontró GOOGLE_API_KEY")