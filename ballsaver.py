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

			self.ballSaverTime = 15 #This needs to be moved to pull from the configuration file
			self.ballSaverGracePeriodThreshold = 3 #This needs to be moved to pull from the configuration file
			self.ballSaveLampsActive = True #Probably should move to mode started instead of init...
			self.ballSavedEarly = False
                        self.log = logging.getLogger('f14.ballsave')


	############################
	#### Standard Functions ####
	############################
	def mode_started(self):
		self.cancel_delayed('stopballsavelamps')
		self.game.utilities.set_player_stats('ballsave_active',True)
		self.ballSaveLampsActive = True
		self.game.trough.ball_save_active = True
		self.update_lamps()

	def mode_stopped(self):
		self.game.trough.ball_save_active = False
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

	def kickBallToTrough(self):
		self.game.utilities.acCoilPulse(coilname='outholeKicker_flasher1',pulsetime=50)

	def kickBallToShooterLane(self):
		self.game.utilities.acCoilPulse(coilname='ballReleaseShooterLane_flasher2',pulsetime=100)

	def saveBall(self):
		#self.game.utilities.display_text(txt='BALL SAVED',time=3)
                #self.layer = dmd.AnimatedLayer(frames=self.game.dmd_assets['ball_saved'].frames, hold=True, repeat=False, frame_time=2)

                # Display the animiation via the utils because this mode will quit immediately
                self.game.utilities.ball_saved_animation()
                #Stop Skillshot
		#self.game.modes.remove(self.game.skillshot_mode)

		#self.game.sound.play('ball_saved')

		#These are from the original code
		#self.kickBallToTrough()
		#self.kickBallToShooterLane()
		self.game.trough.launch_balls(num=1,autolaunch=True)
		self.stopBallSaverMode()

	def saveBallEarly(self): #Need to work on this...
		self.game.utilities.display_text(txt='BALL SAVED',time=3)

		#Stop Skillshot
		#self.game.modes.remove(self.game.skillshot_mode)

		self.game.sound.play('ball_saved')

		#These are from the original code
		#self.kickBallToTrough()
		#self.kickBallToShooterLane()
		self.game.trough.launch_balls(num=1)
		self.stopBallSaverMode()

	def sw_outhole_closed_for_100ms(self, sw):
		if (self.game.utilities.get_player_stats('ballsave_active') == True):
			self.saveBall()
			self.game.utilities.log('BALLSAVE - Ouhole closed for 1s - SwitchStop','info')
			return procgame.game.SwitchStop
		else:
			self.game.utilities.log('BALLSAVE - Ouhole closed for 1s - SwitchContinue','info')
			return procgame.game.SwitchContinue

	#def sw_outhole_closed(self, sw):
		#if (self.game.utilities.get_player_stats('ballsave_active') == True):
			#self.game.utilities.log('BALLSAVE - Ouhole closed - SwitchStop - Disabling timers','info')
			#self.cancel_delayed('ballsaver')
			#return procgame.game.SwitchStop
		#else:
			#self.game.utilities.log('BALLSAVE - Ouhole closed - SwitchContinue','info')
			#return procgame.game.SwitchContinue

	##################################################
	## Skillshot Switches
	## These will set the ball in play when tripped
	##################################################
	def sw_rampEntry_active(self, sw):
                if (self.game.utilities.get_player_stats('ballsave_timer_active') == False):
			self.startBallSaverTimers()
                        self.log.info("Ramp made, ball save active, start timer")
		return procgame.game.SwitchContinue

	##################################################
	## Early Ballsave Switches
	## These will save the ball early if the trough has enough balls to support
	## WORK IN PROGRESS
	##################################################

	#def sw_rightOutlane_active(self, sw):
		#if (self.game.utilities.get_player_stats('ballsave_active') == True):
