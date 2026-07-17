import os
import sys
import time
from collections import deque
import cv2
import numpy as np

# Entorno de TF 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Agregar raiz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inference import ModelInference
from src.vision import MotionDetector
from src.counter import ItemCounter
from src.color_detector import ColorDetector
from src.arduino_serial import ArduinoCommunicator

def solve_route(relative_route):
    """Devuelve la ruta absoluta, ya sea en desarrollo o compilado por PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_route)

def main():
    # Componentes
    model = ModelInference(model_path=solve_route("./model/model.tflite"), labels_path=solve_route("./model/labels.txt"))
    vision = MotionDetector(min_area=3000)
    color_detector = ColorDetector(min_pixels=30)
    arduino = ArduinoCommunicator(baudrate=9600)

    # Captura de video/grabacion
    camera_input = input("Ingresa el índice de la cámara a usar (0 por defecto): ").strip()
    camera_index = 0
    if camera_input:
        try:
            camera_index = int(camera_input)
        except ValueError:
            print(f"Valor inválido '{camera_input}'. Se usará la cámara 0.")
            camera_index = 0

    # cap = cv2.VideoCapture('C:/Users/mxjos/Programacion/Vision Artificial/BandaClasificadora/test_videos/4_cubos.mp4')
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Error al abrir la cámara {camera_index}.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_video = int(cap.get(cv2.CAP_PROP_FPS)) or 30

    # fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    # out = cv2.VideoWriter('./test_videos/demo_4.mp4', fourcc, fps_video, (frame_width, frame_height))

    # Classes
    class_names = []
    for clase in model.class_names:
        if clase == "cubo":
            class_names.extend(["cubo_rojo", "cubo_verde", "cubo_azul", "cubo_desconocido"])
        else:
            class_names.append(clase)

    # Contador
    counting_line_x = frame_width // 2
    counter = ItemCounter(
        class_names=class_names, 
        counting_line_x=counting_line_x, 
        margin_reset=100
    )

    # Rendimiento
    inference_times = deque(maxlen=30)
    frame_times = deque(maxlen=30)
    last_frame_time = time.perf_counter()

    print("Presiona la tecla 'q' para salir.")

    # Para poder redimencionar la pantalla
    cv2.namedWindow('Banda Transportadora', cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detectar movimiento
            has_movement, bbox, center_x = vision.detect(frame)

            if has_movement:
                roi, (x1, y1, x2, y2) = vision.get_roi(frame, bbox)

                # Inferencia
                t_ini = time.perf_counter()
                class_name, confidence = model.predict(roi)
                t_fin = time.perf_counter()
                inference_times.append((t_fin - t_ini) * 1000)

                if class_name == "cubo":
                    color = color_detector.detect(roi)
                    class_name = f"cubo_{color}"

                # Actualizar conteo y enviar datos al arduino
                count_now = counter.update_and_check(center_x, class_name)
                if count_now:
                    arduino.send_detection(class_name)
                    pass

                # Dibujar bounding box y datos
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{class_name}: {confidence:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.circle(frame, (center_x, bbox[1] + (bbox[3]//2)), 5, (0, 0, 255), -1)

            else:
                counter.reset_tracking()
                cv2.putText(frame, "Esperando objeto...", (20, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)

            # Dibujar línea de conteo
            cv2.line(frame, (counting_line_x, 0), (counting_line_x, frame_height), (0, 255, 255), 2)
            cv2.line(frame, (counting_line_x - counter.margin_reset, 0), (counting_line_x - counter.margin_reset, frame_height), (255, 100, 100), 1)
            cv2.line(frame, (counting_line_x + counter.margin_reset, 0), (counting_line_x + counter.margin_reset, frame_height), (255, 100, 100), 1)

            # Panel de conteo
            # ---------------
            alpha = 0.5 
            x_inicio = frame_width - 250 

            alto_panel = 35 + (len(counter.class_counting) * 25)

            overlay = frame.copy()
            cv2.rectangle(overlay, (x_inicio, 10), (frame_width - 10, 10 + alto_panel), (0, 0, 0), -1)

            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            cv2.putText(frame, "CONTEO TOTAL:", (x_inicio + 10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            y_offset = 55
            for clase, cantidad in counter.class_counting.items():
                cv2.putText(frame, f"{clase}: {cantidad}", (x_inicio + 10, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                y_offset += 25
            # ---------------

            # Calcular FPS
            current_time = time.perf_counter()
            frame_times.append((current_time - last_frame_time) * 1000)
            last_frame_time = current_time
            
            fps = 1000 / np.mean(frame_times) if frame_times else 0
            avg_inference = np.mean(inference_times) if inference_times else 0
            
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(frame, f"Inferencia: {avg_inference:.1f}ms", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            cv2.imshow('Banda Transportadora', frame)
            # out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        # out.release()
        cv2.destroyAllWindows()
        arduino.close()

if __name__ == "__main__":
    main()