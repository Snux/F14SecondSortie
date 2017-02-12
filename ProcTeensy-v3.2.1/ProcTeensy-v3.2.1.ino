// Teeny sketch for handling cheap, WS2811 RGB LEDs for PyProcGame
//
// Once initialised, the code sits and waits for commands to come in on the serial port
// Incoming commands are 6 bytes long, the first byte gives the directive and the others
//   are related data
//
// PROTOCOL:
//        1B      1B        4B
//      [COMMAND] [LAMP#] [SHEDULE]
//
//   COMMAND 1Byte, taken by bits: if first two bits are ones then the remaining bits are color amounts
//      like: 11rrggbb  
//      example: 11010011 is rr=01 gg=00 b=11 so red level 1/3 (33%), green=0/3 (0%), blue = 3/3 (100%)
//      command of 00000000 turns off ALL lamps
//   LAMP# if N lamps, index from zero: (0..N-1); 
//      the lamp number 255 is "all RGB lamps" 
//      the lamp number 252 is a mapping for all GI lamps (all lamps 50+)
//      the lamp number 254 is all inserts
//      the lamp number 253 is the radar ring
//      the lamp number 251 is the rear ramp
//   SCHEDULE: a lamp schedule (same as used in pyprocgame for normal lamps)
//
// Included libraries
#include <OctoWS2811.h>

// RGB Strand details:
#define RGB_COUNT 148 // was 148-37
#define LED_PER_STRIP 37

// bitmasks to strip out the parts
#define OP_MASK B11000000   // 0b11000000
#define R_MASK  B00110000   // 0b00110000
#define G_MASK  B00001100   // 0b00001100
#define B_MASK  B00000011   // 0b00001100
#define COLOR_OP B11000000  // 0b11000000
#define RING_OP B10000000

// required for the OctoWS2811
DMAMEM int displayMemory[LED_PER_STRIP*6];
int drawingMemory[LED_PER_STRIP*6];

OctoWS2811 leds(LED_PER_STRIP, displayMemory, drawingMemory, WS2811_RGB | WS2811_800kHz);

// Current state of lamp schedules
unsigned long sched[RGB_COUNT];
unsigned long colour[RGB_COUNT];
unsigned long lamp_index[RGB_COUNT];
byte radar_colour_shift;

long previous_ms = 0;
long interval = 31;
boolean ring_rotate = false;

int dontuse[] = {60, 62, 64, 66, 68, 69, 70, 75, 77, 79, 80, 82};

// 86 - 91 are BRONZE

int dontuse_ct = 12;

void setup() 
{
  pinMode(13, OUTPUT);
  digitalWrite(13 ,LOW); // turn off the LED
  
  // Clear down the schedules, will switch all the lamps off
  byte i;

  for (i=0;i<RGB_COUNT;i++) 
  {
    colour[i]=0;
    sched[i]=0;
    lamp_index[i]=0x1;
  }
  
  // Setup the serial port, need to find the fastest reliable rate
  Serial.begin(115200);

  leds.begin();
  leds.show();
}

int remap(int small_num)
{
  if(small_num==0)
    return 0;
  if(small_num==3)
    return 255;
  if(small_num==2)
    return 200;
  if(small_num==1)
    return 64;
  return 0;
}

void loop() 
{
  unsigned long schedule, this_colour;
  byte lamp_num, byte2, byte3, byte4, byte5;
  byte command;
  byte r,g,b;
  byte i,j;
  
  unsigned long current_ms = millis();
 
  // check the time 
  if(current_ms - previous_ms > interval) 
  {
    previous_ms = current_ms;   
    update_lamps();
  }

  // Each time around, take a look at the serial (USB) buffer and see if we have at least 6 bytes waiting which is
  // enough for a command
  if (Serial.available() >= 6) 
  {

    // Grab the command
    command = Serial.read();
    // and the next 5 bytes
    lamp_num = Serial.read(); byte2 = Serial.read(); byte3 = Serial.read(); byte4 = Serial.read(); byte5 = Serial.read();
    
    if(command == 0) // turn off all lamps
    {
        all_off();
    }
    else if((command & OP_MASK) == RING_OP)
    {
        r = ((command & R_MASK) >> 4); // now r is between 0..3       
        g = ((command & G_MASK) >> 2); //     g is between 0..3
        b = (command & B_MASK);        //     b is between 0..3
        if (r > 0) radar_colour_shift = 16;
        else if (g > 0) radar_colour_shift = 8;
        else if (b > 0) radar_colour_shift = 0;
        for(int lnum=37;lnum<53;lnum++)
          {
                lamp_index[lnum]=0x1;
                sched[lnum]=0xFFFFFFFF;
                colour[lnum]=0;
          }
        ring_rotate = true;
        Serial.print("K");
        Serial.send_now(); // send the ack IMMEDIATELY
    }
    else if((command & OP_MASK) == COLOR_OP)
    {
        // strip out the 2bit values for the R, G, B and
        // scale them up to build a single 24bit (3B) color 

        r = ((command & R_MASK) >> 4); // now r is between 0..3       
        g = ((command & G_MASK) >> 2); //     g is between 0..3
        b = (command & B_MASK);        //     b is between 0..3
        r = remap(r);// * 85; // r is now 0, 85, 170, or 255
        g = remap(g);// * 85; // ...  FIX THIS...
        b = remap(b);// * 85; // ...

        this_colour = r;
        this_colour <<= 8;
        this_colour = this_colour | g;
        this_colour <<= 8;
        this_colour = this_colour | b;

        // now build the schedule as a single 32b (4B) value
        schedule = byte2;
        schedule <<= 8;
        schedule = schedule | byte3;
        schedule <<= 8;
        schedule = schedule | byte4;
        schedule <<= 8;
        schedule = schedule | byte5;

        // lamp_num 255 means do this for all lamps:
        if((lamp_num==255)||(lamp_num==254)||(lamp_num==252)||(lamp_num==253)  || (lamp_num==251))
        {
          int s = 0;
          int e = RGB_COUNT;

          if(lamp_num==252)     // all GI: start at GI, end at RGB_COUNT
            {
              s = 74;
              e = 111;
            }
          else if(lamp_num==254) // all Inserts: start at 0 end at 49
            {
              e = 16;
            }
          else if(lamp_num==253)
            {
              s = 37;
              e = 53;
              ring_rotate = false;
            }
          else if (lamp_num==251)
          {
            s = 111;
          }
          // else 255 --all lamps: start at zero and end at RGB_COUNT

          for(int lnum=s;lnum<e;lnum++)
          {
                lamp_index[lnum]=0x1;
                sched[lnum]=schedule;
                colour[lnum]=this_colour;
          }
          
        } // end all reserved numbers (range) branch
        else // regular single lamp instruction
        {
          // Reset the schedule index for this lamp back to the start
          lamp_index[lamp_num]=0x1;
          sched[lamp_num]=schedule; // store the schedule
          colour[lamp_num]=this_colour; // set the color
        }
        Serial.print("K");
        Serial.send_now(); // send the ack IMMEDIATELY
    }
    else // invalid command!?
    {
        Serial.print("?"); // the message was corrupt
        Serial.send_now();
    }
  } // if a full serial command is available

  // check to see if the USB connection is active
  if(!Serial.dtr()) // no connection open 
  {
    // turn off all the lamps and the onboard LED
    all_off();
    digitalWrite(13, LOW);
  }
  else // there is a connection
  {
    // turn on the onboard LED to indicate a connection
    digitalWrite(13, HIGH);
  }
} // loop
    

void all_off()
{
  byte lamp_num;
  ring_rotate = false;
  for(lamp_num=0;lamp_num<RGB_COUNT;lamp_num++)
    {
      lamp_index[lamp_num]=0x1;
      sched[lamp_num]=0x0;
      colour[lamp_num]=0x0;
    }
}

// Routine called to actually sync lamps
void update_lamps() 
{  
  static byte i,j=0,fall;
  static byte j3;
  static byte offset = 0;

  // If the "radar" is supposed to be rotating, then load up
  // the colours into the appropriate slots in the array
  if (ring_rotate) 
  {
    j+=2;
    for(i=0; i<8; i++) {
      fall = (i + offset) % 16;
      colour[fall+37]=(i*16-j+16) << radar_colour_shift;
    }
    j3 = j*3;
    colour[++fall % 16 +37]=(90+j3) << radar_colour_shift;
    colour[++fall % 16 +37]=(45+j3) << radar_colour_shift;
    colour[++fall % 16 +37]=(j3) << radar_colour_shift;
    if (j==16)
        {
          j=0;
          offset++;
          if (offset == 16) offset=0;
        }
  }

  // Grab the current bit of each schedule and send to the relevant pixel
  for (i=0;i<RGB_COUNT;i++) 
  {

     // Move the current bit along for this lamp
     if (sched[i] & lamp_index[i])
       leds.setPixel(i, colour[i]);
     else
      leds.setPixel(i, 0);

     if (lamp_index[i] >= 0x80000000)
       lamp_index[i] = 0x1;
     else
       lamp_index[i] <<= 1;
  }

  // Push the result to the pixel chain

  leds.show();
}  


