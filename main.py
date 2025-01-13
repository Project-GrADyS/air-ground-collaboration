from air_ground_collaboration_02.air_protocol import AirProtocol
from air_ground_collaboration_02.ground_protocol import GroundProtocol
from air_ground_collaboration_02.poi_protocol import PoIProtocol
from gradysim.simulator.handler.communication import CommunicationMedium, CommunicationHandler
from gradysim.simulator.handler.mobility import MobilityHandler
from gradysim.simulator.handler.timer import TimerHandler
#from gradysim.simulator.handler.visualization import VisualizationHandler, VisualizationConfiguration
from gradysim.simulator.simulation import SimulationBuilder, SimulationConfiguration
from path_planning.grid_path_planning import GridPathPlanning
from random import uniform
from graphs.plot_path import PlotPath
import math
import sys
import csv
import os
import time

my_path = os.path.dirname(os.path.abspath(__file__))

# Metric variables
communication_range = int(sys.argv[5])

# Scenario variables
ugv_num = int(sys.argv[2])
poi_num = int(sys.argv[4])
uav_num = int(sys.argv[3])
map_size = int(sys.argv[9])

generate_graph = int(sys.argv[6])
csv_name = sys.argv[7]
csv_path = sys.argv[8]
experiment_num = sys.argv[1]

#color_list = ['#cf7073', '#01a049', "#00008a", "#efbf04", "#8a00c4", "#ffa600"]

def main():
    config = SimulationConfiguration(
        duration=4000,
        execution_logging=False,
        #log_file="logs/log.txt"
    )
    builder = SimulationBuilder(config)

    ugv_ids: list[int] = []
    uav_ids: list[int] = []
    poi_ids: list[int] = []

    ms = map_size / 2
    
    # PoI
    for _ in range(poi_num):
        sx = uniform(-1 * ms, ms)
        sy = uniform(-1 * ms, ms)
        poi_ids.append(
            builder.add_node(PoIProtocol, (sx, sy, 0))
        )

    # UGV
    angle = 90 / (ugv_num + 1)
    
    for i in range(ugv_num):
        current_angle = angle * (i+1)
        if current_angle <= 45:
            gx = map_size * math.tan(math.radians(current_angle)) - ms
            gy = ms
        else:
            gy = map_size * math.tan(math.radians(90 - current_angle)) - ms
            gx = ms
        ugv_ids.append(
            builder.add_node(GroundProtocol, (-1 * ms, -1 * ms, 0), initial_mission_point=(gx, gy, 0), poi_num=poi_num, ugv_num=ugv_num, uav_num=uav_num, time_poi=-1, got_all=False)
        )
        
    # UAV
    mission = GridPathPlanning(size=map_size, uav_num=uav_num).define_mission()
    for i in range(uav_num):
        uav_ids.append(
            builder.add_node(AirProtocol, (-1 * ms, -1 * ms, 2), mission=mission[i], length=map_size)
        )
    

    builder.add_handler(TimerHandler())

    medium = CommunicationMedium(
        transmission_range=communication_range
    )
    builder.add_handler(CommunicationHandler(medium))

    builder.add_handler(MobilityHandler())

    #conf = VisualizationConfiguration(x_range=(-100,-100), y_range=(-100,-100))

    #builder.add_handler(VisualizationHandler(configuration=conf))

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
    
    got_all = False
    last_second = 0

    initial_time = time.time()

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
                if simulation.get_node(ugv_id).kwargs["got_all"]:
                    got_all = True
    
    bt = math.inf
    for i in range(ugv_num):
        tp = positions_ugv[(i+1)*(-1)]["time_poi"]
        if tp != -1 and tp < bt:
            bt = tp
    if bt == math.inf:
        bt = -1

    if generate_graph != 0:
        plot_path = f"{my_path}/graph_images/{csv_name}_exp{experiment_num}.png"
        PlotPath(positions_uav, positions_ugv, poi_positions, communication_range, plot_path).plot_graph()

    end_time = time.time()
    
    # CSV
    with open(f'{csv_path}/{csv_name}.csv', mode='a', newline="") as fd:
        data = [[experiment_num, ugv_num, uav_num, poi_num, communication_range, bt, end_time - initial_time]]
        writer = csv.writer(fd)
        writer.writerows(data)
    
if __name__ == "__main__":
    main()