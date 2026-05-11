import asyncio
from websockets.asyncio.server import serve

# se realizo la conexion clinte servidor "resuelvo ejercicios ws basico 01 echo"
async def handler(websocket):
    await websocket.send("Conectado: ejercicio ws-basico-01-echo")
    async for message in websocket:
        texto = message.strip()
        if not texto:
            await websocket.send("Error: mensaje vacio")
            continue
        await websocket.send(f"Eco => {texto}")


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8801):
        print("Servidor WS Echo en ws://localhost:8801")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
