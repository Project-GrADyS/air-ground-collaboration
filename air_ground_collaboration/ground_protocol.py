import logging
import random

from gradysim.protocol.interface import IProtocol
from gradysim.protocol.messages.communication import BroadcastMessageCommand
from gradysim.protocol.messages.telemetry import Telemetry
from gradysim.protocol.plugin.mission_mobility import MissionMobilityPlugin, MissionMobilityConfiguration, LoopMission

from typing import List, Tuple, Dict
import json
from tabulate import tabulate

class GroundProtocol(IProtocol):
    sent: int
    received_sensor: int
    received_uav: int
    db_sensor: List[int]
    received_directions: List[Tuple]
    mission_plan: MissionMobilityPlugin
    id: int

    def initialize(self):
        self.sent = 0
        self.received_sensor = 0
        self.received_uav = 0
        self.db_sensor = []
        self.received_directions = []
        self.id = self.provider.get_id()
        self.mission_list = [
            [(50, 50, 0)]
        ]
        
        self.mission_plan = MissionMobilityPlugin(self, MissionMobilityConfiguration(
            loop_mission=LoopMission.NO, 
            speed=1,
            tolerance=0.0
        ))

        self.provider.schedule_timer(
            "mobility",  
            self.provider.current_time() + 1
        )
    
    def handle_timer(self, timer: str):
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
                    "id": self.id,
                    "received_sensor": self.db_sensor
                }
                command = BroadcastMessageCommand(
                        message=json.dumps(reply_msg)
                    )
                self.provider.send_communication_command(command)
            elif msg["type"] == "sensor_direction":
                if msg["directions"] != []:
                    self.received_directions.append(msg["directions"])
                    self.received_uav += 1
                    dir = [tuple(sublist[1]) for sublist in msg["directions"]]
                    mission_list2 = [
                        dir
                    ]
                    self.mission_plan.stop_mission()
                    self.start_mission(mission_list2)
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
            ml2 = ml.pop()
            self.mission_plan.start_mission(ml2)
    
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
