//Arduino sketch for handling various functions in F-14 Second Sortie
//
// TO DO - add code to allow the alphanumeric displays to be used as counters to.
//       - add some error handling.
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
// Directives D controls the LED displays with raw data.  Next byte specifies which display (0 - 5)
// then the next 4 contain raw data for the segments (one per character
//
// Directive C runs a counter.  Next byte signifies which display.  Then start count, up/down, limit, ticks per count
//
// Directive N will send a number to the numeric displays.  Next byte signifies which display.  Next 2 bytes contain number.
//
// Directive A will send an alphanumeric string to one of the A/N displays.  Next byte specifies display.  Next 4 contain string
//
// Directive Q will send the value of a counter back to the PC.  Next byte contains the counter number.

//Code version number
int CODE_VERSION = 2;

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

// 4 alphanumeric displays
Adafruit_AlphaNum4 alpha4[4] = Adafruit_AlphaNum4();

// 2 numeric displays
Adafruit_7segment numeric4[2] = Adafruit_7segment();

// Current state of lamp schedules
volatile unsigned long red[7];
volatile unsigned long green[7];
volatile unsigned long blue[7];
volatile unsigned long sched_reset=0xFFFFFFFF;

// Stored lamp schedules coming in from USB
volatile unsigned long red_stored[7];
volatile unsigned long green_stored[7];
volatile unsigned long blue_stored[7];


// Holds data for the counters when used.

volatile int  count_display[6],         // The value of the counter for the display, if being used.
              count_limit[6],           // If we're counting, what are we aiming for?
              count_direction[6];
volatile boolean count_active[6];       // Is the specific counter active?
volatile byte count_ticks_counter[6],   // If we're counting, how many ticks on this one so far?
              count_ticks_per_count[6]; // If we're counting, how many 1/32 ticks per count?
              
volatile byte count_ticks;              // 1/32 second counter, updated by hardware timer interrupt


void setup() {
  
  // Initialise the tick counter
  count_ticks = 0;

  // Clear down the stored schedules, will switch all the lamps off
  byte i;
  for (i=0;i<6;i++) {
    red_stored[i]=0;
    green_stored[i]=0;
    blue_stored[i]=0;
  }

  // Also set all the displays to non-counting, reset the values
  for (i=0;i<5;i++) {
    count_display[i]=0;
    count_limit[i]=0;
    count_ticks_per_count[i]=0;
    count_active[i]=false;
    count_direction[i]=0;
  }
  
  // Setup the serial port, need to find the fastest reliable rate
  Serial.begin(9600);

  // Initialise the displays and neopixels
  numeric4[0].begin(0x70);
  numeric4[1].begin(0x71);
  alpha4[0].begin(0x75);
  alpha4[1].begin(0x73);
  alpha4[2].begin(0x72);
  alpha4[3].begin(0x74);
  strip.begin();
  
  

  boot_display();
  
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
  byte i;

  // Each time around, take a look at the serial (USB) buffer and see if we have at least 6 bytes waiting which is
  // enough for a command
  if (Serial.available() >= 6) {
    // Grab the command
    command = Serial.read();
    // and the next 5 bytes
    byte1 = Serial.read(); byte2 = Serial.read(); byte3 = Serial.read(); byte4 = Serial.read(); byte5 = Serial.read();
    
    // Take action depending on the command
    switch (command) {
      
      // Set display counting
      case 'C':
        count_limit[byte1] = byte3 * 256 + byte4;
        count_active[byte1] = true;
        if (byte2 == 0) count_direction[byte1] = 1;
        else count_direction[byte1] = -1;
        count_ticks_per_count[byte1] = byte5;
        count_ticks_counter[byte1]=0;
        break;
      
      // Set display to a numeric value
      case 'N':
        count_display[byte1] = byte2 * 256 + byte3;
        count_active[byte1] = false;
        if (byte1 < 2) {
          numeric4[byte1].print(count_display[byte1],DEC);
          numeric4[byte1].writeDisplay();
        } else {
          // TO - DO
        }
        break;

      // Add or subtract a value to a counter
      case 'I':
        if (byte2 == 0) {
          count_display[byte1] += byte3 * 256 + byte4;
        } else {
          count_display[byte1] -= byte3 * 256 + byte4;
        }
        numeric4[byte1].print(count_display[byte1],DEC);
        numeric4[byte1].writeDisplay();
        break;


      // Write data raw
      case 'D':
        // Getting raw data, so turn any possible count off
        count_active[byte1]=false;
        count_display[byte1]=0;
        count_direction[byte1]=0;
        if (byte1 < 2) {
          numeric4[byte1].writeDigitRaw(0,byte2);
          numeric4[byte1].writeDigitRaw(1,byte3);
          numeric4[byte1].writeDigitRaw(3,byte4);
          numeric4[byte1].writeDigitRaw(4,byte5);
          numeric4[byte1].writeDisplay();
        }
        else {
          // TO DO
        }
        break;

      // Write data alphanumeric
      case 'A':
        // Getting alphanumeric data, so turn any possible count off
        count_active[byte1]=false;
        count_display[byte1]=0;
        count_direction[byte1]=0;
        alpha4[byte1 - 2].writeDigitAscii(0,byte2);
        alpha4[byte1 - 2].writeDigitAscii(1,byte3);
        alpha4[byte1 - 2].writeDigitAscii(2,byte4);
        alpha4[byte1 - 2].writeDigitAscii(3,byte5);
        alpha4[byte1 - 2].writeDisplay();
        break;


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

      // PC is queerying the value of a counter - sent it back up the serial line in 2 bytes
      case 'Q':
        Serial.write('Q'+char(count_display[byte1] / 256)+char(count_display[byte1] % 256));
        break;
      
    }
    // Throw a character back to the game, so it knows we're ready for some more
    Serial.write('X');
    }
    
    // If we have a display performing an active count, then process it

    for (i=0;i<2;i++) {
      if (count_active[i]) {
        if (count_ticks_counter[i] >= count_ticks_per_count[i]) {
          count_ticks_counter[i] = 0;
          if (count_display[i] == count_limit[i]) {
            count_active[i] = false;
          }
          if (i < 2) {
            numeric4[i].print(count_display[i],DEC);
            numeric4[i].writeDisplay();
          } else {
          }
          count_display[i] += count_direction[i];
        } 
      }
    }
        
          
 }
    


// Routine called by the hardware timer interrupt
void scheduleProcess() {
  
  // Increment the tick counter
  count_ticks_counter[0] ++;
  count_ticks_counter[1] ++;  
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

// Throw something on the display to start with
void boot_display() {
  int i;
  // Put the identifier for each display on the display for short while
  for (i=0;i<6;i++) {
    if (i < 2) {
      numeric4[i].print(i,DEC);
      numeric4[i].writeDisplay();
    } else {
      alpha4[i-2].clear();
      alpha4[i-2].writeDigitAscii(3, char(i+48));
      alpha4[i-2].writeDisplay();
    }
  }
  
  delay(500);
  numeric4[0].writeDigitRaw(0,B01110001);  //F
  numeric4[0].writeDigitRaw(1,B01000000);  //-
  numeric4[0].writeDigitRaw(3,B00000110);  //1
  numeric4[0].writeDigitRaw(4,B01100110);  //4
  numeric4[1].print(CODE_VERSION,DEC);
  numeric4[0].writeDisplay();
  numeric4[1].writeDisplay();
  alpha4[0].writeDigitAscii(0,'C');
  alpha4[0].writeDigitAscii(1,'o');
  alpha4[0].writeDigitAscii(2,'d');
  alpha4[0].writeDigitAscii(3,'e');
  alpha4[1].writeDigitAscii(0,'V');
  alpha4[1].writeDigitAscii(1,'e');
  alpha4[1].writeDigitAscii(2,'r');
  alpha4[1].writeDigitAscii(3,'s');
  alpha4[2].writeDigitAscii(0,'B');
  alpha4[2].writeDigitAscii(1,'o');
  alpha4[2].writeDigitAscii(2,'o');
  alpha4[2].writeDigitAscii(3,'t');
  alpha4[3].clear();
  alpha4[3].writeDigitAscii(2,'O');
  alpha4[3].writeDigitAscii(3,'K');
  for (i=0;i<4;i++) {
    alpha4[i].writeDisplay();
  }
  //delay(500);
  //for (i=0;i<4;i++) {
  //  alpha4[i].clear();
  //  alpha4[i].writeDisplay();
  //}
  

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

