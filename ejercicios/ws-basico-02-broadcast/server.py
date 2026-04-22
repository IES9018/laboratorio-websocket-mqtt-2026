import asyncio
from websockets import serve  # Cambiado para compatibilidad

CLIENTES = set()

async def broadcast(websocket):
    CLIENTES.add(websocket)
    try:
        async for message in websocket:
            for cliente in CLIENTES:
                if cliente != websocket:  # No enviar al remitente
                    await cliente.send(message)
    finally:
        CLIENTES.remove(websocket)

async def main():
    async with serve(broadcast, "localhost", 8766):  # Nota: puerto 8766, ajusta si es diferente
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
