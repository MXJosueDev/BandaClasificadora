#ifndef CONFIG_H
#define CONFIG_H

// --- PINES ---
const int PIN_SERVO_ROJO = 9;  // Brazo para el cubo ROJO
const int PIN_SERVO_AZUL = 10;   // Brazo para el cubo AZUL

// Brazo Izquierdo (Rojo)
const int REPOSO_ROJO = 0;   // Paralelo a la banda
const int ACCION_ROJO = 90;  // Cruzado sobre la banda

// Brazo Derecho (Azul)
const int REPOSO_AZUL = 180; // Paralelo a la banda
const int ACCION_AZUL = 90;  // Cruzado sobre la banda

// --- TIEMPOS (en milisegundos) ---
const unsigned long TIEMPO_VIAJE = 3000;  // Tiempo que tarda el cubo de la cámara al brazo
const unsigned long TIEMPO_EMPUJE = 1000; // Tiempo que el brazo se queda extendido

#endif