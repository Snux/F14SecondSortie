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
import time
#import pinproc
import random
#import time
#import sys
#import locale
import logging
import procgame.dmd
from procgame.dmd import font_named

#from bonus import *

class BaseGameMode(game.Mode):
	def __init__(self, game, priority):
			super(BaseGameMode, self).__init__(game, priority)
                        self.log = logging.getLogger('f14.base')
			
			
	def mode_started(self):
                        self.log.info('Base mode start')
			#Start Attract Mode
			self.game.modes.add(self.game.attract_mode)
			self.game.utilities.releaseStuckBalls()
                        self.reset()
                        self.lastBonusLoop = time.clock()
                        self.info_on=False
			
	###############################################################
	# MAIN GAME HANDLING FUNCTIONS
	###############################################################
	def start_game(self):
		self.log.info('Start Game')

                # Reset trough counters in case they got messed up somehow.
                self.game.trough.balls_locked = 0
                self.game.trough.num_balls_in_play = 0
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
                self.game.balls_per_game = self.game.user_settings['Standard']['Balls Per Game']
                self.log.info('Starting '+str(self.game.balls_per_game)+ ' ball game')
		self.start_ball()
		
                # Set up some handlers for the main playfield switches.
                for switch in self.game.switches:
                    if switch.name.find('target', 0) != -1:
                        self.add_switch_handler(name=switch.name, event_type='active', \
				delay=0.01, handler=self.target1_6)
                    if switch.name in self.game.tomcatTargetIndex:
                        self.add_switch_handler(name=switch.name, event_type='active', \
                                delay=0.01, handler=self.targetTOMCAT)
                        
                self.add_switch_handler(name='bonusXRight',event_type='active', \
                                delay=0.01, handler=self.bonusLane)
                self.add_switch_handler(name='bonusXLeft',event_type='active', \
                                delay=0.01, handler=self.bonusLane)
                self.game.utilities.arduino_blank_all()

		self.log.info('Game Started')

        # Initial ball start routine.  Saves audit then calls to the restage code to see if
        # extra balls need locking
	def start_ball(self):
		self.log.info('Start Ball')

		#### Update Audits ####
		#self.game.game_data['Audits']['Balls Played'] += 1
		#self.game.save_game_data()

                ## Now we need to check if the number of balls physically locked on the playfield
                ## is at least the number of balls that this player has locked before.  In multiplayer
                ## games it's possible for one player to empty locks that another player has filled.
                ## So we may need to re-fill some locks to get the player back to a fair number
                self.game.locks.check_for_restage()

        ## This actually gets the ball started and is called by the locks restage code once locks have been sorted out
        def start_ball_actual(self):

		#### Queue Ball Modes ####
		#self.game.modes.add(self.game.skillshot_mode)
		#self.game.modes.add(self.game.centerramp_mode)
		#self.game.modes.add(self.game.tilt)
		self.game.modes.add(self.game.ballsaver_mode)
                self.game.modes.add(self.game.kickback_mode)
		#self.game.modes.add(self.game.drops_mode)
		#self.game.modes.add(self.game.collect_mode)
		#self.game.modes.add(self.game.spinner_mode)
		self.game.modes.add(self.game.multiball_mode)

		#### Enable Flippers ####
		self.game.coils.flipperEnable.enable()

		#### Ensure GI is on ####
		self.game.utilities.enableGI()

		#### Kick Out Ball ####
                self.log.info("Launch ball manual, ball starting")
		self.game.trough.launch_balls(num=1)



		#### Enable GI in case it is disabled from TILT ####
		self.game.utilities.enableGI()

                self.game.update_lamps()


		#### Start Shooter Lane Music ####
		self.game.sound.play_music('shooterlane',loops=-1)
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
                    if switch.name in self.game.tomcatTargetIndex:
                        if self.game.utilities.get_player_stats(switch.name):
                            self.game.lamps[switch.name].enable()
                        else:
                            self.game.lamps[switch.name].disable()
            if self.game.utilities.get_player_stats('extra_ball_lit') == True:
                self.game.lamps.extraBall.schedule(schedule=0xFF00FF00)
            else:
                self.game.lamps.extraBall.disable()


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
                self.game.modes.remove(self.game.kickback_mode)
                

		#update games played stats
		self.game.game_data['Audits']['Balls Played'] += 1

		#Update Last Game Scores in game data file
		if self.game.ball == self.game.balls_per_game:
			self.playerAuditKey = 'LastPlayer' + str(self.game.current_player_index + 1) + 'Score'
			self.game.game_data['LastGameScores'][self.playerAuditKey] = self.game.utilities.currentPlayerScore()

		#save game audit data
		self.game.save_game_data()

		self.log.info("End of Ball " + str(self.game.ball) + " Called")
		self.log.info("Total Players: " + str(len(self.game.players)))
		self.log.info("Current Player: " + str(self.game.current_player_index))
		self.log.info("Balls Per Game: " + str(self.game.balls_per_game))
		self.log.info("Current Ball: " + str(self.game.ball))

		#### Remove Ball Modes ####
		#self.game.modes.remove(self.game.tilt)
		#self.game.modes.remove(self.game.spinner_mode)
		self.game.modes.remove(self.game.multiball_mode)

		#self.game.sound.fadeout_music(time_ms=1000) #This is causing delay issues with the AC Relay
		self.game.sound.stop_music()

                if self.game.utilities.get_player_stats('extra_balls') > 0:
                        self.game.utilities.play_animation('shoot_again')
                        self.game.lamps.flyAgain.schedule(schedule=0xFF00FF00)
                        self.start_ball()
                elif self.game.current_player_index == len(self.game.players) - 1:
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
		self.log.info('Game Ended')

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
		self.log.info('Start Game')
		
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

	
	def sw_vUK_active(self, sw):
		self.game.utilities.acCoilPulse(coilname='upKicker_flasher3',pulsetime=50)
                self.game.locks.transitStart('base')
		return procgame.game.SwitchStop


        
        def target1_6(self,sw):
            #self.game.lampctrl.play_show('wipeleftright',repeat=False)
            # if the target was already lit, just score something
            if self.game.utilities.get_player_stats(sw.name):
                self.game.utilities.score(100)
            # otherwise switch the lamp on, note that we hit it and increment the counter
            else:
                self.game.utilities.score(1000)
                self.game.utilities.flickerOn(sw.name)   # switch on the lamp at the target
                self.game.utilities.set_player_stats(sw.name,True)
                completed = self.game.utilities.get_player_stats('target1-6_completed') + 1
                
                self.game.utilities.set_player_stats('target1-6_completed',completed)
                # If we've lit all 6, need to let the mission handler know.
                if completed == 6:
                    self.game.mission.completed1_6()

	def sw_jetBumper_active(self, sw):
		#self.game.sound.play('jet')
		self.game.utilities.score(500)
		return procgame.game.SwitchStop

	def sw_slingL_active(self, sw):
		#self.game.coils.slingL.pulse(30)
		self.game.sound.play('slinglow')
		self.game.utilities.score(100)
                self.bonus()
		return procgame.game.SwitchStop

	def sw_slingR_active(self, sw):
		#self.game.coils.slingR.pulse(30)
		self.game.sound.play('slinglow')
		self.game.utilities.score(100)
                self.bonus()
		return procgame.game.SwitchStop


	##################################################
	## Skillshot Switches
	## These will set the ball in play when tripped
	##################################################
	def sw_rampEntry_active(self, sw):
		self.game.utilities.setBallInPlay(True)

                # Stop the flashing extra ball lamp, if there was one.
                self.game.trough.extra_ball = False
                self.game.trough.update_lamps()

                return procgame.game.SwitchStop

        
	def sw_shooter_open(self, sw):
		# This will play the car take off noise when the ball leaves the shooter lane
		if (self.game.utilities.get_player_stats('ball_in_play') == False):
			self.game.sound.play('shoot1')


	#############################
	## Outlane Switches
	#############################
	def sw_outlaneLeft_closed(self, sw):
		self.game.sound.play('outlane')

	def sw_outlaneRight_closed(self, sw):
		self.game.sound.play('outlane')

        def sw_spinner_closed(self, sw):
		self.game.sound.play('spinner')
                self.game.utilities.score(10)

        # Yagov kickback handling.
        def sw_yagov_active(self, sw):
                # Fire the coil as first thing
                self.game.coils['yagovKickBack'].pulse(100)


                # increment the shot counter
                count=self.game.utilities.get_player_stats('yagov_shots')
                count += 1
                self.game.utilities.set_player_stats('yagov_shots',count)
                
                # every 5 shots award something - need to expand this
                if count % 5 == 0:
                    self.game.utilities.play_animation('f14missile2',frametime=1,txt='YAGOV BONUS - GET THE EXTRA BALL',txtPos='over')
                    self.game.utilities.set_player_stats('extra_ball_lit',True)
                    self.update_lamps()

                    pass

                elif self.game.utilities.get_player_stats('extra_ball_lit') == True:
                    self.game.utilities.set_player_stats('extra_ball_lit',False)
                    self.game.utilities.set_player_stats('extra_balls',1,mode='add')
                    self.game.utilities.play_animation('extra_ball',frametime=2)
                    self.update_lamps()

                else:
                    yagov_bonus = int (count / 5) * 5 + 5
                    if count == 1:
                        display_text = '1 YAGOV SHOT'
                    else:
                        display_text = str(count)+' YAGOV SHOTS'
                    display_text = display_text + ' - BONUS AT '+ str(yagov_bonus)
                    # display the shot counter with a rendom animation
                    self.game.utilities.play_animation('f14_roll'+random.choice(['2','5','6']),frametime=5,txt=display_text,txtPos='over')

                # Make some sound and lights :)
		self.game.sound.play('machine_gun_short')
                self.game.lampctrl.play_show('f14fireboth', repeat=False,callback=self.game.update_lamps)
                

        # The bonus multiplier should increase when the loop is hit in the same direction twice within a few seconds
        def bonusLane(self,sw):
            # increment the loop shot counter, we'll use this some day for a champion score or something
            self.game.utilities.set_player_stats('loop_shots',self.game.utilities.get_player_stats('loop_shots')+1)

            if time.clock() - self.lastBonusLoop < 1:
                pass
            else:
                self.lastBonusLoop=time.clock()
                if sw.name[6:]=="Right":
                    if self.game.utilities.get_player_stats('bonusXRight') == 'on':
                        self.game.utilities.inc_bonusMultiplier()
                        self.cancel_delayed(name="rightoff")
                    self.game.lamps[sw.name].schedule(schedule=0x0F0F0F0F, cycle_seconds=2.0, now=True)
                    self.delay(name="rightoff",event_type=None,delay=4.0,handler=self.bonusLaneOff,param="Right")
                    self.game.utilities.set_player_stats('bonusXRight','on')
                else:
                    if self.game.utilities.get_player_stats('bonusXLeft') == 'on':
                        self.game.utilities.inc_bonusMultiplier()
                        self.cancel_delayed(name="leftoff")
                    self.game.lamps[sw.name].schedule(schedule=0x0F0F0F0F, cycle_seconds=2.0, now=True)
                    self.delay(name="leftoff",event_type=None,delay=4.0,handler=self.bonusLaneOff,param="Left")
                    self.game.utilities.set_player_stats('bonusXLeft','on')

        # called when the
        def bonusLaneOff(self,side):
            if side == "Right":
                self.game.utilities.set_player_stats('bonusXRight','off')
                self.game.lamps["bonusXRight"].disable()
            else:
                self.game.utilities.set_player_stats('bonusXLeft','off')
                self.game.lamps["bonusXLeft"].disable()

        # Increment the bonus counter if we didn't hit the max of 127
        def bonus(self, bonus=1):
            bonus_now = min(self.game.utilities.get_player_stats('bonus') + bonus,127)
            self.game.utilities.set_player_stats('bonus',bonus_now)
            self.game.utilities.light_bonus()

        
        def targetTOMCAT(self,sw):
            self.game.sound.play('shoot1')
            # If this target isn't already lit
            if self.game.utilities.get_player_stats(sw.name) == False:
                # Set it as lit
                self.game.utilities.set_player_stats(sw.name, True)
                # and increment the total number lit
                count = self.game.utilities.get_player_stats('tomcat_completed')
                count += 2
                self.game.utilities.set_player_stats('tomcat_completed',count)
                # If 12 are lit, that's all of them
                if count == 12:
                    # This will light lock for multiball
                    self.game.multiball_mode.liteLock()
                    # reset the counter
                    self.game.utilities.set_player_stats('tomcat_completed',0)
                    # and reset each switch too
                    for switch in self.game.tomcatTargetIndex:
                        self.game.utilities.set_player_stats(switch,False)
                    self.update_lamps()
                # If not 12, then flicker this lamp on
                else:
                    self.game.utilities.flickerOn(sw.name)
                    # and also the matching lamp
                    if sw.name[0:5]=="upper":
                        otherside="lower"+sw.name[5:]
                    else:
                        otherside="upper"+sw.name[5:]
                    self.game.utilities.set_player_stats(otherside, True)
                    self.game.utilities.flickerOn(otherside)
            self.game.utilities.score(500)
            self.bonus()
            
           ####################################################
	# Info - Information for Instant Info Screens.
        ####################################################

	def start_info(self):
		self.info_on = True
		info_layers = self.get_info_layers()
		#info_layers.extend(self.crimescenes.get_info_layers())
		self.game.info.set_layers(info_layers)
                self.game.info.callback = self.info_callback
		self.game.modes.add(self.game.info)

	def get_info_layers(self):
		self.title_layer_0 = dmd.TextLayer(128/2, 12, font_named("04B-03-7px.dmd"), "center").set_text('Ball in Play : '+str(self.game.ball))
		self.value_0_layer = dmd.TextLayer(128/2, 22, font_named("04B-03-7px.dmd"), "center").set_text('Extra Balls to Play : '+str(self.game.utilities.get_player_stats('extra_balls')))

		self.layer_0 = dmd.GroupedLayer(128, 32, [self.title_layer_0, self.value_0_layer])

		self.title_layer_1a = dmd.TextLayer(128/2, 12, font_named("04B-03-7px.dmd"), "center").set_text('Missions completed : '+str(self.game.utilities.get_player_stats('kills_completed')))
		self.title_layer_1b = dmd.TextLayer(128/2, 22, font_named("04B-03-7px.dmd"), "center").set_text('Next mission : '+self.game.utilities.get_player_stats('next_mission'))

		self.layer_1 = dmd.GroupedLayer(128, 32, [self.title_layer_1a, self.title_layer_1b])

                self.title_layer_2a = dmd.TextLayer(128/2, 12, font_named("04B-03-7px.dmd"), "center").set_text('Loop shots : '+str(self.game.utilities.get_player_stats('loop_shots')))
		self.title_layer_2b = dmd.TextLayer(128/2, 22, font_named("04B-03-7px.dmd"), "center").set_text('Yagov shots : '+str(self.game.utilities.get_player_stats('yagov_shots')))

		self.layer_2 = dmd.GroupedLayer(128, 32, [self.title_layer_2a, self.title_layer_2b])

                self.title_layer_3a = dmd.TextLayer(128/2, 12, font_named("04B-03-7px.dmd"), "center").set_text('Multiballs played : '+str(self.game.utilities.get_player_stats('multiballs_played')))
		self.title_layer_3b = dmd.TextLayer(128/2, 22, font_named("04B-03-7px.dmd"), "center").set_text('Balls locked : '+str(self.game.utilities.get_player_stats('balls_locked')))

		self.layer_3 = dmd.GroupedLayer(128, 32, [self.title_layer_3a, self.title_layer_3b])


                return [self.layer_0, self.layer_1, self.layer_2, self.layer_3]

	def info_callback(self):
		self.game.modes.remove(self.game.info)
		self.info_on = False

        ####################################################
	# End Info
        ####################################################

        ####################################################
	# Switch Handlers
        ####################################################

	def sw_flipperLwL_active_for_3s(self,sw):
		if not self.info_on:
			self.start_info()

	def sw_flipperLwR_active_for_3s(self,sw):
		if not self.info_on:
			self.start_info()

