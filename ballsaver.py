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
#     ___         __ __  ____
#    / _ ) ___ _ / // / / __/___ _ _  __ ___  ____
#   / _  |/ _ `// // / _\ \ / _ `/| |/ // -_)/ __/
#  /____/ \_,_//_//_/ /___/ \_,_/ |___/ \__//_/
#
#################################################################################

import procgame.game
from procgame import *
import pinproc
import procgame.dmd
import logging

class BallSaver(game.Mode):
	def __init__(self, game, priority):
			super(BallSaver, self).__init__(game, priority)

                        # Used to determine if this is a regular ball save (at the start of a new ball)
                        # or during some kind of other game function.  For example a timed multiball might
                        # want to have a much longer ball save period

                        self.ballSaverType = 'standard'


                        self.log = logging.getLogger('f14.ballsave')


	############################
	#### Standard Functions ####
	############################
	def mode_started(self):
            # For standard ball save, read the game settings to determine the period
            if self.ballSaverType == 'standard':
                self.ballSaverTime = self.game.user_settings['Standard']['Ball Save Timer Seconds']
                self.ballSaverGracePeriodThreshold =  min(self.ballSaverTime,2)

                # If the config gives a ball save time, then start the mode
                if self.ballSaverTime != 0:
                    self.cancel_delayed('stopballsavelamps')
                    self.game.utilities.set_player_stats('ballsave_active',True)
                    self.ballSaveLampsActive = True
                    self.game.trough.ball_save_active = True
                    self.update_lamps()
                # otherwise it's disabled, so just quit
                else:
                    self.game.modes.remove(self)
            # Otherwise this is for some other usage, in which case the saver time and threshold will have been
            # set before the mode was called.
            elif self.ballSaverType == 'custom':
                self.cancel_delayed('stopballsavelamps')
                self.game.utilities.set_player_stats('ballsave_active',True)
                self.ballSaveLampsActive = True
                self.game.trough.ball_save_active = True
                self.update_lamps()


	def mode_stopped(self):
		self.game.trough.ball_save_active = False
                # Reset the type of the ball save to the default for next time around
                self.ballSaverType = 'standard'
		return super(BallSaver, self).mode_stopped()

	def update_lamps(self):
		print "Update Lamps: Ball Saver"
		if (self.game.utilities.get_player_stats('ballsave_active') == True and self.ballSaveLampsActive == True):
			self.startBallSaverLamps()
		else:
			self.stopBallSaverLamps()
		
	def startBallSaverLamps(self):
		self.game.lamps.insurance.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=False)
                

	def startBallSaverLampsWarning(self):
		self.game.lamps.insurance.schedule(schedule=0x0F0F0F0F, cycle_seconds=0, now=False)

	def stopBallSaverLamps(self):
		self.ballSaveLampsActive = False
		self.game.lamps.insurance.disable()
                self.game.lamps.kill6red.disable()

	def stopBallSaverMode(self):
		self.game.utilities.set_player_stats('ballsave_active',False)
		self.stopBallSaverTimers()
		self.update_lamps()
		self.game.modes.remove(self)

        

	def startBallSaverTimers(self):
		self.game.utilities.set_player_stats('ballsave_timer_active',True)
		self.delay(name='ballsaver',delay=self.ballSaverTime,handler=self.stopBallSaverMode)
		self.delay(name='stopballsavelamps',delay=self.ballSaverTime - self.ballSaverGracePeriodThreshold,handler=self.stopBallSaverLamps)

	def stopBallSaverTimers(self):
		self.game.utilities.set_player_stats('ballsave_timer_active',False)
		self.cancel_delayed('stopballsavelamps')
		self.cancel_delayed('ballsaver')

	#def kickBallToTrough(self):
	#	self.game.utilities.acCoilPulse(coilname='outholeKicker_flasher1',pulsetime=50)

	#def kickBallToShooterLane(self):
	#	self.game.utilities.acCoilPulse(coilname='ballReleaseShooterLane_flasher2',pulsetime=100)

	def saveBall(self):
                # If this is just a regular 'one shot' ball save, then play the animation, launch a ball
                # and then stop the mode
		if self.ballSaverType == 'standard':
                    self.game.utilities.ball_saved_animation()
                    self.log.info("Launch ball auto due to ball saver")
                    self.game.trough.launch_balls(num=1,autolaunch=True)
                    self.stopBallSaverMode()
                # Otherwise just launch a ball and carry on
                elif self.ballSaverType == 'custom':
                    self.game.trough.launch_balls(num=1,autolaunch=True)



	#def saveBallEarly(self): #Need to work on this...
	#	self.game.utilities.display_text(txt='BALL SAVED',time=3)

		#Stop Skillshot
		#self.game.modes.remove(self.game.skillshot_mode)

	#	self.game.sound.play('ball_saved')

        #        self.log.info("Launch ball manual due to ball saver")
	#	self.game.trough.launch_balls(num=1)
	#	self.stopBallSaverMode()

	
	##################################################
	## Ramp entry switch will mark the ball as in progress
	##################################################
	def sw_rampEntry_active(self, sw):
                if (self.game.utilities.get_player_stats('ballsave_timer_active') == False):
			self.startBallSaverTimers()
                        self.log.info("Ramp made, ball save active, start timer")
		return procgame.game.SwitchContinue

