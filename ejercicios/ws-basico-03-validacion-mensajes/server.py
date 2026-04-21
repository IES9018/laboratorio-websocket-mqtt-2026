import asyncio
import json
from datetime import datetime

from websockets import serve


async def handler(websocket):
    await websocket.send('Enviar JSON con formato: {"tipo":"mensaje", "usuario":"ana", "mensaje":"hola"}')
    await websocket.send('Tipos disponibles: mensaje, echo, info, ayuda')

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
                "tipos_disponibles": ["mensaje", "echo", "info", "ayuda"]
            }
            await websocket.send(f"[INFO] {json.dumps(info)}")
            continue
        
        elif tipo == "ayuda":
            ayuda = """
[AYUDA] Comandos disponibles:
- {"tipo":"mensaje", "usuario":"...", "mensaje":"..."} -> Enviar mensaje
- {"tipo":"echo", "mensaje":"..."} -> Repetir mensaje
- {"tipo":"info"} -> Ver info del servidor
- {"tipo":"ayuda"} -> Mostrar esta ayuda
            """
            await websocket.send(ayuda.strip())
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

            ts = datetime.now().strftime("%H:%M:%S")
            await websocket.send(f"[{ts}] OK {usuario}: {mensaje}")
            continue
        
        else:
            await websocket.send(f"Error: tipo '{tipo}' no reconocido. Use: mensaje, echo, info, ayuda")


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8803):
        print("Servidor WS Validacion en ws://localhost:8803")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
