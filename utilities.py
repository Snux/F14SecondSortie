#####################################################################################
##     ____   _______   _________________  _  _____    ________  ___  ______________
##    / __/__<  / / /  / __/ __/ ___/ __ \/ |/ / _ \  / __/ __ \/ _ \/_  __/  _/ __/
##   / _//___/ /_  _/ _\ \/ _// /__/ /_/ /    / // / _\ \/ /_/ / , _/ / / _/ // _/
##  /_/     /_/ /_/  /___/___/\___/\____/_/|_/____/ /___/\____/_/|_| /_/ /___/___/
##
## A P-ROC Project by Mark Sunnucks
## Built on PyProcGame from Adam Preble and Gerry Stellenberg
## Thanks to Scott Danesi for inspiration from his Earthshaker Aftershock
#####################################################################################


#################################################################################
#
#    __  __ __   _  __ _  __   _
#   / / / // /_ (_)/ /(_)/ /_ (_)___  ___
#  / /_/ // __// // // // __// // -_)(_-<
#  \____/ \__//_//_//_/ \__//_/ \__//___/
#
## This mode will be used to house all the global functions that will be used
## throughout the project.
#################################################################################

import procgame.game
from procgame import *
import procgame.dmd
from procgame.dmd import font_named
import pinproc
import locale
import logging
import math
import serial
import time
import player
from player import *


#ser.setPort("COM6")
#ser.baudrate=115200
#ser.open()
#time.sleep(1)
#ser.write("G"+chr(1)+chr(255)+chr(0)+chr(255)+chr(0))
#time.sleep(1)
class UtilitiesMode(game.Mode):
	def __init__(self, game, priority):
			super(UtilitiesMode, self).__init__(game, priority)
			##############################
			#### Set Global Variables ####
			##############################
			self.currentDisplayPriority = 0	
			self.ACCoilInProgress = False
			self.ACNameArray = []
			self.ACNameArray.append('outholeKicker_flasher1')
			self.ACNameArray.append('ballReleaseShooterLane_flasher2')
			self.ACNameArray.append('upKicker_flasher3')
			self.ACNameArray.append('unusedC4_flasher4')
			self.ACNameArray.append('centreRightEject_flasher5')
			self.ACNameArray.append('knocker_flasher6')
			self.ACNameArray.append('rightEject_flasher7')
                        self.ACNameArray.append('unusedC8_flasher8')

                        ## Open up the Arduino COM port if one is specified.
                        self.sect_dict = self.game.config['PRGame']
                        if (self.sect_dict['arduino'] != False) :
                            self.ser=serial.Serial(port=self.sect_dict['arduino'],baudrate=9600,timeout=1)
                            ## Need to sleep here for a couple of seconds to let the port settle down
                            time.sleep(2)
                        

	#######################
	#### Log Functions ####
	#######################
	def log(self,text,level='info'):
		if (level == 'error'):
			logging.error(text)
		elif (level == 'warning'):
			logging.warning(text)
		else:
			logging.info(text)
		#print level + " - " + text


	#################################
	#### Ball Location Functions ####
	#################################
	def troughIsFull(self): #should be moved globally
		if (self.game.switches.trough1.is_active()==True and self.game.switches.trough2.is_active()==True and self.game.switches.trough3.is_active()==True):
			return True
		else:
			return False

	def releaseStuckBalls(self):
		#Checks for balls in locks or outhole and kicks them out
		if self.game.switches.outhole.is_active()==True and self.game.tiltStatus == 0: #Exception for when in tilt
			self.game.utilities.acCoilPulse(coilname='outholeKicker_flasher1',pulsetime=50)
		if self.game.switches.rightEject.is_active()==True:
			self.game.utilities.acCoilPulse(coilname='rightEject_flasher7',pulsetime=50)
		if self.game.switches.rightCentreEject.is_active()==True:
			self.game.utilities.acCoilPulse(coilname='centreRightEject_flasher5',pulsetime=50)
		if self.game.switches.leftCentreEject.is_active()==True:
			self.game.coils.centreLeftEject.pulse(50) #Does not need AC Relay logic
                if self.game.switches.vUK.is_active()==True:
			self.game.utilities.acCoilPulse(coilname='upKicker_flasher3',pulsetime=50)
		if self.game.switches.shooter.is_active()==True:
			self.game.coils.autoLaunch.pulse(100) #Does not need AC Relay logic

	def launch_ball(self):
		if self.game.switches.shooter.is_active()==True:
			self.game.coils.autoLaunch.pulse(100)

	def setBallInPlay(self,ballInPlay=True):
		self.previousBallInPlay = self.get_player_stats('ball_in_play')
		if (ballInPlay == True and self.previousBallInPlay == False):
			self.set_player_stats('ball_in_play',True)
			self.stopShooterLaneMusic()
		elif (ballInPlay == False and self.previousBallInPlay == True):
			self.set_player_stats('ball_in_play',False)

	############################
	#### AC Relay Functions ####
	############################
	def ACRelayEnable(self):
		self.game.coils.acSelect.enable()
		self.ACCoilInProgress = False

	def acCoilPulse(self,coilname,pulsetime=50):
		### Setup variables ###
		self.ACCoilInProgress = True
		self.acSelectTimeBuffer = .3
		self.acSelectEnableBuffer = (pulsetime/1000)+(self.acSelectTimeBuffer*2)

		### Remove any scheduling of the AC coils ###
		for item in self.ACNameArray:
			self.game.coils[item].disable()

		### Stop any flashlamp lampshows
		self.game.lampctrlflash.stop_show()

		### Start the pulse process ###
		self.cancel_delayed(name='acEnableDelay')
		self.game.coils.acSelect.disable()
		self.delay(name='coilDelay',event_type=None,delay=self.acSelectTimeBuffer,handler=self.game.coils[coilname].pulse,param=pulsetime)
		self.delay(name='acEnableDelay',delay=self.acSelectEnableBuffer,handler=self.ACRelayEnable)

	def acFlashPulse(self,coilname,pulsetime=50):
		if (self.ACCoilInProgress == False or coilname not in self.ACNameArray):
			self.game.coils[coilname].pulse(pulsetime)
		else:
			#Should this try again or just cancel?
			#cannot since the delay function does not allow me to pass more than 1 parameter :(
			pass

	def acFlashSchedule(self,coilname,schedule,cycle_seconds,now=True):
		if (self.ACCoilInProgress == False or coilname not in self.ACNameArray):
			self.game.coils[coilname].disable()
			self.game.coils[coilname].schedule(schedule=schedule, cycle_seconds=cycle_seconds, now=now)
		else:
			#Should this try again or just cancel?
			#cannot since the delay function does not allow me to pass more than 1 parameter :(
			pass

	
	###########################
	#### Display Functions ####
	###########################

        def display_text(self,txt,txt2=None,time=2,blink=2):
            if txt2==None:
                self.layer = dmd.TextLayer(128/2, 7, font_named("beware11.dmd"), "center", opaque=True).set_text(txt,seconds=time,blink_frames=blink)
            else:
                self.press_layer = dmd.TextLayer(128/2, -5, font_named("beware20aa.dmd"), "center").set_text(txt,seconds=time)
                self.start_layer = dmd.TextLayer(128/2, 10, font_named("beware20aa.dmd"), "center").set_text(txt2,seconds=time, blink_frames=blink)
                self.start_layer.composite_op = 'blacksrc'
                self.layer = dmd.GroupedLayer(128, 32, [self.press_layer,self.start_layer])
            self.delay(name='dmdoff',event_type=None,delay=time,handler=self.display_clear)


        def display_clear(self):
                try:
                    del self.layer
                except:
                    pass

	def resetDisplayPriority(self):
		self.currentDisplayPriority = 0
		#self.updateBaseDisplay()

	
	######################
	#### GI Functions ####
	######################
	def disableGI(self):
		self.game.coils.gi.enable()
		
	def enableGI(self):
		self.game.coils.gi.disable()

        ######################
        #### Arduino call ####
        ######################
        def write_arduino(self,servalue):
                if (self.sect_dict['arduino'] != False):
                    #self.log('Arduino "%s"' % (servalue[0]))
                    if len(servalue) == 6:
                        self.ser.write(servalue)
                    else:
                        self.log('Length error')
                    if len(self.ser.read()) == 1:
                        self.log('Got handshake')
                    else:
                        self.log('Handshake failed - disable Arduino')
                        self.sect_dict['arduino'] = False

        def arduino_start_count(self,display,direction,limit,ticks):
            self.write_arduino('C'+chr(display)+chr(direction)+chr(limit/256)+chr(limit % 256)+chr(ticks))

        def arduino_blank(self,display):
            self.log('Arduino - blank display '+str(display))
            self.write_arduino('W'+chr(display)+'    ')

        def arduino_write_alpha(self,display,text):
            self.log('Arduino - write '+text+' to display '+str(display))
            self.write_arduino('A'+chr(display)+text)

        def arduino_write_number(self,display,number):
            self.write_arduino('N'+chr(display)+chr(number / 256)+chr(number % 256)+'  ')

        def arduino_blank_all(self):
            self.log('Arduino - clear all displays')
            for i in range (0,6):
                self.arduino_blank(display=i)

	###################################
	#### Music and Sound Functions ####
	###################################
	def stopShooterLaneMusic(self):
		if (self.game.shooter_lane_status == 1):
			self.game.sound.stop_music()
			#self.game.sound.play_music('main',loops=-1)
			self.game.shooter_lane_status = 0

        def flickerOn(self,lamp,duration=0.75,schedule=0x55555555):
                """
                Flickers a lamp briefly and then switches it on
                Optionally specify the duration of the flicker and the lamp schedule

                Usage from other modes :
                self.game.effects.flickerOn(lamp='shootAgain')
                self.game.effects.flickerOn(lamp='shootAgain', duration=3.0)
                """
                self.game.lamps[lamp].schedule(schedule=schedule, cycle_seconds=duration, now=True)
                self.delay(name=lamp+"on",event_type=None,delay=duration,handler=self.game.lamps[lamp].enable)

	##########################
	#### Player Functions ####
	##########################
	def set_player_stats(self,id,value):
		if (self.game.ball <> 0):
			#self.p = self.game.current_player()
			self.game.current_player().player_stats[id]=value

	def get_player_stats(self,id):
		if (self.game.ball <> 0):
			#self.p = self.game.current_player()
			return self.game.current_player().player_stats[id]
		else:
			return False

	def score(self, points):
		if (self.game.ball <> 0): #in case score() gets called when not in game
			self.p = self.game.current_player()
                        self.game.score(points)
			self.p.score += points
			# Update the base display with the current players score
			self.cancel_delayed('updatescore')
			#self.delay(name='updatescore',delay=0.05,handler=self.game.utilities.updateBaseDisplay)

	def currentPlayerScore(self):
		if (self.game.ball <> 0): #in case score() gets called when not in game
			self.p = self.game.current_player()
			return self.p.score
		else:
			return 0

        def update_lamps(self):
                self.light_bonus()

        def light_bonus(self):
                """
                Display the current bonus multiplier and bonus count for
                the player on the playfield lamps
                """

                # Multiplier is easy
                mult=self.game.utilities.get_player_stats('bonus_x')
                if mult > 1:
                    for x in range(2, mult+1):
                        self.game.lamps["bonus"+str(x)+"X"].enable()

                # For the bonus we need to work through the binary value
                bonus = self.game.utilities.get_player_stats('bonus_x')
                bonusbin = "0"*(7-len(bin(bonus)[2:]))+bin(bonus)[2:]
                digitvalue=64
                for digit in list(bonusbin):
                    if digit == "1":
                        self.game.lamps["bonus"+str(digitvalue)+"K"].enable()
                    else:
                        self.game.lamps["bonus"+str(digitvalue)+"K"].disable()
                    digitvalue /= 2