import math
from datetime import datetime
import pytz
from langchain_core.tools import tool
from app.core.settings import settings

@tool
def datetime_info() -> str:
    """
    Devuelve la fecha y hora actual en formato ISO 8601.
    Usa la zona horaria configurada en el sistema.
    """
    try:
        tz_str = settings.get_timezone()
        tz = pytz.timezone(tz_str)
        now = datetime.now(tz)
        return f"Fecha y hora actual ({tz_str}): {now.isoformat()}"
    except Exception as e:
        return f"Error obteniendo fecha: {str(e)}"

@tool
def math_calculator(expression: str) -> str:
    """
    Calculadora matemática útil para realizar operaciones numéricas.
    Esta herramienta solo acepta números como input.
    Soporta operaciones básicas (+, -, *, /) y funciones avanzadas de la librería math 
    como 'log', 'sin', 'cos', 'sqrt', 'pow', etc.
    Ejemplo: 'math.log(10)' o '20 ** 2'.
    """
    try:
        # Por seguridad, limitamos el entorno de ejecución
        # Solo permitimos el módulo 'math'
        allowed_globals = {"__builtins__": None, "math": math}
        
        # Evaluamos la expresión matemática
        result = eval(expression, allowed_globals)
        return str(result)
    except Exception as e:
        return f"Error matemático: {str(e)}. Asegúrate de usar sintaxis Python válida (ej: math.log(10))"

@tool
def convert_date_to_timestamp(date_string: str) -> str:
    """
    Convierte una fecha/hora en formato ISO 8601 a un timestamp numérico de Unix.
    Útil para convertir fechas a un formato numérico antes de usarlas en la calculadora.
    El timestamp es el número de segundos desde 1970-01-01 UTC.
    """
    try:
        # datetime.fromisoformat puede manejar la mayoría de los formatos ISO 8601
        dt_object = datetime.fromisoformat(date_string)
        timestamp = dt_object.timestamp()
        return str(timestamp)
    except ValueError as e:
        return f"Error de conversión: {e}. Asegúrate que el formato sea ISO 8601."
    except Exception as e:
        return f"Error inesperado: {str(e)}"

# Lista de herramientas para exportar
tools = [datetime_info, math_calculator, convert_date_to_timestamp]