import logging
import math

from gradysim.protocol.interface import IProtocol
from gradysim.protocol.messages.communication import BroadcastMessageCommand
from gradysim.protocol.messages.telemetry import Telemetry
from gradysim.protocol.plugin.mission_mobility import MissionMobilityPlugin, MissionMobilityConfiguration, LoopMission

#from path_planning.grid_path_planning import GridPathPlanning

from typing import List, Tuple, Dict
import json

class AirProtocol(IProtocol):
    sent_poi: int
    received_poi: int
    received_ugv: int
    sent_ground: int
    position: Tuple
    pois: List
    mission_plan: MissionMobilityPlugin
    ugv_db: List[int]
    path_planning: List[List[int]]
    
    def initialize(self):
        self.sent = 0
        self.ugv_db = []
        self.received_poi = 0
        self.received_ugv = 0
        self.position = Tuple[float, float, float]
        self.pois = []
        self.path_planning = self.provider.get_kwargs().get("mission")
        self.length = self.provider.get_kwargs().get("length")
        self.mission_plan = MissionMobilityPlugin(self, MissionMobilityConfiguration(
            loop_mission=LoopMission.RESTART,
            speed=5
        ))
        
        self.provider.schedule_timer(
            "mobility",  
            self.provider.current_time() + 1
        )
        
        self.provider.schedule_timer(
            "message",  
            self.provider.current_time() + 1  
        )
            
    def start_mission(self):
        mission_list = self.path_planning
        if not (mission_list == []):
            self.mission_plan.start_mission(mission_list.pop())

    def handle_timer(self, timer: str):
        if timer == "message":
            msg = {
                "type": "ugv_message"
            }
            command = BroadcastMessageCommand(
                message=json.dumps(msg)
            )
            self.provider.send_communication_command(command)
            self.provider.schedule_timer(
                "message",
                self.provider.current_time() + 1
            )
        elif timer == "mobility":
            self.start_mission()

    def handle_packet(self, message: str):
        msg = json.loads(message)
        if msg != '':
            if msg["type"] == "poi_message":
                self.check_duplicates(msg["id"], msg["position"])
                self.received_poi += 1
            elif msg["type"] == "uav_message":
                if self.pois != []:
                    ugv_id = msg["id"]
                    logging.info(f"Found UGV {ugv_id}")
                    #pos_list = self.pois.pop()
                    pos_list = []
                    uav_x = self.position[0]
                    uav_y = self.position[1]
                    received_poi_ugv = msg["received_poi"]
                    for s in self.pois:
                        if s[0] not in received_poi_ugv:
                            pos = self.calculate_direction(s[1][0], s[1][1], s[1][2], self.length, uav_x, uav_y)
                            uav_x = pos[0]
                            uav_y = pos[1]
                            pos_list.append([s[0], pos])
                            received_poi_ugv.append(s[0])
                    self.received_ugv += 1
                    reply_msg = {
                        "type": "poi_direction",
                        "directions": pos_list,
                    }
                    command = BroadcastMessageCommand(
                        message=json.dumps(reply_msg)
                    )
                    self.provider.send_communication_command(command)
                    self.ugv_db.append(msg["id"])
    
    def check_duplicates(self, id, pos):
        for s in self.pois:
            if s[0] == id:
                return
        self.pois.append([id, pos])
    
    def calculate_direction(self, x, y, z, length, initial_x, initial_y):
        vector_x = x - initial_x
        vector_y = y - initial_y
        direction_x = vector_x / math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2))
        direction_y = vector_y / math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2))

        dx = x - initial_x
        dy = y - initial_y

        half_length = length//2

        tb = (-1* half_length - initial_x) / dx
        
        dir_x = initial_x + tb * dx
        dir_y = initial_y + tb * dy

        theta = math.atan2(y - initial_y, x - initial_x)

        if abs(direction_x) > abs(direction_y):
            #Move in the Y direction
            if x > initial_x:
                dir_x = x + 1
                if dir_x > half_length:
                    dir_x = half_length
            else:
                dir_x = x - 1
                if dir_x < half_length:
                    dir_x = -1 * half_length
            dir_y = initial_y + (dir_x - initial_x) * math.tan(theta)
        else:
            #Move in the X direction
            if y > initial_y:
                dir_y = y + 1
                if dir_y > half_length:
                    dir_y = half_length
            else:
                dir_y = y - 1
                if dir_y < half_length:
                    dir_y = -1 * half_length
            dir_x = initial_x + (dir_y - initial_x ) / math.tan(theta)

        if dir_x > 0 and dir_x > half_length:
            dir_x = half_length
        elif dir_x < 0 and dir_x < (-1* half_length):
            dir_x = -1* half_length
        
        if dir_y > 0 and dir_y > half_length:
                dir_x = half_length
        elif dir_y < 0 and dir_y < (-1* half_length):
            dir_y = -1* half_length

        return (dir_x, dir_y, z)

    def handle_telemetry(self, telemetry: Telemetry):
        self.position = telemetry.current_position

    def finish(self):
        logging.info(f"Final counter values: "
                     f"received_poi={self.pois}")
