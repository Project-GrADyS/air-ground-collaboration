import logging
import random
import math

from gradysim.protocol.interface import IProtocol
from gradysim.protocol.messages.communication import BroadcastMessageCommand, SendMessageCommand
from gradysim.protocol.messages.mobility import GotoCoordsMobilityCommand
from gradysim.protocol.messages.telemetry import Telemetry
from gradysim.protocol.plugin.random_mobility import RandomMobilityPlugin, RandomMobilityConfig
from gradysim.protocol.plugin.mission_mobility import MissionMobilityPlugin, MissionMobilityConfiguration, LoopMission, SetSpeedMobilityCommand

from typing import List, Tuple, Dict
import json


class AirProtocol(IProtocol):
    sent_sensor: int
    received_sensor: int
    received_ugv: int
    sent_ground: int
    position: Tuple
    sensors: List
    
    def initialize(self):
        self.sent = 0
        self.received_sensor = 0
        self.received_ugv = 0
        self.position = Tuple[float, float, float]
        self.sensors = []
        self.mission_plan = MissionMobilityPlugin(self, MissionMobilityConfiguration(
            loop_mission=LoopMission.NO, 
            speed=40
        ))
        
        self.provider.schedule_timer(
            "mobility",  
            self.provider.current_time() + 1
        )
        
        self.provider.schedule_timer(
            "message",  
            self.provider.current_time() + 1  
        )

    
    def generate_mission_section(self, start_x, start_y, end_x, end_y, step, substep):
        mission_section = []
        x = start_x
        y = start_y
        limit_y = start_y - substep
        limit_x = start_x

        mission_section.append([start_x, start_y, 2])
        
        for i in range(18):
            if i % 2 == 0:
                if x < end_x:
                    x += step
                mission_section.append([x, limit_y, 2])
            else:
                if y <= end_y:
                    y += step
                else:
                    limit_x += 10
                mission_section.append([limit_x, y, 2])

        mission_section.append([end_x, end_y, 2])
        mission_section.append([-50, -50, 2])
    
        return mission_section

    def define_mission(self):
        mission_sublist = []
        
        # Generate mission sections
        mission_sublist += self.generate_mission_section(-50, -50, 0, -17, 7, 4)
        mission_sublist += self.generate_mission_section(0, -50, 50, -17, 7, 4)
        mission_sublist += self.generate_mission_section(-50, -17, 0, 17, 7, 4)
        mission_sublist += self.generate_mission_section(0, -17, 50, 17, 7, 4)
        mission_sublist += self.generate_mission_section(-50, 17, 0, 50, 7, 4)
        mission_sublist += self.generate_mission_section(0, 17, 50, 50, 7, 4)
        
        return [mission_sublist]

            
    def start_mission(self):
        mission_list = self.define_mission()
        if not (mission_list == []):
            self.mission_plan.start_mission(mission_list.pop())
        else:
            self.mission_plan.stop_mission()
            

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
            if msg["type"] == "sensor_message":
                self.check_duplicates(msg["id"], msg["position"])
                self.received_sensor += 1
            elif msg["type"] == "uav_message":
                if self.sensors != []:
                    #pos_list = self.sensors.pop()
                    pos_list = []
                    i_x = self.position[0]
                    i_y = self.position[1]
                    #print("===============SENSORS===============")
                    #print(self.sensors)
                    for s in self.sensors:
                        #print(s)
                        pos = self.calculate_direction(s[1][0], s[1][1], s[1][2], 100, i_x, i_y)
                        i_x = pos[0]
                        i_y = pos[1]
                        #i_x = s[1][0]
                        #i_y = s[1][1]
                        pos_list.append([s[0], pos])
                    #self.sensors = []
                    self.received_ugv += 1
                    reply_msg = {
                        "type": "sensor_direction",
                        "directions": pos_list,
                    }
                    command = BroadcastMessageCommand(
                        message=json.dumps(reply_msg)
                    )
                    self.provider.send_communication_command(command)
    
    def check_duplicates(self, id, pos):
        for s in self.sensors:
            if s[0] == id:
                return
        self.sensors.append([id, pos])
    
    def calculate_direction(self, x, y, z, length, initial_x, initial_y):
        #print("=========ORIGINAL==========")
        #print([x, y, z])
        #print("==========UAV=============")
        #x_uav = self.position[0]
        #y_uav = self.position[1]
        #print([x_uav, y_uav, self.position[2]])
        '''
        theta = math.atan2(y - initial_y, x - initial_x)
        d = length / 2
        right_edge = initial_y + (d - initial_x) * math.tan(theta)
        left_edge = initial_y + ((-1) * d - initial_x) * math.tan(theta)
        top_edge = initial_x + (d - initial_y) * 1 / math.tan(theta)
        bottom_edge = initial_x + ((-1) * d - initial_y) * 1 / math.tan(theta)
        '''
        #print("==========EDGES=============")
        #print("right = ", right_edge)
        #print("left = ", left_edge)
        #print("top = ", top_edge)
        #print("bottom = ", bottom_edge)
        '''
        vector_x = x - initial_x
        vector_y = y - initial_y
        direction_x = vector_x / math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2))
        direction_y = vector_y / math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2))
        if abs(direction_x) > abs(direction_y):
            if (left_edge > 0 and left_edge > d) or (left_edge < 0 and left_edge < d):
                dir_y = right_edge
            else:
                dir_y = left_edge
            dir_x = length/2
        elif abs(direction_x) < abs(direction_y):
            if (top_edge > 0 and top_edge > d) or (top_edge < 0 and top_edge < d):
                dir_x = bottom_edge
            else:
                dir_x = top_edge
            dir_y = length/2
        '''

        vector_x = x - initial_x
        vector_y = y - initial_y
        direction_x = vector_x / math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2))
        direction_y = vector_y / math.sqrt(math.pow(vector_x, 2) + math.pow(vector_y, 2))

        dx = x - initial_x
        dy = y - initial_y

        d_mag = math.sqrt(dx / math.pow(dx, 2) + math.pow(dy, 2))

        dx_hat = dx / d_mag
        dy_hat = dy / d_mag
        
        tl = (-50 - initial_y) / dy
        tr = (50 - initial_y) / dy
        tb = (-50 - initial_x) / dx
        tt = (50 - initial_x) / dx
        
        dir_x = initial_x + tb * dx
        dir_y = initial_y + tb * dy
        dir_y = 50

        theta = math.atan2(y - initial_y, x - initial_x)

        if abs(direction_x) > abs(direction_y):
            #Move in the Y direction
            if x > initial_x:
                dir_x = 50
            else:
                dir_x = -50
            dir_y = initial_y + (dir_x - initial_x) * math.tan(theta)
        else:
            #Move in the X direction
            if y > initial_y:
                dir_y = 50
            else:
                dir_y = -50
            dir_x = initial_x + (dir_y - initial_x ) / math.tan(theta)
        '''
        print("==========EDGES=============")
        yr = y + tl * dy
        xr = 50
        print(f"right = ({xr},{yr})")
        yl = y + tr * dy
        xl = 50
        print(f"left = ({xl},{yl})")
        xt = x + tt * dx
        yt = 50
        print(f"top = ({xt},{yt})")
        xb = x + tb * dx
        yb = 50
        print(f"bottom = ({xb},{yb})")
        '''
        return (dir_x, dir_y, z)

    def handle_telemetry(self, telemetry: Telemetry):
        self.position = telemetry.current_position

    def finish(self):
        logging.info(f"Final counter values: "
                     f"received_sensor={self.sensors}")
