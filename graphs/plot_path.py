import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from data_line_width_plot import data_linewidth_plot

class PlotPath:

    def __init__(self, positions_uav, positions_ugv, sensor_positions, communication_range, plot_path):
        self.positions_uav = positions_uav
        self.positions_ugv = positions_ugv
        self.sensor_positions = sensor_positions
        self.communication_range = communication_range
        self.plot_path = plot_path

    def plot_graph(self):

        position_uav_df = pd.DataFrame.from_records(self.positions_uav)
        position_ugv_df = pd.DataFrame.from_records(self.positions_ugv)
        position_uav_df = position_uav_df.set_index("timestamp")
        position_ugv_df = position_ugv_df.set_index("timestamp")
        sensor_df = pd.DataFrame.from_records(self.sensor_positions)

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
            data_linewidth_plot(group['x'], group['y'], marker=None, linestyle='-', linewidth=self.communication_range, color=line[0].get_color(), label=None, alpha=0.1)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.savefig(self.plot_path)