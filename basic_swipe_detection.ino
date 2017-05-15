/*
  AK9752 Human Presence and Movement Sensor - Basic Swipe Detection
  By: Ronakraj Gosalia
*/

#include <Wire.h>

#include "SparkFun_AK9750_Arduino_Library.h" //Use Library Manager or download here: https://github.com/sparkfun/SparkFun_AK9750_Arduino_Library

AK9750 movementSensor; //Hook object to the library

struct sensorRaw {
  int ir1;
  int ir2;
  int ir3;
  int ir4;
  float temp;
  int prevIr1;
  int prevIr2;
  int prevIr3;
  int prevIr4;
} sensorRaw;

struct incVals {
  int ir1;
  int ir2;
  int ir3;
  int ir4;
} incVals;

struct decVals {
  int ir1;
  int ir2;
  int ir3;
  int ir4;
} decVals;

struct crossings {
  unsigned long ir1[2];
  unsigned long ir2[2];
  unsigned long ir3[2];
  unsigned long ir4[2];
  int iteration_ir1;
  int iteration_ir2;
  int iteration_ir3;
  int iteration_ir4;
} crossings;

int crossingThreshold = 100;
int timeThreshold = 5000;

void setup()
{
  Serial.begin(115200);
  Serial.println("AK9750 Basic Swipe");

  Wire.begin();

  // default values
  sensorRaw.prevIr1 = 0;
  sensorRaw.prevIr2 = 0;
  sensorRaw.prevIr3 = 0;
  sensorRaw.prevIr4 = 0;
  incVals.ir1 = 0;
  incVals.ir2 = 0;
  incVals.ir3 = 0;
  incVals.ir4 = 0;
  decVals.ir1 = 0;
  decVals.ir2 = 0;
  decVals.ir3 = 0;
  decVals.ir4 = 0;
  reset_crossings();
  
  //Turn on sensor
  if (movementSensor.begin() == false)
  {
    Serial.println("Device not found. Check wiring.");
    while (1);
  }

  Serial.println("AK9750 Human Presence Sensor online");
}

void loop()
{
  if (movementSensor.available())
  {
    sensorRaw.ir1 = movementSensor.getIR1();
    sensorRaw.ir2 = movementSensor.getIR2();
    sensorRaw.ir3 = movementSensor.getIR3();
    sensorRaw.ir4 = movementSensor.getIR4();
    sensorRaw.temp = movementSensor.getTemperatureF();

    movementSensor.refresh(); //Read dummy register after new data is read

    // swipe detection algorithm
    // first checking for left ot right swipe
    // sensor 2 should experience increasing values until threshold, then decreasing values
    // sensor 3 should also experience increasing values until threshold, then decreasing values

    // left sensor received increased signal
//    signed int diffIr1 = sensorRaw.ir1 - sensorRaw.prevIr1;
//    signed int diffIr2 = sensorRaw.ir2 - sensorRaw.prevIr2;
//    signed int diffIr3 = sensorRaw.ir3 - sensorRaw.prevIr3;
//    Serial.print(sensorRaw.ir1);
//    Serial.print(",");
//    Serial.print(sensorRaw.ir2);
//    Serial.print(",");
//    Serial.print(sensorRaw.ir3);
//    Serial.print(",");
//    Serial.println(sensorRaw.ir4);

    store_crossings();
    reset_old_vals();

    // event completed
    if(sensorRaw.ir1 < crossingThreshold && sensorRaw.ir2 < crossingThreshold && sensorRaw.ir3 < crossingThreshold && sensorRaw.ir4 < crossingThreshold) {
      if(crossings.ir1[0] != 0 && crossings.ir2[0] != 0 && crossings.ir3[0] != 0 && crossings.ir4[0] != 0 && crossings.ir1[1] != 0 && crossings.ir2[1] != 0 &&
        crossings.ir3[1] != 0 && crossings.ir4[1] != 0) {
        if(crossings.ir1[0] < (crossings.ir3[0] - timeThreshold) && crossings.ir1[1] < (crossings.ir3[1] - timeThreshold)) {
          // swipe from 1 -> 3 occured
          Serial.println("Swiped 1 -> 3");
        } 
        if(crossings.ir1[0] > (crossings.ir3[0] + timeThreshold) && crossings.ir1[1] > (crossings.ir3[1] + timeThreshold)) {
          // swipe from 3 -> 1 occured
          Serial.println("Swiped 3 -> 1");
        }
        if(crossings.ir2[0] < (crossings.ir4[0] - timeThreshold) && crossings.ir2[1] < (crossings.ir4[1] - timeThreshold)) {
          // swipe from 2 -> 4
          Serial.println("Swiped 2 -> 4");
        }
        if(crossings.ir2[0] > (crossings.ir4[0] + timeThreshold) && crossings.ir2[1] > (crossings.ir4[1] + timeThreshold)) {
          // swipe from 4 -> 2
          Serial.println("Swiped 4 -> 2");
        }
      }

//      Serial.print("IR1[0]: ");
//      Serial.print(crossings.ir1[0]);
//      Serial.print(" IR1[1]: ");
//      Serial.print(crossings.ir1[1]);
//      Serial.print(" IR3[0]: ");
//      Serial.print(crossings.ir3[0]);
//      Serial.print(" IR3[1]: ");
//      Serial.println(crossings.ir3[1]);
      reset_crossings();
    }
//    if(diffIr1 > threshold) {
//       incVals.ir1++;
//    } else if(diffIr1 < -threshold) {
//      decVals.ir1++;
//    } else {
//      if(incVals.ir1 > 7 && incVals.ir1 < 30) {
//        Serial.print("IR1 INC: ");
//        Serial.print(incVals.ir1);
//        Serial.print(" \tIR1 DEC: ");
//        Serial.print(decVals.ir1);
//        Serial.println("\t");
//      }
//      incVals.ir1 = 0;
//      decVals.ir1 = 0;
//    }
//
//    if(diffIr3 > threshold) {
//      incVals.ir3++;
//    } else if(diffIr3 < -threshold) {
//      decVals.ir3++;
//    } else if(incVals.ir3 == decVals.ir3) {
//      //if(incVals.ir3 > 7 && incVals.ir3 < 30) {
//        Serial.print("IR3 INC: ");
//        Serial.print(incVals.ir3);
//        Serial.print(" \tIR3 DEC: ");
//        Serial.print(decVals.ir3);
//        Serial.println("\t");
//      //}
//      incVals.ir3 = 0;
//      decVals.ir3 = 0;
//    }
    
  }

  delay(1);
}

void store_crossings() {
  if(sensorRaw.prevIr1 < crossingThreshold && sensorRaw.ir1 >= crossingThreshold) {
      crossings.ir1[0] = micros();
  } 

  if(sensorRaw.prevIr1 > crossingThreshold && sensorRaw.ir1 <= crossingThreshold) {
      crossings.ir1[1] = micros();
  } 

  if(sensorRaw.prevIr2 < crossingThreshold && sensorRaw.ir2 >= crossingThreshold) {
      crossings.ir2[0] = micros();
  } 

  if(sensorRaw.prevIr2 > crossingThreshold && sensorRaw.ir2 <= crossingThreshold) {
      crossings.ir2[1] = micros();
  } 
  if(sensorRaw.prevIr3 < crossingThreshold && sensorRaw.ir3 >= crossingThreshold) {
      crossings.ir3[0] = micros();
  } 

  if(sensorRaw.prevIr3 > crossingThreshold && sensorRaw.ir3 <= crossingThreshold) {
      crossings.ir3[1] = micros();
  } 
  
  if(sensorRaw.prevIr4 < crossingThreshold && sensorRaw.ir4 >= crossingThreshold) {
      crossings.ir4[0] = micros();
  } 

  if(sensorRaw.prevIr4 > crossingThreshold && sensorRaw.ir4 <= crossingThreshold) {
      crossings.ir4[1] = micros();
  } 
}

void reset_old_vals() {
  sensorRaw.prevIr1 = sensorRaw.ir1;
  sensorRaw.prevIr2 = sensorRaw.ir2;
  sensorRaw.prevIr3 = sensorRaw.ir3;
  sensorRaw.prevIr4 = sensorRaw.ir4;
}

void reset_crossings() {
  crossings.ir1[0] = 0;
  crossings.ir1[1] = 0;
  crossings.ir2[0] = 0;
  crossings.ir2[1] = 0;
  crossings.ir3[0] = 0;
  crossings.ir3[1] = 0;
  crossings.ir4[0] = 0;
  crossings.ir4[1] = 0;
  crossings.iteration_ir1 = 0;
  crossings.iteration_ir2 = 0;
  crossings.iteration_ir3 = 0;
  crossings.iteration_ir4 = 0;
}

