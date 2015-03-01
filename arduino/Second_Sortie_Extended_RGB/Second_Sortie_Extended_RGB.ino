//Arduino sketch for handling 2 strings of RGB lamps, one for GI and one for inserts
//
//Once initialised, the code sits and waits for commands to come in on the serial port
//Incoming commands are 6 bytes long, the first byte gives the directive and the others
//are related data
//
// Directive W,C,Y,M,R, G and B control the neopixels.  Next byte contains the lamp number (0-16), 
// the next four hold the lamp schedule (same as used in pyprocgame for normal lamps
//

// Included libraries
#include <TimerOne.h>             // Hardware timer
#include <Adafruit_NeoPixel.h>

// Which output pin the lamps chain from
#define DATA_PIN_INSERTS 11
#define NUM_LEDS_INSERTS 16

#define DATA_PIN_GI 13
#define NUM_LEDS_GI 50

Adafruit_NeoPixel inserts = Adafruit_NeoPixel(NUM_LEDS_INSERTS,DATA_PIN_INSERTS,NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel gi = Adafruit_NeoPixel(NUM_LEDS_GI,DATA_PIN_GI,NEO_RGB + NEO_KHZ800);

// Current state of lamp schedules
volatile unsigned long sched[NUM_LEDS_INSERTS];
volatile unsigned long colour[NUM_LEDS_INSERTS];
volatile unsigned long lamp_index[NUM_LEDS_INSERTS];

// Holds data for the counters when used.




void setup() {
  

  // Clear down the schedules, will switch all the lamps off
  byte i;
  for (i=0;i<NUM_LEDS_INSERTS;i++) {
    colour[i]=0;
    sched[i]=0;
    lamp_index[i]=0x1;
  }
  
  
  // Setup the serial port, need to find the fastest reliable rate
  Serial.begin(19200);

  inserts.begin();
  gi.begin();


  // Get the hardware timer to count in 1/32 second
  Timer1.initialize(31250);
  
  // and have it call the scheduleProcess routine
  Timer1.attachInterrupt(scheduleProcess);
  

}

void loop() {
  unsigned long schedule, this_colour;
  byte i,byte1, byte2, byte3, byte4, byte5;
  char command;
  
  // Each time around, take a look at the serial (USB) buffer and see if we have at least 6 bytes waiting which is
  // enough for a command
  if (Serial.available() >= 6) {
    // Grab the command
    command = Serial.read();
    // and the next 5 bytes
    byte1 = Serial.read(); byte2 = Serial.read(); byte3 = Serial.read(); byte4 = Serial.read(); byte5 = Serial.read();
    
    // Take action depending on the command
    switch (command) {
      
      // Pixel control
      case 'R':  //Red
      case 'G':  //Green
      case 'B':  //Blue
      case 'W':  //White
      case 'C':  //Cyan
      case 'M':  //Magenta
      case 'Y':  //Yellow

        
  
        schedule = byte2;
        schedule <<= 8;
        schedule = schedule | byte3;
        schedule <<= 8;
        schedule = schedule | byte4;
        schedule <<= 8;
        schedule = schedule | byte5;
        
        
        switch(command) {
            case 'R':
                this_colour = 0xFF0000;
                break;
                
            case 'G':
                this_colour = 0x00FF00;
                break;
            
            case 'B':
                this_colour = 0x0000FF;
                break;
            
            case 'Y':
                this_colour = 0xFFFF00;
                break;
            
            case 'M':
                this_colour = 0xFF00FF;
                break;
            
            case 'C':
                this_colour = 0x00FFFF;
                break;
            
            case 'W':
                this_colour = 0xFFFFFF;
                break;
                
        }
        // If the lamp number is one at the top, then it's actually the GI so change the
        // whole GI string to that colour
        if (byte1 == NUM_LEDS_INSERTS) {
            for (i=0;i<NUM_LEDS_GI;i++) {
              // If there was something in the schedule, switch the lamps on to the colour given, otherwise all off
              if (schedule) 
                 gi.setPixelColor(i,this_colour);
              else 
                 gi.setPixelColor(i,0);
            }
            gi.show();
        }
        else {
          // Reset the schedule index for this lamp back to the start
          lamp_index[byte1]=0x1;
          sched[byte1]=schedule;
          colour[byte1]=this_colour;
        }
        break;

      
    }
  }          
 }
    


// Routine called by the hardware timer interrupt
void scheduleProcess() {
  static byte i;
  
  
  // Grab the current bit of each schedule and send to the relevant pixel
  for (i=0;i<NUM_LEDS_INSERTS;i++) {
     // If the bit is set, switch the colourm, otherwise switch it off
     if (sched[i] & lamp_index[i])
       inserts.setPixelColor(i,colour[i]);
     else
       inserts.setPixelColor(i,0);
     lamp_index[i] <<= 1;
     if (lamp_index[i]==0)
       lamp_index[i]=0x1;
  }
  inserts.show();


}  

