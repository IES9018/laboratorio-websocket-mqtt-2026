# Tutorial 04 - WebSocket básico práctico

Este bloque es para comenzar con WebSocket desde lo más simple a lo ligeramente estructurado.

## Ejercicio 1: Echo

Ruta: ejercicios/ws-basico-01-echo

```bash
python ejercicios/ws-basico-01-echo/server.py
```

Luego abrir cliente.html en navegador.

Objetivo: entender conexión persistente y envío/recepción.

## Ejercicio 2: Broadcast

Ruta: ejercicios/ws-basico-02-broadcast

```bash
python ejercicios/ws-basico-02-broadcast/server.py
```

Abrir cliente.html en dos pestañas distintas.

Objetivo: entender múltiples clientes y difusión de mensajes.

## Ejercicio 3: Validación de mensajes JSON

Ruta: ejercicios/ws-basico-03-validacion-mensajes

```bash
python ejercicios/ws-basico-03-validacion-mensajes/server.py
```

Enviar JSON desde cliente.html.

Objetivo: validar formato y reglas básicas antes de procesar.

## Sugerencias de mejora para estudiantes

1. Agregar campo "tipo" al JSON y manejar distintos comandos.
2. Guardar historial de mensajes en memoria.
3. Incorporar manejo de excepciones y logging.
4. Separar funciones en capas: transporte, aplicación, dominio.
5. Diseñar pruebas de casos correctos e incorrectos.
