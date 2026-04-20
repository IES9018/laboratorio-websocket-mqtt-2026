import asyncio
from datetime import datetime

from websockets.asyncio.server import serve

#el ejercicio esta realizado con mensaje lo envia correctamente 
#y si el mensaje es vacio o tiene mas de 200 caracteres devuelve un error, el servidor se mantiene activo para recibir nuevos mensajes
CLIENTES = set()


async def handler(websocket):
    CLIENTES.add(websocket)
    try:
        await websocket.send("Conectado al servidor WebSocket")
        async for message in websocket:
            clean = message.strip()
            if not clean:
                await websocket.send("Error: mensaje vacio")
                continue
            if len(clean) > 200:
                await websocket.send("Error: maximo 200 caracteres")
                continue

            timestamp = datetime.now().strftime("%H:%M:%S")
            await websocket.send(f"[{timestamp}] eco: {clean}")
    finally:
        CLIENTES.remove(websocket)


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket en ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
