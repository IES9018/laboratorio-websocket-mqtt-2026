import asyncio
from datetime import datetime
from websockets.asyncio.server import serve

CLIENTES = set()

async def broadcast(message):
    """Envía un mensaje a todos los clientes conectados, ignorando errores."""
    for ws in CLIENTES.copy():
        try:
            await ws.send(message)
        except Exception:
            pass  # cliente ya desconectado o error de red

async def handler(websocket):
    CLIENTES.add(websocket)
    username = None
    try:
        # Notificar a todos el número actual de clientes
        count = len(CLIENTES)
        await broadcast(f"Clientes conectados: {count}")
        await websocket.send("Conectado. Envía tu nombre de usuario (obligatorio):")

        # Recibir nombre con tiempo límite
        try:
            first_message = await asyncio.wait_for(websocket.recv(), timeout=10)
        except asyncio.TimeoutError:
            await websocket.send("ERROR: Tiempo agotado. Debes enviar un nombre. Conexión cerrada.")
            return

        clean_name = first_message.strip()
        if not clean_name or len(clean_name) > 30:
            await websocket.send("ERROR: Nombre inválido (vacío o más de 30 caracteres). Conexión cerrada.")
            return

        username = clean_name
        await websocket.send(f"Bienvenido {username}, ya puedes enviar mensajes.")

        # Bucle de mensajes
        async for message in websocket:
            clean = message.strip()

            if not clean:
                await websocket.send(f"[{username}] Error: mensaje vacío")
                continue
            if len(clean) > 200:
                await websocket.send(f"[{username}] Error: máximo 200 caracteres")
                continue

            timestamp = datetime.now().strftime("%H:%M:%S")
            await websocket.send(f"[{timestamp}] {username} dice: {clean}")

    finally:
        # Quitar cliente y notificar desconexión
        CLIENTES.remove(websocket)
        try:
            count = len(CLIENTES)
            await broadcast(f"Clientes conectados: {count}")
        except Exception:
            pass  # no queremos que falle el cierre por un error de broadcast

async def main() -> None:
    async with serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket en ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())