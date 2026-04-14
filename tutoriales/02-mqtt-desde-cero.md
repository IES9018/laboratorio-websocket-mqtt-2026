# Tutorial 02 - MQTT desde cero

## Que es MQTT
Protocolo liviano de mensajeria publish/subscribe, ideal para IoT y eventos simples.

## Conceptos clave
- Broker
- Publisher
- Subscriber
- Topic (ej: ies9018/aula/ws)
- QoS 0, 1, 2

## Ejecucion rapida
1. Abrir una terminal con subscriber:
```bash
python ejercicios/mqtt-01-pub-sub/subscriber.py
```
2. Abrir otra terminal con publisher:
```bash
python ejercicios/mqtt-01-pub-sub/publisher.py
```
3. Ver mensajes en tiempo real.

## Ejercicios sugeridos
1. Cambiar topic por equipo.
2. Probar QoS 0 y QoS 1.
3. Enviar JSON y validarlo.
4. Manejar reconexion automatica.

## Puente a arquitectura
- MQTT modela eventos de dominio.
- Puede convivir con API REST.
- Es una puerta de entrada al enfoque orientado a eventos.
