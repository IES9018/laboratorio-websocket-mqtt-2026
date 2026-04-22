import unittest
import json
from server import Aplicacion, Mensaje, HISTORIAL

class TestAplicacion(unittest.TestCase):
    def setUp(self):
        # Limpiar historial antes de cada test
        HISTORIAL.clear()

    def test_validar_mensaje_correcto(self):
        data = {"usuario": "ana", "mensaje": "hola", "tipo": "mensaje"}
        msg = Aplicacion.validar_mensaje(data)
        self.assertEqual(msg.usuario, "ana")
        self.assertEqual(msg.mensaje, "hola")
        self.assertEqual(msg.tipo, "mensaje")

    def test_validar_mensaje_sin_usuario(self):
        data = {"mensaje": "hola"}
        with self.assertRaises(ValueError) as cm:
            Aplicacion.validar_mensaje(data)
        self.assertIn("Campo 'usuario' obligatorio", str(cm.exception))  # Corregido con tilde

    def test_validar_mensaje_muy_largo(self):
        data = {"usuario": "ana", "mensaje": "a" * 121}
        with self.assertRaises(ValueError) as cm:
            Aplicacion.validar_mensaje(data)
        self.assertIn("demasiado largo", str(cm.exception))

    def test_validar_tipo_invalido(self):
        data = {"usuario": "ana", "mensaje": "hola", "tipo": "invalido"}
        with self.assertRaises(ValueError) as cm:
            Aplicacion.validar_mensaje(data)
        self.assertIn("Tipo invalido", str(cm.exception))

    def test_procesar_comando_historial(self):
        # Agregar un mensaje al historial
        msg = Mensaje("ana", "hola")
        Aplicacion.guardar_historial(msg)
        
        comando = Mensaje("ana", "historial", "comando")
        respuesta = Aplicacion.procesar_comando(comando)
        self.assertEqual(respuesta["tipo"], "respuesta")
        self.assertEqual(len(respuesta["data"]), 1)

    def test_guardar_historial(self):
        msg = Mensaje("ana", "hola")
        Aplicacion.guardar_historial(msg)
        self.assertEqual(len(HISTORIAL), 1)
        self.assertEqual(HISTORIAL[0].usuario, "ana")

if __name__ == "__main__":
    unittest.main()