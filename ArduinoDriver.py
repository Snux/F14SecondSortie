#!/usr/bin/python
# 
# Copyright (c) 2015 Michael Ocean 
# Licence: The MIT License (MIT)
#
# Written by Michael Ocean
#   * includes portions derived from work by Mark Sunnucks, Adam Preble and Gerry Stellenberg
#
#     ___             __      _                ____       _     __         
#    /   |  _________/ /_  __(_)___  ____     / __ )_____(_)___/ /___ ____ 
#   / /| | / ___/ __  / / / / / __ \/ __ \   / __  / ___/ / __  / __ `/ _ \
#  / ___ |/ /  / /_/ / /_/ / / / / / /_/ /  / /_/ / /  / / /_/ / /_/ /  __/
# /_/  |_/_/   \__,_/\__,_/_/_/ /_/\____/  /_____/_/  /_/\__,_/\__, /\___/ 
#                                                             /____/       
#     ____                          ____                  ______                   
#    / __/___  _____   ____  __  __/ __ \_________  _____/ ____/___ _____ ___  ___ 
#   / /_/ __ \/ ___/  / __ \/ / / / /_/ / ___/ __ \/ ___/ / __/ __ `/ __ `__ \/ _ \
#  / __/ /_/ / /     / /_/ / /_/ / ____/ /  / /_/ / /__/ /_/ / /_/ / / / / / /  __/
# /_/  \____/_/     / .___/\__, /_/   /_/   \____/\___/\____/\__,_/_/ /_/ /_/\___/ 
#                  /_/    /____/                                                   
#
# A work-around to allow controlling ws2811 and ws2812 RGB LEDs (e.g., NeoPixels) 
# from pyProcGame using serial commands sent to an Arduino board which actually drives
# the pixels.
#
# REQUIRES: pySerial
#   Hardware: Arduino, ws281x RGB LEDs, etc.
#
# Integrating this into your game requires adding the suggested process_config and end_run_loop
# methods to your game's class file.  See the README for details
#
# -------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import procgame.game 
from procgame.game.gameitems import GameItem #, AttrCollection, Driver
try:
    import serial
except Exception, e:
    print "The PySerial Library is required to use this module."
    raise

import logging
import time
import threading
from collections import deque

class ArduinoClient(object):
    """ The serial bridge to the arduino board.  This object maintains a buffer of outgoing serial 
        commands and sends those commands to the serial device (i.e., Arduino) via its own thread of
        execution.

        Integrating this into your game requires adding the suggested process_config and end_run_loop
        methods.  See the README for details
    """

    serial_client = None
    cmd_buffer = deque()
    running = True
    semaphore = None

    def __init__(self, com_port, baud_rate, timeout=1):
        self.logger = logging.getLogger('game.ArduinoClient')
        self.sender_thread = None
        self.cmd_buffer = deque()
        self.running = False
        self.semaphore = threading.Semaphore(0)
        self.fails = 0

        try:
            self.serial_client = serial.Serial(port=com_port,baudrate=baud_rate,timeout=timeout)
            ## Need to sleep here for a couple of seconds to let the port settle down
            time.sleep(2)
            self.logger.info("Arduino/Serial device ONLINE")
            self.running = True
            self.sender_thread = threading.Thread(target=self.sender, args=())
            self.sender_thread.start()
        except serial.serialutil.SerialException, e:
            #raise e
            self.logger.info("Arduino/Serial device OFFLINE; check connection to %s " % com_port)
            self.serial_client = None

    def rgbschedule(self, colour, lamp_num, sched, now, repeat = True):
        m = chr(colour)+chr(lamp_num)+chr((sched >>24) & 255)+chr((sched >>16) & 255)+chr((sched >>8) & 255)+chr((sched) & 255)
        self.cmd_buffer.append(m)
        self.logger.debug("SCHEDULING %s" % m)        
        self.semaphore.release()

    def quit(self):
        self.running = False
        self.semaphore.release()
        self.logger.info("ArduinoClient: Quit requested...")        

    def sender(self):
        while(self.running):
            self.semaphore.acquire()
            if(self.running):
                m = self.cmd_buffer.popleft()
                
                self.logger.debug("ArduinoClient: SENDING %s" % [bin(ord(x)) for x in m])
                #self.logger.info("Serial buffer length is %d" % len(self.cmd_buffer))
                self.raw_write(m)
                l = len(self.cmd_buffer) 
                if(l > 49):
                    self.logger.info("ArduinoClient: WARNING!! BUFFER LARGE %d" % (l))
                # elif(l > 0):
                #     self.logger.debug("ArduinoClient: Buffer Length %d" % (l))

        self.logger.info("ArduinoClient: TERMINATED.")        


    def raw_write(self,servalue):
        if(self.serial_client is not None):
            self.serial_client.write(servalue)
            resp = self.serial_client.read()
            if len(resp)>0 and (resp[0]=='K'):
                self.fails = 0
                return True

            self.fails += 1
            if len(resp)==0:
                self.logger.info("ArduinoClient: Fails %d - Timeout -['%s']- device hung?" % (self.fails, servalue))
            elif len(resp)>0 and (resp[0]=='?'):
                self.logger.info("ArduinoClient: Fails %d - Error received -['%s']- device confused!?" % (self.fails,servalue))
            else:
                self.logger.info("ArduinoClient: response buffer is CRAZY! [%s]!?" % resp)
            return False
        else:
            self.logger.info("Serial client OFFLINE - write supressed")



class wsRGB(procgame.game.VirtualDriver):
    """Represents a ws2811/ws2812 based RGB LED, driven via serial communication through :class:`ArduinoClient`.
    
    Subclass of :class:`procgame.game.VirtualDriver`.

    A 'first-class' driver object for these RGB leds.  
    It leverages the fact that VirtualDriver does pretty much everything as long as you provide subclassed 
    pulse, schedule and disable methods (which are provided here).  

    Right now patter and pulsed_patter will not work because I haven't 
    coded them and virtualdriver doesn't implement them via schedule.  Shouldn't be that hard to do
    (just don't patter and pulsed_patter!!)

    You can use these in FakePinProc or real PinProc.  If the Arduino is disconnected, they just won't work.
    """
    
    color = 0b11111111 # default color is white

    def __init__(self, game, name, number, color='W'):
        super(wsRGB, self).__init__(game, name, number, polarity=True)

        if not hasattr(game,'arduino_client') or game.arduino_client is None:
            raise ValueError, 'Cannot initialize a wsRGB without an initialized arduino_client attribute in the game object'
        self.set_color(color)
        self.default_color = self.color

    def set_color(self, color_char):
        mappings = {'0': 0b11000000,
                    'W': 0b11111111, 
                    'R': 0b11110000,
                    'G': 0b11001100,
                    'B': 0b11000011,
                    'M': 0b11110011,
                    'P': 0b11100011,
                    'O': 0b11110100,
                    'Y': 0b11111100,
                    'C': 0b11001111,
                    'X': 0b10000000,
                    'Y': 0b10001100,
                    'Z': 0b10110000
        }
        if(color_char not in mappings.keys()):
            print("lamp: %s has default color %s" % (self.name, self.default_color))
        self.color = mappings[color_char]

    def store_default_color(self):
        self.default_color = self.color

    def restore_default_color(self):
        self.color = self.default_color

    def set_color_RGB(self, R,G,B):
        if(R>3 or G>3 or B>3):
            raise ValueError, "Specified R,G,B values must be between [0..3]"
        self.color = 0b11000000 | (R << 4) | (G << 2) | B; 

    def state(self):
        return self.state        

    def disable(self):
        """Schedules this driver to be enabled according to the given `schedule` bitmask."""
        super(wsRGB, self).disable()
        self.logger.debug("wsRGB Driver %s - disable" % self.name)
        self.game.arduino_client.rgbschedule(self.color, self.number, 0x0, True, True)

    def pulse(self, milliseconds=None):
        """Enables this driver for `milliseconds`.
        
        If no parameters are provided or `milliseconds` is `None`, :attr:`default_pulse_time` is used.
        ``ValueError`` will be raised if `milliseconds` is outside of the range 0-255.
        """
        super(wsRGB, self).pulse(milliseconds)

        self.logger.debug("sRGB Driver %s - pulse %d", self.name, milliseconds)
        # self.game.proc.driver_pulse(self.number, milliseconds)
        self.game.arduino_client.rgbschedule(self.color, self.number, milliseconds, False, repeat = False)


    def schedule(self, schedule, cycle_seconds=0, now=True):
        """Schedules this driver to be enabled according to the given `schedule` bitmask."""
        super(wsRGB, self).schedule(schedule, cycle_seconds, now)
        self.logger.debug("wsRGB Driver %s - schedule %08x" % (self.name, schedule))
        self.game.arduino_client.rgbschedule(self.color, self.number, schedule, now, repeat=True)

    def patter(self, on_time=10, off_time=10, original_on_time=0, now=True):
        """Enables a pitter-patter sequence.  

        It starts by activating the driver for `original_on_time` milliseconds.  
        Then it repeatedly turns the driver on for `on_time` milliseconds and off for 
        `off_time` milliseconds.
        """

        if not original_on_time in range(256):
            raise ValueError, 'original_on_time must be in range 0-255.'
        if not on_time in range(128):
            raise ValueError, 'on_time must be in range 0-127.'
        if not off_time in range(128):
            raise ValueError, 'off_time must be in range 0-127.'

        self.logger.debug("Driver %s - patter on:%d, off:%d, orig_on:%d, now:%s", self.name, on_time, off_time, original_on_time, now)

        sched = 0x0 + on_time
        self.game.arduino_client.rgbschedule(self.color, self.number, sched, now, repeat = True)
        self.last_time_changed = time.time()

    def pulsed_patter(self, on_time=10, off_time=10, run_time=0, now=True):
        """Enables a pitter-patter sequence that runs for `run_time` milliseconds.  

        Until it ends, the sequence repeatedly turns the driver on for `on_time` 
        milliseconds and off for `off_time` milliseconds.
        """

        if not run_time in range(256):
            raise ValueError, 'run_time must be in range 0-255.'
        if not on_time in range(128):
            raise ValueError, 'on_time must be in range 0-127.'
        if not off_time in range(128):
            raise ValueError, 'off_time must be in range 0-127.'

        self.logger.debug("Driver %s - pulsed patter on:%d, off:%d, run_time:%d, now:%s", self.name, on_time, off_time, run_time, now)

        time = on_time + off_time
        sched = 0x0 + on_time
        # figure out how many time intervales there are in 255
        # add an ontime shifted by time repeatedly
        raise ValueError, "Lazy Programmer: pulsed_patter is not supported in these LEDs yet."
        self.game.arduino_client.rgbschedule(self.color, self.number, sched, now, repeat = True)

        # self.game.proc.driver_pulsed_patter(self.number, on_time, off_time, run_time, now)
        self.last_time_changed = time.time()


