import os.path
import sys
import time

import random
import pandas as pd
import numpy as np
from threading import Thread, active_count
import simulation_util

# SIMULATION SETUP
# User deciding parameters
seed = 0
infection_chance_per_day = [0.2, 0.3, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1]
days_of_simulation = 90
total_runs = 1
num_threads = 4

num_init_cases = 100
list_init_cbg = None
output_dir = 'output_data/'
do_region = False
do_case = False
simu_id = 0

from_des = False

available_region_level = ['county', 'census_tract', 'cbg']
region_level = 'cbg'
invalid_region_level = False

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
            elif line[0] == 'list_init_cbg':
                list_init_cbg = line[1].split('/')
            elif line[0] == 'simu_id':
                simu_id = int(line[1])
            elif line[0] == 'region_level':
                rl = line[1].lower()
                if rl not in available_region_level:
                    print('Invalid region level. Available region level: %s'%str(available_region_level))
                    invalid_region_level = True
                region_level = rl
except:  # No custom parameters provided
    pass

if invalid_region_level: exit(1)

fn_region = output_dir + 'simu_%d_region_level.csv' if do_region else None
fn_case = output_dir + 'simu_%d_case_level.csv' if do_case else None

# TODO: Multi-level spread probability (County, Censes Track, CBG)
spread_prob_df = pd.concat([pd.read_csv('../spread_probability_top30/%d.csv'%i) for i in range(1,6)],ignore_index=True)
spread_prob_df['from'] = spread_prob_df['from'].apply(lambda x: '%012d'%x)
spread_prob_df['to'] = spread_prob_df['to'].apply(lambda x: '%012d'%x)
spread_prob_df = spread_prob_df[['from', 'to', 'prob']].reset_index(drop = True)
spread_prob_grouped_df = spread_prob_df.groupby('from')
pop_data = pd.read_csv('../src_data/usa_population_revise.csv', dtype ={'GeoId':str, 'Population':np.int64})


simu_args = [days_of_simulation, list_init_cbg, num_init_cases, infection_chance_per_day, from_des, pop_data,  spread_prob_grouped_df, fn_region, fn_case]
k = 0
while total_runs > 0:
    while active_count() > num_threads:
        time.sleep(1)
    Thread(target=simulation_util.main, args=simu_args + [simu_id + k, seed + simu_id + k]).start()
    k += 1
    total_runs -= 1