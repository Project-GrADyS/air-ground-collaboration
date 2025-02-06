import sys
import os
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import json

my_path = os.path.dirname(os.path.abspath(__file__))
folder_path = "experiments"
csv_prefix = sys.argv[1]
algorithms = json.loads(sys.argv[2])
column_name = "time_poi"

algorithm_df = {
    "range": [],
    "num_ugv": [],
    "num_pois": [],
    "num_uav": []
}

for algorithm_version in algorithms:
    dataframes = []
    algorithm_path = f'{my_path}/{folder_path}/{csv_prefix}/algorithm_{algorithm_version}'
    for file_name in os.listdir(algorithm_path + '/data'):
        if file_name.startswith(csv_prefix) and file_name.endswith('.csv'):
            file_path = os.path.join(algorithm_path + '/data', file_name)
            df = pd.read_csv(file_path)
            df_filtered = df[df[column_name] != -1]
            df_filtered = df_filtered.drop(columns="experiment")
            df_filtered["time_poi"] = df_filtered[column_name].mean()
            grouped_df = df_filtered.groupby(['ugv_num', 'uav_num', 'poi_num', 'comm_range'], as_index=False).mean()
            dataframes.append(grouped_df)
        

    combined_df = pd.concat(dataframes, ignore_index=True)
    
    analysis_path = algorithm_path + '/analysis'

    # Bar plot range x time

    grouped_range = combined_df.groupby("comm_range")["time_poi"].mean().reset_index()
    algorithm_df["range"].append(grouped_range)

    sns.barplot(grouped_range, x="comm_range", y="time_poi", hue="comm_range", palette='crest')
    plt.xlabel("Communication Range")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_range_time.png")
    plt.clf()


    # Bar plot numUGV x time

    grouped_ugv = combined_df.groupby("ugv_num")["time_poi"].mean().reset_index()
    algorithm_df["num_ugv"].append(grouped_ugv)

    sns.barplot(grouped_ugv, x="ugv_num", y="time_poi", hue="ugv_num", palette='crest')
    plt.xlabel("Number of UGVs")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_ugv_time.png")
    plt.clf()

    # Bar plot numPoIs x time

    grouped_poi = combined_df.groupby("poi_num")["time_poi"].mean().reset_index()
    algorithm_df["num_pois"].append(grouped_poi)

    sns.barplot(grouped_poi, x="poi_num", y="time_poi", hue="poi_num", palette='crest')
    plt.xlabel("Number of PoIs")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_poi_time.png")
    plt.clf()

    # Bar plot numUAV x time

    grouped_uav = combined_df.groupby("uav_num")["time_poi"].mean().reset_index()
    algorithm_df["num_uav"].append(grouped_uav)

    sns.barplot(grouped_uav, x="uav_num", y="time_poi", hue="uav_num", palette='crest')
    plt.xlabel("Number of UAVs")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_uav_time.png")
    plt.clf()


path = f'{my_path}/{folder_path}/{csv_prefix}'

for key, data_list in algorithm_df.items():
    if key == "range":
        for i, df in enumerate(data_list):
            df["algorithm"] = "v" + str(i + 1)
        combined_df = pd.concat(data_list, ignore_index=True)
        print(combined_df)
        ax = sns.barplot(x="comm_range", y="time_poi", hue="algorithm", data=combined_df, palette='crest')
        ax.spines[['top', 'right']].set_visible(False)
        #sns.move_legend(ax, bbox_to_anchor=(1, 0.5), loc='center left', frameon=False)
        plt.xlabel("Communication Range")
        plt.ylabel("Average Time to find all PoI")
        plt.savefig(f"{path}/{csv_prefix}_range_time.png")
        plt.clf()
    elif key == "num_ugv":
        for i, df in enumerate(data_list):
            df["algorithm"] = "v" + str(i + 1)
        combined_df = pd.concat(data_list, ignore_index=True)
        print(combined_df)
        ax = sns.barplot(x="ugv_num", y="time_poi", hue="algorithm", data=combined_df, palette='crest')
        ax.spines[['top', 'right']].set_visible(False)
        #sns.move_legend(ax, bbox_to_anchor=(1, 0.5), loc='center left', frameon=False)
        plt.xlabel("Number of UGVs")
        plt.ylabel("Average Time to find all PoI")
        plt.savefig(f"{path}/{csv_prefix}_ugv_time.png")
        plt.clf()
    elif key == "num_uav":
        for i, df in enumerate(data_list):
            df["algorithm"] = "v" + str(i + 1)
        combined_df = pd.concat(data_list, ignore_index=True)
        print(combined_df)
        ax = sns.barplot(x="uav_num", y="time_poi", hue="algorithm", data=combined_df, palette='crest')
        ax.spines[['top', 'right']].set_visible(False)
        #sns.move_legend(ax, bbox_to_anchor=(1, 0.5), loc='center left', frameon=False)
        plt.xlabel("Number of UAVs")
        plt.ylabel("Average Time to find all PoI")
        plt.savefig(f"{path}/{csv_prefix}_uav_time.png")
        plt.clf()
    elif key == "num_pois":
        for i, df in enumerate(data_list):
            df["algorithm"] = "v" + str(i + 1)
        combined_df = pd.concat(data_list, ignore_index=True)
        print(combined_df)
        ax = sns.barplot(x="poi_num", y="time_poi", hue="algorithm", data=combined_df, palette='crest')
        ax.spines[['top', 'right']].set_visible(False)
        #sns.move_legend(ax, bbox_to_anchor=(1, 0.5), loc='center left', frameon=False)
        plt.xlabel("Number of PoIs")
        plt.ylabel("Average Time to find all PoI")
        plt.savefig(f"{path}/{csv_prefix}_poi_time.png")
        plt.clf()








