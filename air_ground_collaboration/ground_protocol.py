import logging
import random

from gradysim.protocol.interface import IProtocol
from gradysim.protocol.messages.communication import BroadcastMessageCommand, SendMessageCommand
from gradysim.protocol.messages.mobility import GotoCoordsMobilityCommand
from gradysim.protocol.messages.telemetry import Telemetry
from gradysim.protocol.plugin.random_mobility import RandomMobilityPlugin, RandomMobilityConfig
from gradysim.protocol.plugin.mission_mobility import MissionMobilityPlugin, MissionMobilityConfiguration, LoopMission, SetSpeedMobilityCommand

from typing import List, Tuple, Dict
import json
from tabulate import tabulate


class GroundProtocol(IProtocol):
    sent: int
    received_sensor: int
    received_uav: int
    config: RandomMobilityConfig
    ground: RandomMobilityPlugin
    db_sensor: List[int]
    received_directions: List[Tuple]
    

    def initialize(self):
        self.sent = 0
        self.received_sensor = 0
        self.received_uav = 0
        #self.config = RandomMobilityConfig(z_range=(0,0))
        #self.ground = RandomMobilityPlugin(self, config=self.config)
        self.db_sensor = []
        self.received_directions = []
        self.mission_list = [
            [(50, 50, 0)]
        ]
        
        self.mission_plan = MissionMobilityPlugin(self, MissionMobilityConfiguration(
            loop_mission=LoopMission.NO, 
            speed=2,
            tolerance=0.0
        ))

        self.provider.schedule_timer(
            "mobility",  
            self.provider.current_time() + 1
        )
        
    '''
    def define_mission(self):
        mission_list = []

        mission_list += [(-50, 50, 7)]
        mission_list += [(-50, -50, 7)]
        mission_list += [(-17, -50, 7)]
        mission_list += [(17, -50, 7)]
        mission_list += [(50, -50, 7)]

        return mission_list
    '''
    
    def start_mission_og(self):
        if not (self.mission_list == []):
            self.mission_plan.start_mission(self.mission_list.pop())
        else:
            self.mission_plan.stop_mission()
    
    def handle_timer(self, timer: str):
        '''
        if timer == "message":
            self.sent += 1
            msg = {
                "type": "message"
            }
            command = BroadcastMessageCommand(
                message=json.dumps(msg)
            )

            self.provider.send_communication_command(command)

            self.provider.schedule_timer(
                "message",
                self.provider.current_time() + 1
            )
        '''
        if timer == "mobility":
            self.start_mission(ml=self.mission_list)
            self.provider.schedule_timer(
            "mobility",  
            self.provider.current_time() + 1
            )

    def handle_packet(self, message: str):
        msg = json.loads(message)
        if msg != '':
            if msg["type"] == "ugv_message":
                reply_msg = {
                    "type": "uav_message",
                }
                command = BroadcastMessageCommand(
                        message=json.dumps(reply_msg)
                    )
                self.provider.send_communication_command(command)
            elif msg["type"] == "sensor_direction":
                self.received_directions.append(msg["directions"])
                self.received_uav += 1
                #print("=================GROUND==============")
                #print(msg["directions"])
                #print("=================================")
                dir = [tuple(sublist[1]) for sublist in msg["directions"]]
                inverted_dir = dir[::-1]
                mission_list2 = [
                    dir
                ]
                #print(mission_list2)
                self.start_mission(mission_list2)
                '''
                command = GotoCoordsMobilityCommand(
                    dir[0],
                    dir[1],
                    dir[2]
                )
                '''
                #self.provider.send_mobility_command(command)
            elif msg["type"] == "sensor_message":
                self.received_sensor += 1
                self.check_duplicates(msg["id"])
    
    def check_duplicates(self, id):
        for i in self.db_sensor:
            if i == id:
                return
        self.db_sensor.append(id)
    
    def start_mission(self, ml):
        if not (ml == []):
            self.mission_plan.start_mission(ml.pop())
        else:
            self.mission_plan.stop_mission()

    
    def handle_telemetry(self, telemetry: Telemetry):
        self.position = telemetry.current_position
    

    def finish(self):
        print("\n  Directions received from UAV")
        headers = ['id', 'x', 'y', 'z']
        table_data = []
        inv = self.received_directions[::-1]
        for row in inv:
            for col in row:
                new_row = [col[0]] + col[1]
                table_data.append(new_row)

        print(tabulate(table_data, headers=headers, tablefmt='grid'))

        print("\nSensor messages received by UGV= ", self.db_sensor)
        #logging.info(f"Final counter values: "
                     #f"received_uav={self.received_uav} ; received_dir={received_directions_tb} ; received_sensor={self.received_sensor} ; db_sensor={self.db_sensor}")
