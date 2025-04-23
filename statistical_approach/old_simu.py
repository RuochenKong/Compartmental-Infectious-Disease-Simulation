import os.path
import time

import pandas as pd
import numpy as np
import random
import sys

random.seed(42)
np.random.seed(42)
tot_case = [0]

# HELPER FUNCTIONS
# Get a CBG where the infected case will visit
def get_random_des(src_df):
    randval = random.random()
    cumprob = src_df['des_prob'].cumsum()
    sumprob = src_df['des_prob'].sum()
    if sumprob == 0:
        return
    randval *= sumprob
    checkprob = 0
    for des, prob in zip(src_df['poi_cbg_destination'], cumprob):
        if checkprob == prob:
            continue
        if randval < prob:
            return des
    return src_df.loc[-1, 'poi_cbg_destination']


# Get a CBG where the nealy infected agent originally from
def get_random_src(des_df):
    randval = random.random()
    cumprob = des_df['src_prob'].cumsum()
    sumprob = des_df['src_prob'].sum()
    if sumprob == 0:
        return
    randval *= sumprob
    checkprob = 0
    for src, prob in zip(des_df['poi_cbg_source'], cumprob):
        if checkprob == prob:
            continue
        if randval < prob:
            return src
    return des_df.loc[-1, 'poi_cbg_source']


# SIMULATION SETUP
# User deciding parameters
infection_chance_per_day = [0.1,0.2,0.3,0.3,0.2,0.1,0.1]
days_of_simulation = 180

num_init_cases = [100,100,100,100,100]
list_init_cbg = [250092524002, 361190111013, 270530257013, 360650228002, 261635154001]
# output_dir = 'output_data/'
# do_log = False

# simu_id = 0

# Reset parameters with Input file
# try:
#     with open('params') as f_param:
#         for line in f_param.readlines():
#             line = line.strip().split('=')
#             if line[0] == 'seed':
#                 seed = int(line[1])
#             elif line[0] == 'infection_chance_per_day':
#                 infection_chance_per_day = line[1].split('/')
#                 infection_chance_per_day = [float(chance) for chance in infection_chance_per_day]
#             elif line[0] == 'days_of_simulation':
#                 days_of_simulation = int(line[1])
#             elif line[0] == 'num_init_cases':
#                 num_init_cases = line[1].split('/')
#                 num_init_cases = [int(case) for case in num_init_cases]
#             elif line[0] == 'output_dir':
#                 output_dir = line[1]
#                 if output_dir[-1] != '/':
#                     output_dir += '/'
#                 if not os.path.exists(output_dir):
#                     os.makedirs(output_dir, exist_ok=True)
#             elif line[0] == 'do_log':
#                 do_log = line[1] == 'True'
#             # TODO: map list of Airports to List of CBGs
# except:  # No custom parameters provided
#     pass
#
# # Reset simulation id from the command line
# try:
#     idx = sys.argv.index('-id')
#     simu_id = int(sys.argv[idx+1])
# except:  # No id specified
#     pass
#
# # Open output files
# fn_log = output_dir + 'log_simu_%d.log' % simu_id
# fn_simu = output_dir + 'simu_%d.csv' % simu_id
# f_log = open(fn_log, 'w') if do_log else None

# Loading source data
# -- TODO Low priority: loading only once for all simulation runs
chunked_data = pd.read_csv('src_data/cbg2cbg_revise.csv', chunksize=10000)
chunk_list = []
for chunk in chunked_data:
    chunk_list.append(chunk)
transport_data = pd.concat(chunk_list)

pop_data = pd.read_csv('src_data/usa_population_revise.csv', dtype=np.int64)
N = len(pop_data)
src_cbg_names = list(transport_data['poi_cbg_source'].unique())
n_src_CBG = len(src_cbg_names)

group_by_src = transport_data.groupby('poi_cbg_source')
group_by_des = transport_data.groupby('poi_cbg_destination')


# Initiate a counter
def initCounter():
    counter = pd.DataFrame(dtype=np.int64)
    counter['day'] = [0] * N
    counter['cbg'] = pop_data['GeoId'].copy()
    counter['susceptible'] = pop_data['Population'].copy()
    counter['infectious'] = [0] * N
    counter['recovered'] = [0] * N
    return counter


# Initiate the disease
def initCase(counter, new_case_nums, new_case_CBGs):
    if new_case_CBGs is None:
        new_case_CBGs = []
        for i in range(len(new_case_nums)):
            new_case_CBGs.append(src_cbg_names[random.randint(0, n_src_CBG - 1)])

    index = len(counter)
    active_cases = []  # list of [cbg, num_day]
    for case_num, case_cbg in zip(new_case_nums, new_case_CBGs):
        sus_num = counter[counter['cbg'] == case_cbg].iloc[-1]['susceptible']
        case_num = min(sus_num, case_num)

        counter.loc[index] = [1, case_cbg, sus_num - case_num, case_num, 0]
        index += 1

        for _ in range(case_num):
            active_cases.append([case_cbg, 0])

    return active_cases


# Iteration
def nextDay(counter, active_cases, current_day):
    # if (len(active_cases) == 0):
    #     if do_log: f_log.write('Day#%d no more active cases\n' % current_day)

    new_active_cases = []
    i = 0
    index = len(counter)
    while i < len(active_cases):
        src_cbg, num_day = active_cases[i]
        if random.random() < infection_chance_per_day[num_day]:
            des_cbg = get_random_des(group_by_src.get_group(src_cbg))
            rev_src_cbg = get_random_src(group_by_des.get_group(des_cbg))

            rev_src_cbg_count = counter[counter['cbg'] == rev_src_cbg].iloc[-1]
            if rev_src_cbg_count['susceptible'] == 0:
                # if do_log: f_log.write(
                #     'Day#%d %s try to infect %s, but full\n' % (current_day, active_cases[i], rev_src_cbg))
                pass
            else:  # activate a new case
                counter.loc[index] = [current_day, rev_src_cbg, rev_src_cbg_count['susceptible'] - 1,
                                      rev_src_cbg_count['infectious'] + 1, rev_src_cbg_count['recovered']]
                index += 1
                # collect new case
                new_active_cases.append([rev_src_cbg, 0])
                tot_case[0] += 1
                # if do_log: f_log.write('Day#%d %s infected %s\n' % (current_day, active_cases[i], rev_src_cbg))
        else:
            # if do_log: f_log.write('Day#%d %s causes nothing\n' % (current_day, active_cases[i]))
            pass

        active_cases[i][1] += 1
        if active_cases[i][1] == len(infection_chance_per_day):
            active_cases.pop(i)
            # one case recover
            src_cbg_count = counter[counter['cbg'] == src_cbg].iloc[-1]
            counter.loc[index] = [current_day, src_cbg, src_cbg_count['susceptible'], src_cbg_count['infectious'] - 1,
                                  src_cbg_count['recovered'] + 1]
            index += 1
        else:
            i += 1

        # print(i,len(active_cases))
    active_cases += new_active_cases


simu_counter = initCounter()
active_cases = initCase(simu_counter, num_init_cases, list_init_cbg)

start_time = time.time()
for i in range(2, days_of_simulation+2):
    nextDay(simu_counter, active_cases, i)
end_time = time.time()

print(f"Running time: {end_time-start_time:.4f} seconds for {days_of_simulation} days of simulation,"
      f" with {tot_case[0]} total cases")
# simu_counter.iloc[N:].to_csv(fn_simu, index=False)
