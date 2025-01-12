import subprocess
import csv

num_experiments = 1

args = {
    "ugv_num": ["2", "4", "8"],
    "uav_num": ["1", "2"],
    "poi_num": ["5", "15", "25"],
    "communication_range": ["5", "10", "20"],
    "generate_graph": 1,
    "csv_path": "experiments",
    "csv_name": "experiment_test",
    "map_size": "100"
}

args = {
    "ugv_num": ["2"],
    "uav_num": ["1"],
    "poi_num": ["3"],
    "communication_range": ["15"],
    "generate_graph": 1,
    "csv_path": "experiments",
    "csv_name": "exp02",
    "map_size": "100"
}

header = ['experiment', 'ugv_num', 'uav_num', 'poi_num', 'comm_range', 'time_poi', 'time_simulation'] 
  

# Run experiments

# File name: name_numUGV_numUAV_numpoi_commRange


for comm_range in args["communication_range"]:
    for uav_num in args["uav_num"]:
        for ugv_num in args["ugv_num"]:
            for poi_num in args["poi_num"]:
                file_name = args["csv_name"] + "_ugv" + ugv_num + "_uav" + uav_num + "_poi" + poi_num + "_range" + comm_range
                # Open CSV file and assign header 
                with open(f"{args['csv_path']}/{file_name}.csv", 'w') as file: 
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
                                    args["map_size"]
                                    ],)

# Create plot
subprocess.run(["python3", "run_graphs.py", args["csv_name"]])
