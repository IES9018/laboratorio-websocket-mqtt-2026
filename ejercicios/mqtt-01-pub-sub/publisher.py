import json
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "ies9018/programacion3/demo"


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, keepalive=60)

    print("Publicador MQTT listo. Enter vacio para salir.")
    while True:
        texto = input("Mensaje> ").strip()
        if not texto:
            break

        payload = {
            "mensaje": texto,
            "timestamp": datetime.utcnow().isoformat(),
            "curso": "Programacion III",
        }
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print(f"Publicado en {TOPIC}")

    client.disconnect()


if __name__ == "__main__":
    main()
