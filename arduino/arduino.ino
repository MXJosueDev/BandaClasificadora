#include <Arduino.h>
#include <Servo.h>
#include "config.h"

struct SortingArm {
  Servo motor;
  int pin;
  int angleRepose;
  int angleAction;
  
  int state = 0; // 0 = Reposo, 1 = Cubo en camino, 2 = Empujando
  unsigned long timer = 0;

  void start(int asignedPin, int repose, int action) {
    pin = asignedPin;
    angleRepose = repose;
    angleAction = action;
    motor.attach(pin);
    motor.write(angleRepose);
  }

  void activate() {
    state = 1;                   
    timer = millis();        
  }

  void update() {
    unsigned long tiempoActual = millis();

    // Fase 1
    if (state == 1 && (tiempoActual - timer >= TIEMPO_VIAJE)) {
      motor.write(angleAction);  
      state = 2;                 
      timer = tiempoActual;  
    }
    
    // Fase 2
    else if (state == 2 && (tiempoActual - timer >= TIEMPO_EMPUJE)) {
      motor.write(angleRepose);  
      state = 0;                 
    }
  }
};

SortingArm redArm; // Izquierdo/Rojo
SortingArm blueArm; // Derecho/Azul

void setup() {
  Serial.begin(9600);
  
  redArm.start(PIN_SERVO_ROJO, REPOSO_ROJO, ACCION_ROJO);
  blueArm.start(PIN_SERVO_AZUL, REPOSO_AZUL, ACCION_AZUL);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "cubo_rojo") {
      redArm.activate();
    } 
    else if (command == "cubo_azul") {
      blueArm.activate();
    }
  }

  redArm.update();
  blueArm.update();
}