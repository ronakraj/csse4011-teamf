#include <Wire.h>

#include "SparkFun_AK9750_Arduino_Library.h" //Use Library Manager or download here: https://github.com/sparkfun/SparkFun_AK9750_Arduino_Library

AK9750 movementSensor; //Hook object to the library
int ir1;
int ir2;
int ir3;
int ir4;
signed long int ir1_temp = 0;
signed long int ir2_temp = 0;
signed long int ir3_temp = 0;
signed long int ir4_temp = 0;
int iterations = 2000;

int tempF;

void setup()
{
  Serial.begin(115200);
  Serial.println("AK9750 Basic Swipe");

  Wire.begin();

  //Turn on sensor
  if (movementSensor.begin() == false)
  {
    Serial.println("Device not found. Check wiring.");
    while (1);
  }

  Serial.println("AK9750 Human Presence Sensor online");

  calibrateBackground();
}

void loop() {
  // put your main code here, to run repeatedly: 
  if (movementSensor.available())
  {
    ir1 = movementSensor.getIR1() - ir1_temp;
    ir2 = movementSensor.getIR2() - ir2_temp;
    ir3 = movementSensor.getIR3() - ir3_temp;
    ir4 = movementSensor.getIR4() - ir4_temp;
    tempF = movementSensor.getTemperatureF();

    movementSensor.refresh(); //Read dummy register after new data is read

    Serial.print("{\"IR1\": ");
    Serial.print(ir1);
    Serial.print(", \"IR2\": ");
    Serial.print(ir2);
    Serial.print(", \"IR3\": ");
    Serial.print(ir3);
    Serial.print(", \"IR4\": ");
    Serial.print(ir4);
    Serial.println("}");

      //Serial.print(ir1);
      //Serial.print(",");
      //Serial.print(ir2);
      //Serial.print(",");
      //Serial.print(ir3);
      //Serial.print(",");
//      Serial.println(ir4);
//      
  }
    delay(100);
}

void calibrateBackground() {
    Serial.println("STARTING CALIBRATION SEQUENCE. PLEASE STANDBY...");
  
  for(int i = 0; i < iterations; i++) {
    ir1 = movementSensor.getIR1();
    ir2 = movementSensor.getIR2();
    ir3 = movementSensor.getIR3();
    ir4 = movementSensor.getIR4();
    movementSensor.refresh(); //Read dummy register after new data is read

    if(iterations > 500) {
      ir1_temp = ir1 + ir1_temp;
      ir2_temp = ir2 + ir2_temp;
      ir3_temp = ir3 + ir3_temp;
      ir4_temp = ir4 + ir4_temp;
    }
    delay(10);
  }

  ir1_temp = ir1_temp / (iterations - 500);
  ir2_temp = ir2_temp / (iterations - 500);
  ir3_temp = ir3_temp / (iterations - 500);
  ir4_temp = ir4_temp / (iterations - 500);

  Serial.println("INITIALISATION COMPLETE. BACKGROUND CALIBRATED.");
}

