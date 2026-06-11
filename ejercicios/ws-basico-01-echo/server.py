import asyncio
import sys
import os
import json

# Agregar el directorio actual al path para importar auth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from websockets import serve
from auth import verificar_credenciales, parsear_mensaje_autenticacion, crear_mensaje_autenticacion, crear_token_autenticacion
from validacion import ValidadorMensajes, crear_mensaje_error, crear_mensaje_exito, ErrorValidacion
from logging_ws import crear_loggeador, NivelLog

# Crear loggeador estructurado
log = crear_loggeador("ws-echo", NivelLog.INFO)

# Instancia del validador
validador = ValidadorMensajes()

# Almacenar usuarios autenticados
usuarios_autenticados = {}


async def echo(websocket):
    """Manejador principal que requiere autenticación primero."""
    cliente_id = id(websocket)
    
    # Solicitar autenticación al cliente
    await websocket.send(crear_mensaje_autenticacion(
        "auth_required", 
        "Por favor, autenticarse con formato JSON: {\"username\": \"usuario\", \"password\": \"contraseña\"}"
    ))
    
    log.conexion_entrante(cliente_id, "localhost")
    
    # Esperar mensaje de autenticación del cliente
    try:
        auth_message = await asyncio.wait_for(websocket.recv(), timeout=30)
        credenciales = parsear_mensaje_autenticacion(auth_message)
        
        if credenciales is None:
            await websocket.send(crear_mensaje_autenticacion("auth_error", "Formato de autenticación inválido. Use JSON: {\"username\": \"...\", \"password\": \"...\"}"))
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
        
        await websocket.send(crear_mensaje_autenticacion(
            "auth_success", 
            f"Bienvenido {username}!",
            {"token": token, "username": username}
        ))
        log.autenticacion_exitosa(cliente_id, username)
        
    except asyncio.TimeoutError:
        await websocket.send(crear_mensaje_autenticacion("auth_error", "Tiempo de autenticación agotado"))
        await websocket.close(1008, "Timeout de autenticación")
        log.autenticacion_fallida(cliente_id, "timeout")
        return
    except Exception as e:
        log.error(f"Error en autenticación: {e}", cliente_id=cliente_id, error=str(e))
        await websocket.close(1008, "Error de autenticación")
        return
    
    # Manejar mensajes del cliente después de autenticado
    try:
        async for message in websocket:
            # Intentar parsear como JSON para validar
            try:
                data = json.loads(message)
                # Detectar tipo de mensaje y validar
                tipo = validador.detectar_tipo(data)
                
                if tipo:
                    es_valido, errores = validador.validar(data, tipo)
                    if not es_valido:
                        await websocket.send(crear_mensaje_error(400, "Validación fallida", errores))
                        log.validacion_fallida(cliente_id, errores)
                        continue
                    
                    # Si es un mensaje estructurado, responder en JSON
                    if tipo == "mensaje":
                        respuesta = {
                            "tipo": "eco",
                            "usuario": data.get("usuario", username),
                            "mensaje": data.get("mensaje", message),
                            "recibido": True
                        }
                        await websocket.send(json.dumps(respuesta))
                        log.mensaje_enviado(cliente_id, "eco", len(message))
                    else:
                        await websocket.send(message)
                else:
                    # Mensaje plano, hacer eco
                    await websocket.send(message)
                    log.mensaje_enviado(cliente_id, "texto", len(message))
                    
            except json.JSONDecodeError:
                # No es JSON, hacer eco del mensaje plano
                await websocket.send(message)
                log.mensaje_enviado(cliente_id, "texto_plano", len(message))
                
    except Exception as e:
        log.error_conexion(cliente_id, str(e))
    finally:
        if websocket in usuarios_autenticados:
            usuario = usuarios_autenticados.pop(websocket)
            log.conexion_saliente(cliente_id, usuario["username"])


async def main():
    async with serve(echo, "localhost", 8765):
        log.info("Servidor WebSocket echo iniciado", puerto=8765)
        print("=" * 60)
        print("Servidor WebSocket con autenticación y validación JSON")
        print("Puerto: ws://localhost:8765")
        print("Credenciales: admin/admin123, user/user123, invitado/invitado123")
        print("Formatos válidos: texto plano o JSON {\"usuario\": \"...\", \"mensaje\": \"...\"}")
        print("Logs estructurados en formato JSON")
        print("=" * 60)
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
