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
#     ___
#    / _ ) ___   ___  __ __ ___
#   / _  |/ _ \ / _ \/ // /(_-<
#  /____/ \___//_//_/\_,_//___/
#
#################################################################################

import procgame
from procgame import *
import locale
import logging

class Bonus(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
			super(Bonus, self).__init__(game, priority)
			# Settings Variables #
			self.delay_time = 1.5
			self.bonus_value = 1000

			# System Variables #
			self.total_value = 0
			

	def mode_started(self):

		# Disable the flippers
		self.game.coils.flipperEnable.disable()
		self.game.sound.stop_music()
		self.game.utilities.disableGI()

		#### Disable All Lamps ####
		for lamp in self.game.lamps:
			lamp.disable()

	def mode_stopped(self):
		# Enable the flippers
		self.game.coils.flipperEnable.enable() # Can possibly remove this and let the "Ball Start" function handle it.
		#self.game.sound.stop_music() # Only needed if using background Bonus music
		self.game.utilities.enableGI()

	def calculate(self,callback):
		#self.game.sound.play_music('bonus', loops=1)
		self.callback = callback
		self.total_value = self.game.utilities.get_player_stats('bonus') * self.bonus_value * self.game.utilities.get_player_stats('bonus_x')
		self.bonus()

	def bonus(self):
		self.game.utilities.display_text(txt=str(self.game.utilities.get_player_stats('bonus'))+' BONUS'.upper(),txt2=locale.format("%d", self.game.utilities.get_player_stats('bonus') * self.bonus_value, True),time=self.delay_time)
		#self.game.sound.play('bonus_features')
		#self.game.sound.play('bonus_music')
		self.game.utilities.acFlashSchedule(coilname='upKicker_flasher3',schedule=0x0000000C, cycle_seconds=1, now=True)
		self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.multiplier)

	def multiplier(self):
		self.game.utilities.display_text(txt='X'+str(self.game.utilities.get_player_stats('bonus_x')).upper(),txt2=locale.format("%d", self.total_value, True),time=self.delay_time)
		#self.game.sound.play('bonus_features')
		self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.total)

	def total(self):
		self.game.utilities.score(self.total_value) # this should upadte the player score in question
		self.game.utilities.display_text(txt=locale.format("%d", self.game.utilities.currentPlayerScore(), True),time=self.delay_time)
		#self.game.sound.play('bonus_total')
		#self.game.utilities.acFlashSchedule(coilname='ejectHole_CenterRampFlashers4',schedule=0x00CCCCCC, cycle_seconds=1, now=True)
		#self.game.utilities.acFlashSchedule(coilname='outholeKicker_CaptiveFlashers',schedule=0x00CCCCCC, cycle_seconds=1, now=True)
		#self.game.coils.backboxLightingB.schedule(schedule=0x00CCCCCC, cycle_seconds=1, now=True)
		#self.game.lampctrlflash.play_show('bonus_total', repeat=False)
		self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.finish)		

	def finish(self):
		self.game.sound.stop_music()
		self.callback()
		#self.game.base_mode.end_ball()