import asyncio
from websockets.asyncio.server import serve

CLIENTES = set()


async def broadcast(texto: str) -> None:
    if not CLIENTES:
        return
    await asyncio.gather(*(cliente.send(texto) for cliente in CLIENTES), return_exceptions=True)


async def handler(websocket):
    CLIENTES.add(websocket)
    try:
        await websocket.send(f"Conectado. Clientes activos: {len(CLIENTES)}")
        await broadcast(f"[SISTEMA] Nuevo cliente conectado. Total: {len(CLIENTES)}")

        async for message in websocket:
            msg = message.strip()
            if not msg:
                await websocket.send("Error: mensaje vacio")
                continue
            await broadcast(f"[BROADCAST] {msg}")
    finally:
        CLIENTES.discard(websocket)
        await broadcast(f"[SISTEMA] Cliente desconectado. Total: {len(CLIENTES)}")


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8802):
        print("Servidor WS Broadcast en ws://localhost:8802")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
