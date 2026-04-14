import asyncio
import json
from datetime import datetime

import paho.mqtt.client as mqtt
from websockets.asyncio.server import serve

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "ies9018/programacion3/bridge"

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(BROKER, PORT, keepalive=60)


async def handler(websocket):
    await websocket.send("Bridge listo: WebSocket -> MQTT")
    async for message in websocket:
        data = {
            "mensaje": message,
            "origen": "websocket",
            "timestamp": datetime.utcnow().isoformat(),
        }
        mqtt_client.publish(TOPIC, json.dumps(data), qos=1)
        await websocket.send(f"Publicado en MQTT topic {TOPIC}")


async def main() -> None:
    async with serve(handler, "0.0.0.0", 9876):
        print("Bridge en ws://localhost:9876")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
