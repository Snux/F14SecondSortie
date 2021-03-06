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
			#self.game.utilities.get_player_stats('balls_locked') = 0
                        #self.ballsLanded = 0
			#self.game.utilities.get_player_stats('upper_lock') = 'off'
			#self.game.utilities.get_player_stats('middle_lock') = 'off'
			#self.game.utilities.get_player_stats('lower_lock') = 'off'

			self.multiballStarting = False
                        self.skipLanding = False
			self.multiballIntroLength = 11.287
                        self.log = logging.getLogger('f14.multiball')

	def mode_started(self):
		self.update_lamps()
		return super(Multiball, self).mode_started()

	#def mode_stopped(self):
		#self.game.update_lamps()

	def update_lamps(self):
		self.disableLockLamps()

		if self.game.utilities.get_player_stats('upper_lock') == 'lit':
			self.game.lamps.upperLock.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.lockOn.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		elif self.game.utilities.get_player_stats('upper_lock') == 'locked':
			self.game.lamps.upperLock.enable()

                if self.game.utilities.get_player_stats('upper_landing') == 'landing':
                        self.game.lamps.upperLanding.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.landing.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
                elif self.game.utilities.get_player_stats('upper_landing') == 'landed':
                        self.game.lamps.upperLanding.enable()

                if self.game.utilities.get_player_stats('middle_lock') == 'lit':
			self.game.lamps.middleLock.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.lockOn.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		elif self.game.utilities.get_player_stats('middle_lock') == 'locked':
			self.game.lamps.middleLock.enable()

                if self.game.utilities.get_player_stats('middle_landing') == 'landing':
                        self.game.lamps.middleLanding.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.landing.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
                elif self.game.utilities.get_player_stats('middle_landing') == 'landed':
                        self.game.lamps.middleLanding.enable()


                if self.game.utilities.get_player_stats('lower_lock') == 'lit':
			self.game.lamps.lowerLock.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.lockOn.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		elif self.game.utilities.get_player_stats('lower_lock') == 'locked':
			self.game.lamps.lowerLock.enable()

                if self.game.utilities.get_player_stats('lower_landing') == 'landing':
                        self.game.lamps.lowerLanding.schedule(schedule=0xFF00FF00, cycle_seconds=0, now=True)
			self.game.lamps.landing.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
                elif self.game.utilities.get_player_stats('lower_landing') == 'landed':
                        self.game.lamps.lowerLanding.enable()


                if self.game.utilities.get_player_stats('balls_locked') == 3:
                    self.game.lamps.release.schedule(schedule=0xF0F0F0F0, cycle_seconds=0, now=True)
			
        # Switch off all the lamps related to the locks, then the update lamp routine can just take care
        # of switching back on the ones that are needed
	def disableLockLamps(self):
		self.game.lamps.lowerLock.disable()
		self.game.lamps.middleLock.disable()
		self.game.lamps.upperLock.disable()
                self.game.lamps.lowerLanding.disable()
		self.game.lamps.middleLanding.disable()
		self.game.lamps.upperLanding.disable()
                self.game.lamps.release.disable()
                self.game.lamps.lockOn.disable()
                self.game.lamps.landing.disable()


        # This will be called from the base mode whenever all the TOMCAT targets have been lit.
        # It will decide which lock to light - this can be made more complex later
	def liteLock(self):
	        if self.game.utilities.get_player_stats('multiball_running') ==  'None':
                    if (self.game.utilities.get_player_stats('balls_locked') == 0):
                            self.game.utilities.set_player_stats('middle_lock','lit')
                            self.game.utilities.play_animation('lock_is_lit',frametime=2)
                    elif (self.game.utilities.get_player_stats('balls_locked') == 1):
                            self.game.utilities.set_player_stats('upper_lock','lit')
                            self.game.utilities.play_animation('lock_is_lit',frametime=2)
                    elif (self.game.utilities.get_player_stats('balls_locked') == 2):
                            self.game.utilities.set_player_stats('lower_lock','lit')
                            self.game.utilities.play_animation('lock_is_lit',frametime=2)
                    self.update_lamps()

	
	def startMultiball(self):
                self.log.info("Start multiball")
		self.multiballStarting = True
		self.game.utilities.set_player_stats('multiball_running','Standard')
                self.game.utilities.set_player_stats('multiballs_played',1,mode='add')
		self.resetMultiballStats()
                self.setupLanding()
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

                # Switch the stats over to landing instead of regular locks lit
                self.setupLanding()

                # Make sure the trough knows how many balls are locked
                self.game.trough.num_balls_locked = 0
                self.game.utilities.set_player_stats('balls_locked',0)
        
		#self.game.sound.play('centerRampComplete')
		self.game.sound.play_music('dangerzone')

                #kick the balls out
		self.game.utilities.acCoilPulse(coilname='lowerEject_flasher7',pulsetime=50)
                self.game.utilities.acCoilPulse(coilname='upperEject_flasher5',pulsetime=50)
                self.game.coils.middleEject.pulse(50)
                self.kickVUK()
                
                # We know one ball will arrive in the landing from the vUK at the start but
                # it doesn't count
                self.skipLanding = True


                # Tell the trough we now now have 3 balls in play, then have it kick another
                self.game.trough.num_balls_in_play = 4
                #self.log.info("Launch ball auto due to multiball")
		#self.game.trough.launch_balls(num=1,autolaunch=True)

		self.multiballStarting = False
		self.game.update_lamps()
                self.multiball_reminder()

        def multiball_reminder(self):
                self.game.utilities.play_animation('tomcat_multiball_rotate')
		self.delay(name='reminder', event_type=None, delay=4.0, handler=self.multiball_reminder)

	def stopMultiball(self):
                self.log.info("Stop multiball")
		self.game.utilities.set_player_stats('multiball_running','None')
                self.resetLanding()
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

        # This handles the holding over of successfully landed balls from previous multiball
        def setupLanding(self):
                if self.game.utilities.get_player_stats('upper_landing') == 'off':
                    self.game.utilities.set_player_stats('upper_landing','landing')
                if self.game.utilities.get_player_stats('middle_landing') == 'off':
                    self.game.utilities.set_player_stats('middle_landing','landing')
                if self.game.utilities.get_player_stats('lower_landing') == 'off':
                    self.game.utilities.set_player_stats('lower_landing','landing')

        # At the end of multiball this will clear locks waiting for landing
        def resetLanding(self):
                if self.game.utilities.get_player_stats('upper_landing') == 'landing':
                    self.game.utilities.set_player_stats('upper_landing','off')
                if self.game.utilities.get_player_stats('middle_landing') == 'landing':
                    self.game.utilities.set_player_stats('middle_landing','off')
                if self.game.utilities.get_player_stats('lower_landing') == 'landing':
                    self.game.utilities.set_player_stats('lower_landing','off')


        # Called from lock handler when a ball stops in a lock and it was lit
        # for regular lock or for landing
        def lock_ball(self,location,replacement):
            # FIrst of all work out if this is a regular lock or it's for landing during multiball

            if self.game.utilities.get_player_stats(location+'_lock') == 'lit':
                self.log.info("Locking ball in location "+location)
                ballsLocked = self.game.utilities.get_player_stats('balls_locked')
                ballsLocked += 1
                self.game.utilities.play_animation('ball_'+str(ballsLocked)+'_locked',frametime=2)
                self.game.utilities.set_player_stats(location+'_lock','locked')
                self.game.utilities.set_player_stats('balls_locked',ballsLocked)
                self.update_lamps()
                # Only lock ball physically and launch another if a ball wasn't already cleared
                # from the lock to make space for this one.
                if replacement == False:
                    self.log.info("Launch ball manual as ball locked")
                    self.game.trough.launch_balls(num=1,stealth=True)
            else:
                self.log.info("Ball has landed in location "+location)
                ballsLanded = self.game.utilities.get_player_stats('balls_landed')
                ballsLanded += 1
                self.game.utilities.play_animation('f14landing',txt='LANDINGS : '+str(ballsLanded))
                self.game.utilities.set_player_stats('balls_landed',ballsLanded)
                if replacement == False:
                    self.game.utilities.set_player_stats(location+'_landing','landed')
                    if location == 'upper':
                        self.game.utilities.acCoilPulse(coilname='upperEject_flasher5',pulsetime=50)
                    elif location == 'middle':
                        self.game.coils.middleEject.pulse(50)
                    else:
                        self.game.utilities.acCoilPulse(coilname='lowerEject_flasher7',pulsetime=50)
                if ballsLanded % 3 == 0:
                    self.game.utilities.display_text(txt='JACKPOT')
                    self.game.utilities.set_player_stats('upper_landing','landing')
                    self.game.utilities.set_player_stats('middle_landing','landing')
                    self.game.utilities.set_player_stats('lower_landing','landing')
            self.update_lamps()


        def sw_vUK_active(self, sw):
                if self.game.utilities.get_player_stats('balls_locked') == 3:
                    self.startMultiball()
                    return procgame.game.SwitchStop
                elif (self.game.utilities.get_player_stats('lower_lock') == 'lit' or
                      self.game.utilities.get_player_stats('middle_lock') == 'lit' or
                      self.game.utilities.get_player_stats('upper_lock') == 'lit' ):
                         self.game.lampctrlflash.play_show('topstrobe',repeat=False)
                         # Let the lampshow play etc, then kick the ball after 1.5 seconds.
                         self.game.utilities.play_animation('lock_on',frametime=1,txt='MISSILE LOCK ON')
                         self.game.sound.play('lock_on')
                         self.delay(name='kickvuk', event_type=None, delay=1.5, handler=self.kickVUK)
                         return procgame.game.SwitchStop

        def kickVUK(self):
            self.game.utilities.acCoilPulse(coilname='upKicker_flasher3',pulsetime=50)
            self.game.locks.transitStart('base')




	
        def sw_debug_active(self,sw):
            self.log.info("Balls locked = "+str(self.game.utilities.get_player_stats('balls_locked')))
            self.log.info("Upper lock = "+self.game.utilities.get_player_stats('upper_lock'))
            self.log.info("Middle lock = "+self.game.utilities.get_player_stats('middle_lock'))
            self.log.info("Lower lock = "+self.game.utilities.get_player_stats('lower_lock'))

