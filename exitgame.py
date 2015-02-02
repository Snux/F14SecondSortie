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
import procgame
from procgame import *
class ExitGameMode(game.Mode):
	""" Simple mode to exit the game if the user holds both flipper buttons and start
		(and the game has that feature enabled).  Shamelessly stolen from tomlogic! """
                
	def __init__(self, game, priority):
		super(ExitGameMode, self).__init__(game, priority)
	
	def sw_startButton_active(self, sw):
		if self.game.user_settings['Standard']['Exit on flippers + start']:
			if self.game.switches.flipperLwL.is_closed() and self.game.switches.flipperLwR.is_closed():
				self.game.end_run_loop()
				return procgame.game.SwitchStop
		return procgame.game.SwitchContinue