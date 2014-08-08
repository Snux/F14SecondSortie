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
			
                        #setup logging
                        self.log = logging.getLogger('f14.locks')
                        
                        # Various info

                        # Is there a ball heading towards the divertor ramp
                        self.ballInTransit = False

                        # Is the ball which is coming into a lock just a replacement for an existing one?
                        self.ballReplacement = False

                        # Are we currently trying to restage a ball
                        self.restageLock = 'none'

                        # Add a handler for the ramp entry switch
                        self.add_switch_handler(name='rampEntry',event_type='active',delay=0.01, handler=self.transitStart)

                        # All the locks can be routed to the same handler
                        self.add_switch_handler(name='upperEject',event_type='active',delay=0.1, handler=self.lockhandler)
                        self.add_switch_handler(name='middleEject',event_type='active',delay=0.1, handler=self.lockhandler)
                        self.add_switch_handler(name='lowerEject',event_type='active',delay=0.1, handler=self.lockhandler)

                        # All the ramp switches route to the same handler
                        self.add_switch_handler(name='upperRampMade',event_type='active',delay=0.01,handler=self.ramphandler)
                        self.add_switch_handler(name='middleRampMade',event_type='active', delay=0.01, handler=self.ramphandler)
                        self.add_switch_handler(name='lowerRampMade',event_type='active', delay = 0.01, handler=self.ramphandler)


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
                if self.restageLock == 'upper':
                    self.log.info("Setting upper divertor to restage upper lock")
                    self.game.coils.upperDivertor.enable()
                    self.delay(name='failsafe', event_type=None, delay=5000, handler=self.failsafe)
                elif self.restageLock == 'middle':
                    self.log.info("Setting lower divertor to restage middle lock")
                    self.game.coils.lowerDivertor.enable()
                    self.delay(name='failsafe', event_type=None, delay=5000, handler=self.failsafe)
                elif self.restageLock == 'lower':
                    self.log.info("No divertor set, restage lower lock")

                elif self.game.utilities.get_player_stats('upper_lock') == 'lit' :
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

        ## This routine gets called when a ball is rolling down one of the ramps towards a lock
        ## It will take care of kicking out the ball which is already in the lock, if required
        ## If it does do the kickout, it sets a flag to indicate that which is used by the
        ## lock handler
        def ramphandler(self,sw):
            self.log.info("Ramp handler called for "+sw.name)
            if sw.name == 'lowerRampMade' and self.game.switches.lowerEject.is_active() == True:
                self.game.utilities.acCoilPulse(coilname='lowerEject_flasher7',pulsetime=50)
                self.ballReplacement = True
            elif sw.name == 'middleRampMade' and self.game.switches.middleEject.is_active() == True:
                self.game.coils.middleEject.pulse(50)
                self.ballReplacement = True
            elif sw.name == 'upperRampMade' and self.game.switches.upperEject.is_active() == True:
                self.game.utilities.acCoilPulse(coilname='upperEject_flasher5',pulsetime=50)
                self.ballReplacement = True
            if self.ballReplacement == True:
                self.log.info("Ball kicked from lock")
            else:
                self.log.info("No action required from ramp switch")


        ## This routine is called whenever a ball lands in a lock
        ## Code could get quite complex, but is easier centrally here than scattered across all
        ## the various modes
        def lockhandler(self,sw):
            self.log.info("Lock handler called for "+sw.name)
            # If we were restaging a missing locked ball, then we succeeded.
            if self.restageLock != 'none':
                self.log.info("Restaged "+self.restageLock+" lock")
                # Reset the indicator to say we're not staging now
                self.restageLock = 'none'
                # Call the restage check again in a second to see if we're good to go
                self.delay(name='check_staging', event_type=None, delay=1.0, handler=self.check_for_restage)
            else:
                if sw.name == 'upperEject':
                    if self.game.utilities.get_player_stats('upper_lock') == 'lit':
                        self.game.multiball_mode.lock_ball('upper',self.ballReplacement)
                    elif self.ballReplacement == False:
                        self.game.utilities.acCoilPulse(coilname='upperEject_flasher5',pulsetime=50)
                if sw.name == 'middleEject':
                    if self.game.utilities.get_player_stats('middle_lock') == 'lit':
                        self.game.multiball_mode.lock_ball('middle',self.ballReplacement)
                    elif self.ballReplacement == False:
                        self.game.coils.middleEject.pulse(50)
                if sw.name == 'lowerEject':
                    if self.game.utilities.get_player_stats('lower_lock') == 'lit':
                        self.game.multiball_mode.lock_ball('lower',self.ballReplacement)
                    elif self.ballReplacement == False:
                        self.game.utilities.acCoilPulse(coilname='lowerEject_flasher7',pulsetime=50)
            self.ballReplacement = False
            self.ballInTransit = False
            self.setDivertors()

            # Force the trough to recount the locked balls, after we've waited half a second for balls to clear and switches to settle
            self.delay(name='lock_count', event_type=None, delay=0.50, handler=self.game.trough.lock_count)
            
            

        # Called at the start of a ball if the number of locked balls is not enough for
        # this player.  Will autolaunch balls to locks.
        def check_for_restage(self):
            # Work through the locks for the player and see if there is a ball there.
            if self.game.utilities.get_player_stats('upper_lock') == 'locked' and self.game.switches.upperEject.is_closed() == False:
                self.restageLock = 'upper'
                self.game.trough.launch_balls(num=1,stealth=True,autolaunch=True)
            elif self.game.utilities.get_player_stats('middle_lock') == 'locked' and self.game.switches.middleEject.is_closed() == False:
                self.restageLock = 'middle'
                self.game.trough.launch_balls(num=1,stealth=True,autolaunch=True)
            elif self.game.utilities.get_player_stats('lower_lock') == 'locked' and self.game.switches.lowerEject.is_closed() == False:
                self.restageLock = 'lower'
                self.game.trough.launch_balls(num=1,stealth=True,autolaunch=True)
            else:
                self.game.base_mode.start_ball_actual()


        
        def sw_debug_active(self,sw):
            self.log.info("Balls in transit = "+str(self.ballInTransit))
