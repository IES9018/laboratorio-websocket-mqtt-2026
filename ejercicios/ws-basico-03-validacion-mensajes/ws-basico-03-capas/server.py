import asyncio
import logging
from websockets.asyncio.server import serve
from router import procesar_comando # Importamos el router

async def handler(websocket):
    addr = websocket.remote_address
    print(f"🔌 Conectado: {addr}")
    
    try:
        await websocket.send("Bienvenido. Use JSON (mensaje, echo, info, historial)")
        
        async for raw_message in websocket:
            # La magia ocurre aquí: delegamos al router
            respuesta = procesar_comando(raw_message)
            await websocket.send(respuesta)
            
    finally:
        print(f"⚙️ Desconectado: {addr}")

async def main():
    async with serve(handler, "0.0.0.0", 8803):
        print("🚀 Servidor en Capas corriendo en el puerto 8803")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())