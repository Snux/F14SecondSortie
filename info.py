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


# Mode for displaying instant info - stolen unashamedly from JD :)
#################################################################################
##
#     ____       ___
#    /  _/___   / _/___
#   _/ / / _ \ / _// _ \
#  /___//_//_//_/  \___/
#
#
##
#################################################################################


import procgame
from procgame import *
import procgame.dmd
from procgame.dmd import font_named

class Info(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Info, self).__init__(game, priority)
		self.title_layer = dmd.TextLayer(128/2, 1, font_named("04B-03-7px.dmd"), "center").set_text('SECOND SORTIE - INSTANT INFO')
		#self.item_layer = dmd.TextLayer(128/2, 15, self.game.fonts['tiny7'], "center")
		#self.value_layer = dmd.TextLayer(128/2, 23, self.game.fonts['tiny7'], "center")

		self.info_layer = dmd.GroupedLayer(128, 32, [self.title_layer])

	def set_layers(self, layers):
		self.layers = [self.info_layer]
		self.layers.extend(layers)
	
	def mode_started(self):
		self.index = 0
		self.index_max = len(self.layers) - 1
		self.update_display()
		
	def sw_flipperLwL_active(self,sw):
		if self.game.switches.flipperLwR.is_active():
			self.progress(False)

	def sw_flipperLwR_active(self,sw):
		if self.game.switches.flipperLwL.is_active():
			self.progress(True)

	def sw_flipperLwL_inactive(self,sw):
		if self.game.switches.flipperLwR.is_inactive():
			self.exit()

	def sw_flipperLwR_inactive(self,sw):
		if self.game.switches.flipperLwL.is_inactive():
			self.exit()

	def exit(self):
		self.cancel_delayed('delayed_progression')
                self.callback()

	def progress(self, direction):
		self.cancel_delayed('delayed_progression')
		if direction:
			if self.index == self.index_max:
				self.index = 0
			else:
				self.index += 1
		else:
			if self.index == 0:
				self.index = self.index_max
			else:
				self.index -= 1
		self.update_display()

	def update_display(self):
		#self.layer = self.layers[self.index]
                self.layers[self.index].composite_op = 'blacksrc'
                self.layer = dmd.GroupedLayer(128, 32, [self.title_layer,self.layers[self.index]])
		#self.item_layer.set_text('Item ' + str(self.index))
		#self.value_layer.set_text(str(self.index))
		self.delay(name='delayed_progression', event_type=None, delay=3.0, handler=self.progress, param=True)

