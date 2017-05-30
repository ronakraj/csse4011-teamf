import processing.serial.*;

Serial myPort;        // The serial port
int xPos = 1;         // horizontal position of the graph
float inByte1 = 0;
float inByte2 = 0;
float inByte3 = 0;
float inByte4 = 0;

void setup () {
  // set the window size:
  size(800, 600);


  // I know that the first port in the serial list on my mac
  // is always my  Arduino, so I open Serial.list()[0].
  // Open whatever port is the one you're using.
  myPort = new Serial(this, "COM8", 115200);

  // don't generate a serialEvent() unless you get a newline character:
  myPort.bufferUntil('\n');

  // set inital background:
  background(0);
}
void draw () {
  // draw the line:
  stroke(76, 218, 255);
  line(xPos, height, xPos, height - inByte1);
  
  stroke(255, 205, 53);
  line(xPos, height, xPos, height - inByte2);
  
  stroke(255, 10, 0);
  line(xPos, height, xPos, height - inByte3);
  
  stroke(0, 255, 50);
  line(xPos, height, xPos, height - inByte4);

  // at the edge of the screen, go back to the beginning:
  if (xPos >= width) {
    xPos = 0;
    background(0);
  } else {
    // increment the horizontal position:
    xPos++;
  }
}


void serialEvent (Serial myPort) {
  // get the ASCII string:
  String inString = myPort.readStringUntil('\n');

  if (inString != null) {
    // trim off any whitespace:
    inString = trim(inString);
    println(inString);
    
    String tempValues[] = split(inString, ',');
    
    String received1 = tempValues[0];
    String received2 = tempValues[1];
    String received3 = tempValues[2];
    String received4 = tempValues[3];
    
    // convert to an int and map to the screen height:
    int rec = int(received1);
    if(rec > 0) {
      inByte1 = map(rec, 0, 3000, 0, height);
    }
    
    rec = int(received2);
    if(rec > 0) {
      inByte2 = map(rec, 0, 3000, 0, height);
    }
    
    rec = int(received3);
    if(rec > 0) {
      inByte3 = map(rec, 0, 3000, 0, height);
    }
    
    rec = int(received4);
    if(rec > 0) {
      inByte4 = map(rec, 0, 3000, 0, height);
    }
  }
  
}