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

ser=serial.Serial("COM6",300)
time.sleep(1)
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
		print level + " - " + text


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

	def displayText(self,priority,topText=' ',bottomText=' ',seconds=2,justify='left',topBlinkRate=0,bottomBlinkRate=0):
		# This function will be used as a very basic display prioritizing helper
		# Check if anything with a higher priority is running
		if (priority >= self.currentDisplayPriority):
			self.cancel_delayed('resetDisplayPriority')
			self.game.alpha_score_display.cancel_script()
			self.game.alpha_score_display.set_text(topText,0,justify)
			self.game.alpha_score_display.set_text(bottomText,1,justify)
			self.delay(name='resetDisplayPriority',event_type=None,delay=seconds,handler=self.resetDisplayPriority)
			self.currentDisplayPriority = priority

	def resetDisplayPriority(self):
		self.currentDisplayPriority = 0
		#self.updateBaseDisplay()

	def updateBaseDisplay(self):
		print "Update Base Display Called"
		if (self.currentDisplayPriority == 0 and self.game.tiltStatus == 0 and self.game.ball <> 0):
			self.p = self.game.current_player()
			self.game.alpha_score_display.cancel_script()
			self.game.alpha_score_display.set_text(locale.format("%d", self.p.score, grouping=True),0,justify='left')
			self.game.alpha_score_display.set_text(self.p.name.upper() + "  BALL "+str(self.game.ball),1,justify='right')
			print self.p.name
			print "Ball " + str(self.game.ball)
	
	######################
	#### GI Functions ####
	######################
	def disableGI(self):
		self.game.coils.gi.enable()
		
	def enableGI(self):
		self.game.coils.gi.disable()

        def write_arduino(self,servalue):
                #self.log('Arduino "%s"' % (servalue))
                ser.write(servalue)
                #self.ser.flush()
                #ser.write(servalue)


	###################################
	#### Music and Sound Functions ####
	###################################
	def stopShooterLaneMusic(self):
		if (self.game.shooter_lane_status == 1):
			self.game.sound.stop_music()
			#self.game.sound.play_music('main',loops=-1)
			self.game.shooter_lane_status = 0


	##########################
	#### Player Functions ####
	##########################
	def set_player_stats(self,id,value):
		if (self.game.ball <> 0):
			self.p = self.game.current_player()
			self.p.player_stats[id]=value

	def get_player_stats(self,id):
		if (self.game.ball <> 0):
			self.p = self.game.current_player()
			return self.p.player_stats[id]
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

