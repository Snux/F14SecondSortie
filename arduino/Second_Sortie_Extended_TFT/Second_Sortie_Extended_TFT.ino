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
// Directive W,C,Y,M,R, G and B control the neopixels.  Next byte contains the lamp number (0-16), 
// the next four hold the lamp schedule (same as used in pyprocgame for normal lamps
//
// Directives D controls the LED displays with raw data.  Next byte specifies which display (0 - 5)
// then the next 4 contain raw data for the segments (one per character
//
// Directive T runs a counter.  Next byte signifies which display.  Then start count, up/down, limit, ticks per count
//
// Directive N will send a number to the numeric displays.  Next byte signifies which display.  Next 2 bytes contain number.
//
// Directive A will send an alphanumeric string to one of the A/N displays.  Next byte specifies display.  Next 4 contain string
//
// Directive Q will send the value of a counter back to the PC.  Next byte contains the counter number.
//
// Directive E will blank a display
//
// Directive S controls the radar insert.  Next byte flags red, next flags green, next flags rotate

//Code version number
int CODE_VERSION = 2;

// Included libraries
#include <Wire.h>                 // For i2c control
#include <TimerOne.h>             // Hardware timer

#include "Adafruit_LEDBackpack.h" // i2c LED backpack

#include "Adafruit_GFX.h"         // reguired by above
#include <Adafruit_NeoPixel.h>    // Neopixels
#include <SPI.h>
#include <SD.h>
#include "Adafruit_HX8357.h"


// Which output pin the neopixels chain from
#define RGB_COUNT 16

// Define the blinky parts 
// 16 FAST RGB LEDs on pin 11
Adafruit_NeoPixel strip = Adafruit_NeoPixel(RGB_COUNT, 11, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel GI = Adafruit_NeoPixel(30, 11, NEO_GRB + NEO_KHZ800);
// A 16 pixel Neopixel ring for the radar
Adafruit_NeoPixel radar = Adafruit_NeoPixel(16, 7);

#define TFT_DC 9
#define TFT_CS 10
#define SD_CS 4
#define TFT_RST 8
// Use hardware SPI (on Uno, #13, #12, #11) and the above for CS/DC
Adafruit_HX8357 tft = Adafruit_HX8357(TFT_CS, TFT_DC, TFT_RST);



// 4 alphanumeric displays
Adafruit_AlphaNum4 alpha4[4] = Adafruit_AlphaNum4();

// 2 numeric displays
//Adafruit_7segment numeric4[2] = Adafruit_7segment();

// Current state of lamp schedules
volatile unsigned long red[RGB_COUNT];
volatile unsigned long green[RGB_COUNT];
volatile unsigned long blue[RGB_COUNT];
volatile unsigned long lamp_index[RGB_COUNT];

// Is the radar insert green or red (otherwise off) and is it spinning?
volatile boolean radar_green, radar_red, radar_blue,radar_spin;

// Holds data for the counters when used.

volatile int  count_display[6],         // The value of the counter for the display, if being used.
              count_limit[6],           // If we're counting, what are we aiming for?
              count_direction[6];
volatile boolean count_active[6];       // Is the specific counter active?
volatile byte count_ticks_counter[6],   // If we're counting, how many ticks on this one so far?
              count_ticks_per_count[6]; // If we're counting, how many 1/32 ticks per count?
              
volatile byte count_ticks;              // 1/32 second counter, updated by hardware timer interrupt
volatile uint8_t  offset   = 0; // position of radar spin

uint16_t read16(File &f);
uint32_t read32(File &f);

void setup() {
  
  // Initialise the tick counter
  count_ticks = 0;

  // Initial state for the radar insert - green and spinning
  radar_green = true;
  radar_red = false;
  radar_blue = false;
  radar_spin = true;

  // Clear down the schedules, will switch all the lamps off
  byte i;
  for (i=0;i<RGB_COUNT-1;i++) {
    red[i]=0;
    green[i]=0;
    blue[i]=0;
    lamp_index[i]=0x1;
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
  Serial.begin(19200);

  // Initialise the displays and neopixels
  //numeric4[0].begin(0x70);
  //numeric4[1].begin(0x71);
  //alpha4[0].begin(0x75);
  //alpha4[1].begin(0x73);
  //alpha4[2].begin(0x72);
  //alpha4[3].begin(0x74);
  tft.begin(HX8357D);
  strip.begin();
  radar.begin();
Serial.print("Initializing SD card...");
  if (!SD.begin(SD_CS)) {
    Serial.println("failed!");
  }
  Serial.println("OK!");
  
  

  boot_display();
  
  // Set the pixel brightness for playfield inserts
  strip.setBrightness(128);
  strip.show(); // Initialize all pixels to 'off'

  // Set the pixel brightness for the radar
  radar.setBrightness(128);
  radar.show(); // Initialize all pixels to 'off'


  // Get the hardware timer to count in 1/32 second
  Timer1.initialize(31250);
  
  // and have it call the scheduleProcess routine
  Timer1.attachInterrupt(scheduleProcess);
  

}

void loop() {
  unsigned long schedule;
  byte byte1, byte2, byte3, byte4, byte5;
  char command;
  byte i,j;
  
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
      case 'T':
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
//          numeric4[byte1].print(count_display[byte1],DEC);
//          numeric4[byte1].writeDisplay();
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
//        numeric4[byte1].print(count_display[byte1],DEC);
//        numeric4[byte1].writeDisplay();
        break;


      // Insert control radar
      case 'S':
        radar_red = byte1;
        radar_green = byte2;
        radar_blue = byte3;
        radar_spin = byte4;
        break;
        
      // Write data raw
      case 'D':
        // Getting raw data, so turn any possible count off
        count_active[byte1]=false;
        count_display[byte1]=0;
        count_direction[byte1]=0;
        if (byte1 < 2) {
//        numeric4[byte1].writeDigitRaw(0,byte2);
//        numeric4[byte1].writeDigitRaw(1,byte3);
//        numeric4[byte1].writeDigitRaw(3,byte4);
//        numeric4[byte1].writeDigitRaw(4,byte5);
 //       numeric4[byte1].writeDisplay();
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
//      alpha4[byte1 - 2].writeDigitAscii(0,byte2);
//      alpha4[byte1 - 2].writeDigitAscii(1,byte3);
//      alpha4[byte1 - 2].writeDigitAscii(2,byte4);
//      alpha4[byte1 - 2].writeDigitAscii(3,byte5);
//      alpha4[byte1 - 2].writeDisplay();
        break;

      // Blank the display
      case 'E':
        // Blanking the display, so it needs to stop counting (if it was)
        count_active[byte1]=false;
        count_display[byte1]=0;
        count_direction[byte1]=0;
        if (byte1 < 2) {
//          numeric4[byte1].clear();
//          numeric4[byte1].writeDisplay();
        } else {
 //         alpha4[byte1-2].clear();
 //         alpha4[byte1-2].writeDisplay();
        }
        break;

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
        
        // Reset the schedule index for this lamp back to the start
        lamp_index[byte1]=0x1;      
        
        switch(command) {
            case 'R':
                red[byte1] = schedule;
                green[byte1]=0;
                blue[byte1]=0;
                break;
                
            case 'G':
                green[byte1] = schedule;
                red[byte1]=0;
                blue[byte1]=0;
                break;
            
            case 'B':
                blue[byte1] = schedule;
                red[byte1]=0;
                green[byte1]=0;
                break;
            
            case 'Y':
                red[byte1] = schedule;
                green[byte1] = schedule;
                blue[byte1]=0;
                break;
            
            case 'M':
                red[byte1] = schedule;
                blue[byte1] = schedule;
                green[byte1]=0;
                break;
            
            case 'C':
                green[byte1] = schedule;
                blue[byte1] = schedule;
                red[byte1]=0;
                break;
            
            case 'W':
                red[byte1] = schedule;
                green[byte1] = schedule;
                blue[byte1] = schedule;
                break;
                
        }
        
        break;

      // PC is queerying the value of a counter - sent it back up the serial line in 2 bytes
      case 'Q':
        Serial.write('Q'+char(count_display[byte1] / 256)+char(count_display[byte1] % 256));
        break;
      
    }
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
   //       numeric4[i].print(count_display[i],DEC);
   //       numeric4[i].writeDisplay();
          } else {
          }
          count_display[i] += count_direction[i];
        } 
      }
    }
        
          
 }
    


// Routine called by the hardware timer interrupt
void scheduleProcess() {
  static byte i;
  // Increment the tick counter
  count_ticks_counter[0] ++;
  count_ticks_counter[1] ++;  
  count_ticks ++;
  
  
  // Grab the current bit of each schedule and send to the relevant pixel
  for (i=0;i<RGB_COUNT;i++) {
     strip.setPixelColor(i,255*((red[i] & lamp_index[i])!=0),255*((green[i] & lamp_index[i]) !=0),255 * ((blue[i] & lamp_index[i]) !=0));
     // Move the current bit along for this lamp
     lamp_index[i] <<= 1;
     if (lamp_index[i] > 0x80000000) lamp_index[i] = 0x1;
  } 

  // Push the result to the pixel chain
  strip.show();
  
  // Every 4 ticks (1/8 of a second) update the radar
  if (count_ticks % 4 == 0) {
    offset++;
    if (offset == 16) offset = 0;
    for(i=0; i<16; i++) {
      if (radar_spin) 
        radar.setPixelColor(   (offset+i)%16, i * 10 * radar_red,i*10*radar_green, i * 10 * radar_blue);
      else
        radar.setPixelColor(   (offset+i)%16, 255 * radar_red,255*radar_green,255*radar_blue);
    }
    radar.show();
  }
}  

// Throw something on the display to start with
void boot_display() {
  int i;
  tft.fillScreen(HX8357_BLACK);
  tft.setRotation(1);
  bmpDraw("f14.bmp", 0, 0);
  tft.setCursor(20,230);
  tft.setTextColor(HX8357_GREEN);    tft.setTextSize(3);
  tft.println("Fuel  98%");
  tft.setCursor(20,255);
  tft.println("Alt.  23800ft");
  tft.setCursor(20,280);
  tft.println("Kills 14");

  tft.setCursor(260,230);
  tft.println("Missiles 5");
  tft.setCursor(260,255);
  tft.setTextColor(HX8357_RED);
  tft.println("Ammo Empty");
  tft.setCursor(260,280);
  tft.setTextColor(HX8357_GREEN);
  tft.println("Chaff 4 / 5");
  // Put the identifier for each display on the display for short while
  /*
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
  
*/
}

#define BUFFPIXEL 20

void bmpDraw(char *filename, uint8_t x, uint16_t y) {

  File     bmpFile;
  int      bmpWidth, bmpHeight;   // W+H in pixels
  uint8_t  bmpDepth;              // Bit depth (currently must be 24)
  uint32_t bmpImageoffset;        // Start of image data in file
  uint32_t rowSize;               // Not always = bmpWidth; may have padding
  uint8_t  sdbuffer[3*BUFFPIXEL]; // pixel buffer (R+G+B per pixel)
  uint8_t  buffidx = sizeof(sdbuffer); // Current position in sdbuffer
  boolean  goodBmp = false;       // Set to true on valid header parse
  boolean  flip    = true;        // BMP is stored bottom-to-top
  int      w, h, row, col;
  uint8_t  r, g, b;
  uint32_t pos = 0, startTime = millis();

  if((x >= tft.width()) || (y >= tft.height())) return;

  Serial.println();
  Serial.print(F("Loading image '"));
  Serial.print(filename);
  Serial.println('\'');

  // Open requested file on SD card
  if ((bmpFile = SD.open(filename)) == NULL) {
    Serial.print(F("File not found"));
    return;
  }

  // Parse BMP header
  if(read16(bmpFile) == 0x4D42) { // BMP signature
    Serial.print(F("File size: ")); Serial.println(read32(bmpFile));
    (void)read32(bmpFile); // Read & ignore creator bytes
    bmpImageoffset = read32(bmpFile); // Start of image data
    Serial.print(F("Image Offset: ")); Serial.println(bmpImageoffset, DEC);
    // Read DIB header
    Serial.print(F("Header size: ")); Serial.println(read32(bmpFile));
    bmpWidth  = read32(bmpFile);
    bmpHeight = read32(bmpFile);
    if(read16(bmpFile) == 1) { // # planes -- must be '1'
      bmpDepth = read16(bmpFile); // bits per pixel
      Serial.print(F("Bit Depth: ")); Serial.println(bmpDepth);
      if((bmpDepth == 24) && (read32(bmpFile) == 0)) { // 0 = uncompressed

        goodBmp = true; // Supported BMP format -- proceed!
        Serial.print(F("Image size: "));
        Serial.print(bmpWidth);
        Serial.print('x');
        Serial.println(bmpHeight);

        // BMP rows are padded (if needed) to 4-byte boundary
        rowSize = (bmpWidth * 3 + 3) & ~3;

        // If bmpHeight is negative, image is in top-down order.
        // This is not canon but has been observed in the wild.
        if(bmpHeight < 0) {
          bmpHeight = -bmpHeight;
          flip      = false;
        }

        // Crop area to be loaded
        w = bmpWidth;
        h = bmpHeight;
        if((x+w-1) >= tft.width())  w = tft.width()  - x;
        if((y+h-1) >= tft.height()) h = tft.height() - y;

        // Set TFT address window to clipped image bounds
        tft.setAddrWindow(x, y, x+w-1, y+h-1);

        for (row=0; row<h; row++) { // For each scanline...

          // Seek to start of scan line.  It might seem labor-
          // intensive to be doing this on every line, but this
          // method covers a lot of gritty details like cropping
          // and scanline padding.  Also, the seek only takes
          // place if the file position actually needs to change
          // (avoids a lot of cluster math in SD library).
          if(flip) // Bitmap is stored bottom-to-top order (normal BMP)
            pos = bmpImageoffset + (bmpHeight - 1 - row) * rowSize;
          else     // Bitmap is stored top-to-bottom
            pos = bmpImageoffset + row * rowSize;
          if(bmpFile.position() != pos) { // Need seek?
            bmpFile.seek(pos);
            buffidx = sizeof(sdbuffer); // Force buffer reload
          }

          for (col=0; col<w; col++) { // For each pixel...
            // Time to read more pixel data?
            if (buffidx >= sizeof(sdbuffer)) { // Indeed
              bmpFile.read(sdbuffer, sizeof(sdbuffer));
              buffidx = 0; // Set index to beginning
            }

            // Convert pixel from BMP to TFT format, push to display
            b = sdbuffer[buffidx++];
            g = sdbuffer[buffidx++];
            r = sdbuffer[buffidx++];
            tft.pushColor(tft.color565(r,g,b));
          } // end pixel
        } // end scanline
        Serial.print(F("Loaded in "));
        Serial.print(millis() - startTime);
        Serial.println(" ms");
      } // end goodBmp
    }
  }

  bmpFile.close();
  if(!goodBmp) Serial.println(F("BMP format not recognized."));
}


// These read 16- and 32-bit types from the SD card file.
// BMP data is stored little-endian, Arduino is little-endian too.
// May need to reverse subscript order if porting elsewhere.

uint16_t read16(File &f) {
  uint16_t result;
  ((uint8_t *)&result)[0] = f.read(); // LSB
  ((uint8_t *)&result)[1] = f.read(); // MSB
  return result;
}

uint32_t read32(File &f) {
  uint32_t result;
  ((uint8_t *)&result)[0] = f.read(); // LSB
  ((uint8_t *)&result)[1] = f.read();
  ((uint8_t *)&result)[2] = f.read();
  ((uint8_t *)&result)[3] = f.read(); // MSB
  return result;
}

