from gradysim.simulator.handler.communication import CommunicationMedium, CommunicationHandler
from gradysim.simulator.handler.mobility import MobilityHandler
from gradysim.simulator.handler.timer import TimerHandler
from gradysim.simulator.simulation import SimulationBuilder, SimulationConfiguration
from path_planning.grid_path_planning import GridPathPlanning
from simulation_config.algorithm_config import set_algorithms
from random import uniform
from plot_graph.plot_path import PlotPath
import math
import sys
import csv
import os
import time
import json

my_path = os.path.dirname(os.path.abspath(__file__))

# Scenario variables
ugv_num = int(sys.argv[2])
poi_num = int(sys.argv[4])
uav_num = int(sys.argv[3])
map_size = int(sys.argv[9])
communication_range = int(sys.argv[5])

# Algorithm version
#algorithm_strings = json.loads(sys.argv[10])
#algorithms = reconstruct_classes(algorithm_strings)
algorithm_versions = list(json.loads(sys.argv[10]))

# Config variables
generate_graph = int(sys.argv[6])
csv_name = sys.argv[7]
csv_path = sys.argv[8]
experiment_num = sys.argv[1]

# Other
half_map_size = map_size / 2
random_poi = []

for _ in range(poi_num):
    random_poi.append((uniform(-1 * half_map_size, half_map_size), uniform(-1 * half_map_size, half_map_size), 0))

def main(algorithm_version):

    algorithms = set_algorithms(algorithm_version)
    air_protocol = algorithms[0]
    ground_protocol = algorithms[1]
    poi_protocol = algorithms[2]

    config = SimulationConfiguration(
        duration=4000,
        execution_logging=False,
        #log_file="logs/log.txt"
    )
    builder = SimulationBuilder(config)

    ugv_ids: list[int] = []
    uav_ids: list[int] = []
    poi_ids: list[int] = []

    half_map_size = map_size / 2
    
    # PoI 
    for i in range(poi_num):
        poi_ids.append(
            builder.add_node(poi_protocol, random_poi[i])
        )

    # UGV
    angle = 90 / (ugv_num + 1)
    
    for i in range(ugv_num):
        current_angle = angle * (i+1)
        if current_angle <= 45:
            gx = map_size * math.tan(math.radians(current_angle)) - half_map_size
            gy = half_map_size
        else:
            gy = map_size * math.tan(math.radians(90 - current_angle)) - half_map_size
            gx = half_map_size
        ugv_ids.append(
            builder.add_node(ground_protocol, (-1 * half_map_size, -1 * half_map_size, 0), initial_mission_point=(gx, gy, 0), poi_num=poi_num, ugv_num=ugv_num, uav_num=uav_num, time_poi=-1, got_all=False, found_poi=[]),
        )
        
    # UAV
    mission = GridPathPlanning(size=map_size, uav_num=uav_num).define_mission()
    for i in range(uav_num):
        uav_ids.append(
            builder.add_node(air_protocol, (-1 * half_map_size, -1 * half_map_size, 2), mission=mission[i], length=map_size)
        )
    

    builder.add_handler(TimerHandler())

    medium = CommunicationMedium(
        transmission_range=communication_range
    )
    builder.add_handler(CommunicationHandler(medium))

    builder.add_handler(MobilityHandler())

    simulation = builder.build()

    positions_uav = []
    positions_ugv = []
    poi_positions = []

    for poi_id in poi_ids:
        poi_position = simulation.get_node(poi_id).position
        poi_positions.append({
            "role": "poi",
            "x": poi_position[0],
            "y": poi_position[1],
            "z": poi_position[2],
            "group": poi_id
        })

    found_poi = []
    got_all = False
    last_second = 0

    while simulation.step_simulation():
        if got_all:
            break
        else:
            current_time = simulation._current_timestamp
             
            # Para não sobrecarregar o simulador
            if current_time - last_second < 0.1:
                continue

            last_second = current_time
            for uav_id in uav_ids:
                uav_position = simulation.get_node(uav_id).position
                positions_uav.append({
                    "role": "uav",
                    "agent": uav_id,
                    "timestamp": current_time,
                    "x": uav_position[0],
                    "y": uav_position[1],
                    "z": uav_position[2],
                })

            for ugv_id in ugv_ids:
                ugv_position = simulation.get_node(ugv_id).position
                time_poi = simulation.get_node(ugv_id).kwargs
                positions_ugv.append({
                    "role": "ugv",
                    "agent": ugv_id,
                    "timestamp": current_time,
                    "x": ugv_position[0],
                    "y": ugv_position[1],
                    "z": ugv_position[2],
                    "time_poi": time_poi["time_poi"]
                })
                fp = simulation.get_node(ugv_id).kwargs["found_poi"]
                found_poi = list(set(found_poi + fp))
                #print(found_poi)
                if len(found_poi) == poi_num:
                    got_all = True
                    total_time = positions_ugv[-1]["time_poi"]
    
    if not got_all:
        total_time = -1

    if generate_graph != 0:
        plot_path = f"{my_path}/experiments/{csv_path}/algorithm_{algorithm_version}/images/{csv_name}_exp{experiment_num}.png"
        PlotPath(positions_uav, positions_ugv, poi_positions, communication_range, plot_path).plot_graph()
    
    # CSV
    with open(f'experiments/{csv_path}/algorithm_{algorithm_version}/data/{csv_name}.csv', mode='a', newline="") as fd:
        data = [[experiment_num, ugv_num, uav_num, poi_num, communication_range, total_time]]
        writer = csv.writer(fd)
        writer.writerows(data)
    
if __name__ == "__main__":
    for algorithm_version in algorithm_versions:
        main(algorithm_version)