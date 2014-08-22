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
#
#     ___  __                    ______       __
#    / _ \/ /__ ___ _____ ____  / __/ /____ _/ /____
#   / ___/ / _ `/ // / -_) __/ _\ \/ __/ _ `/ __(_-<
#  /_/  /_/\_,_/\_, /\__/_/   /___/\__/\_,_/\__/___/
#              /___/
#################################################################################

import procgame.game

class Player(procgame.game.Player):

	def __init__(self, name):
			super(Player, self).__init__(name)

			### Create Player Stats Array ############################
			self.player_stats = {}

			### General Stats ########################################
			self.player_stats['ball_in_play']=False
                        self.player_stats['extra_balls']=0
                        self.player_stats['extra_ball_lit']=False

			### Ball Saver ###########################################
			self.player_stats['ballsave_active']=False
			self.player_stats['ballsave_timer_active']=False

			### Bonus and Status #####################################
			self.player_stats['status']=''
			self.player_stats['bonus_x']=1
                        self.player_stats['bonus']=0
                        self.player_stats['loop_shots']=0
                        self.player_stats['bonusXRight']='off'
                        self.player_stats['bonusXLeft']='off'
			self.player_stats['center_shots']=0
                        self.player_stats['yagov_shots']=0
                        self.player_stats['kickback_lit']=False

			### Kickback Stats ####################################
			self.player_stats['kickback_active']=False

			### Jackpot Stats ########################################
			self.player_stats['jackpot_level']=1
			self.player_stats['total_jackpots_collected']=0
			self.player_stats['last_multiball_jackpots_collected']=0

			### Multiball Stats ######################################
			self.player_stats['upper_lock']='off'
			self.player_stats['middle_lock']='off'
			self.player_stats['lower_lock']='off'
			self.player_stats['multiball_running']=False
			self.player_stats['jackpot_lit']=False
			self.player_stats['balls_locked']=0
                        self.player_stats['balls_landed']=0
                        self.player_stats['upper_landing']='off'
                        self.player_stats['middle_landing']='off'
                        self.player_stats['lower_landing']='off'

			### Right Ramp Stats #####################################
			self.player_stats['fault_visits']=0
			self.player_stats['million_lit']=False

			### Skillshot ############################################
			self.player_stats['skillshot_active']=False
			self.player_stats['skillshot_x']=1

			### Kill Status Stats ####################################
			## Count of completed missions
			self.player_stats['kills_completed']=0
                        self.player_stats['target1-6_completed']=0
                        self.player_stats['tomcat_completed']=0
                        self.player_stats['next_mission']='None'
                        self.player_stats['mission_in_progress']='None'

                        ## Per mission status
                        ## -1 = Initial
                        ##  0 = Available
                        ##  1 = In progress
                        ##  2 = Complete
			self.player_stats['kill1']=-1
			self.player_stats['kill2']=-1
                        self.player_stats['kill3']=-1
                        self.player_stats['kill4']=-1
                        self.player_stats['kill5']=-1
                        self.player_stats['kill6']=-1
                        self.player_stats['kill7']=-1


                        ## Status of the 1-6 lamps
                        self.player_stats['target1']=False
			self.player_stats['target2']=False
                        self.player_stats['target3']=False
                        self.player_stats['target4']=False
                        self.player_stats['target5']=False
                        self.player_stats['target6']=False

                        
                        self.player_stats['lowerLeftT']=False
                        self.player_stats['lowerLeftO']=False
                        self.player_stats['lowerLeftM']=False
                        self.player_stats['upperLeftT']=False
                        self.player_stats['upperLeftO']=False
                        self.player_stats['upperLeftM']=False
                        self.player_stats['upperRightC']=False
                        self.player_stats['upperRightA']=False
                        self.player_stats['upperRightT']=False
                        self.player_stats['lowerRightC']=False
                        self.player_stats['lowerRightA']=False
                        self.player_stats['lowerRightT']=False