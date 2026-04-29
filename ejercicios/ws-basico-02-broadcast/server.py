import asyncio
import logging
import sys
from websockets.asyncio.server import serve

# 1. Configuración del Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("ejercicio_02_broadcast.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("BroadcastServer")

# Conjunto global de clientes conectados
CLIENTES = set()

async def broadcast(texto: str) -> None:
    """Difunde un mensaje a todos los clientes conectados de forma asíncrona."""
    if not CLIENTES:
        return
    
    logger.info(f"📢 Difundiendo a {len(CLIENTES)} clientes: {texto}")
    
    # asyncio.gather envía los mensajes en paralelo. 
    # return_exceptions=True evita que el bucle se detenga si un cliente falló.
    await asyncio.gather(
        *(cliente.send(texto) for cliente in CLIENTES), 
        return_exceptions=True
    )

async def handler(websocket):
    addr = websocket.remote_address
    CLIENTES.add(websocket)
    logger.info(f"🔌 Cliente conectado desde {addr}. Total: {len(CLIENTES)}")
    
    try:
        # Notificamos al nuevo cliente y a los demás
        await websocket.send(f"Conectado. Clientes activos: {len(CLIENTES)}")
        await broadcast(f"[SISTEMA] Nuevo cliente conectado de {addr}. Total: {len(CLIENTES)}")

        async for message in websocket:
            msg = message.strip()
            if not msg:
                logger.warning(f"⚠️ Mensaje vacío de {addr}")
                await websocket.send("Error: mensaje vacio")
                continue
            
            # El corazón del broadcast: reenviar lo recibido a TODOS
            logger.info(f"💬 Mensaje recibido de {addr}: {msg}")
            await broadcast(f"[BROADCAST] {msg}")

    except Exception as e:
        logger.error(f"❌ Error inesperado con el cliente {addr}: {e}")
        
    finally:
        # Limpieza al desconectar
        CLIENTES.discard(websocket)
        logger.info(f"📉 Cliente {addr} desconectado. Restantes: {len(CLIENTES)}")
        await broadcast(f"[SISTEMA] Cliente desconectado. Total: {len(CLIENTES)}")

async def main() -> None:
    PUERTO = 8802
    async with serve(handler, "0.0.0.0", PUERTO):
        logger.info(f"🚀 Servidor WS Broadcast iniciado en ws://localhost:{PUERTO}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor de Broadcast detenido por el usuario")