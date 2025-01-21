import logging

from gradysim.protocol.interface import IProtocol
from gradysim.protocol.messages.communication import BroadcastMessageCommand
from gradysim.protocol.messages.telemetry import Telemetry
from gradysim.protocol.plugin.mission_mobility import MissionMobilityPlugin, MissionMobilityConfiguration, LoopMission

from typing import List, Tuple, Dict
import json
from tabulate import tabulate

class GroundProtocol(IProtocol):
    sent: int
    received_poi: int
    received_uav: int
    db_poi: List[int]
    received_directions: List[Tuple]
    mission_plan: MissionMobilityPlugin
    id: int
    initial_mission_point: int
    poi_num: int

    def initialize(self):
        self.start = self.provider.current_time()
        self.ix = 0
        self.time_poi = -1
        self.sent = 0
        self.received_poi = 0
        self.received_uav = 0
        self.db_poi = []
        self.received_directions = []
        self.id = self.provider.get_id()
        self.got_all = self.provider.get_kwargs().get("got_all")
        self.initial_mission_point = self.provider.get_kwargs().get("initial_mission_point")
        self.poi_num = self.provider.get_kwargs().get("poi_num")
        #self.found_poi = self.provider.get_kwargs().get("found_poi")
        self.ugv_num = self.provider.get_kwargs().get("ugv_num")
        self.uav_num = self.provider.get_kwargs().get("uav_num")
        self.mission_list = [
            [self.initial_mission_point],
        ]
        
        self.mission_plan = MissionMobilityPlugin(self, MissionMobilityConfiguration(
            loop_mission=LoopMission.RESTART, 
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

    def handle_packet(self, message: str):
        msg = json.loads(message)
        if msg != '':
            if msg["type"] == "ugv_message":
                reply_msg = {
                    "type": "uav_message",
                    "id": self.id,
                    "received_poi": self.db_poi
                }
                command = BroadcastMessageCommand(
                        message=json.dumps(reply_msg)
                    )
                self.provider.send_communication_command(command)
            elif msg["type"] == "poi_direction":
                if msg["directions"] != []:
                    d = msg["directions"]
                    logging.info(f"Received message of UAV with directions: {d}")
                    self.received_uav += 1
                    dir = [tuple(sublist[1]) for sublist in msg["directions"]]
                    mission_list2 = [
                        dir
                    ]
                    #self.mission_plan.stop_mission()
                    self.start_mission(mission_list2)
                    self.received_directions.append(msg["directions"])
            elif msg["type"] == "poi_message":
                self.received_poi += 1
                self.check_duplicates(msg["id"])
                '''
                if len(self.db_poi) == self.poi_num and not self.got_all:
                    self.end = self.provider.current_time()
                    self.time_poi = self.end - self.start
                    self.provider.set_kwargs("time_poi", self.time_poi)
                    self.provider.set_kwargs("got_all", True)
                    self.got_all = True
                '''
    
    def check_duplicates(self, id):
        for i in self.db_poi:
            if i == id:
                return
        self.db_poi.append(id)
        self.provider.set_kwargs("found_poi", self.db_poi)
    
    def start_mission(self, ml):
        if not (ml == []):
            ml2 = ml.pop()
            self.mission_plan.start_mission(ml2)
    
    def handle_telemetry(self, telemetry: Telemetry):
        self.end = self.provider.current_time()
        self.time_poi = self.end - self.start
        self.provider.set_kwargs("time_poi", self.time_poi)

    def finish(self):
        '''
        print("\n  Directions received from UAV")
        headers = ['id', 'x', 'y', 'z']
        table_data = []
        inv = self.received_directions[::-1]
        for row in inv:
            for col in row:
                new_row = [col[0]] + col[1]
                table_data.append(new_row)

        print(tabulate(table_data, headers=headers, tablefmt='grid'))

        print("\npoi messages received by UGV= ", self.db_poi)
        '''
        #logging.info(f"Final counter values: "
                     #f"received_uav={self.received_uav} ; received_dir={received_directions_tb} ; received_poi={self.received_poi} ; db_poi={self.db_poi}")
