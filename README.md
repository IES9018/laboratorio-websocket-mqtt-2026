# IES 9-018 - Programacion III 2026
## Laboratorio: WebSocket + MQTT (base para Arquitectura y Practicas III)

Este repositorio conecta los contenidos que ya vieron:
- Monolito, capas, microservicios, DDD
- Mensajeria (Kafka, RabbitMQ) como contexto
- Inicio practico con WebSocket y MQTT

Objetivo: construir bases funcionales y modificables para que cada estudiante haga fork, experimente y entregue mejoras por Pull Request.

## 1. Como trabajar con este repo (fork + PR)

### Opcion A: desde la web de GitHub
1. Abrir el repo base de la catedra.
2. Click en Fork.
3. Clonar su fork.

### Opcion B: con GitHub CLI
```bash
gh repo fork IES9018/laboratorio-websocket-mqtt-2026 --clone=true
cd laboratorio-websocket-mqtt-2026
```

## 2. Configuracion local

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Sincronizar con el repo de la catedra

```bash
git remote add upstream https://github.com/IES9018/laboratorio-websocket-mqtt-2026.git
git fetch upstream
git checkout main
git merge upstream/main
```

## 4. Flujo de entrega sugerido

```bash
git checkout -b feat/ws-ejercicio-01
# editar archivos
git add .
git commit -m "feat: resuelvo ws ejercicio 01"
git push -u origin feat/ws-ejercicio-01
# luego abrir PR
```

Con CLI:
```bash
gh pr create --base main --head feat/ws-ejercicio-01 --title "Entrega WS ejercicio 01" --body "Resolucion inicial"
```

## 5. Estructura del repositorio

- tutoriales/: teoria aplicada y guias paso a paso.
- ejercicios/: practicas funcionales para modificar.
- LISTA_ESTUDIANTES.md: repositorios fork de cada estudiante.
- seguimiento-estudiantes.json: estado de entregas y observaciones.
- .github/ISSUE_TEMPLATE/: plantillas de issues para bug, consulta y feedback.
- .github/pull_request_template.md: plantilla de entrega por PR.

## 6. Ruta sugerida de aprendizaje

1. tutoriales/01-websocket-desde-cero.md
2. ejercicios/ws-01-servidor-http-basico/server_http_basico.py
3. ejercicios/ws-02-websocket-echo/
4. tutoriales/04-websocket-basico-practico.md
5. ejercicios/ws-basico-01-echo/
6. ejercicios/ws-basico-02-broadcast/
7. ejercicios/ws-basico-03-validacion-mensajes/
8. tutoriales/02-mqtt-desde-cero.md
9. ejercicios/mqtt-01-pub-sub/
10. ejercicios/integrador-01-bridge-ws-mqtt/

## 7. Criterios de evaluacion de cada entrega

- Funciona localmente
- Codigo claro y comentado donde haga falta
- Commit mensajes coherentes
- PR con descripcion tecnica breve
- Evidencia (captura/log) de pruebas

## 8. Relacion con Arquitectura y Practicas III

- Arquitectura y Diseno de Interfaces: modelado de interaccion en tiempo real.
- Practica Profesionalizante III: ejecucion del proyecto, testing y calidad.

## 9. Comandos para supervision docente (GitHub CLI)

```bash
# Ver PRs abiertas del repo base
gh pr list --repo IES9018/laboratorio-websocket-mqtt-2026 --state open

# Ver detalle de una PR
gh pr view 12 --repo IES9018/laboratorio-websocket-mqtt-2026 --comments

# Revisar archivos cambiados de una PR
gh pr diff 12 --repo IES9018/laboratorio-websocket-mqtt-2026

# Crear issue de feedback
gh issue create --repo IES9018/laboratorio-websocket-mqtt-2026 --title "Correcciones WS ejercicio 02" --body "Detalle de mejoras"

# Listar issues abiertas
gh issue list --repo IES9018/laboratorio-websocket-mqtt-2026 --state open
```

## 10. Cambios sugeridos para estudiantes

1. Agregar autenticacion basica en WebSocket.
2. Convertir mensajes a JSON y validar esquema.
3. Registrar logs estructurados con nivel INFO/ERROR.
4. Incorporar pruebas basicas de conexion.
5. Crear version de cliente WebSocket con interfaz mas clara.
