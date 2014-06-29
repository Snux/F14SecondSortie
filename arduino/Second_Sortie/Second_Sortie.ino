//Arduino sketch for handling various functions in F-14 Second Sortie
//
// Currently handles the 7 RGB 'Neopixels' for the KILL inserts and
// two 7 segment LED displays.  The code could be tuned for sure, but
// it currently works fine.
//
//Once initialised, the code sits and waits for commands to come in on the serial port
//Incoming commands are 6 bytes long, the first byte gives the directive and the others
//are related data
//
// Directive R, G and B control the neopixels.  Next byte contains the lamp number (0-6), 
// the next four hold the lamp schedule (same as used in pyprocgame for normal lamps
//
// Directive D controls the LED displays.  Next byte specifies which display (0 or 1)
// then the next 4 contain raw data for the segments (one per character


// Included libraries
#include <Wire.h>                 // For i2c control
#include <TimerOne.h>             // Hardware timer
#include "Adafruit_LEDBackpack.h" // i2c LED backpack
#include "Adafruit_GFX.h"         // reguired by above
#include <Adafruit_NeoPixel.h>    // Neopixels

// Which output pin the neopixels chain from
#define PIN 12

// Define the blinky parts 
// 7 neopixels in a chain
Adafruit_NeoPixel strip = Adafruit_NeoPixel(7, PIN, NEO_GRB + NEO_KHZ800);

// 2 7 segment displays
Adafruit_7segment matrix = Adafruit_7segment();
Adafruit_7segment matrix2 = Adafruit_7segment();

// Current state of lamp schedules
volatile unsigned long red[7];
volatile unsigned long green[7];
volatile unsigned long blue[7];
volatile unsigned long sched_reset=0xFFFFFFFF;

// Stored lamp schedules coming in from USB
volatile unsigned long red_stored[7];
volatile unsigned long green_stored[7];
volatile unsigned long blue_stored[7];

void setup() {

  // Clear down the stored schedules, will switch all the lamps off
  byte i;
  for (i=0;i<6;i++) {
    red_stored[i]=0;
    green_stored[i]=0;
    blue_stored[i]=0;
  }
  
  // Setup the serial port, need to find the fastest reliable rate
  Serial.begin(300);

  // Setup the blinky parts
  matrix.begin(0x70);
  matrix2.begin(0x71);
  strip.begin();
  
  // Set the pixel brightness
  strip.setBrightness(128);
  strip.show(); // Initialize all pixels to 'off'

  // Get the hardware timer to count in 1/32 second
  Timer1.initialize(31250);
  
  // and have it call the scheduleProcess routine
  Timer1.attachInterrupt(scheduleProcess);

}

void loop() {
  unsigned long schedule;
  byte byte1, byte2, byte3, byte4, byte5;
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
      case 'R':
      case 'G':
      case 'B':
        schedule = byte2;
        schedule <<= 8;
        schedule = schedule | byte3;
        schedule <<= 8;
        schedule = schedule | byte4;
        schedule <<= 8;
        schedule = schedule | byte5;
        if (command == 'R') red_stored[byte1]=schedule;
        if (command == 'G') green_stored[byte1]=schedule;
        if (command == 'B') blue_stored[byte1]=schedule;
        break;
        
      // 7 seg control  
      case 'D':
        if (byte1 == 0) {
        matrix2.writeDigitRaw(0,byte2);
        matrix2.writeDigitRaw(1,byte3);
        matrix2.writeDigitRaw(3,byte4);
        matrix2.writeDigitRaw(4,byte5);
        matrix2.writeDisplay();
        }
        else {
        matrix.writeDigitRaw(0,byte2);
        matrix.writeDigitRaw(1,byte3);
        matrix.writeDigitRaw(3,byte4);
        matrix.writeDigitRaw(4,byte5);
        matrix.writeDisplay();
        }
        break;
        
    } 
  }
    
}

// Routine called by the hardware timer interrupt
void scheduleProcess() {
  
  // Grab the current (right most) bit of each schedule and send to the relevant pixel
  // then shift each schedule right
  byte i;
  for (i=0;i<7;i++) {
    strip.setPixelColor(i,255*(red[i] & 0x1),255*(green[i] & 0x1),255 * (blue[i] & 0x1));
    red[i] >>= 1;
    green[i] >>= 1;
    blue[i] >>= 1;
  } 

  // Push the result to the pixel chain
  strip.show();
  
  // If we've shifted the sched_reset all the way out, we've done the 32 schedule bits
  // and need to set them up again
  if (sched_reset==0) {
    for (i=0;i<7;i++) {
      red[i]=red_stored[i];
      green[i]=green_stored[i];
      blue[i]=blue_stored[i];
    }
    sched_reset=0xFFFFFFFF;
  }
  else {
    sched_reset >>= 1;
  }
  
}  

// These routines are left in from the Neopixel example.  Might be useful for an attract
// mode or something.  Currently not used.

void rainbow(uint8_t wait) {
  uint16_t i, j;
  uint16_t counter = 1800;
  for(j=0; j<256; j++) {
    for(i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel((i+j) & 255));
    }
    strip.show();
    matrix.println(counter);
    counter--;
    matrix.writeDisplay();
    delay(wait);
  }
}

// Slightly different, this makes the rainbow equally distributed throughout
void rainbowCycle(uint8_t wait) {
  uint16_t i, j;
  uint16_t counter = 4500;
  for(j=0; j<256*5; j++) { // 5 cycles of all colors on wheel
    for(i=0; i< strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel(((i * 256 / strip.numPixels()) + j) & 255));
    }
    strip.show();
    matrix.println(counter);
    counter--;
    matrix.writeDisplay();
    delay(wait);
  }
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  if(WheelPos < 85) {
   return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if(WheelPos < 170) {
   WheelPos -= 85;
   return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
   WheelPos -= 170;
   return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}

