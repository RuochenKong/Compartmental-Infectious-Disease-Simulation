import os.path
import sys
import time

import random
import pandas as pd
import numpy as np
from threading import Thread, active_count
import mkypox_util

# SIMULATION SETUP
# User deciding parameters
seed = 0
infection_chance_per_day = [0.2, 0.3, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1]
days_of_simulation = 90
total_runs = 1
num_threads = 4

num_init_cases = [10]
list_init_cbg = None
output_dir = 'output_data/'
do_log = False
do_spread = False
simu_id = 0

from_airport = True

# Reset parameters with Input file
try:
    with open('params') as f_param:
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
            elif line[0] == 'do_log':
                do_log = line[1] == 'True'
            elif line[0] == 'do_spread':
                do_spread = line[1] == 'True'
            elif line[0] == 'from_airport':
                from_airport = line[1] == 'True'
            elif line[0] == 'list_init_cbg':
                list_init_cbg = line[1].split('/')
                list_init_cbg = [np.int64(int(cbg)) for cbg in list_init_cbg]

except:  # No custom parameters provided
    pass

# Reset simulation id from the command line
try:
    idx = sys.argv.index('-id')
    simu_id = int(sys.argv[idx + 1])
except:  # No id specified
    pass

# Open output files
fn_spread = output_dir + 'spreading_history_%d.csv' if do_spread else None
fn_log = output_dir + 'log_simu_%d.log' if do_log else None
fn_simu = output_dir + 'simu_%d.csv'

# Loading source data
# -- TODO Low priority: loading only once for all simulation runs
chunked_data = pd.read_csv('src_data/cbg2cbg_revise.csv', chunksize=10000)
chunk_list = []
for chunk in chunked_data:
    chunk_list.append(chunk)
transport_data = pd.concat(chunk_list)
src_cbg_names = list(transport_data['poi_cbg_source'].unique())

pop_data = pd.read_csv('src_data/usa_population_revise.csv', dtype=np.int64)
airport_cbg = pd.read_csv('src_data/airports_geoinfo.csv', dtype={'GeoId':np.int64})
airport_cbg = list(airport_cbg['GeoId'])

group_by_src = transport_data.groupby('poi_cbg_source')
group_by_des = transport_data.groupby('poi_cbg_destination')

simu_args = [days_of_simulation, num_init_cases, list_init_cbg, infection_chance_per_day,
             pop_data, from_airport, airport_cbg, src_cbg_names, group_by_src, group_by_des,
             fn_simu, fn_spread, fn_log]

k = 0
while total_runs > 0:
    while active_count() > num_threads:
        time.sleep(1)
    Thread(target=mkypox_util.main, args=simu_args + [simu_id + k, random.Random(seed + simu_id + k)]).start()
    k += 1
    total_runs -= 1



