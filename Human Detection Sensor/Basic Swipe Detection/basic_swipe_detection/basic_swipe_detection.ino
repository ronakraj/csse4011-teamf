//  AK9752 Human Presence and Movement Sensor - Basic Swipe Detection
//  By: Ronakraj Gosalia


#include <Wire.h>

#include "SparkFun_AK9750_Arduino_Library.h" //Use Library Manager or download here: https://github.com/sparkfun/SparkFun_AK9750_Arduino_Library

AK9750 movementSensor; //Hook object to the library

struct sensorRaw {
  long ir1;
  long ir2;
  long ir3;
  long ir4;
  float temp;
  long prevIr1;
  long prevIr2;
  long prevIr3;
  long prevIr4;
} sensorRaw;

struct sensorOffsets {
  signed long ir1;
  signed long ir2;
  signed long ir3;
  signed long ir4;
} sensorOffsets;

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
  signed long ir1[2];
  signed long ir2[2];
  signed long ir3[2];
  signed long ir4[2];
  int iteration_ir1;
  int iteration_ir2;
  int iteration_ir3;
  int iteration_ir4;
} crossings;

int crossingThreshold = 200;
int timeThreshold = 0;
int iterations = 1000;

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
  } else {
    Serial.println("STARTING CALIBRATION SEQUENCE. PLEASE STANDBY...");
    sensorOffsets.ir1 = 0;
    sensorOffsets.ir2 = 0;
    sensorOffsets.ir3 = 0;
    sensorOffsets.ir4 = 0;
    
    for(int i = 0; i < iterations; i++) {
      sensorRaw.ir1 = movementSensor.getIR1();
      sensorRaw.ir2 = movementSensor.getIR2();
      sensorRaw.ir3 = movementSensor.getIR3();
      sensorRaw.ir4 = movementSensor.getIR4();
      movementSensor.refresh(); //Read dummy register after new data is read
      
      if(iterations > 100) {
        sensorOffsets.ir1 = sensorRaw.ir1 + sensorOffsets.ir1;
        sensorOffsets.ir2 = sensorRaw.ir2 + sensorOffsets.ir2;
        sensorOffsets.ir3 = sensorRaw.ir3 + sensorOffsets.ir3;
        sensorOffsets.ir4 = sensorRaw.ir4 + sensorOffsets.ir4;
      }
      delay(10);
    }
    sensorOffsets.ir1 = sensorOffsets.ir1 / (iterations - 100);
    sensorOffsets.ir2 = sensorOffsets.ir2 / (iterations - 100);
    sensorOffsets.ir3 = sensorOffsets.ir3 / (iterations - 100);
    sensorOffsets.ir4 = sensorOffsets.ir4 / (iterations - 100);
  
    Serial.println("INITIALISATION COMPLETE. BACKGROUND CALIBRATED.");
  }

  Serial.println("AK9750 Human Presence Sensor online");
}

void loop()
{
  if (movementSensor.available())
  {
    sensorRaw.ir1 = movementSensor.getIR1() - sensorOffsets.ir1;
    sensorRaw.ir2 = movementSensor.getIR2() - sensorOffsets.ir2;
    sensorRaw.ir3 = movementSensor.getIR3() - sensorOffsets.ir3;
    sensorRaw.ir4 = movementSensor.getIR4() - sensorOffsets.ir4;
   // sensorRaw.temp = movementSensor.getTemperatureF();

//   Serial.print(sensorRaw.ir1);
//   Serial.print(',');
//   Serial.print(sensorRaw.ir2);
//   Serial.print(',');
//   Serial.print(sensorRaw.ir3);
//   Serial.print(',');
//   Serial.println(sensorRaw.ir4);

    movementSensor.refresh(); //Read dummy register after new data is read

    store_crossings();
    reset_old_vals();

    // event completed
    // RULE BASED CLASSIFIER
    if(sensorRaw.ir1 < crossingThreshold && sensorRaw.ir2 < crossingThreshold && sensorRaw.ir3 < crossingThreshold && sensorRaw.ir4 < crossingThreshold) { 
      if(crossings.ir1[0] != 0 && crossings.ir2[0] != 0 && crossings.ir3[0] != 0 && crossings.ir4[0] != 0 && crossings.ir1[1] != 0 && crossings.ir2[1] != 0 &&
        crossings.ir3[1] != 0 && crossings.ir4[1] != 0) {
        
//        if(crossings.ir1[0] < (crossings.ir3[0] - timeThreshold) && crossings.ir1[1] < (crossings.ir3[1] - timeThreshold)) {
//          // swipe from 1 -> 3 occured
//          Serial.println("Swiped 1 -> 3");
//        } 
//        if(crossings.ir1[0] > (crossings.ir3[0] + timeThreshold) && crossings.ir1[1] > (crossings.ir3[1] + timeThreshold)) {
//          // swipe from 3 -> 1 occured
//          Serial.println("Swiped 3 -> 1");
//        }
//        if(crossings.ir2[0] < (crossings.ir4[0] - timeThreshold) && crossings.ir2[1] < (crossings.ir4[1] - timeThreshold)) {
//          // swipe from 2 -> 4
//          Serial.println("Swiped 2 -> 4");
//        }
//        if(crossings.ir2[0] > (crossings.ir4[0] + timeThreshold) && crossings.ir2[1] > (crossings.ir4[1] + timeThreshold)) {
//          // swipe from 4 -> 2
//          Serial.println("Swiped 4 -> 2");
//        }

        signed long diff_13_s = crossings.ir1[0] - crossings.ir3[0]; // difference between start along 13 axis
        signed long diff_24_s = crossings.ir2[0] - crossings.ir4[0]; // difference between start along 24 axis
        signed long diff_13_f = crossings.ir1[1] - crossings.ir3[1]; // difference between finish along 13 axis
        signed long diff_24_f = crossings.ir2[1] - crossings.ir4[1]; // difference between finish along 24 axis

        
        Serial.print("{\"IR13S\": ");
        Serial.print(diff_13_s);
        Serial.print(",");
        Serial.print(" \"IR24S\": ");
        Serial.print(diff_24_s);
        Serial.print(",");
        Serial.print(" \"IR13F\": ");
        Serial.print(diff_13_f);
        Serial.print(",");
        Serial.print(" \"IR24F\": ");
        Serial.print(diff_24_f);
        Serial.print(",");

//        Serial.print("{\"IR1S\": ");
//        Serial.print(crossings.ir1[0] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR2S\": ");
//        Serial.print(crossings.ir2[0] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR3S\": ");
//        Serial.print(crossings.ir3[0] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR4S\": ");
//        Serial.print(crossings.ir4[0] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR1F\": ");
//        Serial.print(crossings.ir1[1] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR2F\": ");
//        Serial.print(crossings.ir2[1] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR3F\": ");
//        Serial.print(crossings.ir3[1] - crossings.ir1[0]);
//        Serial.print(",");
//        Serial.print(" \"IR4F\": ");
//        Serial.print(crossings.ir4[1] - crossings.ir1[0]);
//        Serial.print(",");
        Serial.print(" \"IR1T\": ");
        Serial.print(crossings.iteration_ir1);
        Serial.print(",");
        Serial.print(" \"IR2T\": ");
        Serial.print(crossings.iteration_ir2);
        Serial.print(",");
        Serial.print(" \"IR3T\": ");
        Serial.print(crossings.iteration_ir3);
        Serial.print(",");
        Serial.print(" \"IR4T\": ");
        Serial.print(crossings.iteration_ir4);
        Serial.println("}");

        reset_crossings();
        }
    }
  }
  delay(10);
}

void store_crossings() {
  if(sensorRaw.prevIr1 < crossingThreshold && sensorRaw.ir1 >= crossingThreshold) {
      if(crossings.iteration_ir1 == 0) { //only store initial rise
        //Serial.println("++ CROSSING 1");
        crossings.ir1[0] = millis();
      }
      crossings.iteration_ir1++;
  } 

  if(sensorRaw.prevIr1 > crossingThreshold && sensorRaw.ir1 <= crossingThreshold) {
    //Serial.println("-- CROSSING 1");
      crossings.ir1[1] = millis();
  } 

  if(sensorRaw.prevIr2 < crossingThreshold && sensorRaw.ir2 >= crossingThreshold) {
      if(crossings.iteration_ir2 == 0) { // only store initial rise
        //Serial.println("++ CROSSING 2");
        crossings.ir2[0] = millis();
      }
      crossings.iteration_ir2++;
  } 

  if(sensorRaw.prevIr2 > crossingThreshold && sensorRaw.ir2 <= crossingThreshold) {
    //Serial.println("-- CROSSING 2");
      crossings.ir2[1] = millis();
  } 
  if(sensorRaw.prevIr3 < crossingThreshold && sensorRaw.ir3 >= crossingThreshold) {
      if(crossings.iteration_ir3 == 0) {
        //Serial.println("++ CROSSING 3");
        crossings.ir3[0] = millis();
      }
      crossings.iteration_ir3++;
  } 

  if(sensorRaw.prevIr3 > crossingThreshold && sensorRaw.ir3 <= crossingThreshold) {
    //Serial.println("-- CROSSING 3");
      crossings.ir3[1] = millis();
  } 
  
  if(sensorRaw.prevIr4 < crossingThreshold && sensorRaw.ir4 >= crossingThreshold) {
      if(crossings.iteration_ir4 == 0) {
        //Serial.println("++ CROSSING 4");
        crossings.ir4[0] = millis();
      }
      crossings.iteration_ir4++;
  } 

  if(sensorRaw.prevIr4 > crossingThreshold && sensorRaw.ir4 <= crossingThreshold) {
    //Serial.println("-- CROSSING 4");
      crossings.ir4[1] = millis();
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

