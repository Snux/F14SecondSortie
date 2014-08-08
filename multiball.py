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
#     __  ___     ____  _ __        ____
#    /  |/  /_ __/ / /_(_) /  ___ _/ / /
#   / /|_/ / // / / __/ / _ \/ _ `/ / /
#  /_/  /_/\_,_/_/\__/_/_.__/\_,_/_/_/
#
#################################################################################

import procgame.game
from procgame import *
import pinproc
from random import choice
from random import seed
import logging

class Multiball(game.Mode):
	def __init__(self, game, priority):
			super(Multiball, self).__init__(game, priority)
			self.ballsLocked = 0
			self.upperLock = 'off'
			self.middleLock = 'off'
			self.lowerLock = 'off'

			self.multiballStarting = False
			self.multiballIntroLength = 11.287
                        self.log = logging.getLogger('f14.multiball')

	def mode_started(self):
		self.getUserStats()
		self.update_lamps()
		return super(Multiball, self).mode_started()

	#def mode_stopped(self):
		#self.game.update_lamps()

	def update_lamps(self):
		self.disableLockLamps()

		if (self.upperLock == 'lit'):
			self.game.lamps.upperLock.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.lockOn.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		elif (self.upperLock == 'locked'):
			self.game.lamps.upperLock.enable()

                if (self.middleLock == 'lit'):
			self.game.lamps.middleLock.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.lockOn.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		elif (self.middleLock == 'locked'):
			self.game.lamps.middleLock.enable()

                if (self.lowerLock == 'lit'):
			self.game.lamps.lowerLock.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.lockOn.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		elif (self.lowerLock == 'locked'):
			self.game.lamps.lowerLock.enable()
			
			
	def disableLockLamps(self):
		self.game.lamps.lowerLock.disable()
		self.game.lamps.middleLock.disable()
		self.game.lamps.upperLock.disable()
                self.game.lamps.lockOn.disable()

	def getUserStats(self):
		self.upperLock = self.game.utilities.get_player_stats('upper_lock')
		self.middleLock = self.game.utilities.get_player_stats('middle_lock')
		self.lowerLock = self.game.utilities.get_player_stats('lower_lock')
		self.ballsLocked = self.game.utilities.get_player_stats('balls_locked')
                self.log.info("Upper lock : "+self.upperLock)
                self.log.info("Middle lock : "+self.middleLock)
                self.log.info("Lower lock : "+self.lowerLock)
                self.log.info("Balls locked : "+str(self.ballsLocked))
		
	def liteLock(self):
	#	self.callback = callback
                if self.game.utilities.get_player_stats('multiball_running') ==  False:
                    if (self.ballsLocked == 0):
                            self.game.utilities.set_player_stats('middle_lock','lit')
                            self.game.utilities.play_animation('lock_is_lit',frametime=2)
                            self.getUserStats()
                    elif (self.ballsLocked == 1):
                            self.game.utilities.set_player_stats('upper_lock','lit')
                            self.game.utilities.play_animation('lock_is_lit',frametime=2)
                            self.getUserStats()
                    elif (self.ballsLocked == 2):
                            self.game.utilities.set_player_stats('lower_lock','lit')
                            self.game.utilities.play_animation('lock_is_lit',frametime=2)
                            self.getUserStats()
                    self.update_lamps()

	
	def startMultiball(self):
                self.log.info("Start multiball")
		self.multiballStarting = True
		self.game.utilities.set_player_stats('multiball_running',True)
		self.resetMultiballStats()
		#self.game.collect_mode.incrementActiveZoneLimit()
		self.getUserStats()
		self.update_lamps()
		self.multiballIntro()

	def multiballIntro(self):
                self.log.info("Multiball intro")
		self.game.utilities.disableGI()
		self.game.sound.stop_music()
		# Sound FX #
		#self.game.sound.play('main_loop_tape_stop')
		self.game.utilities.play_animation('second_sortie_rotate')
		self.resetMultiballStats()
		self.delay(delay=2,handler=self.multiballRun)

	def multiballRun(self):
                self.log.info("Multiball run")
		self.game.utilities.enableGI()

                # Make sure the trough knows how many balls are locked
                self.game.trough.num_balls_locked = 0
                self.game.utilities.set_player_stats('balls_locked',0)
                self.getUserStats()

		#self.game.sound.play('centerRampComplete')
		self.game.sound.play_music('dangerzone')

                #kick the balls out
		self.game.utilities.acCoilPulse(coilname='lowerEject_flasher7',pulsetime=50)
                self.game.utilities.acCoilPulse(coilname='upperEject_flasher5',pulsetime=50)
                self.game.coils.middleEject.pulse(50)

                # Tell the trough we now now have 3 balls in play, then have it kick another
                self.game.trough.num_balls_in_play = 3
                self.log.info("Launch ball auto due to multiball")
		self.game.trough.launch_balls(num=1,autolaunch=True)

		self.multiballStarting = False
		self.game.update_lamps()
                self.multiball_reminder()

        def multiball_reminder(self):
                self.game.utilities.play_animation('tomcat_multiball_rotate')
		self.delay(name='reminder', event_type=None, delay=4.0, handler=self.multiball_reminder)

	def stopMultiball(self):
                self.log.info("Stop multiball")
		self.game.utilities.set_player_stats('multiball_running',False)
                self.cancel_delayed('reminder')
		self.game.sound.stop_music()
		self.game.sound.play_music('tomcatmain',loops=-1)
		self.resetMultiballStats()
		self.game.update_lamps()
		#self.callback()

	def resetMultiballStats(self):
		self.game.utilities.set_player_stats('upper_lock','off')
		self.game.utilities.set_player_stats('middle_lock','off')
		self.game.utilities.set_player_stats('lower_lock','off')
                self.game.trough.num_balls_locked = 0
		self.game.utilities.set_player_stats('balls_locked',0)
		self.getUserStats()

        # Called from lock handler when a ball stops in a lock and it was lit
        def lock_ball(self,location,replacement):
            self.log.info("Locking ball in location "+location)
            self.ballsLocked += 1
            self.game.utilities.play_animation('ball_'+str(self.ballsLocked)+'_locked',frametime=2)
            self.game.utilities.set_player_stats(location+'_lock','locked')
            self.game.utilities.set_player_stats('balls_locked',self.ballsLocked)
            self.getUserStats()
            self.update_lamps()
            # Only lock ball physically and launch another if a ball wasn't already cleared
            # from the lock to make space for this one.
            if self.ballsLocked == 3:
                self.startMultiball()
            elif replacement == False:
                #self.game.trough.num_balls_locked += 1
                self.log.info("Launch ball manual as ball locked")
                self.game.trough.launch_balls(num=1,stealth=True)


                    

	
        def sw_debug_active(self,sw):
            self.log.info("Balls locked = "+str(self.ballsLocked))
            self.log.info("Upper lock = "+self.upperLock)
            self.log.info("Middle lock = "+self.middleLock)
            self.log.info("Lower lock = "+self.lowerLock)

