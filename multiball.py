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
import logger

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
                self.log.info("Balls locked : "+self.ballsLocked)
		
	def liteLock(self,callback):
		self.callback = callback
		if (self.ballsLocked == 0):
			self.game.utilities.set_player_stats('lock1_lit',True)
			print "Setting Ball 1 Lock to Lit"
			self.getUserStats()
		elif (self.ballsLocked == 1):
			self.game.utilities.set_player_stats('lock2_lit',True)
			self.getUserStats()
		elif (self.ballsLocked == 2):
			self.game.utilities.set_player_stats('lock3_lit',True)
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
		#self.game.sound.play('earthquake_1')
		#self.game.sound.play_music('multiball_intro',loops=1,music_volume=.5)
		#self.game.coils.quakeMotor.schedule(schedule=0x08080808,cycle_seconds=-1,now=True)
                self.game.utilities.play_animation('second_sortie_rotate')
		self.resetMultiballStats()
		self.delay(delay=2,handler=self.multiballRun)

	def multiballRun(self):
                self.log.info("Multiball run")
		self.game.utilities.enableGI()

                # Make sure the trough knows how many balls are locked
                self.game.trough.num_balls_locked = 0
                self.balls_locked = 0

		#self.game.sound.play('centerRampComplete')
		self.game.sound.play_music('dangerzone',loops=-1,music_volume=.6)

                #kick the balls out
		self.game.utilities.acCoilPulse(coilname='rightEject_flasher7',pulsetime=50)
                self.game.utilities.acCoilPulse(coilname='centreRightEject_flasher5',pulsetime=50)
                self.game.coils.centreLeftEject.pulse(50)
		self.game.trough.launch_balls(num=1,autolaunch=True)
		self.multiballStarting = False
		self.game.update_lamps()

	def stopMultiball(self):
		self.game.utilities.set_player_stats('multiball_running',False)
		self.game.sound.stop_music()
		self.game.sound.play_music('main',loops=-1,music_volume=.5)
		self.resetMultiballStats()
		self.game.update_lamps()
		self.game.coils.quakeMotor.disable()
		self.callback()

	def resetMultiballStats(self):
		self.game.utilities.set_player_stats('upperLock','off')
		self.game.utilities.set_player_stats('middleLock','off')
		self.game.utilities.set_player_stats('lowerLock','off')
		self.game.utilities.set_player_stats('balls_locked',0)
		self.getUserStats()

        def sw_vUK_closed_for_1s(self, sw):
                if (self.upperLock == 'lit'):
                    self.game.coils.upperDivertor.enable()
                elif (self.middleLock == 'lit'):
                    self.game.coils.lowerDivertor.enable()
                self.game.utilities.acCoilPulse(coilname='upKicker_flasher3',pulsetime=50)

        def sw_rightEject_closed_for_1s(self,sw):
                if (self.lowerLock == 'lit'):
                    self.ballsLocked += 1
                    self.game.utilities.set_player_stats('lower_lock','locked')
                    self.game.utilities.set_player_stats('balls_locked',self.ballsLocked)
                    self.getUserStats()
                    self.update_lamps()
                return procgame.game.SwitchContinue

        def sw_rightCentreEject_closed_for_1s(self,sw):
                if (self.upperLock == 'lit'):
                    self.game.coils.upperDivertor.disable()
                    self.ballsLocked += 1
                    self.game.utilities.set_player_stats('upper_lock','locked')
                    self.game.utilities.set_player_stats('balls_locked',self.ballsLocked)
                    self.getUserStats()
                    self.update_lamps()
                
                return procgame.game.SwitchContinue

        def sw_leftCentreEject_closed_for_1s(self,sw):
                if (self.middleLock == 'lit'):
                    self.game.coils.lowerDivertor.disable()
                    self.ballsLocked += 1
                    self.game.utilities.set_player_stats('middle_lock','locked')
                    self.game.utilities.set_player_stats('balls_locked',self.ballsLocked)
                    self.getUserStats()
                    self.update_lamps()
                else:
                    

		return procgame.game.SwitchContinue


	def sw_underPlayfieldDrop1_active(self, sw):
		if (self.ballLock1Lit == True):
			self.lockBall1()
		elif (self.ballLock2Lit == True):
			self.lockBall2()
		elif (self.ballLock3Lit == True):
			self.startMultiball()
		else:
			pass

	def sw_ballPopperBottom_closed(self, sw):
		if(self.multiballStarting == True):
			return procgame.game.SwitchStop
		else:
			return procgame.game.SwitchContinue

	def sw_outhole_closed_for_500ms(self, sw):
		#if (self.game.trough.num_balls_in_play == 2):
			#Last ball - Need to stop multiball
			#self.stopMultiball()
		return procgame.game.SwitchContinue



