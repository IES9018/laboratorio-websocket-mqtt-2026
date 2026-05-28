import asyncio
from datetime import datetime

from websockets import serve


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
