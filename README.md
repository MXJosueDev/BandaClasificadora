# BandaClasificadora

Este proyecto detecta frutas en una banda transportadora usando visión artificial y un modelo TensorFlow Lite. El flujo principal captura video desde una cámara, detecta movimiento, realiza inferencia con el modelo y muestra un conteo por clase en pantalla.

## Requisitos de software

Antes de ejecutar el proyecto asegúrate de tener instalado obligatoriamente:

- Python 3.12.x
- uv
- Una cámara web conectada (o una cámara integrada)
- Opcional: Arduino y puerto serie, si deseas habilitar la comunicación serial

### Instalar uv

Si aún no lo tienes instalado, instálalo primero. En Windows puedes hacerlo con:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Luego verifica que quede disponible ejecutando:

```bash
uv --version
```

## 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd BandaClasificadora
```

## 2. Crear el entorno virtual con uv

Si ya tienes `uv` instalado, no necesitas crear un `venv` manualmente. `uv` puede crear y gestionar el entorno por ti.

Desde la carpeta del proyecto ejecuta:

```bash
uv venv --python 3.12 .venv
uv sync
```

Esto crea el entorno virtual en `.venv` e instala las dependencias definidas en `pyproject.toml`.

Importante: `uv` no activa automáticamente el entorno para cada comando. Si quieres ejecutar el proyecto de forma sencilla, usa `uv run`:

```bash
uv run python scripts/main.py
```

Si prefieres activar el entorno manualmente en Windows, puedes hacerlo con:

```bash
.venv\Scripts\activate
```

## 3. Instalar dependencias

Con `uv`, la instalación queda cubierta por `uv sync`.

## 4. Verificar los archivos del modelo

El proyecto espera encontrar los archivos del modelo en la carpeta `model/`:

- `model/model.tflite`
- `model/labels.txt`

Si alguno de estos archivos falta, la inferencia no podrá ejecutarse.

## 5. Ejecutar el proyecto

El punto de entrada principal es el script:

```bash
python scripts/main.py
```

Al ejecutarlo, el programa te pedirá el índice de la cámara a usar. Si no estás seguro, escribe:

```text
0
```

### Qué hacer durante la ejecución

- Presiona `q` para salir de la ventana de video.
- La interfaz mostrará:
  - el video en vivo,
  - la clase detectada,
  - el nivel de confianza,
  - el conteo total por clase.

## 6. Estructura del proyecto

- `scripts/main.py`: punto de entrada del sistema.
- `src/inference.py`: carga el modelo TensorFlow Lite y realiza inferencia.
- `src/vision.py`: detección de movimiento y región de interés.
- `src/counter.py`: lógica de conteo por clase.
- `src/arduino_serial.py`: comunicación opcional con Arduino.
- `model/`: archivos del modelo entrenado y etiquetas.
- `notebooks/model_train.ipynb`: notebook para entrenar el modelo.

## 7. Solución de problemas

### La cámara no se abre

- Verifica que la cámara esté conectada.
- Prueba con otro índice de cámara, por ejemplo `1`.
- Cierra otras aplicaciones que puedan estar usando la cámara.

### Error al importar TensorFlow o OpenCV

- Asegúrate de estar dentro del entorno virtual.
- Reinstala las dependencias con:

```bash
uv sync
```

### El modelo no carga

- Confirma que los archivos `model/model.tflite` y `model/labels.txt` existan.
- Revisa que la ruta sea correcta desde la raíz del proyecto.

## 9. Resumen rápido

Para arrancar el proyecto normalmente, ejecuta:

```bash
uv venv --python 3.12 .venv
uv sync
uv run python scripts/main.py
```
