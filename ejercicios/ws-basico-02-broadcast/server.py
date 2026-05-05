import asyncio
import sys
import os
import json

# Agregar el directorio actual al path para importar auth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from websockets import serve
from auth import verificar_credenciales, parsear_mensaje_autenticacion, crear_mensaje_autenticacion, crear_token_autenticacion
from validacion import ValidadorMensajes, crear_mensaje_error, ErrorValidacion
from logging_ws import crear_loggeador, NivelLog

# Crear loggeador estructurado
log = crear_loggeador("ws-broadcast", NivelLog.INFO)

# Instancia del validador
validador = ValidadorMensajes()

CLIENTES = set()
usuarios_autenticados = {}


async def broadcast(websocket):
    """Manejador que requiere autenticación antes de permitir mensajes."""
    cliente_id = id(websocket)
    
    # Solicitar autenticación
    await websocket.send(crear_mensaje_autenticacion(
        "auth_required",
        "Por favor, autenticarse con formato JSON: {\"username\": \"usuario\", \"password\": \"contraseña\"}"
    ))
    
    log.conexion_entrante(cliente_id, "localhost")
    
    try:
        auth_message = await asyncio.wait_for(websocket.recv(), timeout=30)
        credenciales = parsear_mensaje_autenticacion(auth_message)
        
        if credenciales is None:
            await websocket.send(crear_mensaje_autenticacion("auth_error", "Formato de autenticación inválido"))
            await websocket.close(1008, "Autenticación fallida")
            log.autenticacion_fallida(cliente_id, "formato inválido")
            return
            
        username, password = credenciales
        
        if not verificar_credenciales(username, password):
            await websocket.send(crear_mensaje_autenticacion("auth_error", "Credenciales inválidas"))
            await websocket.close(1008, "Autenticación fallida")
            log.autenticacion_fallida(cliente_id, "credenciales incorrectas")
            return
        
        # Autenticación exitosa
        token = crear_token_autenticacion(username)
        usuarios_autenticados[websocket] = {"username": username, "token": token}
        CLIENTES.add(websocket)
        
        await websocket.send(crear_mensaje_autenticacion(
            "auth_success",
            f"Bienvenido {username}!",
            {"token": token, "username": username}
        ))
        log.autenticacion_exitosa(cliente_id, username)
        log.info(f"Cliente {username} unido al broadcast", clientes_conectados=len(CLIENTES))
        
    except asyncio.TimeoutError:
        await websocket.send(crear_mensaje_autenticacion("auth_error", "Tiempo de autenticación agotado"))
        await websocket.close(1008, "Timeout")
        log.autenticacion_fallida(cliente_id, "timeout")
        return
    except Exception as e:
        log.error(f"Error en autenticación: {e}", cliente_id=cliente_id, error=str(e))
        await websocket.close(1008, "Error")
        return
    
    # Manejar mensajes broadcast con validación
    try:
        async for message in websocket:
            usuario = usuarios_autenticados[websocket]["username"]
            
            # Intentar parsear como JSON para validar
            try:
                data = json.loads(message)
                tipo = validador.detectar_tipo(data)
                
                if tipo:
                    es_valido, errores = validador.validar(data, tipo)
                    if not es_valido:
                        await websocket.send(crear_mensaje_error(400, "Validación fallida", errores))
                        log.validacion_fallida(cliente_id, errores)
                        continue
                    
                    # Si es un mensaje estructurado, usar el texto
                    if tipo == "mensaje":
                        texto = data.get("mensaje", "")
                    elif tipo == "broadcast":
                        texto = data.get("texto", "")
                    else:
                        texto = message
                else:
                    texto = message
            except json.JSONDecodeError:
                texto = message
            
            log.mensaje_recibido(cliente_id, "broadcast", len(message))
            
            # Broadcast a todos los clientes
            mensaje_broadcast = json.dumps({
                "tipo": "mensaje",
                "usuario": usuario,
                "texto": texto
            })
            
            destinatarios = 0
            for cliente in CLIENTES:
                if cliente != websocket and cliente in usuarios_autenticados:
                    try:
                        await cliente.send(mensaje_broadcast)
                        destinatarios += 1
                    except Exception as e:
                        log.error_conexion(id(cliente), str(e))
            
            log.mensaje_enviado(cliente_id, "broadcast", len(mensaje_broadcast), destinatarios=destinatarios)
            
    except Exception as e:
        log.error_conexion(cliente_id, str(e))
    finally:
        CLIENTES.discard(websocket)
        if websocket in usuarios_autenticados:
            usuario = usuarios_autenticados.pop(websocket)
            log.conexion_saliente(cliente_id, usuario["username"])
            log.info(f"Cliente {usuario['username']} abandonado el broadcast", clientes_conectados=len(CLIENTES))


async def main():
    async with serve(broadcast, "localhost", 8766):
        log.info("Servidor WebSocket broadcast iniciado", puerto=8766)
        print("=" * 60)
        print("Servidor WebSocket Broadcast con autenticación y validación")
        print("Puerto: ws://localhost:8766")
        print("Credenciales: admin/admin123, user/user123, invitado/invitado123")
        print("Logs estructurados en formato JSON")
        print("=" * 60)
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
