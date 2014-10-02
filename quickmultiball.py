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

class QuickMultiball(game.Mode):
	def __init__(self, game, priority):
			super(QuickMultiball, self).__init__(game, priority)
			#self.game.utilities.get_player_stats('balls_locked') = 0
                        #self.ballsLanded = 0
			#self.game.utilities.get_player_stats('upper_lock') = 'off'
			#self.game.utilities.get_player_stats('middle_lock') = 'off'
			#self.game.utilities.get_player_stats('lower_lock') = 'off'

			self.multiballStarting = False
                        self.log = logging.getLogger('f14.quick_multiball')

	def mode_started(self):
		self.update_lamps()
		return super(QuickMultiball, self).mode_started()

                self.reset_targets()
            
                # This is a timed multiball, we want it to play for at least 30 seconds
                # We will use the standard ball saver mode to do this, but will need to flag it as 
                # a custom ball save and set the required time to over-ride the default.
                self.game.ballsaver_mode.ballSaverTime = 30
                self.game.ballsaver_mode.ballSaverType = 'custom'
                self.game.modes.add(self.game.ballsaver_mode)

                # Update the multiball flag so other modes are aware
                self.game.utilities.set_player_stats('multiball_running','Quick')

                # Now we need to decide where the second ball is going to come from.
                # If there is a ball in the trough, we'll have one from there as it means
                # we won't need to disturb one which is locked....

                if self.game.trough.num_balls() > 0:
                    self.game.trough.launch_balls(num=1,autolaunch=True)

        # Reset the targets for next round
        def reset_targets(self):
            for target in self.game.tomcatTargetIndex:
                self.tomcatTargets[target]=False

	#def mode_stopped(self):
		#

	def update_lamps(self):
            for target in self.game.tomcatTargetIndex:
                if self.tomcatTargets[target]==False:
                    self.game.lamps[target].schedule(schedule=0xFFFF0000)
                else:
                    self.game.lamps[target].enable()

        



	
	def startMultiball(self):
                self.log.info("Start multiball")
		self.multiballStarting = True
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

                
		#self.game.sound.play('centerRampComplete')
		self.game.sound.play_music('dangerzone')

                
                
		self.multiballStarting = False
		self.game.update_lamps()
                self.multiball_reminder()

        def multiball_reminder(self):
                self.game.utilities.play_animation('tomcat_multiball_rotate')
		self.delay(name='reminder', event_type=None, delay=4.0, handler=self.multiball_reminder)

	def stopMultiball(self):
                self.log.info("Stop quick multiball")
		self.game.utilities.set_player_stats('multiball_running','None')
                self.cancel_delayed('reminder')
		self.game.sound.stop_music()
		self.game.sound.play_music('tomcatmain',loops=-1)
		self.resetMultiballStats()
		self.game.update_lamps()
		#self.callback()

	

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

        

        # This handler for the TOMCAT targets is actually polled by the base mode which handles all of these

        def targetTOMCAT(self,sw):
            # If this mode is active, then process the switch hit and return SwitchStop to the base mode
            # so no other mode is using it
            if self.active :
                if sw.name == self.game.tomcatTargetIndex[self.current_position]:
                    self.game.utilities.score(20000)
                    self.game.utilities.display_text(txt="TARGET HIT",time=3)
                    self.target_speed /= 2
                else:
                    self.game.utilities.score(1500)
                self.tomcatTargets[sw.name]=True
                self.game.sound.play('tomcat')
                #if sw.name[0:5]=="upper":
                #    otherside="lower"+sw.name[5:]
                #else:
                #    otherside="upper"+sw.name[5:]
                #self.tomcatTargets[otherside]=True
                return procgame.game.SwitchStop

	
        
