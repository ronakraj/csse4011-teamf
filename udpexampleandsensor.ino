/*
 * 31 mar 2015
 * This sketch display UDP packets coming from an UDP client.
 * On a Mac the NC command can be used to send UDP. (nc -u 192.168.1.101 2390).
 *
 * Configuration : Enter the ssid and password of your Wifi AP. Enter the port number your server is listening on.
 *
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

#include "SparkFun_AK9750_Arduino_Library.h"

AK9750 xySensor;
AK9750 zxSensor;

#pragma GCC diagnostic ignored "-Wwrite-strings"

#define SDA     0                          // ESP8266-01
#define SCL     2                          // ESP8266-01
#define LED_PIN 5                          // on Sparkfun Thing board

int quadrant = 0;
String s = "";

extern "C" {  //required for read Vdd Voltage
#include "user_interface.h"
  // uint16 readvdd33(void);
}
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

struct sensorRawzx {
  int ir1;
  int ir2;
  int ir3;
  int ir4;
  float temp;
  int prevIr1;
  int prevIr2;
  int prevIr3;
  int prevIr4;
} sensorRawzx;


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

void init_sensor() {
  Wire.begin(SDA, SCL);
  delay(3);
  sensorRaw.prevIr1 = 0;
  sensorRaw.prevIr2 = 0;
  sensorRaw.prevIr3 = 0;
  sensorRaw.prevIr4 = 0;
  sensorRawzx.ir1 = 0;
  sensorRawzx.ir2 = 0;
  sensorRawzx.ir3 = 0;
  sensorRawzx.ir4 = 0;
  incVals.ir1 = 0;
  incVals.ir2 = 0;
  incVals.ir3 = 0;
  incVals.ir4 = 0;
  decVals.ir1 = 0;
  decVals.ir2 = 0;
  decVals.ir3 = 0;
  decVals.ir4 = 0;
  reset_crossings();
  
  if (xySensor.begin() == false)
  {
    Serial.println("xySensor not found. Check wiring.");
   // while(1);
  }

  if (zxSensor.begin(Wire, I2C_SPEED_STANDARD, 0x66) == false) {
    Serial.println("zxSensor not found. Check wiring.");
    //while(1);
  }

}

int crossingThreshold = 40;
int timeThreshold = 0;

int status = WL_IDLE_STATUS;
const char* ssid = "CSSE4011TEAM4";  //  your network SSID (name)
const char* pass = "4011rulez";       // your network password

unsigned int localPort = 12345;      // local port to listen for UDP packets

byte packetBuffer[512]; //buffer to hold incoming and outgoing packets

// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;

void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
  init_sensor();

  // setting up Station AP
  WiFi.begin(ssid, pass);
 
  // Wait for connect to AP
  Serial.print("[Connecting]");
  Serial.print(ssid);
  int tries=0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    tries++;
    if (tries > 30){
      break;
    }
  }
  Serial.println();


printWifiStatus();

  Serial.println("Connected to wifi");
  Serial.print("Udp server started at port ");
  Serial.println(localPort);
  Udp.begin(localPort);
}

void loop()
{
  int noBytes = Udp.parsePacket();
  String received_command = "";
  if (xySensor.available()) {
    sensorRaw.ir1 = xySensor.getIR1();
    sensorRaw.ir2 = xySensor.getIR2();
    sensorRaw.ir3 = xySensor.getIR3();
    sensorRaw.ir4 = xySensor.getIR4();
    sensorRaw.temp = xySensor.getTemperatureF();

    xySensor.refresh(); //Read dummy register after new data is read

    store_crossings();
    reset_old_vals();
  }

  if (zxSensor.available()) {
    sensorRawzx.ir1 = zxSensor.getIR1();
    sensorRawzx.ir2 = zxSensor.getIR2();
    sensorRawzx.ir3 = zxSensor.getIR3();
    sensorRawzx.ir4 = zxSensor.getIR4();
    sensorRawzx.temp = zxSensor.getTemperatureF();

    zxSensor.refresh(); //Read dummy register after new data is read

    //store_crossings();
    //reset_old_vals();
    
  }
 
  //if ( 1 ) {
    Serial.print(millis() / 1000);
    Serial.print(":Packet of ");
    Serial.print(noBytes);
    Serial.print(" received from ");
    Serial.print(Udp.remoteIP());
    Serial.print(":");
    Serial.println(Udp.remotePort());
    // We've received a packet, read the data from it
    Udp.read(packetBuffer,noBytes); // read the packet into the buffer

    // display the packet contents in HEX
    for (int i=1;i<=noBytes;i++)
    {
      Serial.print(packetBuffer[i-1],HEX);
      received_command = received_command + char(packetBuffer[i - 1]);
      if (i % 32 == 0)
      {
        Serial.println();
      }
      else Serial.print(' ');
    } // end for
    Serial.println();
    //192.168.43.223:34268
    if (received_command[0] == 'q') {
        quadrant = received_command[1];
        Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
        //Udp.write("Answer from ESP8266 ChipID#");
        //Udp.print(system_get_chip_id());
        //Udp.write("#IP of ESP8266#");
        
        //Udp.println(WiFi.localIP());
        Udp.print(sensorRaw.ir1);
        Udp.write(",");
        Udp.print(sensorRaw.ir2);
        Udp.write(",");
        Udp.print(sensorRaw.ir3);
        Udp.write(",");
        Udp.print(sensorRaw.ir4);
        Udp.write(",");
        Udp.print(sensorRawzx.ir1);
        Udp.write(",");
        Udp.print(sensorRawzx.ir2);
        Udp.write(",");
        Udp.print(sensorRawzx.ir3);
        Udp.write(",");
        Udp.println(sensorRawzx.ir4);
        Udp.endPacket();
       
        Serial.println(received_command);
        Serial.println();
    } else if (received_command[0] == 'r') {
        if(sensorRaw.ir1 < crossingThreshold && sensorRaw.ir2 < crossingThreshold && sensorRaw.ir3 < crossingThreshold && sensorRaw.ir4 < crossingThreshold) {
          if(crossings.ir1[0] != 0 && crossings.ir2[0] != 0 && crossings.ir3[0] != 0 && crossings.ir4[0] != 0 && crossings.ir1[1] != 0 && crossings.ir2[1] != 0 &&
            crossings.ir3[1] != 0 && crossings.ir4[1] != 0) {
            if(crossings.ir1[0] < (crossings.ir3[0] - timeThreshold) && crossings.ir1[1] < (crossings.ir3[1] - timeThreshold)) {
              // swipe from 1 -> 3 occured
              //Serial.println("Swiped 1 -> 3");
              s = " swipe:13";
            } 
            if(crossings.ir1[0] > (crossings.ir3[0] + timeThreshold) && crossings.ir1[1] > (crossings.ir3[1] + timeThreshold)) {
              // swipe from 3 -> 1 occured
              Serial.println("Swiped 3 -> 1");
              s = " swipe:31";
            }
            if(crossings.ir2[0] < (crossings.ir4[0] - timeThreshold) && crossings.ir2[1] < (crossings.ir4[1] - timeThreshold)) {
              // swipe from 2 -> 4
              Serial.println("Swiped 2 -> 4");
              s = " swipe:24";
            }
            if(crossings.ir2[0] > (crossings.ir4[0] + timeThreshold) && crossings.ir2[1] > (crossings.ir4[1] + timeThreshold)) {
              // swipe from 4 -> 2
              Serial.println("Swiped 4 -> 2");
              s = " swipe:42";
            }
          }
          reset_crossings();
        }
        Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
        Udp.write("quadrant:");
        Udp.print(quadrant);
        Udp.println(s);
        Udp.endPacket();
       
        Serial.println(received_command);
        Serial.println();
        s = "";
    } else {
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("quadrant:");
      Udp.print(quadrant);
      Udp.endPacket();
     
      Serial.println(received_command);
      Serial.println();
    }
   
    /*Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    //Udp.write("Answer from ESP8266 ChipID#");
    //Udp.print(system_get_chip_id());
    //Udp.write("#IP of ESP8266#");
    
    //Udp.println(WiFi.localIP());
    Udp.print(sensorRaw.ir1);
    Udp.write(",");
    Udp.print(sensorRaw.ir2);
    Udp.write(",");
    Udp.print(sensorRaw.ir3);
    Udp.write(",");
    Udp.print(sensorRaw.ir4);
    Udp.write(",");
    Udp.print(sensorRawzx.ir1);
    Udp.write(",");
    Udp.print(sensorRawzx.ir2);
    Udp.write(",");
    Udp.print(sensorRawzx.ir3);
    Udp.write(",");
    Udp.println(sensorRawzx.ir4);
    Udp.endPacket();
   
    Serial.println(received_command);
    Serial.println();
    */
    delay(10);
  //} // end if


}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
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


