import sys
import os
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import json

my_path = os.path.dirname(os.path.abspath(__file__))
folder_path = "experiments"
csv_prefix = sys.argv[1]
protocols = json.loads(sys.argv[2])
column_name = "time_poi"


for protocol_version in protocols:
    dataframes = []
    #time_df = []
    protocol_path = f'{my_path}/{folder_path}/{csv_prefix}/protocol_{protocol_version}'
    for file_name in os.listdir(protocol_path + '/data'):
        if file_name.startswith(csv_prefix) and file_name.endswith('.csv'):
            file_path = os.path.join(protocol_path + '/data', file_name)
            df = pd.read_csv(file_path)
            df_filtered = df[df[column_name] != -1]
            df_filtered = df_filtered.drop(columns="experiment")
            df_filtered["time_poi"] = df_filtered[column_name].mean()
            grouped_df = df_filtered.groupby(['ugv_num', 'uav_num', 'poi_num', 'comm_range'], as_index=False).mean()
            #time_df.append(df)
            dataframes.append(grouped_df)
        

    combined_df = pd.concat(dataframes, ignore_index=True)
    #print(combined_df)
    #combined_time = pd.concat(time_df, ignore_index=True)

    '''
    ts = combined_time["time_simulation"].sum()
    h = ts // 3600
    m = (ts % 3600) // 60
    s = ts % 60

    print("\n")
    print(f"Total simulation time: {h} hours {m} minutes and {s} seconds")
    print("\n")
    '''
    analysis_path = protocol_path + '/analysis'

    # Bar plot range x time

    grouped_range = combined_df.groupby("comm_range")["time_poi"].mean().reset_index()
    
    sns.barplot(grouped_range, x="comm_range", y="time_poi", hue="comm_range", palette='crest')
    plt.xlabel("Communication Range")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_range_time.png")
    plt.clf()


    # Bar plot numUGV x time

    grouped_ugv = combined_df.groupby("ugv_num")["time_poi"].mean().reset_index()

    sns.barplot(grouped_ugv, x="ugv_num", y="time_poi", hue="ugv_num", palette='crest')
    plt.xlabel("Number of UGVs")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_ugv_time.png")
    plt.clf()

    # Bar plot numPoIs x time

    grouped_poi = combined_df.groupby("poi_num")["time_poi"].mean().reset_index()

    sns.barplot(grouped_poi, x="poi_num", y="time_poi", hue="poi_num", palette='crest')
    plt.xlabel("Number of PoIs")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_poi_time.png")
    plt.clf()

    # Bar plot numUAV x time

    grouped_uav = combined_df.groupby("uav_num")["time_poi"].mean().reset_index()

    sns.barplot(grouped_uav, x="uav_num", y="time_poi", hue="uav_num", palette='crest')
    plt.xlabel("Number of UAVs")
    plt.ylabel("Average Time to find all PoI")
    plt.savefig(f"{analysis_path}/{csv_prefix}_uav_time.png")
    plt.clf()








