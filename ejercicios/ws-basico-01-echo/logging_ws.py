"""
Módulo de logging estructurado para WebSocket.
Proporciona logs con nivel INFO/ERROR en formato JSON.
"""

import json
import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pathlib import Path


class NivelLog(Enum):
    """Niveles de logging disponibles."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class FormatoLog(Enum):
    """Formatos de salida disponibles."""
    JSON = "json"
    TEXTO = "texto"
    SIMPLE = "simple"


class LoggeadorEstructurado:
    """Loggeador con salida estructurada para WebSocket."""
    
    def __init__(
        self,
        nombre: str = "websocket",
        nivel: NivelLog = NivelLog.INFO,
        formato: FormatoLog = FormatoLog.JSON,
        archivo: Optional[str] = None
    ):
        self.nombre = nombre
        self.nivel = nivel
        self.formato = formato
        self.archivo = archivo
        self._contador_eventos = {
            "conexiones": 0,
            "desconexiones": 0,
            "mensajes": 0,
            "errores": 0,
            "auth_exitosa": 0,
            "auth_fallida": 0,
        }
        
        # Configurar logging de Python
        self._logger = logging.getLogger(nombre)
        self._logger.setLevel(nivel.value)
        
        # Limpiar handlers existentes
        self._logger.handlers.clear()
        
        # Agregar handler de consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(nivel.value)
        
        if formato == FormatoLog.JSON:
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # Agregar handler de archivo si se especifica
        if archivo:
            self._agregar_handler_archivo(archivo, formato)
    
    def _agregar_handler_archivo(self, ruta: str, formato: FormatoLog):
        """Agrega un handler para escribir a archivo."""
        try:
            path = Path(ruta)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(ruta, encoding='utf-8')
            file_handler.setLevel(self.nivel.value)
            
            if formato == FormatoLog.JSON:
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception as e:
            self._logger.error(f"No se pudo crear archivo de log: {e}")
    
    def _crear_entrada_log(
        self,
        nivel: str,
        mensaje: str,
        contexto: Optional[Dict[str, Any]] = None
    ) -> str:
        """Crea una entrada de log estructurada."""
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "nivel": nivel,
            "servicio": self.nombre,
            "mensaje": mensaje,
        }
        
        if contexto:
            entrada["contexto"] = contexto
        
        if self.formato == FormatoLog.JSON:
            return json.dumps(entrada, ensure_ascii=False)
        else:
            return json.dumps(entrada, ensure_ascii=False)
    
    def debug(self, mensaje: str, **contexto):
        """Log a nivel DEBUG."""
        self._logger.debug(self._crear_entrada_log("DEBUG", mensaje, contexto))
    
    def info(self, mensaje: str, **contexto):
        """Log a nivel INFO."""
        self._contador_eventos["mensajes"] += 1
        self._logger.info(self._crear_entrada_log("INFO", mensaje, contexto))
    
    def warning(self, mensaje: str, **contexto):
        """Log a nivel WARNING."""
        self._logger.warning(self._crear_entrada_log("WARNING", mensaje, contexto))
    
    def error(self, mensaje: str, **contexto):
        """Log a nivel ERROR."""
        self._contador_eventos["errores"] += 1
        self._logger.error(self._crear_entrada_log("ERROR", mensaje, contexto))
    
    def critical(self, mensaje: str, **contexto):
        """Log a nivel CRITICAL."""
        self._contador_eventos["errores"] += 1
        self._logger.critical(self._crear_entrada_log("CRITICAL", mensaje, contexto))
    
    # Métodos específicos para WebSocket
    
    def conexion_entrante(self, cliente_id: str, ip: str = "desconocido"):
        """Log de nueva conexión."""
        self._contador_eventos["conexiones"] += 1
        self.info(
            f"Cliente conectado: {cliente_id}",
            tipo_evento="conexion",
            cliente_id=cliente_id,
            ip=ip,
            accion="conectar"
        )
    
    def conexion_saliente(self, cliente_id: str, motivo: str = ""):
        """Log de desconexión."""
        self._contador_eventos["desconexiones"] += 1
        self.info(
            f"Cliente desconectado: {cliente_id}",
            tipo_evento="desconexion",
            cliente_id=cliente_id,
            motivo=motivo,
            accion="desconectar"
        )
    
    def autenticacion_exitosa(self, cliente_id: str, usuario: str):
        """Log de autenticación exitosa."""
        self._contador_eventos["auth_exitosa"] += 1
        self.info(
            f"Autenticación exitosa para usuario: {usuario}",
            tipo_evento="autenticacion",
            cliente_id=cliente_id,
            usuario=usuario,
            resultado="exito"
        )
    
    def autenticacion_fallida(self, cliente_id: str, motivo: str = "credenciales inválidas"):
        """Log de autenticación fallida."""
        self._contador_eventos["auth_fallida"] += 1
        self.warning(
            f"Autenticación fallida: {motivo}",
            tipo_evento="autenticacion",
            cliente_id=cliente_id,
            motivo=motivo,
            resultado="fallo"
        )
    
    def mensaje_recibido(self, cliente_id: str, tipo: str, tamano: int):
        """Log de mensaje recibido."""
        self.info(
            f"Mensaje recibido de tipo '{tipo}'",
            tipo_evento="mensaje",
            cliente_id=cliente_id,
            tipo_mensaje=tipo,
            tamano=tamano,
            accion="recibir"
        )
    
    def mensaje_enviado(self, cliente_id: str, tipo: str, tamano: int):
        """Log de mensaje enviado."""
        self.info(
            f"Mensaje enviado de tipo '{tipo}'",
            tipo_evento="mensaje",
            cliente_id=cliente_id,
            tipo_mensaje=tipo,
            tamano=tamano,
            accion="enviar"
        )
    
    def error_conexion(self, cliente_id: str, error: str):
        """Log de error en conexión."""
        self.error(
            f"Error en conexión: {error}",
            tipo_evento="error",
            cliente_id=cliente_id,
            error=error,
            accion="error_conexion"
        )
    
    def validacion_fallida(self, cliente_id: str, errores: list):
        """Log de validación fallida."""
        self.warning(
            f"Validación fallida: {len(errores)} errores",
            tipo_evento="validacion",
            cliente_id=cliente_id,
            errores=errores,
            resultado="fallo"
        )
    
    def obtener_metricas(self) -> Dict[str, int]:
        """Retorna las métricas actuales del loggeador."""
        return self._contador_eventos.copy()
    
    def reiniciar_metricas(self):
        """Reinicia los contadores de eventos."""
        for clave in self._contador_eventos:
            self._contador_eventos[clave] = 0


# Instancias preconfiguradas para cada servidor
def crear_loggeador(nombre: str, nivel: NivelLog = NivelLog.INFO) -> LoggeadorEstructurado:
    """Factory para crear loggeadores preconfigurados."""
    return LoggeadorEstructurado(
        nombre=nombre,
        nivel=nivel,
        formato=FormatoLog.JSON,
        archivo=None
    )


# Loggeador global para importar
loggeador = crear_loggeador("websocket-server")