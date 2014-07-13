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
##
#     ___                   __  ___         __
#    / _ ) ___ _ ___ ___   /  |/  /___  ___/ /___
#   / _  |/ _ `/(_-</ -_) / /|_/ // _ \/ _  // -_)
#  /____/ \_,_//___/\__/ /_/  /_/ \___/\_,_/ \__/
#
## 
#################################################################################

import procgame.game
from procgame import *
#import pinproc
#import random
#import time
#import sys
#import locale

#from bonus import *

class BaseGameMode(game.Mode):
	def __init__(self, game, priority):
			super(BaseGameMode, self).__init__(game, priority)
			
			
	def mode_started(self):
                        self.game.utilities.log('Base mode start','info')
			#Start Attract Mode
			self.game.modes.add(self.game.attract_mode)
			self.game.utilities.releaseStuckBalls()
                        self.reset()
			
	###############################################################
	# MAIN GAME HANDLING FUNCTIONS
	###############################################################
	def start_game(self):
		self.game.utilities.log('Start Game','info')

		#Reset Prior Game Scores
		self.game.game_data['LastGameScores']['LastPlayer1Score'] = ' '
		self.game.game_data['LastGameScores']['LastPlayer2Score'] = ' '
		self.game.game_data['LastGameScores']['LastPlayer3Score'] = ' '
		self.game.game_data['LastGameScores']['LastPlayer4Score'] = ' '

		#This function is to be used when starting a NEW game, player 1 and ball 1
		#Clean Up
		self.game.modes.remove(self.game.attract_mode)
		#self.game.modes.add(self.game.tilt)
		
		self.game.add_player() #will be first player at this point
		self.game.ball = 1

		self.start_ball()
		#self.game.sound.play('game_start_rev')
		#self.delay(delay=1.2,handler=self.game.sound.play,param='game_start')
		#self.game.sound.play('game_start')

                # Set up some handlers for the main playfield switches.
                for switch in self.game.switches:
                    if switch.name.find('target', 0) != -1:
                        self.add_switch_handler(name=switch.name, event_type='active', \
				delay=0.01, handler=self.target1_6)

                self.game.utilities.arduino_blank_all()

		self.game.utilities.log('Game Started')
		
	def start_ball(self):
		self.game.utilities.log('Start Ball','info')

		#### Update Audits ####
		self.game.game_data['Audits']['Balls Played'] += 1
		self.game.save_game_data()

		#### Queue Ball Modes ####
		#self.game.modes.add(self.game.skillshot_mode)
		#self.game.modes.add(self.game.centerramp_mode)
		#self.game.modes.add(self.game.tilt)
		self.game.modes.add(self.game.ballsaver_mode)
		#self.game.modes.add(self.game.drops_mode)
		#self.game.modes.add(self.game.collect_mode)
		#self.game.modes.add(self.game.spinner_mode)
		#self.game.modes.add(self.game.multiball_mode)

		#### Enable Flippers ####
		self.game.coils.flipperEnable.enable()

		#### Ensure GI is on ####
		self.game.utilities.enableGI()

		#### Kick Out Ball ####
		self.game.trough.launch_balls(num=1)


		#### Enable GI in case it is disabled from TILT ####
		self.game.utilities.enableGI()

                self.game.update_lamps()

		#### Start Shooter Lane Music ####
		self.game.sound.play_music('dangerzone',loops=-1)
		self.game.shooter_lane_status = 1

		#### Debug Info ####
		print "Ball Started"


        ### Update lamps, generally called when the ball starts
        def update_lamps(self):
            for switch in self.game.switches:
                    if switch.name.find('target', 0) != -1:
                        if self.game.utilities.get_player_stats(switch.name):
                            self.game.lamps[switch.name].enable()
                        else:
                            self.game.lamps[switch.name].disable()

	def finish_ball(self):
                self.game.modes.remove(self.game.kill1mission)
		self.game.modes.add(self.game.bonus_mode)
		if self.game.tiltStatus == 0:
			self.game.bonus_mode.calculate(self.game.base_mode.end_ball)
		else:
			self.end_ball()
		
	def end_ball(self):
		#Remove Bonus
		self.game.modes.remove(self.game.bonus_mode)
                

		#update games played stats
		self.game.game_data['Audits']['Balls Played'] += 1

		#Update Last Game Scores in game data file
		if self.game.ball == self.game.balls_per_game:
			self.playerAuditKey = 'LastPlayer' + str(self.game.current_player_index + 1) + 'Score'
			self.game.game_data['LastGameScores'][self.playerAuditKey] = self.game.utilities.currentPlayerScore()

		#save game audit data
		self.game.save_game_data()

		self.game.utilities.log("End of Ball " + str(self.game.ball) + " Called",'info')
		self.game.utilities.log("Total Players: " + str(len(self.game.players)),'info')
		self.game.utilities.log("Current Player: " + str(self.game.current_player_index),'info')
		self.game.utilities.log("Balls Per Game: " + str(self.game.balls_per_game),'info')
		self.game.utilities.log("Current Ball: " + str(self.game.ball),'info')

		#### Remove Ball Modes ####
		#self.game.modes.remove(self.game.tilt)
		#self.game.modes.remove(self.game.spinner_mode)
		#self.game.modes.remove(self.game.multiball_mode)

		#self.game.sound.fadeout_music(time_ms=1000) #This is causing delay issues with the AC Relay
		self.game.sound.stop_music()

		if self.game.current_player_index == len(self.game.players) - 1:
			#Last Player or Single Player Drained
			#print "Last player or single player drained"
			if self.game.ball == self.game.balls_per_game:
				#Last Ball Drained
				print "Last ball drained, ending game"
				self.end_game()
			else:
				#Increment Current Ball
				#print "Increment current ball and set player back to 1"
				self.game.current_player_index = 0
				self.game.ball += 1
				self.start_ball()
		else:
			#Not Last Player Drained
			print "Not last player drained"
			self.game.current_player_index += 1
			self.start_ball()


	def end_game(self):
		self.game.utilities.log('Game Ended','info')

		#### Disable Flippers ####
		self.game.coils.flipperEnable.disable()

		#### Disable AC Relay ####
		self.cancel_delayed(name='acEnableDelay')
		self.game.coils.acSelect.disable()

		#### Update Gmaes Played Stats ####
		self.game.game_data['Audits']['Games Played'] += 1

		#### Save Game Audit Data ####
		self.game.save_game_data()

		self.reset()

                self.game.modes.add(self.game.attract_mode)

        def reset(self):
                self.game.ball = 0
		self.game.old_players = []
		self.game.old_players = self.game.players[:]
		self.game.players = []
		self.game.current_player_index = 0

                self.game.shooter_lane_status = 0
		self.game.tiltStatus = 0

		#setup high scores
		self.game.ighscore_categories = []

		#### Classic High Score Data ####
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'ClassicHighScoreData'
		self.game.highscore_categories.append(cat)

		#### Mileage Champ ####
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'BonusLoops'
		self.game.highscore_categories.append(cat)

		for category in self.game.highscore_categories:
			category.load_from_game(self.game)
	###############################################################
	# BASE SWITCH HANDLING FUNCTIONS
	###############################################################		
		
	def sw_startButton_active_for_20ms(self, sw):
		self.game.utilities.log('Start Game','info')
		
		#Trough is full!
		if self.game.ball == 0:
			if self.game.utilities.troughIsFull()==True:
				#########################
				#Start New Game
				#########################
				self.start_game()
			else:
				#missing balls
				self.game.utilities.releaseStuckBalls()
				#self.game.alpha_score_display.set_text("MISSING PINBALLS",0)
				#self.game.alpha_score_display.set_text("PLEASE WAIT",1)
		elif self.game.ball == 1 and len(self.game.players) < 4:
			self.game.add_player()
			if (len(self.game.players) == 2):
				#self.game.sound.play('player_2_vox')
				self.game.utilities.display_text(txt='PLAYER 2',txt2='ADDED',time=1)
			elif (len(self.game.players) == 3):
				#self.game.sound.play('player_3_vox')
                                self.game.utilities.display_text(txt='PLAYER 3',txt2='ADDED',time=1)
			elif (len(self.game.players) == 4):
				#self.game.sound.play('player_4_vox')
                                self.game.utilities.display_text(txt='PLAYER 4',txt2='ADDED',time=1)
		else:
			pass		
		return procgame.game.SwitchStop

	def sw_startButton_active_for_1s(self, sw):
		#will put launcher in here eventually
		pass
		
	def sw_outhole_closed_for_1s(self, sw):
		### Ball handling ###
                self.game.utilities.log('Base outhole call','info')
		if self.game.trough.num_balls_in_play == 1: #Last ball in play
			self.game.utilities.setBallInPlay(False) # Will need to use the trough mode for this
			#self.game.utilities.acCoilPulse('outholeKicker_CaptiveFlashers')
			self.delay('finishBall',delay=1,handler=self.finish_ball)
		return procgame.game.SwitchStop

	def sw_vUK_closed_for_1s(self, sw):
		self.game.utilities.acCoilPulse(coilname='upKicker_flasher3',pulsetime=50)
		return procgame.game.SwitchStop


        def sw_rightEject_closed_for_1s(self,sw):
                self.game.utilities.acCoilPulse(coilname='rightEject_flasher7',pulsetime=50)
		return procgame.game.SwitchStop

        def target1_6(self,sw):
            if self.game.utilities.get_player_stats(sw.name):
                self.game.utilities.score(100)
            else:
                self.game.utilities.score(1000)
                self.game.utilities.flickerOn(sw.name)   # switch on the lamp at the target
                self.game.utilities.set_player_stats(sw.name,True)
                completed = self.game.utilities.get_player_stats('target1-6_completed') + 1
                
                self.game.utilities.set_player_stats('target1-6_completed',completed)
                # If we've lit all 6, need to add the
                if completed == 6:
                    self.game.mission.completed1_6()

                
        def sw_rightCentreEject_closed_for_1s(self,sw):
                self.game.utilities.acCoilPulse(coilname='centreRightEject_flasher5',pulsetime=50)
		return procgame.game.SwitchStop

        def sw_leftCentreEject_closed_for_1s(self,sw):
                self.game.coils.centreLeftEject.pulse(50)
		return procgame.game.SwitchStop

	def sw_jetBumper_active(self, sw):
		#self.game.sound.play('jet')
		self.game.utilities.score(500)
		return procgame.game.SwitchStop

	def sw_slingL_active(self, sw):
		#self.game.coils.slingL.pulse(30)
		self.game.sound.play('slinglow')
		self.game.utilities.score(100)
		return procgame.game.SwitchStop

	def sw_slingR_active(self, sw):
		#self.game.coils.slingR.pulse(30)
		self.game.sound.play('slinglow')
		self.game.utilities.score(100)
		return procgame.game.SwitchStop

	def sw_spinner_active(self, sw):
		#self.game.utilities.acFlashPulse(coilname='dropReset_CenterRampFlashers2',pulsetime=40)
		#self.game.coils.dropReset_CenterRampFlashers2.pulse(40)
		#self.game.sound.play('spinner')
		#self.game.utilities.score(100)
		return procgame.game.SwitchStop

	##################################################
	## Skillshot Switches
	## These will set the ball in play when tripped
	##################################################
	def sw_rampEntry_active(self, sw):
		self.game.utilities.setBallInPlay(True)
                return procgame.game.SwitchStop

	def sw_shooter_open(self, sw):
		# This will play the car take off noise when the ball leaves the shooter lane
		if (self.game.utilities.get_player_stats('ball_in_play') == False):
			self.game.sound.play('shoot1')

	#############################
	## Zone Switches
	#############################


	def sw_shooter_closed_for_1s(self, sw):
		if (self.game.utilities.get_player_stats('ball_in_play') == True):
			#Kick the ball into play
			self.game.utilities.launch_ball()
		return procgame.game.SwitchStop

	#############################
	## Outlane Switches
	#############################
	def sw_outlaneLeft_closed(self, sw):
		self.game.sound.play('outlane')

	def sw_outlaneRight_closed(self, sw):
		self.game.sound.play('outlane')
