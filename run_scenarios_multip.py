import subprocess
import csv
import time
import json
from multiprocessing import Pool
from simulation_config.folder_config import create_folder
from simulation_config.algorithm_config import set_algorithms, serialize_algorithms

"""
Run simulations using python multiprocessing library
"""

def run_experiment(params):
    i, ugv_num, uav_num, poi_num, comm_range, file_name, csv_path, map_size, algorithms_serialized, algorithm_version, generate_graph = params
    subprocess.run(["python3", "main.py", 
                    str(i + 1), 
                    ugv_num, 
                    uav_num, 
                    poi_num, 
                    comm_range,
                    str(generate_graph),
                    file_name,
                    csv_path,
                    map_size,
                    algorithms_serialized,
                    algorithm_version])

def main():
    start_time = time.time()

    num_experiments = 10

    args = {
        "ugv_num": ["2", "4", "8"],
        "uav_num": ["1", "2"],
        "poi_num": ["5", "15", "25"],
        "communication_range": ["5", "10", "20"],
        "generate_graph": 1,
        "csv_path": "experiment02",
        "map_size": "100",
        "algorithms": ["v1", "v2"] 
    }

    header = ['experiment', 'ugv_num', 'uav_num', 'poi_num', 'comm_range', 'time_poi'] 

    # Create experiment folder structure
    folder_path = f'experiments/{args["csv_path"]}'
    create_folder(folder_path)

    tasks = []
    for algorithm_version in args["algorithms"]:
        algorithm_path_analysis = folder_path + f'/algorithm_{algorithm_version}/analysis'
        algorithm_path_data = folder_path + f'/algorithm_{algorithm_version}/data'
        algorithm_path_images = folder_path + f'/algorithm_{algorithm_version}/images'
        create_folder(algorithm_path_analysis)
        create_folder(algorithm_path_data)
        create_folder(algorithm_path_images)

        algorithms = set_algorithms(algorithm_version)
        algorithms_serialized = serialize_algorithms(algorithms)

        for comm_range in args["communication_range"]:
            for uav_num in args["uav_num"]:
                for ugv_num in args["ugv_num"]:
                    for poi_num in args["poi_num"]:
                        file_name = args["csv_path"] + "_ugv" + ugv_num + "_uav" + uav_num + "_poi" + poi_num + "_range" + comm_range
                        with open(algorithm_path_data + f"/{file_name}.csv", 'w') as file: 
                            dw = csv.DictWriter(file, fieldnames=header)
                            dw.writeheader()
                        for i in range(num_experiments):
                            tasks.append((i, ugv_num, uav_num, poi_num, comm_range, file_name, args["csv_path"], 
                                          args["map_size"], algorithms_serialized, algorithm_version, args["generate_graph"]))

    # Use multiprocessing to run experiments in parallel
    with Pool() as pool:
        pool.map(run_experiment, tasks)

    # Create plot
    subprocess.run(["python3", "run_graphs.py", args["csv_path"], json.dumps(args["algorithms"])],)

    end_time = time.time()
    total_time = end_time - start_time
    h = total_time // 3600
    m = (total_time % 3600) // 60
    s = total_time % 60

    print("\n")
    print(f"Total simulation time: {h} hours {m} minutes and {s} seconds")
    print("\n")

if __name__ == "__main__":
    main()
