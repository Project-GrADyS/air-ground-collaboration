import subprocess
import csv

num_experiments = 1

args = {
    "ugv_num": "2",
    "uav_num": "1",
    "sensor_num": "3",
    "communication_range": "5",
    "generate_graph": 0,
    "csv_path": "experiments",
    "csv_name": "document5"
}

header = ['experiment', 'ugv_num', 'uav_num', 'sensor_num', 'time_poi'] 
  
# Open CSV file and assign header 
with open(f"{args['csv_path']}/{args['csv_name']}.csv", 'w') as file: 
    dw = csv.DictWriter(file, fieldnames=header)
    dw.writeheader()

# Run experiments
for i in range(num_experiments):
    subprocess.run(["python3", 
                    "main.py", 
                    str(i+1), 
                    args["ugv_num"], 
                    args["uav_num"], 
                    args["sensor_num"], 
                    args["communication_range"],
                    str(args["generate_graph"]),
                    args["csv_name"],
                    args["csv_path"]
                ])
    