import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "ies9018/programacion3/demo"


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Conectado al broker con codigo {rc}")
    client.subscribe(TOPIC, qos=1)
    print(f"Suscripto a {TOPIC}")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode('utf-8')}")


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    print("Esperando mensajes... CTRL+C para salir")
    client.loop_forever()


if __name__ == "__main__":
    main()
