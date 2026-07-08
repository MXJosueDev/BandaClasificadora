import os
import sys
import time
from collections import deque
import cv2
import numpy as np

# Configurar entorno de TF 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Agregar raiz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from src.inference import ModelInference
from src.vision import MotionDetector
from src.counter import ItemCounter
from src.arduino_serial import ArduinoCommunicator

def main():
    # Componentes
    modelo = ModelInference(model_path="./model/model.tflite", labels_path="./model/labels.txt")
    vision = MotionDetector(min_area=3000)
    # arduino = ArduinoCommunicator(port='COM3', baudrate=9600) # COM3 para windows

    # Captura de video/grabacion
    camera_input = input("Ingresa el índice de la cámara a usar (0 por defecto): ").strip()
    camera_index = 0
    if camera_input:
        try:
            camera_index = int(camera_input)
        except ValueError:
            print(f"Valor inválido '{camera_input}'. Se usará la cámara 0.")
            camera_index = 0

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error al abrir la cámara {camera_index}.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_video = int(cap.get(cv2.CAP_PROP_FPS)) or 30

    # fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    # out = cv2.VideoWriter('./test_videos/demo_frutas_3.mp4', fourcc, fps_video, (frame_width, frame_height))

    # Contador
    linea_conteo_x = frame_width // 2
    contador = ItemCounter(
        class_names=modelo.class_names, 
        linea_conteo_x=linea_conteo_x, 
        margen_reset=100
    )

    # Rendimiento
    inference_times = deque(maxlen=30)
    frame_times = deque(maxlen=30)
    last_frame_time = time.perf_counter()

    print("Presiona la tecla 'q' para salir.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detectar movimiento
            hay_movimiento, bbox, centro_x = vision.detect(frame)

            # Dibujar línea de conteo
            cv2.line(frame, (linea_conteo_x, 0), (linea_conteo_x, frame_height), (0, 255, 255), 2)
            cv2.line(frame, (linea_conteo_x - contador.margen_reset, 0), (linea_conteo_x - contador.margen_reset, frame_height), (255, 100, 100), 1)
            cv2.line(frame, (linea_conteo_x + contador.margen_reset, 0), (linea_conteo_x + contador.margen_reset, frame_height), (255, 100, 100), 1)

            if hay_movimiento:
                roi, (x1, y1, x2, y2) = vision.get_roi(frame, bbox)

                # Inferencia
                t_ini = time.perf_counter()
                nombre_clase, confidence = modelo.predict(roi)
                t_fin = time.perf_counter()
                inference_times.append((t_fin - t_ini) * 1000)

                # Actualizar conteo y enviar datos al arduino
                contada_ahora = contador.update_and_check(centro_x, nombre_clase)
                if contada_ahora:
                    # arduino.enviar_fruta(nombre_clase)
                    pass

                # Dibujar bounding box y datos
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{nombre_clase}: {confidence:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.circle(frame, (centro_x, bbox[1] + (bbox[3]//2)), 5, (0, 0, 255), -1)

            else:
                contador.reset_tracking()
                cv2.putText(frame, "Esperando fruta...", (20, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)

            # Panel de conteo
            cv2.rectangle(frame, (frame_width - 290, 10), (frame_width - 10, 40 + (len(modelo.class_names) * 30)), (0, 0, 0), -1)
            cv2.putText(frame, "CONTEO TOTAL:", (frame_width - 280, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            y_offset = 65
            for clase, cantidad in contador.conteo_clases.items():
                cv2.putText(frame, f"{clase}: {cantidad}", (frame_width - 280, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
                y_offset += 30

            # Calcular FPS
            current_time = time.perf_counter()
            frame_times.append((current_time - last_frame_time) * 1000)
            last_frame_time = current_time
            
            fps = 1000 / np.mean(frame_times) if frame_times else 0
            avg_inference = np.mean(inference_times) if inference_times else 0
            
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(frame, f"Inferencia: {avg_inference:.1f}ms", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            cv2.imshow('Frutas en Banda', frame)
            # out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        # out.release()
        cv2.destroyAllWindows()
        # arduino.close()

if __name__ == "__main__":
    main()