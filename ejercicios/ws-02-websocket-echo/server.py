import asyncio
import logging
from datetime import datetime

from websockets import serve

# Configurar logging con timestamp
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CLIENTES = set()
user_counter = 0  # Contador global para IDs de usuario

async def handler(websocket):
    global user_counter
    user_id = user_counter
    user_counter += 1
    CLIENTES.add(websocket)
    logging.info(f"Usuario {user_id} conectado. Clientes conectados: {len(CLIENTES)}")
    try:
        await websocket.send(f"Conectado al servidor WebSocket como Usuario {user_id} (Clientes conectados: {len(CLIENTES)})")
        async for message in websocket:
            clean = message.strip()
            if not clean:
                logging.warning(f"Mensaje inválido de Usuario {user_id}: vacío")
                continue  # Rechazar: no enviar respuesta
            if len(clean) > 200:
                logging.warning(f"Mensaje inválido de Usuario {user_id}: supera 200 caracteres")
                continue  # Rechazar: no enviar respuesta

            logging.info(f"Mensaje recibido de Usuario {user_id}: {clean}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            response = f"[{timestamp}] Usuario {user_id}: {clean} (Clientes conectados: {len(CLIENTES)})"
            await websocket.send(response)
            logging.info(f"Eco enviado a Usuario {user_id}: {response}")
    finally:
        CLIENTES.remove(websocket)
        logging.info(f"Usuario {user_id} desconectado. Clientes conectados: {len(CLIENTES)}")

async def main() -> None:
    async with serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket en ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())


