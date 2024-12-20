import subprocess
import csv

num_experiments = 2

args = {
    "ugv_num": ["3", "5"],
    "uav_num": ["1", "2", "3"],
    "sensor_num": ["3", "5", "7"],
    "communication_range": ["5", "10"],
    "generate_graph": 1,
    "csv_path": "experiments",
    "csv_name": "test",
    "map_size": "100"
}


header = ['experiment', 'ugv_num', 'uav_num', 'sensor_num', 'comm_range', 'time_poi', 'time_simulation'] 
  

# Run experiments

# File name: name_numUGV_numUAV_numSensor_commRange


for comm_range in args["communication_range"]:
    for uav_num in args["uav_num"]:
        for ugv_num in args["ugv_num"]:
            for sensor_num in args["sensor_num"]:
                file_name = args["csv_name"] + "_ugv" + ugv_num + "_uav" + uav_num + "_sensor" + sensor_num + "_range" + comm_range
                # Open CSV file and assign header 
                with open(f"{args['csv_path']}/{file_name}.csv", 'w') as file: 
                    dw = csv.DictWriter(file, fieldnames=header)
                    dw.writeheader()
                for i in range(num_experiments):
                    subprocess.run(["python3", "main.py", 
                                    str(i+1), 
                                    ugv_num, 
                                    uav_num, 
                                    sensor_num, 
                                    comm_range,
                                    str(args["generate_graph"]),
                                    file_name,
                                    args["csv_path"],
                                    args["map_size"]
                                    ],)

# Create plot
subprocess.run(["python3", "run_graphs.py", args["csv_name"]])
