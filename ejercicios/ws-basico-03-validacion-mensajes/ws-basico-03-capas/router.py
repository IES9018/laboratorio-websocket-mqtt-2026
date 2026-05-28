# router.py
import json
import logging
from logic import validar_limites_sensor

logger = logging.getLogger("AppLayer")

def procesar_solicitud(mensaje_crudo: str) -> dict:
    """
    Capa de Aplicación: Orquestación y validación de formato.
    """
    try:
        # 1. Intento convertir el texto a diccionario
        data = json.loads(mensaje_crudo)
        
        # 2. Validación de estructura (¿Vienen los campos que espero?)
        if "tipo" not in data or "valor" not in data:
            return {"status": "error", "msg": "Esquema inválido: se requiere 'tipo' y 'valor'"}

        # 3. Conversión de tipos
        tipo_sensor = str(data["tipo"])
        valor_sensor = float(data["valor"])

        # 4. Llamada a la Capa de Dominio
        if validar_limites_sensor(tipo_sensor, valor_sensor):
            return {
                "status": "success", 
                "msg": f"Lectura de {tipo_sensor} procesada correctamente",
                "data": {"tipo": tipo_sensor, "valor": valor_sensor}
            }
        else:
            return {
                "status": "error", 
                "msg": f"Valor fuera de rango para el sensor {tipo_sensor}"
            }

    except json.JSONDecodeError:
        return {"status": "error", "msg": "El mensaje no es un JSON válido"}
    except ValueError:
        return {"status": "error", "msg": "El campo 'valor' debe ser un número"}
    except Exception as e:
        logger.error(f"Error inesperado en AppLayer: {e}")
        return {"status": "error", "msg": "Error interno al procesar el mensaje"}