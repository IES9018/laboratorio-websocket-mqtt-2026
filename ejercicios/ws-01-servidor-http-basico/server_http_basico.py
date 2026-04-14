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

            html = f"""
<html>
<head>
    <title>Mi servidor web</title>
    <meta charset=\"UTF-8\" />
</head>
<body>
    <h1>Hola exitoso estudiante {nombre}!</h1>
    <p>Este servidor usa sockets TCP y protocolo HTTP manual.</p>
</body>
</html>
"""

            respuesta = b"HTTP/1.1 200 OK\r\n"
            respuesta += b"Content-Type: text/html; charset=utf-8\r\n"
            respuesta += b"\r\n"
            cliente.sendall(respuesta + html.encode("utf-8"))
            cliente.close()

            time.sleep(0.5)
            opcion = input("Desea cerrar el servidor? (s/n): ").lower().strip()
            if opcion == "s":
                print("Cerrando servidor...")
                break
    finally:
        sock.close()


if __name__ == "__main__":
    main()
