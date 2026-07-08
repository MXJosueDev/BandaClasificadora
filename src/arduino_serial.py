import serial
import time

class ArduinoCommunicator:
    def __init__(self, port='COM3', baudrate=9600):
        """Inicializa la conexión serial con el Arduino."""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  
            print(f"Conectado a Arduino en {port}")
        except Exception as e:
            print(f"No se pudo conectar al Arduino en {port}. Error: {e}")
            self.ser = None

    def enviar_fruta(self, nombre_clase):
        """Envía el nombre de la clase detectada por serial."""
        if self.ser and self.ser.is_open:
            mensaje = f"{nombre_clase}\n"
            try:
                self.ser.write(mensaje.encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar datos: {e}")
                
    def close(self):
        """Cierra el puerto serial de forma segura."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Conexión serial cerrada.")