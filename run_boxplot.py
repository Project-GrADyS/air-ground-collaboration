import sys
import os
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import json

my_path = os.path.dirname(os.path.abspath(__file__))
folder_path = "experiments"
csv_prefix = "experiment_all"
algorithms = ["v1", "v2", "v3"]
column_name = "time_poi"

alg_df = []

for algorithm_version in algorithms:
    dataframes = []
    algorithm_path = f'{my_path}/{folder_path}/{csv_prefix}/algorithm_{algorithm_version}'
    for file_name in os.listdir(algorithm_path + '/data'):
        if file_name.startswith(csv_prefix) and file_name.endswith('.csv'):
            file_path = os.path.join(algorithm_path + '/data', file_name)
            df = pd.read_csv(file_path)
            df_filtered = df[df[column_name] != -1]
            df_filtered = df_filtered.drop(columns="experiment")
            #df_filtered["time_poi"] = df_filtered[column_name].mean()
            #grouped_df = df_filtered.groupby(['ugv_num', 'uav_num', 'poi_num', 'comm_range'], as_index=False).mean()
            dataframes.append(df_filtered)

    combined_df = pd.concat(dataframes, ignore_index=True)
    #print(combined_df)
    alg_df.append(combined_df)

path = f'{my_path}/{folder_path}/{csv_prefix}'

all_df = pd.concat({'v1': alg_df[0], 'v2': alg_df[1], 'v3': alg_df[2]}, names=['version', 'old_index'])
all_df = all_df.reset_index(level=0).reset_index(drop=True)

# UGV Number
sns.boxplot(data=all_df, x='ugv_num', y='time_poi', hue='version', palette='crest', showfliers = False)
plt.xlabel("Number of UGVs")
plt.ylabel("Time to find all PoI")
plt.savefig(f"{path}/{csv_prefix}_boxplot_ugv_time.png")
plt.clf()

# UAV Number
sns.boxplot(data=all_df, x='uav_num', y='time_poi', hue='version', palette='crest', showfliers = False)
plt.xlabel("Number of UAVs")
plt.ylabel("Time to find all PoI")
plt.savefig(f"{path}/{csv_prefix}_boxplot_uav_time.png")
plt.clf()

# PoI Number
sns.boxplot(data=all_df, x='poi_num', y='time_poi', hue='version', palette='crest', showfliers = False)
plt.xlabel("Number of PoIs")
plt.ylabel("Time to find all PoI")
plt.savefig(f"{path}/{csv_prefix}_boxplot_poi_time.png")
plt.clf()

# Communication Range
sns.boxplot(data=all_df, x='comm_range', y='time_poi', hue='version', palette='crest', showfliers = False)
plt.xlabel("Communication Range")
plt.ylabel("Time to find all PoI")
plt.savefig(f"{path}/{csv_prefix}_boxplot_range_time.png")
plt.clf()

