import asyncio
import logging
import sys
from websockets.asyncio.server import serve

# 1. Configuración del Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("ejercicio_01.log"), # Registro en archivo
        logging.StreamHandler(sys.stdout)        # Registro en consola
    ]
)
logger = logging.getLogger("EchoServer")

async def handler(websocket):
    # Identificar al cliente
    addr = websocket.remote_address
    logger.info(f"🔌 Nueva conexión desde: {addr}")
    
    try:
        await websocket.send("Conectado: ejercicio ws-basico-01-echo")
        
        async for message in websocket:
            # Lógica que ya tenías
            texto = message.strip()
            
            if not texto:
                logger.warning(f"⚠️ Mensaje vacío recibido de {addr}")
                await websocket.send("Error: mensaje vacio")
                continue
            
            logger.info(f"📩 {addr} envió: {texto}")
            await websocket.send(f"Eco => {texto}")

    except Exception as e:
        # Captura errores de red o desconexiones inesperadas
        logger.error(f"❌ Error durante la comunicación con {addr}: {e}")
    
    finally:
        # Siempre se ejecuta al terminar la conexión
        logger.info(f"⚙️ Conexión cerrada con {addr}")

async def main() -> None:
    # Usamos 0.0.0.0 para que sea accesible desde otros dispositivos en la red
    async with serve(handler, "0.0.0.0", 8801):
        logger.info("🚀 Servidor WS Echo iniciado en ws://localhost:8801")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario (Ctrl+C)")