import time
from fastapi import HTTPException

# Variables globales para el estado del rate limit
# (En producción esto iría en Redis, pero en memoria sirve para el ejercicio)
request_counts = {}
LIMIT_PER_MINUTE = 10

def check_rate_limit(client_ip: str):
    """
    Verifica si una IP ha excedido el límite de solicitudes por minuto.
    Lanza HTTPException 429 si se excede.
    """
    current_time = time.time()
    
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    # Filtramos: mantenemos solo los timestamps de los últimos 60 segundos
    # (Borramos lo viejo)
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < 60]
    
    if len(request_counts[client_ip]) >= LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    # Registramos la nueva solicitud
    request_counts[client_ip].append(current_time)