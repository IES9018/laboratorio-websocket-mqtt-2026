import socket
import time


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 8080))
    sock.listen(1)

    print("Servidor listo. Abri http://localhost:8080 en tu navegador")
    nombre = input("Ingrese su nombre: ").strip().upper() or "ESTUDIANTE"

    try:
        while True:
            cliente, direccion = sock.accept()
            print(f"Conexion desde {direccion}")

            request = cliente.recv(1024).decode("utf-8")
            print("Request recibido:")
            print(request)

            # Obtener la ruta
            primera_linea = request.split("\n")[0]
            ruta = primera_linea.split(" ")[1]

            if ruta == "/saludo":
                contenido = f"<h1>Hola {nombre}, estas en /saludo 😎</h1>"
            else:
                contenido = f"<h1>Hola estudiante {nombre}!</h1>"

            html = f"""
<html>
<head>
    <title>Mi servidor web</title>
    <meta charset="UTF-8" />
</head>
<body>
    {contenido}
    <p>Servidor con sockets + manejo de rutas básico</p>
</body>
</html>
"""

            respuesta = "HTTP/1.1 200 OK\r\n"
            respuesta += "Content-Type: text/html; charset=utf-8\r\n\r\n"
            respuesta += html

            cliente.sendall(respuesta.encode("utf-8"))
            cliente.close()

            time.sleep(0.5)

    finally:
        sock.close()


if __name__ == "__main__":
    main()