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
#     __            __
#    / /  ___  ____/ /__ ___
#   / /__/ _ \/ __/  '_/(_-<
#  /____/\___/\__/_/\_\/___/
#
#################################################################################
#
# The main ramp with it's divertors and related ramps and locks is a complicated
# beast to handle.  Rather than every module having it's own divertors, ramp and
# lock handling we'll handle it all here so it'll be easier to track things.
#
#################################################################################

import procgame
from procgame import *
import locale
import logging
import random
import procgame.dmd
from procgame.dmd import font_named

class LocksMode(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
			super(LocksMode, self).__init__(game, priority)
			self.kill_list=['kill1','kill2','kill3','kill4','kill5','kill6','kill7']
                        self.mission_name= {'kill1' : 'alpha',
                                            'kill2' : 'bravo',
                                            'kill3' : 'charlie',
                                            'kill4' : 'delta',
                                            'kill5' : 'echo',
                                            'kill6' : 'foxtrot',
                                            'kill7' : 'golf'
                                            }


                        #setup logging
                        self.log = logging.getLogger('f14.locks')
                        
                        # Various info
                        
                        # Is there a ball heading towards the divertor ramp
                        self.ballInTransit = False

                        # Add a handler for the ramp entry switch
                        self.add_switch_handler(name='rampEntry',event_type='active',delay=0.01, handler=self.transitStart)




        # Used to indicate that a ball is heading towards the divertors.  Either called from this modes switch handler on the
        # ramp entry, or directly from the base mode when when the vUK is kicked.
        def transitStart(self,sw):
            self.log.info("Ball is in transit to divertor")
            self.ballInTransit = True
            self.setDivertors()

        # If the ball is in the shooter lane, check to see if we thought the ball was actually heading to the
        # divertors and reset if it was
        def sw_shooter_closed_for_1s(self, sw):
            if self.ballInTransit == True:
                self.log.info("Ball no longer in transit - returned to shooter")
                self.ballInTransit = False
                self.setDivertors()

        # Used to decide which divertor (or none) to activate, which will decide where the ball will go
        def setDivertors(self):
            if self.ballInTransit == False:
                self.log.info("Switching divertors off")
                self.game.coils.upperDivertor.disable()
                self.game.coils.lowerDivertor.disable()
            else:
                if self.game.utilities.get_player_stats('upper_lock') == 'lit':
                    self.log.info("Setting upper divertor as upper lock is lit")
                    self.game.coils.upperDivertor.enable()
                    self.delay(name='failsafe', event_type=None, delay=5000, handler=self.failsafe)
                elif self.game.utilities.get_player_stats('middle_lock') == 'lit':
                    self.log.info("Setting lower divertor as middle lock is lit")
                    self.game.coils.lowerDivertor.enable()
                    self.delay(name='failsafe', event_type=None, delay=5000, handler=self.failsafe)
                elif self.game.utilities.get_player_stats('lower_lock') == 'lit':
                    self.log.info("Leaving for lower ramp as lock is lit")
                else:
                    self.log.info("No locks - choosing divertor")
                    ## This can be extended to pick a random path for the ball or some other clever logic

        # Called if the divertor has been open for more than 5 seconds.
        def failsafe(self):
            self.log.warning("Failsafe reset of divertors")
            self.ballInTransit = False
            self.setDivertors()


        ## This is emergency code for the 3 ramp switches.  If a ramp switch is triggered and there is a ball in the lock already
        ## we need to kick it out otherwise we'll jam the lock up and stop the game.  This should in theory not be required when
        ## all game play possibilities have been coded, but for now it's safer :)
        def sw_lowerRampMade_active(self,sw):
            if self.game.switches.lowerEject.is_active() == True:
                self.log.info("Emergency kick lower lock")
                self.game.utilities.acCoilPulse(coilname='lowerEject_flasher7',pulsetime=50)
            else:
                self.log.info("No action, lower lock is empty")


        def sw_middleRampMade_active(self,sw):
            if self.game.switches.middleEject.is_active() == True:
                self.log.info("Emergency kick middle lock")
                self.game.coils.middleEject.pulse(50)
            else:
                self.log.info("No action, middle lock is empty")

        def sw_upperRampMade_active(self,sw):
            if self.game.switches.upperEject.is_active() == True:
                self.log.info("Emergency kick upper lock")
                self.game.utilities.acCoilPulse(coilname='upperEject_flasher5',pulsetime=50)
            else:
                self.log.info("No action, upper lock is empty")

        def sw_debug_active(self,sw):
            self.log.info("Balls in transit = "+str(self.ballInTransit))
