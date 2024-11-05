from air_ground_collaboration.air_protocol_01 import AirProtocol
from air_ground_collaboration.ground_protocol_01 import GroundProtocol
from air_ground_collaboration.sensor_protocol import SensorProtocol
from gradysim.simulator.handler.communication import CommunicationMedium, CommunicationHandler
from gradysim.simulator.handler.mobility import MobilityHandler
from gradysim.simulator.handler.timer import TimerHandler
from gradysim.simulator.handler.visualization import VisualizationHandler
from gradysim.simulator.simulation import SimulationBuilder, SimulationConfiguration
from random import uniform
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

communication_range = 20

def main():
    # To enhance our viewing experience we are setting the simulator
    # to real-time mode. This means that the simulator will run
    # approximately synchronized with real-time, enabling us to see
    # the nodes moving properly. We are also decreasing the total
    # simulator time, so we don't have to wait for that long
    #self.provider.tracked_variables['blabla'] = 'oi'
    config = SimulationConfiguration(
        duration=1000,
        real_time=1000,
        execution_logging=False
    )
    builder = SimulationBuilder(config)

    ugv_ids: list[int] = []
    sensor_ids: list[int] = []

    # UGV
    
    for _ in range(1):
        ugv_ids.append(
            builder.add_node(GroundProtocol, (-50, -50, 0))
        )
    
    #Sensor
    
    for _ in range(3):
        rx = uniform(-50, 50)
        ry = uniform(-50, 50)
        sensor_ids.append(
            builder.add_node(SensorProtocol, (rx, ry, 0))
        )
    
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

    # Listas para guardar as posições dos nós durante a simulação
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
    
    # Rodando a simulação passo-a-passo e coletando a posição em todos os passos
    while simulation.step_simulation():
        current_time = simulation._current_timestamp # Não gostei disso, vou tornar uma propriedade mais fácil de acessar

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
    from matplotlib.patheffects import PathPatchEffect, SimpleLineShadow, Normal

    position_uav_df = pd.DataFrame.from_records(positions_uav)
    position_ugv_df = pd.DataFrame.from_records(positions_ugv)
    position_uav_df = position_uav_df.set_index("timestamp")
    position_ugv_df = position_ugv_df.set_index("timestamp")

    sensor_df = pd.DataFrame.from_records(sensor_positions)

    # Estilizando gráfico
    sns.set_theme()
    sns.set_context("talk")
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 12))

    # Plotando posições dos sensores (fixos) com um "x"
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

    # Plotando as posições dos agentes ao longo do tempo. Líder em vermelho e seguidores em azul
    grouped_uav = position_uav_df.groupby("agent")
    grouped_ugv = position_ugv_df.groupby("agent")
    
    for name, group in grouped_uav:
        role = group["role"].iloc[0]
        plt.plot(group['x'], group['y'], marker='o', linestyle='-', ms=1,
                 label=role, color='#bad1f720')
    
    for name, group in grouped_ugv:
        role = group["role"].iloc[0]
        line = plt.plot(group['x'], group['y'], marker='o', linestyle='-', ms=1,
                 label=role, color='#cf7073')
        data_linewidth_plot(group['x'], group['y'], marker=None, linestyle='-', linewidth=communication_range, color=line[0].get_color(), label=None, alpha=0.1)
    

    # Mostrando legenda. As duas primeiras linhas garantem que não vão ter elementos repetidos na legenda
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    current_datetime = datetime.datetime.now()
    timestamp = current_datetime.timestamp()


    # Salvando o gráfico
    plt.savefig(f"path_{timestamp}.png")

class data_linewidth_plot():
    def __init__(self, x, y, **kwargs):
        self.ax = kwargs.pop("ax", plt.gca())
        self.fig = self.ax.get_figure()
        self.lw_data = kwargs.pop("linewidth", 1)
        self.lw = 1
        self.fig.canvas.draw()

        self.ppd = 72./self.fig.dpi
        self.trans = self.ax.transData.transform
        self.linehandle, = self.ax.plot([],[],**kwargs)
        if "label" in kwargs: kwargs.pop("label")
        self.line, = self.ax.plot(x, y, **kwargs)
        self.line.set_color(self.linehandle.get_color())
        self._resize()
        self.cid = self.fig.canvas.mpl_connect('draw_event', self._resize)

    def _resize(self, event=None):
        lw =  ((self.trans((1, self.lw_data))-self.trans((0, 0)))*self.ppd)[1]
        if lw != self.lw:
            self.line.set_linewidth(lw)
            self.lw = lw
            self._redraw_later()

    def _redraw_later(self):
        self.timer = self.fig.canvas.new_timer(interval=10)
        self.timer.single_shot = True
        self.timer.add_callback(lambda : self.fig.canvas.draw_idle())
        self.timer.start()


if __name__ == "__main__":
    main()
