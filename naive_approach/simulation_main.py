import os.path
import sys
import time
from datetime import datetime

import random
import pandas as pd
import numpy as np
from threading import Thread, active_count
import simulation_util

# SIMULATION SETUP -- Default
# User deciding parameters
seed = 0
param_fn = 'params'
infection_chance_per_day = [0.2, 0.3, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1]
days_of_simulation = 90
total_runs = 1
num_threads = 4

num_init_cases = 10
init_region_id = None
output_dir = 'output_data/'
do_region = True
do_case = False
simu_id = 0

from_des = False
from_random_airports = False

available_region_level = ['county', 'census_tract', 'cbg']
region_level = 'cbg'
invalid_region_level = False


# Change to User specified parameter setting file
try:
    param_fn = sys.argv[1]
except:
    pass

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Parameter Parsing and Source Data Loading start.")
start_time = time.time()

# Reset parameters with Input file
try:
    with open(param_fn) as f_param:
        for line in f_param.readlines():
            line = line.strip().split('=')
            if line[0] == 'seed':
                seed = int(line[1])
            elif line[0] == 'infection_chance_per_day':
                infection_chance_per_day = line[1].split('/')
                infection_chance_per_day = [float(chance) for chance in infection_chance_per_day]
            elif line[0] == 'days_of_simulation':
                days_of_simulation = int(line[1])
            elif line[0] == 'num_init_cases':
                num_init_cases = line[1].split('/')
                num_init_cases = [int(case) for case in num_init_cases]
                if len(num_init_cases) == 1: num_init_cases = num_init_cases[0]
            elif line[0] == 'total_runs':
                total_runs = int(line[1])
            elif line[0] == 'num_threads':
                num_threads = int(line[1])
            elif line[0] == 'output_dir':
                output_dir = line[1]
                if output_dir[-1] != '/':
                    output_dir += '/'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
            elif line[0] == 'do_region':
                do_region = line[1] == 'True'
            elif line[0] == 'do_case':
                do_case = line[1] == 'True'
            elif line[0] == 'from_des':
                from_des = line[1] == 'True'
            elif line[0] == 'init_region_id':
                init_region_id = line[1].split('/')
            elif line[0] == 'simu_id':
                simu_id = int(line[1])
            elif line[0] == 'region_level':
                rl = line[1].lower()
                if rl not in available_region_level:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR:Invalid region level. Available region level: {str(available_region_level)}")
                    invalid_region_level = True
                region_level = rl.lower()
            elif line[0] == 'from_random_airports':
                from_random_airports = line[1] == 'True'
except:  # No custom parameters provided
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING:\"params\" and custom parameter file does not exist. Running with default setup.")
    pass

if invalid_region_level: exit(1)
if from_random_airports: from_des = False
if type(num_init_cases) == int:
    num_init_cases = [num_init_cases] if init_region_id is None else [num_init_cases for _ in range(len(init_region_id))]
if init_region_id is not None and len(num_init_cases) != len(init_region_id):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR:len(init_region_id) != len(num_init_cases)")
    exit(1)


fn_region = output_dir + 'simu_%d_region_level.csv' if do_region else None
fn_case = output_dir + 'simu_%d_case_level.csv' if do_case else None

if region_level == 'cbg':
    transport_data = pd.read_csv('../src_data/cbg2cbg.csv',dtype={'poi_cbg_source':str, 'poi_cbg_destination':str})
    pop_data = pd.read_csv('../src_data/usa_cbg_population.csv', dtype ={'GeoId':str, 'Population':np.int64})
elif region_level == 'census_tract':
    transport_data = pd.read_csv('../src_data/ct2ct.csv',dtype={'poi_cbg_source':str, 'poi_cbg_destination':str})
    pop_data = pd.read_csv('../src_data/usa_census_tract_population.csv', dtype ={'GeoId':str, 'Population':np.int64})
else:
    transport_data = pd.read_csv('../src_data/county2county.csv',dtype={'poi_cbg_source':str, 'poi_cbg_destination':str})
    pop_data = pd.read_csv('../src_data/usa_county_population.csv', dtype ={'GeoId':str, 'Population':np.int64})

group_by_src = transport_data.groupby('poi_cbg_source')
group_by_des = transport_data.groupby('poi_cbg_destination')

if init_region_id is None:
    random.seed(seed)
    if from_random_airports:
        airport_df = pd.read_csv('../airport_data_process/airports_GeoId.csv',dtype=str)
        airport_geoids = list(airport_df['GeoId'])
        init_region_id = random.sample(airport_geoids,len(num_init_cases))
        if region_level == 'census_tract':
            tmp_id = [geoid[:11] for geoid in init_region_id]
            init_region_id = tmp_id
        elif region_level == 'county':
            tmp_id = [geoid[:5] for geoid in init_region_id]
            init_region_id = tmp_id
    else:
        if from_des:
            des_ids = list(group_by_des.groups.keys())
            init_region_id = random.sample(des_ids,len(num_init_cases))
        else:
            src_ids = list(group_by_src.groups.keys())
            init_region_id = random.sample(src_ids,len(num_init_cases))

end_time = time.time()
print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Parsing and Loading finish, taking {end_time-start_time:.4f} seconds.")

simu_args = [days_of_simulation, init_region_id, num_init_cases, infection_chance_per_day, from_des, pop_data, group_by_des, group_by_src, fn_region, fn_case]
k = 0
while total_runs > 0:
    while active_count() > num_threads:
        time.sleep(1)
    Thread(target=simulation_util.main, args=simu_args + [simu_id + k, seed + simu_id + k]).start()
    k += 1
    total_runs -= 1