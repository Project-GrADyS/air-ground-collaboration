from air_ground_collaboration_01.air_protocol import AirProtocol
from air_ground_collaboration_01.ground_protocol import GroundProtocol
from air_ground_collaboration_01.sensor_protocol import SensorProtocol
from gradysim.simulator.handler.communication import CommunicationMedium, CommunicationHandler
from gradysim.simulator.handler.mobility import MobilityHandler
from gradysim.simulator.handler.timer import TimerHandler
from gradysim.simulator.handler.visualization import VisualizationHandler
from gradysim.simulator.simulation import SimulationBuilder, SimulationConfiguration
from random import uniform
import datetime
import matplotlib.pyplot as plt
from data_line_width_plot import data_linewidth_plot
import math

# Metric variables
communication_range = 10

# Scenario variables
ugv_num = 1
sensor_num = 3
uav_num = 1

def main():
    config = SimulationConfiguration(
        duration=2000,
        execution_logging=False,
        #log_file="logs/log.txt"
    )
    builder = SimulationBuilder(config)

    ugv_ids: list[int] = []
    sensor_ids: list[int] = []
    
    #Sensor
    for _ in range(sensor_num):
        sx = uniform(-50, 50)
        sy = uniform(-50, 50)
        sensor_ids.append(
            builder.add_node(SensorProtocol, (sx, sy, 0))
        )
    
    # UGV
    d = ugv_num + 1
    angle = 90 / d
    for i in range(ugv_num):
        a = (i+1) * math.tan(math.radians(angle))
        if a < 1:
            gx = 50
            gy = 100 * a
            gy = gy - 50
        elif a == 1:
            gx = 50
            gy = 50
        else:
            gy = 50
            gx = 100 / a
            gx = gx - 50
        ugv_ids.append(
            builder.add_node(GroundProtocol, (-50, -50, 0), initial_mission_point=(gx, gy, 0))
        )
    '''
    ugv_ids.append(
        builder.add_node(GroundProtocol, (-50, -50, 0), initial_mission_point=(50, 45, 0))
    )
    '''
    
    # UAV
    uav_id = builder.add_node(AirProtocol, (-50, -50, 2))
    

    builder.add_handler(TimerHandler())

    medium = CommunicationMedium(
        transmission_range=communication_range
    )
    builder.add_handler(CommunicationHandler(medium))

    builder.add_handler(MobilityHandler())

    builder.add_handler(VisualizationHandler())

    simulation = builder.build()

    positions_uav = []
    positions_ugv = []
    sensor_positions = []

    for sensor_id in sensor_ids:
        sensor_position = simulation.get_node(sensor_id).position
        sensor_positions.append({
            "role": "sensor",
            "x": sensor_position[0],
            "y": sensor_position[1],
            "z": sensor_position[2],
            "group": sensor_id
        })
    
    while simulation.step_simulation():
        current_time = simulation._current_timestamp

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
            positions_ugv.append({
                "role": "ugv",
                "agent": ugv_id,
                "timestamp": current_time,
                "x": ugv_position[0],
                "y": ugv_position[1],
                "z": ugv_position[2],
            })

    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    position_uav_df = pd.DataFrame.from_records(positions_uav)
    position_ugv_df = pd.DataFrame.from_records(positions_ugv)
    position_uav_df = position_uav_df.set_index("timestamp")
    position_ugv_df = position_ugv_df.set_index("timestamp")
    sensor_df = pd.DataFrame.from_records(sensor_positions)

    sns.set_theme()
    sns.set_context("talk")
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 12))
    
    sns.scatterplot(data=sensor_df, x="x", y="y", ax=ax, marker='x', color='black',
                    label='sensors', s=100, linewidth=2)
    for line in range(0,sensor_df.shape[0]):
        plt.text(
            sensor_df["x"][line]+1.5,
            sensor_df["y"][line]+0.5,
            sensor_df["group"][line],
            ha='left',
            weight='normal'
     )
    
    grouped_uav = position_uav_df.groupby("agent")
    grouped_ugv = position_ugv_df.groupby("agent")
    
    for name, group in grouped_uav:
        role = group["role"].iloc[0]
        agent = group["agent"].iloc[0]
        s = role + ' ' + str(agent)
        plt.plot(group['x'], group['y'], marker='o', linestyle='-', ms=1,
                 label=s, color='#bad1f720')
    
    for name, group in grouped_ugv:
        role = group["role"].iloc[0]
        agent = group["agent"].iloc[0]
        s = role + ' ' + str(agent)
        line = plt.plot(group['x'], group['y'], marker='o', linestyle='-', ms=1,
                 label=s, color='#cf7073' if agent==3 else '#01a049')
        data_linewidth_plot(group['x'], group['y'], marker=None, linestyle='-', linewidth=communication_range, color=line[0].get_color(), label=None, alpha=0.1)
    
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    current_datetime = datetime.datetime.now()
    timestamp = current_datetime.timestamp()

    plt.savefig(f"path_{timestamp}.png")


if __name__ == "__main__":
    main()