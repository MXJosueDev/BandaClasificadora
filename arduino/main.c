#include <Servo.h>

Servo servoRojo;
Servo servoVerde;
Servo servoAzul;

const int pinServoRojo = 9;
const int pinServoVerde = 10;
const int pinServoAzul = 11;

void setup()
{
  Serial.begin(9600);

  servoRojo.attach(pinServoRojo);
  servoVerde.attach(pinServoVerde);
  servoAzul.attach(pinServoAzul);

  servoRojo.write(0);
  servoVerde.write(0);
  servoAzul.write(0);
}

void loop()
{
  if (Serial.available() > 0)
  {
    String comando = Serial.readStringUntil('\n');

    comando.trim();

    if (comando == "cubo_rojo")
    {
      accionarServo(servoRojo);
    }
    else if (comando == "cubo_verde")
    {
      accionarServo(servoVerde);
    }
    else if (comando == "cubo_azul")
    {
      accionarServo(servoAzul);
    }
    else
    {
    }
  }
}

void accionarServo(Servo &miServo)
{
  miServo.write(90); // 90 grados
  delay(1000);
  miServo.write(0);
}