import subprocess
import csv
from multiprocessing import Pool, cpu_count
import os

# Simulation parameters
num_experiments = 10

args = {
    "ugv_num": ["2", "4", "8"],
    "uav_num": ["1", "2"],
    "poi_num": ["5", "15", "25"],
    "communication_range": ["5", "10", "20"],
    "generate_graph": 1,
    "csv_path": "experiments",
    "csv_name": "multip",
    "map_size": "100"
}

header = ['experiment', 'ugv_num', 'uav_num', 'poi_num', 'comm_range', 'time_poi', 'time_simulation']

# Ensure CSV directory exists
os.makedirs(args["csv_path"], exist_ok=True)

# Function to run a single experiment
def run_experiment(params):
    i, ugv_num, uav_num, poi_num, comm_range, file_name = params
    subprocess.run([
        "python3", "main.py",
        str(i + 1),
        ugv_num,
        uav_num,
        poi_num,
        comm_range,
        str(args["generate_graph"]),
        file_name,
        args["csv_path"],
        args["map_size"]
    ])

# Function to prepare the CSV file
def prepare_csv(file_name):
    with open(f"{args['csv_path']}/{file_name}.csv", 'w') as file:
        dw = csv.DictWriter(file, fieldnames=header)
        dw.writeheader()

# Main function
def main():
    tasks = []
    for comm_range in args["communication_range"]:
        for uav_num in args["uav_num"]:
            for ugv_num in args["ugv_num"]:
                for poi_num in args["poi_num"]:
                    file_name = f"{args['csv_name']}_ugv{ugv_num}_uav{uav_num}_poi{poi_num}_range{comm_range}"
                    prepare_csv(file_name)  # Prepare the CSV file
                    for i in range(num_experiments):
                        tasks.append((i, ugv_num, uav_num, poi_num, comm_range, file_name))

    # Use multiprocessing to run experiments in parallel
    num_workers = min(cpu_count(), len(tasks))  # Limit workers to CPU cores or number of tasks
    with Pool(num_workers) as pool:
        pool.map(run_experiment, tasks)

    # Create plots after all experiments
    subprocess.run(["python3", "run_graphs.py", args["csv_name"]])

if __name__ == "__main__":
    main()
