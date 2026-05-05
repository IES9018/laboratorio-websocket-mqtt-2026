"""
Módulo de autenticación básica para WebSocket.
Proporciona funciones para validar credenciales de usuario.
"""

import hashlib
import json
from typing import Optional, Tuple

# Usuarios válidos (en producción, esto debería venir de una base de datos)
# Formato: {"username": "password_hash"}
USUARIOS_VALIDOS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "user": hashlib.sha256("user123".encode()).hexdigest(),
    "invitado": hashlib.sha256("invitado123".encode()).hexdigest(),
}

# Credenciales en texto plano para referencia (solo para desarrollo)
CREDENCIALES = {
    "admin": "admin123",
    "user": "user123",
    "invitado": "invitado123",
}


def verificar_credenciales(username: str, password: str) -> bool:
    """
    Verifica si las credenciales son válidas.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        
    Returns:
        True si las credenciales son válidas, False en caso contrario
    """
    if not username or not password:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return USUARIOS_VALIDOS.get(username) == password_hash


def crear_token_autenticacion(username: str) -> str:
    """
    Crea un token de autenticación simple para el usuario.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        Token de autenticación
    """
    import time
    import secrets
    data = f"{username}:{time.time()}:{secrets.token_hex(8)}"
    return hashlib.sha256(data.encode()).hexdigest()


def parsear_mensaje_autenticacion(mensaje: str) -> Optional[Tuple[str, str]]:
    """
    Parsea un mensaje de autenticación en formato JSON.
    
    Args:
        mensaje: Mensaje JSON con formato {"username": "...", "password": "..."}
        
    Returns:
        Tupla (username, password) si el mensaje es válido, None si no lo es
    """
    try:
        data = json.loads(mensaje)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        if username and password:
            return (username, password)
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


def crear_mensaje_autenticacion(tipo: str, mensaje: str, datos: dict = None) -> str:
    """
    Crea un mensaje de autenticación en formato JSON.
    
    Args:
        tipo: Tipo de mensaje (auth_success, auth_error, auth_required)
        mensaje: Descripción del mensaje
        datos: Datos adicionales opcionales
        
    Returns:
        Mensaje JSON
    """
    data = {
        "tipo": tipo,
        "mensaje": mensaje,
    }
    if datos:
        data.update(datos)
    return json.dumps(data)


def obtener_credenciales_demo() -> dict:
    """
    Retorna las credenciales de demo disponibles.
    
    Returns:
        Diccionario con usuarios y contraseñas
    """
    return CREDENCIALES.copy()