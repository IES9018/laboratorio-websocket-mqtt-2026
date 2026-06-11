import asyncio
import json
import sys
import os
from datetime import datetime
from websockets import serve

# Agregar el directorio actual al path para importar auth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth import verificar_credenciales, parsear_mensaje_autenticacion, crear_mensaje_autenticacion, crear_token_autenticacion
from logging_ws import crear_loggeador, NivelLog

# Crear loggeador estructurado
log = crear_loggeador("ws-validacion", NivelLog.INFO)

# Capa de Dominio: Modelos y datos
class Mensaje:
    def __init__(self, usuario, mensaje, tipo="mensaje", timestamp=None):
        self.usuario = usuario
        self.mensaje = mensaje
        self.tipo = tipo
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            "usuario": self.usuario,
            "mensaje": self.mensaje,
            "tipo": self.tipo,
            "timestamp": self.timestamp.isoformat()
        }

HISTORIAL = []
usuarios_autenticados = {}

# Capa de Aplicación: Lógica de negocio
class Aplicacion:
    @staticmethod
    def validar_mensaje(data):
        try:
            usuario = str(data.get("usuario", "")).strip()
            mensaje = str(data.get("mensaje", "")).strip()
            tipo = str(data.get("tipo", "mensaje")).strip()

            if not usuario:
                raise ValueError("Campo 'usuario' obligatorio")
            if not mensaje:
                raise ValueError("Campo 'mensaje' obligatorio")
            if len(mensaje) > 120:
                raise ValueError("Mensaje demasiado largo (max 120)")
            if tipo not in ["mensaje", "comando"]:
                raise ValueError("Tipo invalido: debe ser 'mensaje' o 'comando'")

            return Mensaje(usuario, mensaje, tipo)
        except Exception as e:
            raise ValueError(f"Error de validacion: {str(e)}")

    @staticmethod
    def procesar_comando(mensaje):
        if mensaje.tipo == "comando" and mensaje.mensaje.lower() == "historial":
            return {"tipo": "respuesta", "data": [m.to_dict() for m in HISTORIAL]}
        return None

    @staticmethod
    def guardar_historial(mensaje):
        HISTORIAL.append(mensaje)
        log.info(
            f"Mensaje guardado en historial",
            tipo_evento="historial",
            usuario=mensaje.usuario,
            mensaje=mensaje.mensaje
        )

# Capa de Transporte: WebSocket handler con autenticación
async def handler(websocket):
    cliente_id = id(websocket)
    log.conexion_entrante(cliente_id, "localhost")
    
    # Solicitar autenticación
    await websocket.send(crear_mensaje_autenticacion(
        "auth_required",
        "Autenticarse con JSON: {\"username\": \"...\", \"password\": \"...\"}"
    ))
    
    try:
        auth_message = await asyncio.wait_for(websocket.recv(), timeout=30)
        credenciales = parsear_mensaje_autenticacion(auth_message)
        
        if credenciales is None:
            await websocket.send(crear_mensaje_autenticacion("auth_error", "Formato inválido"))
            await websocket.close(1008, "Auth fallida")
            log.autenticacion_fallida(cliente_id, "formato inválido")
            return
            
        username, password = credenciales
        
        if not verificar_credenciales(username, password):
            await websocket.send(crear_mensaje_autenticacion("auth_error", "Credenciales inválidas"))
            await websocket.close(1008, "Auth fallida")
            log.autenticacion_fallida(cliente_id, "credenciales incorrectas")
            return
        
        token = crear_token_autenticacion(username)
        usuarios_autenticados[websocket] = {"username": username, "token": token}
        
        await websocket.send(crear_mensaje_autenticacion(
            "auth_success",
            f"Bienvenido {username}!",
            {"token": token, "username": username}
        ))
        log.autenticacion_exitosa(cliente_id, username)
        
    except asyncio.TimeoutError:
        await websocket.send(crear_mensaje_autenticacion("auth_error", "Timeout de autenticación"))
        await websocket.close(1008, "Timeout")
        log.autenticacion_fallida(cliente_id, "timeout")
        return
    except Exception as e:
        log.error(f"Error en auth: {e}", cliente_id=cliente_id, error=str(e))
        await websocket.close(1008, "Error")
        return

    # Mensaje de ayuda después de autenticado
    await websocket.send('Enviar JSON con formato: {"usuario":"ana", "mensaje":"hola", "tipo":"mensaje"} o {"tipo":"comando", "mensaje":"historial"}')

    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
                mensaje = Aplicacion.validar_mensaje(data)
                
                if mensaje.tipo == "comando":
                    respuesta = Aplicacion.procesar_comando(mensaje)
                    if respuesta:
                        await websocket.send(json.dumps(respuesta))
                    else:
                        await websocket.send("Error: Comando desconocido")
                else:
                    Aplicacion.guardar_historial(mensaje)
                    ts = mensaje.timestamp.strftime("%H:%M:%S")
                    await websocket.send(f"[{ts}] OK {mensaje.usuario}: {mensaje.mensaje}")
                
            except ValueError as e:
                logging.warning(f"Error de validacion: {str(e)}")
                await websocket.send(f"Error: {str(e)}")
            except json.JSONDecodeError:
                logging.warning("Mensaje no es JSON valido")
                await websocket.send("Error: El mensaje debe ser JSON valido")
            except Exception as e:
                logging.error(f"Error inesperado: {str(e)}")
                await websocket.send("Error interno del servidor")
    except Exception as e:
        logging.error(f"Error en handler: {str(e)}")
    finally:
        if websocket in usuarios_autenticados:
            usuario = usuarios_autenticados.pop(websocket)
            logging.info(f"Usuario {usuario['username']} desconectado")

async def main() -> None:
    async with serve(handler, "0.0.0.0", 8803):
        logging.info("Servidor WS Validacion con autenticación en ws://localhost:8803")
        logging.info("Credenciales: admin/admin123, user/user123, invitado/invitado123")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
