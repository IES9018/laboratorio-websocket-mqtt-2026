# Tutorial 03 - WebSocket vs MQTT y relacion con arquitectura

## Comparativa rapida

| Criterio | WebSocket | MQTT |
|---|---|---|
| Modelo | Conexion cliente-servidor persistente | Publish/subscribe via broker |
| Uso tipico | UI en tiempo real | Eventos y telemetria |
| Complejidad inicial | Baja a media | Baja |
| Escalado | Requiere estrategia de sesiones | Broker desacopla productores/consumidores |

## Cuando usar cada uno
- WebSocket: chat web, notificaciones a UI, dashboards.
- MQTT: sensores, eventos, integracion entre servicios.
- Juntos: UI por WebSocket + backend orientado a eventos por MQTT.

## Enlace con DDD
- Publicar eventos de dominio a topics.
- Mantener capa de dominio aislada de protocolo.

## Mini guia de evolucion
1. Empezar con monolito en capas.
2. Introducir mensajeria interna (MQTT en entorno de laboratorio).
3. Separar modulos por bounded context.
4. Migrar partes a servicios cuando exista necesidad real.
