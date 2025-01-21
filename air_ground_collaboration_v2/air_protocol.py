from air_ground_collaboration_v1.air_protocol import AirProtocol as AirProtocolv1

from gradysim.protocol.messages.communication import BroadcastMessageCommand

from typing import List, Tuple, Dict
import json
import math

class AirProtocol(AirProtocolv1):

    def initialize(self):
        return super().initialize()
    
    def handle_timer(self, timer):
        return super().handle_timer(timer)
    
    def handle_packet(self, message):
        msg = json.loads(message)
        if msg != '':
            if msg["type"] == "poi_message":
                self.check_duplicates(msg["id"], msg["position"])
                self.received_poi += 1
            elif msg["type"] == "uav_message":
                if self.pois != []:
                    pos_list = []
                    uav_x = self.position[0]
                    uav_y = self.position[1]
                    uav_position = (uav_x, uav_y)
                    received_poi_ugv = msg["received_poi"]
                    sorted_pois = self.order_points_by_proximity(uav_position, self.pois)
                    for s in sorted_pois:
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
    
    def distance(self, point1, point2):
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    def order_points_by_proximity(self, uav_position, list_poi):
        """
        Order points such that each subsequent point is closest to the previous one.

        Parameters:
        - uav_position (tuple): The UAV's position as (uav_x, uav_y).
        - list_poi: A list of points in the format [index, [x, y, z]].

        Returns:
        - list_ordered_poi: Points ordered by proximity.
        """
        ordered_points = []
        current_position = uav_position
        remaining_points = list_poi[:]
        
        while remaining_points:
            # Find the closest point to the current position
            closest_point = min(
                remaining_points,
                key=lambda point: self.distance(current_position, point[1][:2])  # Use only x, y for distance
            )
            
            # Add the closest point to the ordered list
            ordered_points.append(closest_point)
            
            # Update the current position to the closest point
            current_position = closest_point[1][:2]
            
            # Remove the closest point from the remaining points
            remaining_points.remove(closest_point)
        
        return ordered_points


    
    def handle_telemetry(self, telemetry):
        return super().handle_telemetry(telemetry)
    
    def finish(self):
        return super().finish()