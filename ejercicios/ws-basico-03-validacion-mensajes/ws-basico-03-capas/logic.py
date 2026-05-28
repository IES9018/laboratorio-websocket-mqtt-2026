# logic.py

def validar_limites_sensor(tipo: str, valor: float) -> bool:
    """
    Reglas de Negocio: Verifica si los valores recibidos 
    están dentro de los parámetros físicos reales.
    """
    limites = {
        "temperatura": {"min": -50, "max": 70},
        "humedad": {"min": 0, "max": 100},
        "presion": {"min": 900, "max": 1100}
    }
    
    config = limites.get(tipo.lower())
    if config:
        # Verifica si el valor está entre el mínimo y máximo permitido
        es_valido = config["min"] <= valor <= config["max"]
        return es_valido
    
    # Si el sensor no está en la lista, permitimos el paso por defecto
    return True