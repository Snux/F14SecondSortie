#################################################################################
##     _________    ____  ________  _______ __  _____    __ __ __________  __
##    / ____/   |  / __ \/_  __/ / / / ___// / / /   |  / //_// ____/ __ \/ /
##   / __/ / /| | / /_/ / / / / /_/ /\__ \/ /_/ / /| | / ,<  / __/ / /_/ / / 
##  / /___/ ___ |/ _, _/ / / / __  /___/ / __  / ___ |/ /| |/ /___/ _, _/_/  
## /_____/_/  |_/_/ |_| /_/ /_/ /_//____/_/ /_/_/  |_/_/ |_/_____/_/ |_(_)   
##     ___    ______________________  _____ __  ______  ________ __
##    /   |  / ____/_  __/ ____/ __ \/ ___// / / / __ \/ ____/ //_/
##   / /| | / /_    / / / __/ / /_/ /\__ \/ /_/ / / / / /   / ,<   
##  / ___ |/ __/   / / / /___/ _, _/___/ / __  / /_/ / /___/ /| |  
## /_/  |_/_/     /_/ /_____/_/ |_|/____/_/ /_/\____/\____/_/ |_|                     
##                                                     
## A P-ROC Project by Scott Danesi, Copyright 2013-2014
## Built on the PyProcGame Framework from Adam Preble and Gerry Stellenberg
#################################################################################

#################################################################################
##     ____  __    _____  ____________     ______________  ___________
##    / __ \/ /   /   \ \/ / ____/ __ \   / ___/_  __/   |/_  __/ ___/
##   / /_/ / /   / /| |\  / __/ / /_/ /   \__ \ / / / /| | / /  \__ \ 
##  / ____/ /___/ ___ |/ / /___/ _, _/   ___/ // / / ___ |/ /  ___/ / 
## /_/   /_____/_/  |_/_/_____/_/ |_|   /____//_/ /_/  |_/_/  /____/  
## 
#################################################################################

import procgame.game

class Player(procgame.game.Player):

	def __init__(self, name):
			super(Player, self).__init__(name)

			### Create Player Stats Array ############################
			self.player_stats = {}

			### General Stats ########################################
			self.player_stats['ball_in_play']=False

			### Ball Saver ###########################################
			self.player_stats['ballsave_active']=False
			self.player_stats['ballsave_timer_active']=False

			### Bonus and Status #####################################
			self.player_stats['status']=''
			self.player_stats['bonus_x']=1

			### Center Ramp Stats ####################################
			self.player_stats['bonus']=0
			self.player_stats['center_shots']=0

			### Kickback Stats ####################################
			self.player_stats['kickback_active']=False

			### Jackpot Stats ########################################
			self.player_stats['jackpot_level']=1
			self.player_stats['total_jackpots_collected']=0
			self.player_stats['last_multiball_jackpots_collected']=0

			### Multiball Stats ######################################
			self.player_stats['lock1_lit']=False
			self.player_stats['lock2_lit']=False
			self.player_stats['lock3_lit']=False
			self.player_stats['multiball_running']=False
			self.player_stats['jackpot_lit']=False
			self.player_stats['balls_locked']=0

			### Right Ramp Stats #####################################
			self.player_stats['fault_visits']=0
			self.player_stats['million_lit']=False

			### Skillshot ############################################
			self.player_stats['skillshot_active']=False
			self.player_stats['skillshot_x']=1

			### Kill Status Stats ####################################
			## Count of completed missions
			self.player_stats['kills_completed']=0

                        ## Per mission status
                        ## -1 = Initial
                        ##  0 = Available
                        ##  1 = In progress
                        ##  2 = Complete
			self.player_stats['alpha_kill_status']=-1
			self.player_stats['bravo_kill_status']=-1
			self.player_stats['charlie_kill_status']=-1
			self.player_stats['delta_kill_status']=-1
			self.player_stats['echo_kill_status']=-1
			self.player_stats['fox_kill_status']=-1
			self.player_stats['golf_kill_status']=-1

                        ## Status of the 1-6 lamps
                        self.player_stats['target1']=False
			self.player_stats['target2']=False
                        self.player_stats['target3']=False
                        self.player_stats['target4']=False
                        self.player_stats['target5']=False
                        self.player_stats['target6']=False