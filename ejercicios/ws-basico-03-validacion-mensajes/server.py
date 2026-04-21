import asyncio
import json
from datetime import datetime

from websockets import serve

HISTORIAL = []
MAX_HISTORIAL = 10


async def handler(websocket):
    await websocket.send('Enviar JSON con formato: {"tipo":"mensaje", "usuario":"ana", "mensaje":"hola"}')
    await websocket.send('Tipos disponibles: mensaje, echo, info, ayuda, historial')

    async for raw in websocket:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send("Error: el mensaje debe ser JSON valido")
            continue

        # Obtener tipo de comando (default: mensaje)
        tipo = str(data.get("tipo", "mensaje")).strip().lower()
        usuario = str(data.get("usuario", "")).strip()
        mensaje = str(data.get("mensaje", "")).strip()

        # Manejar distintos tipos de comandos
        if tipo == "echo":
            await websocket.send(f"[ECHO] {mensaje}")
            continue
        
        elif tipo == "info":
            info = {
                "servidor": "WebSocket Validacion v1.0",
                "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipos_disponibles": ["mensaje", "echo", "info", "ayuda", "historial"]
            }
            await websocket.send(f"[INFO] {json.dumps(info)}")
            continue
        
        elif tipo == "ayuda":
            ayuda = """
[AYUDA] Comandos disponibles:
- {"tipo":"mensaje", "usuario":"...", "mensaje":"..."} -> Enviar mensaje
- {"tipo":"echo", "mensaje":"..."} -> Repetir mensaje
- {"tipo":"info"} -> Ver info del servidor
- {"tipo":"historial"} -> Ver mensajes guardados
- {"tipo":"ayuda"} -> Mostrar esta ayuda
            """
            await websocket.send(ayuda.strip())
            continue
        
        elif tipo == "historial":
            if not HISTORIAL:
                await websocket.send("[HISTORIAL] No hay mensajes guardados")
            else:
                await websocket.send(f"[HISTORIAL] Últimos {len(HISTORIAL)} mensajes:")
                for m in HISTORIAL:
                    await websocket.send(f"  [{m['timestamp']}] {m['usuario']}: {m['mensaje']}")
            continue
        
        elif tipo == "mensaje":
            # Validar campos para mensaje
            if not usuario:
                await websocket.send("Error: campo 'usuario' obligatorio")
                continue
            if not mensaje:
                await websocket.send("Error: campo 'mensaje' obligatorio")
                continue
            if len(mensaje) > 120:
                await websocket.send("Error: mensaje demasiado largo (max 120)")
                continue

            # Guardar en historial
            mensaje_guardado = {
                "usuario": usuario,
                "mensaje": mensaje,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            HISTORIAL.append(mensaje_guardado)
            
            # Mantener solo los últimos MAX_HISTORIAL mensajes
            if len(HISTORIAL) > MAX_HISTORIAL:
                HISTORIAL.pop(0)

            ts = datetime.now().strftime("%H:%M:%S")
            await websocket.send(f"[{ts}] OK {usuario}: {mensaje}")
            continue
        
        else:
            await websocket.send(f"Error: tipo '{tipo}' no reconocido. Use: mensaje, echo, info, ayuda, historial")


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8803):
        print("Servidor WS Validacion en ws://localhost:8803")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8803):
        print("Servidor WS Validacion en ws://localhost:8803")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
