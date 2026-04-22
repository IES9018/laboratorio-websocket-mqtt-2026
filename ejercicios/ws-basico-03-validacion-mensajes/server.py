import asyncio
import json
import logging
from datetime import datetime
from websockets import serve

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Capa de Dominio: Modelos y datos
class Mensaje:
    def __init__(self, usuario, mensaje, tipo="mensaje", timestamp=None):
        self.usuario = usuario
        self.mensaje = mensaje
        self.tipo = tipo
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            "usuario": self.usuario,
            "mensaje": self.mensaje,
            "tipo": self.tipo,
            "timestamp": self.timestamp.isoformat()
        }

HISTORIAL = []  # Historial en memoria

# Capa de Aplicación: Lógica de negocio
class Aplicacion:
    @staticmethod
    def validar_mensaje(data):
        try:
            usuario = str(data.get("usuario", "")).strip()
            mensaje = str(data.get("mensaje", "")).strip()
            tipo = str(data.get("tipo", "mensaje")).strip()

            if not usuario:
                raise ValueError("Campo 'usuario' obligatorio")
            if not mensaje:
                raise ValueError("Campo 'mensaje' obligatorio")
            if len(mensaje) > 120:
                raise ValueError("Mensaje demasiado largo (max 120)")
            if tipo not in ["mensaje", "comando"]:
                raise ValueError("Tipo invalido: debe ser 'mensaje' o 'comando'")

            return Mensaje(usuario, mensaje, tipo)
        except Exception as e:
            raise ValueError(f"Error de validacion: {str(e)}")

    @staticmethod
    def procesar_comando(mensaje):
        if mensaje.tipo == "comando" and mensaje.mensaje.lower() == "historial":
            return {"tipo": "respuesta", "data": [m.to_dict() for m in HISTORIAL]}
        return None

    @staticmethod
    def guardar_historial(mensaje):
        HISTORIAL.append(mensaje)
        logging.info(f"Mensaje guardado en historial: {mensaje.usuario}: {mensaje.mensaje}")

# Capa de Transporte: WebSocket handler
async def handler(websocket):
    logging.info("Cliente conectado")
    await websocket.send('Enviar JSON con formato: {"usuario":"ana", "mensaje":"hola", "tipo":"mensaje"} o {"tipo":"comando", "mensaje":"historial"}')

    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
                mensaje = Aplicacion.validar_mensaje(data)
                
                if mensaje.tipo == "comando":
                    respuesta = Aplicacion.procesar_comando(mensaje)
                    if respuesta:
                        await websocket.send(json.dumps(respuesta))
                    else:
                        await websocket.send("Error: Comando desconocido")
                else:
                    Aplicacion.guardar_historial(mensaje)
                    ts = mensaje.timestamp.strftime("%H:%M:%S")
                    await websocket.send(f"[{ts}] OK {mensaje.usuario}: {mensaje.mensaje}")
                
            except ValueError as e:
                logging.warning(f"Error de validacion: {str(e)}")
                await websocket.send(f"Error: {str(e)}")
            except json.JSONDecodeError:
                logging.warning("Mensaje no es JSON valido")
                await websocket.send("Error: El mensaje debe ser JSON valido")
            except Exception as e:
                logging.error(f"Error inesperado: {str(e)}")
                await websocket.send("Error interno del servidor")
    except Exception as e:
        logging.error(f"Error en handler: {str(e)}")
    finally:
        logging.info("Cliente desconectado")

async def main() -> None:
    async with serve(handler, "0.0.0.0", 8803):
        logging.info("Servidor WS Validacion en ws://localhost:8803")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
