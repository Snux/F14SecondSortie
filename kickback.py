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
#     __ __ _       __    __              __
#    / //_/(_)____ / /__ / /  ___ _ ____ / /__
#   / ,<  / // __//  '_// _ \/ _ `// __//  '_/
#  /_/|_|/_/ \__//_/\_\/_.__/\_,_/ \__//_/\_\
#
#################################################################################

import procgame.game
from procgame import *
import procgame.dmd
from procgame.dmd import font_named
import pinproc
import locale
import math
import random
import logging

#### Set Locale ####
locale.setlocale(locale.LC_ALL, "")

class KickbackMode(game.Mode):
	def __init__(self, game, priority):
			super(KickbackMode, self).__init__(game, priority)
			self.log = logging.getLogger('f14.kickback')

	def mode_started(self):

		## This mode gets started when a ball starts

                ## After the kick back has activated, there is a short grace period before it de-activates
                self.kickback_grace=False

                # which side is currently lit
                self.rescue = 'off'
                self.rescueRight()

        # Light the right rescue lamp
        def rescueRight(self):
            self.rescue = 'right'
            self.update_lamps()
            self.delay(name='rescue', event_type=None, delay=1, handler=self.rescueLeft)

        # Light the left rescue lamp
        def rescueLeft(self):
            self.rescue = 'left'
            self.update_lamps()
            self.delay(name='rescue', event_type=None, delay=1, handler=self.rescueRight)

        # Set the kick back is active
        def enable_kickback(self):
            self.game.utilities.set_player_stats('kickback_lit',True)
            self.game.utilities.play_animation('rescue_active',frametime=1)
            self.update_lamps()
        
        def update_lamps(self):
                if self.game.utilities.get_player_stats('kickback_lit')==True:
                    if self.kickback_grace == True:
                        self.game.lamps.kickBack.schedule(schedule=0xF0F0F0F0)
                    else:
                        self.game.lamps.kickBack.enable()
                else:
                    self.game.lamps.kickBack.disable()
                if self.rescue == 'right':
                    self.game.lamps.leftRescue.enable()
                else:
                    self.game.lamps.leftRescue.disable()
                if self.rescue == 'left':
                    self.game.lamps.rightRescue.enable()
                else:
                    self.game.lamps.rightRescue.disable()

        # If the left rescue target is hit, and it's lit, enable the kickback
        def sw_leftRescue_active(self,sw):
            if self.rescue == 'left':
                if self.game.utilities.get_player_stats('kickback_lit')==False:
                    self.enable_kickback()

        def sw_rightRescue_active(self,sw):
            if self.rescue == 'right':
                if self.game.utilities.get_player_stats('kickback_lit')==False:
                    self.enable_kickback()


        # If the ball drains down the left outlane
        def sw_outlaneLeft_active(self,sw):

            # If the kickback is enabled
            if self.game.utilities.get_player_stats('kickback_lit')==True:
                # Fire the kickback
                self.game.coils.rescueKickBack.pulse(100)
                # If we're not in the grace period already, then schedule it
                if self.kickback_grace == False:
                    self.delay(name='grace', event_type=None, delay=2, handler=self.grace_finished)
                    self.kickback_grace=True
                self.update_lamps()
                self.game.utilities.play_animation('ball_rescued',frametime=1)

        # At the end of the grace period, switch the kickback off
        def grace_finished(self):
            self.kickback_grace=False
            self.game.utilities.set_player_stats('kickback_lit',False)
            self.update_lamps()

        # This mode gets started and stopped on each ball, so at the end of the mode cancel any grace
	def mode_stopped(self):
            if self.kickback_grace == True:
                self.cancel_delayed('grace')
                self.grace_finished()
            self.cancel_delayed('rescue')
            self.rescue = 'none'
            self.update_lamps()
