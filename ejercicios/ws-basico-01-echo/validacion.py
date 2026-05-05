"""
Módulo de validación de esquemas JSON para WebSocket.
Proporciona validación de mensajes contra esquemas definidos.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TipoMensaje(Enum):
    """Tipos de mensaje válidos."""
    MENSAJE = "mensaje"
    COMANDO = "comando"
    AUTH = "auth"
    BROADCAST = "broadcast"
    ECO = "eco"
    ERROR = "error"
    INFO = "info"


@dataclass
class CampoEsquema:
    """Define un campo dentro de un esquema."""
    nombre: str
    tipo: type
    requerido: bool = True
    valor_default: Any = None
    longitud_max: Optional[int] = None
    longitud_min: Optional[int] = None
    valores_permitidos: Optional[List[Any]] = None


@dataclass
class EsquemaMensaje:
    """Define un esquema completo para un tipo de mensaje."""
    tipo: str
    campos: List[CampoEsquema] = field(default_factory=list)
    campos_opcionales: List[CampoEsquema] = field(default_factory=list)
    
    def obtener_todos_campos(self) -> Dict[str, CampoEsquema]:
        """Retorna un diccionario de todos los campos."""
        resultado = {}
        for campo in self.campos + self.campos_opcionales:
            resultado[campo.nombre] = campo
        return resultado


# Esquemas predefinidos
ESQUEMAS = {
    "mensaje": EsquemaMensaje(
        tipo="mensaje",
        campos=[
            CampoEsquema("usuario", str, requerido=True, longitud_min=1, longitud_max=50),
            CampoEsquema("mensaje", str, requerido=True, longitud_min=1, longitud_max=500),
        ],
        campos_opcionales=[
            CampoEsquema("timestamp", str, requerido=False),
        ]
    ),
    "comando": EsquemaMensaje(
        tipo="comando",
        campos=[
            CampoEsquema("comando", str, requerido=True, valores_permitidos=["historial", "usuarios", "ayuda", "status"]),
        ],
        campos_opcionales=[
            CampoEsquema("parametros", str, requerido=False),
        ]
    ),
    "auth": EsquemaMensaje(
        tipo="auth",
        campos=[
            CampoEsquema("username", str, requerido=True, longitud_min=1, longitud_max=50),
            CampoEsquema("password", str, requerido=True, longitud_min=1, longitud_max=100),
        ]
    ),
    "broadcast": EsquemaMensaje(
        tipo="broadcast",
        campos=[
            CampoEsquema("texto", str, requerido=True, longitud_min=1, longitud_max=500),
        ],
        campos_opcionales=[
            CampoEsquema("destinatario", str, requerido=False),
        ]
    ),
}


class ErrorValidacion(Exception):
    """Excepción para errores de validación."""
    def __init__(self, errores: List[str]):
        self.errores = errores
        super().__init__(f"Errores de validación: {', '.join(errores)}")


class ValidadorMensajes:
    """Validador de mensajes JSON contra esquemas."""
    
    def __init__(self, esquemas: Optional[Dict[str, EsquemaMensaje]] = None):
        self.esquemas = esquemas or ESQUEMAS
    
    def validar(self, data: Any, tipo_mensaje: str) -> Tuple[bool, List[str]]:
        """
        Valida un mensaje contra un esquema.
        
        Args:
            data: Datos a validar (diccionario o string JSON)
            tipo_mensaje: Tipo de mensaje a validar
            
        Returns:
            Tupla (es_valido, lista_errores)
        """
        errores = []
        
        # Parsear JSON si es string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                return False, [f"JSON inválido: {str(e)}"]
        
        # Verificar que sea diccionario
        if not isinstance(data, dict):
            return False, ["El mensaje debe ser un objeto JSON"]
        
        # Obtener esquema
        esquema = self.esquemas.get(tipo_mensaje)
        if not esquema:
            return False, [f"Esquema desconocido: {tipo_mensaje}"]
        
        # Validar campos requeridos
        campos_dict = esquema.obtener_todos_campos()
        
        for nombre, campo in campos_dict.items():
            if campo.requerido and nombre not in data:
                errores.append(f"Campo requerido ausente: {nombre}")
        
        # Validar valores
        for nombre, valor in data.items():
            if nombre not in campos_dict:
                errores.append(f"Campo desconocido: {nombre}")
                continue
            
            campo = campos_dict[nombre]
            
            # Validar tipo
            if not isinstance(valor, campo.tipo):
                errores.append(f"Campo '{nombre}': tipo inválido. Esperado {campo.tipo.__name__}, recibido {type(valor).__name__}")
                continue
            
            # Validar longitud (para strings)
            if isinstance(valor, str):
                if campo.longitud_max and len(valor) > campo.longitud_max:
                    errores.append(f"Campo '{nombre}': excede longitud máxima ({campo.longitud_max})")
                if campo.longitud_min and len(valor) < campo.longitud_min:
                    errores.append(f"Campo '{nombre}': no cumple longitud mínima ({campo.longitud_min})")
            
            # Validar valores permitidos
            if campo.valores_permitidos and valor not in campo.valores_permitidos:
                errores.append(f"Campo '{nombre}': valor '{valor}' no está en valores permitidos: {campo.valores_permitidos}")
        
        return len(errores) == 0, errores
    
    def validar_o_error(self, data: Any, tipo_mensaje: str) -> Dict[str, Any]:
        """
        Valida y lanza excepción si hay errores.
        
        Args:
            data: Datos a validar
            tipo_mensaje: Tipo de mensaje
            
        Returns:
            Datos validados
            
        Raises:
            ErrorValidacion: Si hay errores de validación
        """
        es_valido, errores = self.validar(data, tipo_mensaje)
        if not es_valido:
            raise ErrorValidacion(errores)
        return data
    
    def detectar_tipo(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Detecta el tipo de mensaje basándose en los campos presentes.
        
        Args:
            data: Diccionario con los datos
            
        Returns:
            Tipo de mensaje detectado o None
        """
        if "username" in data and "password" in data and len(data) == 2:
            return "auth"
        if "comando" in data:
            return "comando"
        if "usuario" in data and "mensaje" in data:
            return "mensaje"
        if "texto" in data:
            return "broadcast"
        return None


def crear_mensaje_error(codigo: int, descripcion: str, detalles: Any = None) -> str:
    """
    Crea un mensaje de error en formato JSON.
    
    Args:
        codigo: Código de error
        descripcion: Descripción del error
        detalles: Detalles adicionales opcionales
        
    Returns:
        Mensaje JSON
    """
    data = {
        "tipo": "error",
        "codigo": codigo,
        "descripcion": descripcion,
    }
    if detalles:
        data["detalles"] = detalles
    return json.dumps(data)


def crear_mensaje_exito(mensaje: str, datos: Any = None) -> str:
    """
    Crea un mensaje de éxito en formato JSON.
    
    Args:
        mensaje: Mensaje de éxito
        datos: Datos adicionales opcionales
        
    Returns:
        Mensaje JSON
    """
    data = {
        "tipo": "ok",
        "mensaje": mensaje,
    }
    if datos:
        data["data"] = datos
    return json.dumps(data)


def crear_mensaje_info(tipo: str, contenido: Any) -> str:
    """
    Crea un mensaje informativo en formato JSON.
    
    Args:
        tipo: Tipo de información
        contenido: Contenido del mensaje
        
    Returns:
        Mensaje JSON
    """
    return json.dumps({
        "tipo": "info",
        "subtipo": tipo,
        "contenido": contenido,
    })


# Instancia global del validador
validador = ValidadorMensajes()