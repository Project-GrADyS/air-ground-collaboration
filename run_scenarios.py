import subprocess
import csv
import time
import json
from simulation_config.folder_config import create_folder
from simulation_config.protocol_config import set_protocols

start_time = time.time()

num_experiments = 10

args = {
    "ugv_num": ["2", "4", "8"],
    "uav_num": ["1", "2"],
    "poi_num": ["5", "15", "25"],
    "communication_range": ["5", "10", "20"],
    "generate_graph": 1,
    "csv_path": "experiment_test",
    "map_size": "100"
}

header = ['experiment', 'ugv_num', 'uav_num', 'poi_num', 'comm_range', 'time_poi', 'time_simulation'] 

num_experiments = 5

args = {
    "ugv_num": ["3"],
    "uav_num": ["2"],
    "poi_num": ["5"],
    "communication_range": ["10"],
    "generate_graph": 1,
    "csv_path": "experiment_test",
    "protocols": ["v1", "v2"],
    "map_size": "100"
}

# Create experiment folder structure
folder_path = f'experiments/{args["csv_path"]}'
create_folder(folder_path)

# Run experiments

# File name: name_numUGV_numUAV_numpoi_commRange

for protocol_version in args["protocols"]:
    protocol_path_analysis = folder_path + f'/protocol_{protocol_version}/analysis'
    protocol_path_data = folder_path + f'/protocol_{protocol_version}/data'
    protocol_path_images = folder_path + f'/protocol_{protocol_version}/images'
    create_folder(protocol_path_analysis)
    create_folder(protocol_path_data)
    create_folder(protocol_path_images)

    protocols = set_protocols(protocol_version)
    protocols_serialized = json.dumps([f"{cls.__module__}.{cls.__name__}" for cls in protocols])

    for comm_range in args["communication_range"]:
        for uav_num in args["uav_num"]:
            for ugv_num in args["ugv_num"]:
                for poi_num in args["poi_num"]:
                    file_name = args["csv_path"] + "_ugv" + ugv_num + "_uav" + uav_num + "_poi" + poi_num + "_range" + comm_range
                    with open(protocol_path_data + f"/{file_name}.csv", 'w') as file: 
                        dw = csv.DictWriter(file, fieldnames=header)
                        dw.writeheader()
                    for i in range(num_experiments):
                        subprocess.run(["python3", "main.py", 
                                        str(i+1), 
                                        ugv_num, 
                                        uav_num, 
                                        poi_num, 
                                        comm_range,
                                        str(args["generate_graph"]),
                                        file_name,
                                        args["csv_path"],
                                        args["map_size"],
                                        protocols_serialized,
                                        protocol_version
                                        ],)

# Create plot
subprocess.run(["python3", "run_graphs.py", args["csv_path"], json.dumps(args["protocols"])],)

end_time = time.time()

total_time = end_time - start_time
h = total_time // 3600
m = (total_time % 3600) // 60
s = total_time % 60

print("\n")
print(f"Total simulation time: {h} hours {m} minutes and {s} seconds")
print("\n")
