import serial
import serial.tools.list_ports
import time
import threading
import queue
import logging

# logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class ArduinoCommunicator:
    def __init__(self, port=None, baudrate=9600):
        """
        Inicializa la comunicación con Arduino de forma no bloqueante.
        Si 'port' es None, intentará autodetectarlo.
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
        self.message_queue = queue.Queue()
        self.is_running = True
        
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _auto_detect_port(self):
        """Busca automáticamente el puerto (Arduino, ESP32, etc.) en cualquier SO."""
        ports = serial.tools.list_ports.comports()
        
        keywords = ["arduino", "ch340", "cp210", "esp32", "ftdi", "espressif", "uart", "usb serial"]
        
        for p in ports:
            usb_info = f"{p.description} {p.manufacturer}".lower()
            
            if any(kw in usb_info for kw in keywords):
                return p.device
        
        return ports[0].device if ports else None

    def _connect(self):
        """Intenta establecer o recuperar la conexión serial."""
        if self.ser and self.ser.is_open:
            return True

        target_port = self.port or self._auto_detect_port()
        
        if not target_port:
            logging.warning("No se encontró Arduino disponible.")
            return False

        try:
            self.ser = serial.Serial(target_port, self.baudrate, timeout=1)
            time.sleep(2) 
            logging.info(f"Conectado exitosamente a Arduino en {target_port}")
            return True
        except serial.SerialException as e:
            logging.error(f"Fallo al conectar en {target_port}: {e}")
            self.ser = None
            return False

    def _worker_loop(self):
        """Bucle en segundo plano que gestiona la conexión y los envíos."""
        while self.is_running:
            try:
                message = self.message_queue.get(timeout=0.5)
                
                while self.is_running and not self._connect():
                    time.sleep(2)
                
                if self.ser and self.ser.is_open:
                    try:
                        self.ser.write(f"{message}\n".encode('utf-8'))
                        logging.debug(f"Enviado: {message}")
                    except serial.SerialException:
                        logging.error("Conexión perdida al intentar enviar. Reencolando mensaje...")
                        self.ser.close()
                        self.ser = None
                        self.message_queue.put(message)
                
                self.message_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error inesperado en el hilo de Arduino: {e}")

    def send_detection(self, class_name):
        """
        Envía el nombre de la clase detectada. 
        Este método retorna INSTANTÁNEAMENTE.
        """
        if self.is_running:
            self.message_queue.put(class_name)

    def close(self):
        """Cierra el hilo y el puerto serial de forma segura."""
        self.is_running = False
        self.worker_thread.join(timeout=2)
        
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Conexión serial cerrada de forma segura.")