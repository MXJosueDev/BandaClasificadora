# Documentación técnica — BandaClasificadora

## 1) Objetivo del proyecto

Este proyecto detecta objetos sobre una banda transportadora con visión artificial, los clasifica con un modelo TensorFlow Lite, cuenta cuántos objetos han cruzado una línea de conteo y, opcionalmente, envía la clase detectada por serial a un Arduino.

---

## 2) Flujo general del sistema

El flujo principal ocurre en `scripts/main.py`:

1. **Carga de componentes**
   - `ModelInference`: carga modelo `.tflite` y etiquetas.
   - `MotionDetector`: detecta movimiento y obtiene bounding box.
   - `ColorDetector`: separa color en HSV para casos de clase `cubo`.
   - `ItemCounter`: decide cuándo contar un objeto al cruzar una línea.
   - `ArduinoCommunicator`: envía detecciones por serial sin bloquear el bucle principal.

2. **Configuración inicial por consola**
   - Orientación de línea de conteo: `vertical` u `horizontal`.
   - Índice de cámara (por defecto `0`).

3. **Captura de video**
   - Se abre `cv2.VideoCapture(camera_index)`.
   - Se leen dimensiones del frame para dibujar línea y panel.

4. **Bucle por frame**
   - Detecta movimiento (`MotionDetector.detect`).
   - Si hay objeto:
     - Recorta ROI (`get_roi`).
     - Hace inferencia (`ModelInference.predict`).
     - Si la clase es `cubo`, estima color (`ColorDetector.detect`) y convierte en:
       - `cubo_rojo`, `cubo_verde`, `cubo_azul` o `cubo_desconocido`.
     - Evalúa cruce de línea (`ItemCounter.update_and_check`).
     - Si hubo conteo nuevo, envía clase por serial a Arduino.
     - Dibuja caja, centro y texto de predicción.
   - Si no hay movimiento:
     - Reinicia tracking de cruce para evitar conteos inválidos.
   - Dibuja línea de conteo y margen de reset.
   - Dibuja panel lateral con conteo por clase.
   - Calcula y muestra FPS e inferencia promedio.

5. **Finalización**
   - Tecla `q` para salir.
   - Libera cámara, cierra ventanas y serial de Arduino.

---

## 3) Descripción de módulos

### `src/inference.py` — Inferencia del modelo

- Usa `ai_edge_litert.Interpreter` para cargar y ejecutar el modelo TensorFlow Lite.
- Lee `labels.txt` para mapear índice de salida a nombre de clase.
- Preprocesamiento:
  - BGR -> RGB
  - resize al tamaño esperado por el modelo
  - expansión de dimensión a batch `[1, h, w, c]`
- Retorna `(class_name, confidence)`.

### `src/vision.py` — Detección de movimiento y ROI

- Utiliza `cv2.createBackgroundSubtractorMOG2`.
- Aplica limpieza morfológica (`MORPH_OPEN`) para reducir ruido.
- Busca contornos y elige el más grande sobre `min_area`.
- Devuelve:
  - bandera de movimiento,
  - bounding box,
  - centro del objeto.
- `get_roi` extrae región con `padding` para no cortar el objeto.

### `src/color_detector.py` — Clasificación de color para cubos

- Convierte ROI a HSV.
- Evalúa máscaras por rangos de color:
  - rojo (dos rangos por circularidad de tono),
  - verde,
  - azul.
- Cuenta píxeles por color y escoge el dominante.
- Si no supera `min_pixels`, retorna `desconocido`.

### `src/counter.py` — Lógica de conteo por cruce

- Mantiene contador por clase (`class_counting`).
- Usa una línea de conteo central (x o y según orientación).
- Solo cuenta cuando detecta **cruce real** entre frame anterior y actual.
- Protecciones para evitar doble conteo:
  - `already_counted`
  - `margin_reset` (debe alejarse de la línea para volver a contar)
  - `max_salt` (si hay salto grande de posición, reinicia estado)

### `src/arduino_serial.py` — Comunicación serial no bloqueante

- Autodetecta puertos comunes (Arduino/CH340/CP210/ESP32/etc.).
- Usa `queue.Queue` + hilo `worker` para que enviar datos no frene FPS.
- Reintenta conexión y reencola mensaje si se pierde el puerto.
- `send_detection(class_name)` solo encola y retorna rápido.

---

## 4) Integración con Arduino

Código Arduino: `banda-clasificadora-arduino/src/main.cpp`.

- Recibe por serial líneas de texto (`readStringUntil('\n')`).
- Según clase recibida, parpadea LED integrado con patrón distinto:
  - `cubo_rojo`: 1 parpadeo
  - `cubo_verde`: 2 parpadeos
  - `cubo_azul`: 3 parpadeos
  - otro valor: 4 parpadeos

Esto permite validar rápidamente que la clasificación y el envío serial funcionan.

---

## 5) Archivos clave del repositorio

- `/home/runner/work/BandaClasificadora/BandaClasificadora/scripts/main.py`: orquestación completa.
- `/home/runner/work/BandaClasificadora/BandaClasificadora/src/*.py`: módulos de visión, inferencia, conteo y serial.
- `/home/runner/work/BandaClasificadora/BandaClasificadora/model/model.tflite`: modelo para inferencia.
- `/home/runner/work/BandaClasificadora/BandaClasificadora/model/labels.txt`: nombres de clase.
- `/home/runner/work/BandaClasificadora/BandaClasificadora/notebooks/model_train.ipynb`: entrenamiento.
- `/home/runner/work/BandaClasificadora/BandaClasificadora/banda-clasificadora-arduino/`: firmware para microcontrolador.

---

## 6) Notas de ajuste práctico

Parámetros que normalmente se ajustan según cámara/escena:

- `min_area` en `MotionDetector`: sensibilidad de detección de objeto.
- `padding` en ROI: recorte más o menos holgado.
- `min_pixels` en `ColorDetector`: tolerancia de detección de color.
- `margin_reset` y `max_salt` en `ItemCounter`: robustez del conteo.

Si cambias iluminación, distancia o velocidad de la banda, estos valores pueden necesitar calibración.
