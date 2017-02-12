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

#                               `\\             //'
#                                 \\           //
#                                  \\. __-__ .//
#                        ___/-_.-.__`/~     ~\'__.-._-\___
# .|.       ___________.'__/__ ~-[ \.\'-----'/./ ]-~ __\__`.___________       .|.
# ~o~~~~~~~--------______-~~~~~-_/_/ |   .   | \_\_-~~~~~-______--------~~~~~~~o~
# ' `               + + +  (X)(X)  ~--\__ __/--~  (X)(X)  + + +               ' `
#                              (X) `/.\' ~ `/.\' (X)
#                                  "\_/"   "\_/"

###################################
# SYSTEM IMPORTS
###################################
import procgame.game
from procgame import *
import pinproc
import locale
import os
import logging
import threading
from time import strftime
import procgame.dmd
import procgame.assetmanager
from procgame.modes import ScoreDisplay
from procgame.modes import score_display
from procgame.dmd import font_named
from procgame.dmd import hdfont_named

###################################
# MODE IMPORTS
###################################
from base import *
from attract import *
from utilities import *
from tilt import *
from player import *
from ballsaver import *
from bonus import *
from mission import *
from locks import *
from multiball import *
# from quickmultiball import *
from trough import *
from kickback import *
from info import *
from service import *
from exitgame import *
from ArduinoDriver import ArduinoClient, wsRGB


# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

################################################
# GLOBAL PATH VARIABLES
################################################
game_machine_type = 'wpc'
curr_file_path = os.path.dirname(os.path.abspath(__file__))
settings_path = curr_file_path + "/config/settings.yaml"
game_data_path = curr_file_path + "/config/game_data.yaml"
game_data_template_path = curr_file_path + "/config/game_data_template.yaml"
settings_template_path = curr_file_path + "/config/settings_template.yaml"
game_machine_yaml = curr_file_path + "/config/f14.yaml"
game_music_path = curr_file_path + "/assets/music/"
game_sound_path = curr_file_path + "/assets/sound/"
game_dmd_path = curr_file_path + "/assets/dmd/"
game_lampshows = curr_file_path + "/assets/lamps/"
fnt_path = "/shared/dmd/"

ballsPerGame = 5  # this will eventually be called from the config file


################################################
# GAME CLASS
################################################
class F14SecondSortie(game.BasicGame):
    def __init__(self):
        #super(F14SecondSortie, self).__init__(pinproc.MachineTypeWPC95)
        self.curr_file_path = curr_file_path
        super(F14SecondSortie, self).__init__(pinproc.MachineTypeWPC95)
        self.load_config(game_machine_yaml)

        self.tomcatTargetIndex = (["lowerLeftT", "lowerLeftO", "lowerLeftM", "upperLeftT", "upperLeftO", "upperLeftM",
                                   "upperRightC", "upperRightA", "upperRightT", "lowerRightC", "lowerRightA",
                                   "lowerRightT"])

        self.logging_enabled = True
        # self.balls_per_game = ballsPerGame

        ### Set Logging Info ###
        logging.basicConfig(filename='f14.txt', level=logging.INFO)

        #### Settings and Game Data ####
        self.load_settings(settings_template_path, settings_path)
        self.load_game_data(game_data_template_path, game_data_path)

        # update audit data on boot up time
        self.game_data['Time Stamps']['Last Boot-Up'] = str(strftime("%d %b %Y %H:%M"))
        if self.game_data['Time Stamps']['First Boot-Up'] == 'Not Set':
            self.game_data['Time Stamps']['First Boot-Up'] = self.game_data['Time Stamps']['Last Boot-Up']
        self.save_game_data()

        # used to hold the 'fonts' dictionary
        fonts = {}
        animations = {}

        self.lampshow_path = config.value_for_key_path('lampshow_path', curr_file_path + "/assets/lampshows/")
        self.dmd_path = config.value_for_key_path('dmd_path', curr_file_path + "/assets/dmd/")
        self.sound_path = config.value_for_key_path('sound_path', curr_file_path + "/assets/sound/")

        self.voice_path = self.sound_path + config.value_for_key_path('voice_dir', "voice/")
        self.sfx_path = self.sound_path + config.value_for_key_path('sfx_dir', "sfx/")
        self.music_path = self.sound_path + config.value_for_key_path('music_dir', "music/")

        self.hdfont_path = config.value_for_key_path('hdfont_dir', curr_file_path + "/assets/fonts/")



        #### Setup Sound Controller ####

        self.sound = sound.SoundController(self)
        #self.RegisterSound()  #### Pre-load animations
        #self.RegisterAnimations()


        #### Setup Lamp Controller ####
        self.lampctrl = procgame.lamps.LampController(self)
        self.lampctrlflash = procgame.lamps.LampController(self)
        #self.RegisterLampshows()

        # call load_assets function to load fonts, sounds, etc.
        self.load_assets()

        #### software version number ####
        self.revision = "2.0.0"

        #### Mode Definitions ####
        OSC_closed_switches = ['trough1', 'trough2', 'trough3', 'trough4']

        #self.osc = modes.OSC_Mode(game=self, priority=1, closed_switches=OSC_closed_switches)
        #self.modes.add(self.osc)

        self.score_display = score_display.ScoreDisplay(self, 0)
        self.reset()

        self.utilities = UtilitiesMode(self, 100)
        self.trough = Trough(self, 0)
        self.info = Info(self, 200)
        self.base_mode = BaseGameMode(self, 0)
        self.attract_mode = AttractMode(self, 1)
        self.mission = MissionMode(self, 2)
        self.locks = LocksMode(self, 50)
        self.kill1mission = Kill1Mode(self, 3)
        self.kill2mission = Kill2Mode(self, 3)
        self.kill3mission = Kill3Mode(self, 3)
        self.kill4mission = Kill4Mode(self, 3)
        self.kill5mission = Kill5Mode(self, 3)
        self.kill6mission = Kill6Mode(self, 3)
        self.kill7mission = Kill7Mode(self, 3)
        self.ballsaver_mode = BallSaver(self, 1)
        self.kickback_mode = KickbackMode(self, 1)
        self.exitgame_mode = ExitGameMode(self, 1)
        # self.tilt = Tilt(self,200)
        self.bonus_mode = Bonus(self, 102)
        self.multiball_mode = Multiball(self, 101)
        # self.quick_multiball_mode = QuickMultiball(self,101)

        self.service_mode = ServiceMode(self, 300, font_named("Font07x5.dmd"), font_named("font_8x6_bold.dmd"), [])

        #### Initial Mode Queue ####
        self.modes.add(self.exitgame_mode)
        self.modes.add(self.utilities)
        self.modes.add(self.trough)
        self.modes.add(self.base_mode)
        self.modes.add(self.mission)
        self.modes.add(self.locks)

    def process_config(self):
        """ A subclassed version of process_config.  Does what the usual one does, then looks for WSRGBS section
        in the game yaml to define any ws2811/ws2812-based RGB LEDs
        """
        super(F14SecondSortie, self).process_config()
        self.wsRGBs = procgame.game.AttrCollection()
        self.arduino_client = None

        ## Open up the Arduino COM port if one is specified.
        if ('arduino' in self.config['PRGame'] and self.config['PRGame']['arduino'] != False):
            comport = self.config['PRGame']['arduino']
            self.arduino_client = ArduinoClient(comport, baud_rate=115200, timeout=1)

        for l in self.lamps:
            l.set_color_RGB = lambda *args, **kwargs: None

        if 'WsRGBs' in self.config:
            sect_dict = self.config['WsRGBs']
            for name in sect_dict:
                item_dict = sect_dict[name]

                item = None
                yaml_number = item_dict['number']
                if (not isinstance(yaml_number, basestring) or yaml_number[0] != 'A'):
                    raise ValueError(
                        'Malformed Yaml File: wsRGB item named "%s" should have a number of the form: A#' % name)

                number = int(yaml_number[1:])

                item = wsRGB(game=self, name=name, number=number)
                item.yaml_number = yaml_number
                if 'label' in item_dict:
                    item.label = item_dict['label']
                if 'type' in item_dict:
                    item.type = item_dict['type']

                if 'default_color' in item_dict:
                    color = item_dict['default_color']
                    item.set_color(color)
                else:
                    self.logger.warning(
                        'Configuration item named "%s" has no default_color attribute.  Defaulting to white.' % name)
                    item.set_color('W')
                item.store_default_color()

                self.wsRGBs.add(name, item)

                self.logger.info(" wsRGB name=%s; number=%s; color=%s" % (item.name, item.yaml_number, item.color))
                self.lamps.add(name, item)

            self.logger.info(" SPECIAL wsRGB name=%s; number=%s; color=%s" % (item.name, item.yaml_number, item.color))
    def reset(self):
        super(F14SecondSortie, self).reset()
        self.ball = 0
        self.old_players = []
        self.old_players = self.players[:]
        self.players = []
        self.current_player_index = 0

        self.shooter_lane_status = 0
        self.tiltStatus = 0

        # setup high scores
        self.highscore_categories = []

        #### Classic High Score Data ####
        cat = highscore.HighScoreCategory()
        cat.game_data_key = 'ClassicHighScoreData'
        self.highscore_categories.append(cat)

        #### Mileage Champ ####
        cat = highscore.HighScoreCategory()
        cat.game_data_key = 'BonusLoops'
        self.highscore_categories.append(cat)

        #self.score_display.reset()
        self.modes.add(self.score_display)

        for category in self.highscore_categories:
            category.load_from_game(self)


    def save_settings(self):
        super(F14SecondSortie, self).save_settings(settings_path)


    def save_game_data(self):
        super(F14SecondSortie, self).save_game_data(game_data_path)

    def load_assets(self):
        """ function to clean up code/make things easier to read;
            this handles reading/loading of all assets (sounds, dmd images,
            dmd fonts, lightshows) from the file system
        """
        self.asset_mgr = assetmanager.AssetManager(game=self)
        self.animations = self.asset_mgr.animations
        self.fontstyles = self.asset_mgr.fontstyles
        self.fonts = self.asset_mgr.fonts


    def create_player(self, name):
        return Player(name)
    
    def end_run_loop(self):
        super(F14SecondSortie, self).end_run_loop()
        if self.arduino_client.running:
            self.arduino_client.quit()

def cleanup():
    import sdl2.ext
    sdl2.ext.quit()
    #from procgame.modes.osc import OSC_INST
    #global OSC_INST
    #if(OSC_INST is not None):
    #    OSC_INST.OSC_shutdown()

def main():
    game = None
    #try:
    game = F14SecondSortie()
    log = logging.getLogger('f14.main')
    log.info("Before run loop")
    game.run_loop()
        #game.reset()
    log.info("Call cleanup")
    cleanup();
    log.info("Back from cleanup")
    #finally:
    #del game
    threading.enumerate()
    log.info("Done with thread")


if __name__ == '__main__':
    main()
