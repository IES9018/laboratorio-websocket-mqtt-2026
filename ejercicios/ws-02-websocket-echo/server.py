import asyncio
from datetime import datetime
from websockets.asyncio.server import serve


CLIENTES = set()


async def handler(websocket):
    CLIENTES.add(websocket)
    
    username = None
    
    try:
        await websocket.send("Conectado al servidor WebSocket.")
        
        try:
            first_message = await asyncio.wait_for(websocket.recv(), timeout=10)
        except asyncio.TimeoutError:
            await websocket.send("Error. Tiempo de espera agotado. Debes enviar un nombre.")
            return
        
        clean_name = first_message.strip()
        
        if not clean_name or len(clean_name) > 30:
            await websocket.send("Error: Nombre de usuario inválido (debe contener no más de 30 caracteres)")
            return
        
        username = clean_name
        
        await websocket.send(f"Bienvenido {username}. Ahora puedes enviar mensajes")
        
        
        async for message in websocket:
            clean = message.strip()
            
            if not clean:
                await websocket.send(f"[{username}] Error: mensaje vacío")
                continue
            
            if len(clean) > 200:
                print(f"Mensaje largo detectado: {len(clean)} caracteres")
                await websocket.send(f"[{username}] Error: máximo 200 caracteres")
                continue
                   

            timestamp = datetime.now().strftime("%H:%M:%S")
            await websocket.send(f"[{timestamp}] {username} dice: {clean}")
    
    finally:
        CLIENTES.remove(websocket)


async def main() -> None:
    async with serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket en ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

# Probado, anda con éxito - Ejercicio websocket echo