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
#     __  ___       _         _____                   _____         __
#    /  |/  /___ _ (_)___    / ___/___ _ __ _  ___   / ___/___  ___/ /___
#   / /|_/ // _ `// // _ \  / (_ // _ `//  ' \/ -_) / /__ / _ \/ _  // -_)
#  /_/  /_/ \_,_//_//_//_/  \___/ \_,_//_/_/_/\__/  \___/ \___/\_,_/ \__/
#
#################################################################################

###################################
# SYSTEM IMPORTS
###################################
import procgame.game
from procgame import *
import pinproc
import locale
import os
import logging
from time import strftime

###################################
# MODE IMPORTS
###################################
from base import *
from attract import *
from utilities import *
from tilt import *
from centerramp import *
from player import *
from ballsaver import *
from bonus import *
from mission import *
#from droptargets import *
#from collectzones import *
#from spinner import *
#from multiball import *
from trough import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

################################################
# GLOBAL PATH VARIABLES
################################################
game_machine_type = 'wpc'
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))
settings_path = curr_file_path + "/config/settings.yaml"
game_data_path = curr_file_path + "/config/game_data.yaml"
game_data_template_path = curr_file_path + "/config/game_data_template.yaml"
settings_template_path = curr_file_path + "/config/settings_template.yaml"
game_machine_yaml = curr_file_path + "/config/f14.yaml"
game_music_path = curr_file_path + "/assets/music/"
game_sound_path = curr_file_path + "/assets/sound/"
game_lampshows = curr_file_path + "/lamps/"
fnt_path = "/shared/dmd/"

ballsPerGame = 3 # this will eventually be called from the config file


################################################
# GAME CLASS
################################################
class F14SecondSortie(game.BasicGame):
	def __init__(self):
		super(F14SecondSortie, self).__init__(pinproc.MachineTypeWPC95)
		self.load_config(game_machine_yaml)

                
        	self.logging_enabled = True
		self.balls_per_game = ballsPerGame

                ### Set Logging Info ###
		logging.basicConfig(filename='f14.txt',level=logging.INFO)

		#### Settings and Game Data ####
		self.load_settings(settings_template_path, settings_path)
		self.load_game_data(game_data_template_path, game_data_path)

		#update audit data on boot up time
		self.game_data['Time Stamps']['Last Boot-Up'] =str(strftime("%d %b %Y %H:%M"))
		if self.game_data['Time Stamps']['First Boot-Up']=='Not Set':
			self.game_data['Time Stamps']['First Boot-Up'] = self.game_data['Time Stamps']['Last Boot-Up']
		self.save_game_data()
                self.reset()

	def reset(self):
		super(F14SecondSortie, self).reset()
                
		self.ball = 0
		self.old_players = []
		self.old_players = self.players[:]
		self.players = []
		self.current_player_index = 0

                self.shooter_lane_status = 0
		self.tiltStatus = 0

		#setup high scores
		self.highscore_categories = []

		#### Classic High Score Data ####
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'ClassicHighScoreData'
		self.highscore_categories.append(cat)

		#### Mileage Champ ####
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'BonusLoops'
		self.highscore_categories.append(cat)

		for category in self.highscore_categories:
			category.load_from_game(self)

		#### Setup Sound Controller ####
		self.sound = sound.SoundController(self)
		self.RegisterSound()

		#### Setup Lamp Controller ####
		self.lampctrl = procgame.lamps.LampController(self)
		self.lampctrlflash = procgame.lamps.LampController(self)
		#self.RegisterLampshows()

		#### software version number ####
		self.revision = "2.0.0"

		#### Mode Definitions ####
		self.utilities = UtilitiesMode(self,100)
		self.trough = Trough(self,0)
		self.base_mode = BaseGameMode(self,0)
		self.attract_mode = AttractMode(self,1)
                self.mission = MissionMode(self,2)
                self.kill1mission = Kill1Mode(self,3)
		#self.centerramp_mode = CenterRampMode(self,8)
		#self.drops_mode = DropTargets(self,9)
		#self.collect_mode = CollectZones(self,10)
		#self.spinner_mode = Spinner(self,11)
		#self.skillshot_mode = SkillshotMode(self,100)
		self.ballsaver_mode = BallSaver(self,1)
		#self.tilt = Tilt(self,200)
		self.bonus_mode = Bonus(self,1000)
		#self.multiball_mode = Multiball(self,101)
		
		#### Initial Mode Queue ####
		self.modes.add(self.utilities)
		self.modes.add(self.trough)
		self.modes.add(self.base_mode)
                self.modes.add(self.mission)

	def save_settings(self):
			super(F14SecondSortie, self).save_settings(settings_path)

	def save_game_data(self):
			super(F14SecondSortie, self).save_game_data(game_data_path)

	def RegisterSound(self):
		# Sound Settings:
		#self.sound.music_volume_offset = 10 #This will be hardcoded at 10 since I have external volume controls I will be using
		# Music Registration
		self.sound.register_sound('startup', game_sound_path+"Jet_F14_TakeOff.wav")
                self.sound.register_sound('inbound', game_sound_path+"inbound.wav")
                self.sound.register_sound('slinglow', game_sound_path+"slinglow.wav")
                self.sound.register_sound('tomcat', game_sound_path+"tomcat.wav")
                self.sound.register_sound('launch', game_sound_path+"launch.wav")
                self.sound.register_sound('launchspeech', game_sound_path+"missiles launched speech.wav")
                self.sound.register_sound('alarm', game_sound_path+"alarm.wav")
                self.sound.register_sound('explode1', game_sound_path+"explode1.wav")
                self.sound.register_sound('explode2', game_sound_path+"explode2.wav")
                self.sound.register_sound('shoot1', game_sound_path+"shoot1.wav")
                self.sound.register_music('dangerzone',game_music_path+"Kenny Loggins - Danger Zone.mp3")
		
		self.sound.set_volume(10)

	def RegisterLampshows(self):
		self.lampctrl.register_show('attract1', game_lampshows + 'attract_random.lampshow')
		self.lampctrl.register_show('center_ramp_1', game_lampshows + 'center_ramp_complete.lampshow')
		self.lampctrlflash.register_show('bonus_total', game_lampshows + 'bonus_total.lampshow')

	def create_player(self, name):
		return Player(name)

def main():
    game = None
    log = logging.getLogger('f14.main')
    try:
        game = F14SecondSortie()
        game.run_loop()
        game.reset()
    finally:
        del game

if __name__ == '__main__':
	main()
