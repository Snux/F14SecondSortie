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
import random
import procgame.dmd
from procgame.dmd import font_named

class MissionMode(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
			super(MissionMode, self).__init__(game, priority)
			self.kill_list=['kill1','kill2','kill3','kill4','kill5','kill6','kill7']
                        self.mission_name= {'kill1' : 'alpha',
                                            'kill2' : 'bravo',
                                            'kill3' : 'charlie',
                                            'kill4' : 'delta',
                                            'kill5' : 'echo',
                                            'kill6' : 'foxtrot',
                                            'kill7' : 'golf'
                                            }
                        

                        #setup logging
                        self.log = logging.getLogger('f14.mission')
			
	def sw_vUK_active(self, sw):
            if (self.game.utilities.get_player_stats('mission_in_progress') == 'None' and self.game.utilities.get_player_stats('kill1') == 0):
                self.game.modes.add(self.game.kill1mission)
                return procgame.game.SwitchStop

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
                    self.layer = dmd.AnimatedLayer(frames=self.game.dmd_assets[self.mission_name[mission_to_play]+'_available'].frames, hold=False, repeat=False, frame_time=2)
                    self.game.utilities.set_player_stats('target1',False)
                    self.game.utilities.set_player_stats('target2',False)
                    self.game.utilities.set_player_stats('target3',False)
                    self.game.utilities.set_player_stats('target4',False)
                    self.game.utilities.set_player_stats('target5',False)
                    self.game.utilities.set_player_stats('target6',False)
                    self.game.utilities.set_player_stats('target1-6_completed',0)

                # Determine the mission the player will do next, if there is one.
                next_mission = 'None';
                for mission in self.kill_list:
                    if self.game.utilities.get_player_stats(mission) == 0 and next_mission == 'None':
                        next_mission = mission;
                self.game.utilities.set_player_stats('next_mission',next_mission)



                self.game.update_lamps()



	def update_lamps(self):
                self.log.info("Update Lamps: Mission")
                for mission in self.kill_list:
                    status=self.game.utilities.get_player_stats(mission);
                    if status == -1:
                        self.log.info("- setting "+mission+" to disabled")
                        self.game.lamps[mission].disable()
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].disable()
                        self.game.lamps[mission+'blue'].disable()
                    elif status == 0:
                        self.log.info("- setting "+mission+" to available")
                        self.game.lamps[mission].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'blue'].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].disable()
                    elif status == 1:
                        self.log.info("- setting "+mission+" to in progress")
                        self.game.lamps[mission].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'red'].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'green'].disable()
                        self.game.lamps[mission+'blue'].disable()
                    else:
                        self.log.info("- setting "+mission+" to complete")
                        self.game.lamps[mission].enable()
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].enable()
                        self.game.lamps[mission+'blue'].disable()

                # If there is a mission waiting to be played, flash the release lamp
                if self.game.utilities.get_player_stats('next_mission') != 'None':
                    self.game.lamps.release.schedule(schedule=0xF0F0F0F0)
                    self.log.info(" - next mission to play is " +self.game.utilities.get_player_stats('next_mission'))
                else:
                    self.game.lamps.release.disable()



#     ___    __       __          __  ___ _            _
#    / _ |  / /___   / /  ___ _  /  |/  /(_)___  ___  (_)___   ___
#   / __ | / // _ \ / _ \/ _ `/ / /|_/ // /(_-< (_-< / // _ \ / _ \
#  /_/ |_|/_// .__//_//_/\_,_/ /_/  /_//_//___//___//_/ \___//_//_/
#           /_/
#
# Moving lit TOMCAT target, hit the lit one.

class Kill1Mode(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
            super(Kill1Mode, self).__init__(game, priority)

            self.tomcatTargets={}
            self.tomcatTargetIndex={}
            #setup logging
            self.log = logging.getLogger('f14.mission number 1')
            target_index = 0
            self.current_position=0
            self.target_speed = 1

            for switch in self.game.switches:
                if switch.name[0:5] in self.game.tomcatTargetIndex:
                    self.add_switch_handler(name=switch.name, event_type='active' ,delay=0.01, handler=self.targetTOMCAT)
                    self.tomcatTargets[switch.name]=False
                    
                    target_index += 1
            
            

        def mode_started(self):
            self.log.info("kill 1 starting")
            self.game.utilities.set_player_stats('mission_in_progress','kill1')
            self.game.utilities.set_player_stats('kill1',1)
            self.game.update_lamps()
            for target in self.tomcatTargets:
                self.tomcatTargets[target]=False
            self.game.utilities.arduino_write_alpha(display=2,text='FUEL')
            self.game.utilities.arduino_write_number(display=0,number=960)
            self.game.utilities.arduino_start_count(display=0,direction=1,limit=0,ticks=1)
            self.current_position = random.randint(0,11)
            anim = dmd.Animation().load("/P-ROC/games/F14SecondSortie/assets/dmd/alpha2.dmd")
            self.first_layer = dmd.AnimatedLayer(frames=anim.frames, hold=False, repeat=True, frame_time=4)

            self.second_layer = dmd.TextLayer(128/2, 14, font_named("Font_CC_5px_az.dmd"),"center").set_text("SHOOT THE MOVING TARGET")
            self.third_layer = dmd.TextLayer(128/2, 20, font_named("Font_CC_5px_az.dmd"),"center").set_text("BEFORE FUEL RUNS OUT")
            self.second_layer.composite_op = 'blacksrc'
            self.third_layer.composite_op = 'blacksrc'

            self.layer = dmd.GroupedLayer(128, 32, [self.first_layer,self.second_layer,self.third_layer])
            self.delay(name='move_target',delay=3,handler=self.move_target)
            self.delay(name='fuel_out',delay=30,handler=self.fuel_out)

        def move_target(self):
            self.game.lamps[self.game.tomcatTargetIndex[self.current_position]].disable()
            self.current_position += random.choice([-1,1])
            if self.current_position == 12:
                self.current_position = 0
            elif self.current_position == -1:
                self.current_position = 11
            self.game.lamps[self.game.tomcatTargetIndex[self.current_position]].enable()
            mission_text = list("------------")
            mission_text[self.current_position] = '+'
            self.third_layer= dmd.TextLayer(128/2, 24, font_named("Font_CC_7px_az.dmd"), "center").set_text(''.join(mission_text))
            self.layer = dmd.GroupedLayer(128, 32, [self.first_layer,self.second_layer,self.third_layer])
            self.delay(name='move_target',delay=self.target_speed,handler=self.move_target)
            #self.update_lamps()

        def fuel_out(self):
            self.game.utilities.display_text(txt="FUEL EMPTY",time=3,blink=4)
            self.game.modes.remove(self)


        def mode_stopped(self):
            for x in self.tomcatTargets:
                self.tomcatTargets[x]=False
            self.game.utilities.set_player_stats('kill1',2)
            self.game.utilities.set_player_stats('mission_in_progress','None')
            self.log.info("mode finishing")
            self.game.utilities.arduino_blank_all()
            del self.layer
            self.cancel_delayed('move_target')
            self.cancel_delayed('fuel_out')
            self.game.update_lamps()


        def update_lamps(self):
            #for target in self.tomcatTargets:
            #    self.game.lamps[target].disable()
            #self.game.lamps[self.tomcatTargetIndex[self.current_position]].enable()
            pass

        def targetTOMCAT(self,sw):
            if sw.name == self.game.tomcatTargetIndex[self.current_position]:
                self.game.utilities.score(20000)
                self.game.utilities.display_text(txt="TARGET HIT",time=3)
                self.target_speed /= 2
            else:
                self.game.utilities.score(1500)
            self.tomcatTargets[sw.name]=True
            self.game.sound.play('tomcat')
            #if sw.name[0:5]=="upper":
            #    otherside="lower"+sw.name[5:]
            #else:
            #    otherside="upper"+sw.name[5:]
            #self.tomcatTargets[otherside]=True
            return procgame.game.SwitchStop


            