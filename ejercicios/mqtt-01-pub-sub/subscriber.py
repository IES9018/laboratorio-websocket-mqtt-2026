import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "ies9018/equipo1/demo"  # Cambiado por equipo

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Conectado al broker con codigo {rc}")
    client.subscribe(TOPIC, qos=0)  # QoS 0 para probar
    print(f"Suscripto a {TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        # Validar JSON: verificar claves requeridas
        required_keys = ["mensaje", "timestamp", "curso"]
        if not all(key in payload for key in required_keys):
            print(f"Error: JSON invalido, faltan claves. Recibido: {payload}")
            return
        print(f"[{msg.topic}] Mensaje valido: {payload['mensaje']} | Timestamp: {payload['timestamp']} | Curso: {payload['curso']}")
    except json.JSONDecodeError:
        print(f"Error: No es JSON valido. Recibido: {msg.payload.decode('utf-8')}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Desconexion inesperada. Intentando reconectar...")
        client.reconnect()
    else:
        print("Desconexion limpia.")

def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(BROKER, PORT, keepalive=60)
    print("Esperando mensajes... CTRL+C para salir")
    client.loop_start()  # Cambiado para reconexion automatica
    try:
        while True:
            pass  # Mantener vivo
    except KeyboardInterrupt:
        client.disconnect()
        print("Saliendo...")

if __name__ == "__main__":
    main()
