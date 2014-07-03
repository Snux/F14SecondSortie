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
#     __  ___ _            _               __ __               __ __
#    /  |/  /(_)___  ___  (_)___   ___    / // /___ _ ___  ___/ // /___  ____
#   / /|_/ // /(_-< (_-< / // _ \ / _ \  / _  // _ `// _ \/ _  // // -_)/ __/
#  /_/  /_//_//___//___//_/ \___//_//_/ /_//_/ \_,_//_//_/\_,_//_/ \__//_/
#
#################################################################################

import procgame
from procgame import *
import locale
import logging

class MissionMode(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
			super(MissionMode, self).__init__(game, priority)
			#self.superSpinnerSpins = self.game.user_settings['Feature']['Super Spinner Spins']
			#self.superSpinnerTime = self.game.user_settings['Feature']['Super Spinner Time']
			#self.superSpinnerLit = False
			#self.superSpinnerEnabled = False
                        self.kill_list=['kill1','kill2','kill3','kill4','kill5','kill6','kill7']
                        self.mission_name= {'kill1' : 'Alpha',
                                            'kill2' : 'Bravo',
                                            'kill3' : 'Charlie',
                                            'kill4' : 'Delta',
                                            'kill5' : 'Echo',
                                            'kill6' : 'Foxtrot',
                                            'kill7' : 'Golf'
                                            }
                        

                        #setup logging
                        self.log = logging.getLogger('f14.mission')
			
	
        # Called by the base mode when lamps 1-6 have been lit.
        ## Per mission status
                        ## -1 = Initial
                        ##  0 = Available
                        ##  1 = In progress
                        ##  2 = Complete
        def completed1_6(self):
            if self.game.utilities.get_player_stats('kills_completed') < 7:
                # First look for a mission that is still in initial state
                initial_missions=[]
                for mission in self.kill_list:
                    if self.game.utilities.get_player_stats(mission) == -1:
                        initial_missions.append(mission)
                        self.log.info("Mission "+mission+" is available")

                # If we actually have one available, then process the first one
                if len(initial_missions) > 0:
                    mission_to_play = initial_missions[0]
                    self.log.info("Setting mission "+mission_to_play+" to available")
                    self.game.utilities.set_player_stats(mission_to_play,0)
                    self.game.utilities.display_text(txt=self.mission_name[mission_to_play]+" Ready",time=3)
                    self.game.utilities.set_player_stats('target1',False)
                    self.game.utilities.set_player_stats('target2',False)
                    self.game.utilities.set_player_stats('target3',False)
                    self.game.utilities.set_player_stats('target4',False)
                    self.game.utilities.set_player_stats('target5',False)
                    self.game.utilities.set_player_stats('target6',False)
                    self.game.utilities.set_player_stats('target1-6_completed',0)

                    self.game.update_lamps()


	def update_lamps(self):
                self.log.info("Update Lamps: Mission")
                for mission in self.kill_list:
                    status=self.game.utilities.get_player_stats(mission);
                    if status == -1:
                        self.log.info("- setting "+mission+" to disabled")
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].disable()
                        self.game.lamps[mission+'blue'].disable()
                    elif status == 0:
                        self.log.info("- setting "+mission+" to available")
                        self.game.lamps[mission+'blue'].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].disable()
                    elif status == 1:
                        self.log.info("- setting "+mission+" to in progress")
                        self.game.lamps[mission+'red'].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'green'].disable()
                        self.game.lamps[mission+'blue'].disable()
                    else:
                        self.log.info("- setting "+mission+" to complete")
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].enable()
                        self.game.lamps[mission+'blue'].disable()

	