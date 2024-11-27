import subprocess
import csv

num_experiments = 2

args = {
    "ugv_num": ["2", "3", "5"],
    "uav_num": "1",
    "sensor_num": ["3", "5", "10"],
    "communication_range": ["5", "10"],
    "generate_graph": 1,
    "csv_path": "experiments",
    "csv_name": "test"
}

header = ['experiment', 'ugv_num', 'uav_num', 'sensor_num', 'time_poi', 'time_simulation'] 
  

# Run experiments

# File name: name_numUGV_numUAV_numSensor_commRange

for comm_range in args["communication_range"]:
    for ugv_num in args["ugv_num"]:
        for sensor_num in args["sensor_num"]:
            file_name = args["csv_name"] + "_ugv" + ugv_num + "_uav" + args["uav_num"] + "_sensor" + sensor_num + "_range" + comm_range
            # Open CSV file and assign header 
            with open(f"{args['csv_path']}/{file_name}.csv", 'w') as file: 
                dw = csv.DictWriter(file, fieldnames=header)
                dw.writeheader()
            for i in range(num_experiments):
                success = False
                attempts = 0
                while not success and attempts < 3:
                    try:
                        subprocess.run(["python3", "main.py", 
                                        str(i+1), 
                                        ugv_num, 
                                        args["uav_num"], 
                                        sensor_num, 
                                        comm_range,
                                        str(args["generate_graph"]),
                                        file_name,
                                        args["csv_path"]
                                    ], 
                                    check=True
                                )
                        success = True
                    except subprocess.CalledProcessError as e:
                        attempts += 1
                        if "Address already in use" in str(e.stderr):
                            print(f"Port in use error encountered. Killing processes and retrying...")
                            subprocess.run(["kill -9 $(ps -A | grep python | awk '{print $1}')"])
                        else:
                            print(f"An unexpected error occurred: {e}")
                        if attempts >= 3:
                            print("Max retries reached. Moving to the next experiment.")
    