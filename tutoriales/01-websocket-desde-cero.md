# Tutorial 01 - WebSocket desde cero

## Que problema resuelve
HTTP tradicional es request/response. Para interaccion en tiempo real (chat, tablero, notificaciones) conviene un canal persistente bidireccional.

## Conceptos clave
- Handshake HTTP -> upgrade a WebSocket
- Conexion persistente
- Mensajes texto/binario en ambas direcciones

## Ejecucion rapida
1. Instalar dependencias.
2. Levantar servidor:
```bash
python ejercicios/ws-02-websocket-echo/server.py
```
3. Abrir cliente:
- Abrir ejercicios/ws-02-websocket-echo/static/index.html en navegador.
4. Enviar mensajes y verificar eco.

## Ejercicios sugeridos
1. Agregar prefijo de usuario a cada mensaje.
2. Agregar contador de clientes conectados.
3. Rechazar mensajes vacios o > 200 caracteres.
4. Registrar logs con timestamp.

## Puente a arquitectura
- Monolito: WebSocket como modulo interno.
- Capas: separar transporte, aplicacion y dominio.
- Microservicios: gateway WebSocket + servicio de eventos.
