# BandaClasificadora

## Requisitos de software

Antes de ejecutar el proyecto asegúrate de tener instalado obligatoriamente:

- uv
- Una cámara web conectada (o una cámara integrada)

### Instalar uv

Si aún no lo tienes instalado, instálalo primero. 

[Página Oficial](https://docs.astral.sh/uv/getting-started/installation/) 

## Pasos para instalacion (Solo primera vez)

### 1. Clonar el repositorio (o descomprimir la carpeta)

```bash
git clone https://github.com/MXJosueDev/BandaClasificadora
```

### 2. Crear el entorno virtual con uv

```bash
uv venv --python 3.12 .venv
```

Esto crea el entorno virtual en `.venv` e instala las dependencias definidas en `pyproject.toml`.

### 3. Instalar dependencias

```bash
uv sync
```
### 4. ¡Listo!

## Ejecutar el proyecto

El punto de entrada principal es el script:

```bash
uv run python scripts/main.py
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

## Compilar el proyecto

```bash
pyinstaller main.spec
```

## Estructura del proyecto

- `scripts/main.py`: punto de entrada del sistema.
- `src/inference.py`: carga el modelo TensorFlow Lite y realiza inferencia.
- `src/vision.py`: detección de movimiento y región de interés.
- `src/counter.py`: lógica de conteo por clase.
- `src/arduino_serial.py`: comunicación opcional con Arduino.
- `model/`: archivos del modelo entrenado y etiquetas.
- `notebooks/model_train.ipynb`: notebook para entrenar el modelo.

## Solución de problemas

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

## Resumen rápido

Para arrancar el proyecto normalmente, ejecuta:

```bash
uv venv --python 3.12 .venv
uv sync
uv run python scripts/main.py
```
