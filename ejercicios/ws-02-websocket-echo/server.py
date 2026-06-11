import asyncio
import sys
import os
import json
from datetime import datetime

from websockets import serve

# Agregar el directorio del primer ejercicio al path para importar auth y validacion
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ws-basico-01-echo"))

from auth import verificar_credenciales, parsear_mensaje_autenticacion, crear_mensaje_autenticacion, crear_token_autenticacion
from validacion import ValidadorMensajes, crear_mensaje_error
from logging_ws import crear_loggeador, NivelLog

# Crear loggeador estructurado
log = crear_loggeador("ws-echo-static", NivelLog.INFO)

# Instancia del validador
validador = ValidadorMensajes()

CLIENTES = set()
user_counter = 0
usuarios_autenticados = {}

async def handler(websocket):
    global user_counter
    cliente_id = id(websocket)
    
    # Solicitar autenticación
    await websocket.send(crear_mensaje_autenticacion(
        "auth_required",
        "Autenticarse con JSON: {\"username\": \"...\", \"password\": \"...\"}"
    ))
    
    log.conexion_entrante(cliente_id, "localhost")
    
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
        CLIENTES.add(websocket)
        
        await websocket.send(crear_mensaje_autenticacion(
            "auth_success",
            f"Bienvenido {username}!",
            {"token": token, "username": username}
        ))
        log.autenticacion_exitosa(cliente_id, username)
        log.info(f"Usuario {username} conectado", clientes_conectados=len(CLIENTES))
        
    except asyncio.TimeoutError:
        await websocket.send(crear_mensaje_autenticacion("auth_error", "Timeout"))
        await websocket.close(1008, "Timeout")
        log.autenticacion_fallida(cliente_id, "timeout")
        return
    except Exception as e:
        log.error(f"Error en auth: {e}", cliente_id=cliente_id, error=str(e))
        await websocket.close(1008, "Error")
        return

    try:
        async for message in websocket:
            clean = message.strip()
            if not clean:
                log.warning(f"Mensaje vacío de {username}", cliente_id=cliente_id)
                continue
            
            # Intentar parsear como JSON para validar
            try:
                data = json.loads(clean)
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
                            "mensaje": data.get("mensaje", clean),
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send(json.dumps(respuesta))
                        log.mensaje_enviado(cliente_id, "eco_json", len(clean))
                        continue
            except json.JSONDecodeError:
                pass
            
            # Mensaje plano - validar longitud
            if len(clean) > 200:
                log.warning(f"Mensaje demasiado largo de {username}", cliente_id=cliente_id, longitud=len(clean))
                await websocket.send(crear_mensaje_error(400, "Mensaje demasiado largo (máx 200 caracteres)", None))
                continue

            log.mensaje_recibido(cliente_id, "texto", len(clean))
            timestamp = datetime.now().strftime("%H:%M:%S")
            response = f"[{timestamp}] {username}: {clean} (Clientes: {len(CLIENTES)})"
            await websocket.send(response)
            log.mensaje_enviado(cliente_id, "eco", len(response))
            except json.JSONDecodeError:
                pass
            
            # Mensaje plano - validar longitud
            if len(clean) > 200:
                logging.warning(f"Mensaje inválido de {username}: supera 200 caracteres")
                await websocket.send(crear_mensaje_error(400, "Mensaje demasiado largo (máx 200 caracteres)", None))
                continue

            logging.info(f"Mensaje de {username}: {clean}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            response = f"[{timestamp}] {username}: {clean} (Clientes: {len(CLIENTES)})"
            await websocket.send(response)
            logging.info(f"Eco enviado a {username}: {response}")
            logging.info(f"Eco enviado a {username}: {response}")
    finally:
        CLIENTES.discard(websocket)
        if websocket in usuarios_autenticados:
            usuario = usuarios_autenticados.pop(websocket)
            logging.info(f"Usuario {usuario['username']} desconectado. Clientes: {len(CLIENTES)}")

async def main() -> None:
    async with serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket con autenticación en ws://localhost:8765")
        print("Credenciales: admin/admin123, user/user123, invitado/invitado123")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())


