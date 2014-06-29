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
#     __ __ _        __     ____
#    / // /(_)___ _ / /    / __/____ ___   ____ ___
#   / _  // // _ `// _ \  _\ \ / __// _ \ / __// -_)
#  /_//_//_/ \_, //_//_/ /___/ \__/ \___//_/   \__/
#           /___/
#################################################################################

import procgame.game
from procgame import *
import pinproc

class HighScore(game.Mode):
	def __init__(self, game, priority):
			super(HighScore, self).__init__(game, priority)


	############################
	#### Standard Functions ####
	############################
	def mode_started(self):
		pass

	def update_lamps(self):
		pass

	def checkScores(self,callback):
		pass
	