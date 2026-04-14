import asyncio
import json
from datetime import datetime

from websockets.asyncio.server import serve


async def handler(websocket):
    await websocket.send('Enviar JSON con formato: {"usuario":"ana", "mensaje":"hola"}')

    async for raw in websocket:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send("Error: el mensaje debe ser JSON valido")
            continue

        usuario = str(data.get("usuario", "")).strip()
        mensaje = str(data.get("mensaje", "")).strip()

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


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8803):
        print("Servidor WS Validacion en ws://localhost:8803")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
