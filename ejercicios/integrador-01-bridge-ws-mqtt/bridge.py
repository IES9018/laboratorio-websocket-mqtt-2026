import asyncio
import json
from datetime import datetime

import paho.mqtt.client as mqtt
from websockets.server import serve

BROKERS = [
    ("test.mosquitto.org", 1883),
    ("broker.hivemq.com", 1883),
    ("localhost", 1883),
]
PORT = 1883
TOPIC = "ies9018/programacion3/bridge"
connected_broker = None
connected_port = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado a MQTT broker {connected_broker}:{connected_port}")
    else:
        print(f"Error de conexion MQTT: codigo {rc}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)

for broker, port in BROKERS:
    try:
        mqtt_client.connect(broker, port, keepalive=60)
        connected_broker = broker
        connected_port = port
        break
    except Exception as exc:
        print(f"No se pudo conectar al broker MQTT {broker}:{port}: {exc}")

if connected_broker is None:
    print("No se pudo conectar a ningun broker MQTT. El bridge seguira corriendo sin MQTT.")
else:
    mqtt_client.loop_start()


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
