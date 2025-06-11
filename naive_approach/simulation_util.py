import numpy as np
import pandas as pd
import random
import time
from datetime import datetime
import sys

rand = None

def init_random_seed(seed):
    global rand
    rand = random.Random(seed)
    np.random.seed(seed)

def init_counter(pop_data):
    counter = {}
    total_infected_tracker = {}
    N = len(pop_data)
    for i in range(N):
        cbg = pop_data.loc[i,'GeoId']
        pop = int(pop_data.loc[i,'Population'])
        counter[cbg] = [pop, 0, 0] # S, I, R
        total_infected_tracker[cbg] = [pop, 0] # population, total infected
    return counter, total_infected_tracker

# Get a CBG where the infected case will visit
def get_random_des(src_df):
    randval = rand.random()
    cumprob = src_df['des_prob'].cumsum()
    sumprob = src_df['des_prob'].sum()
    if sumprob == 0: return
    randval *= sumprob
    checkprob = 0
    for des, prob in zip(src_df['poi_cbg_destination'], cumprob):
        if checkprob == prob:
            continue
        if randval < prob:
            return des
    return src_df.loc[-1, 'poi_cbg_destination']

# Get  a CBG where the nealy infected agent originally from
def get_random_src(des_df):
    randval = rand.random()
    cumprob = des_df['src_prob'].cumsum()
    sumprob = des_df['src_prob'].sum()
    if sumprob == 0: return
    randval *= sumprob
    checkprob = 0
    for src, prob in zip(des_df['poi_cbg_source'], cumprob):
        if checkprob == prob:
            continue
        if randval < prob:
            return src
    return des_df.loc[-1, 'poi_cbg_source']


def init_spread_from_des(pop_data, starts, num_init_cases, infectious_day, f_region, f_case):
    active_case = {}
    counter,total_case_tracker = init_counter(pop_data)
    region_level_output_str = 'Day,GeoId,Susceptible,Infectious,Recovered\n'
    case_level_output_str = 'Day,from_GeoId,from_case,to_GeoId,to_case\n'
    simulation_day = 0

    # random initiate spread in 5 regions
    for idx, s in enumerate(starts):
        num_init_cases_refine = min(counter[s][0], num_init_cases[idx])
        active_case[s] = [[0] * infectious_day, [0] * infectious_day] # [case/day, idx/day]
        active_case[s][0][0] = num_init_cases_refine
        counter[s][0] -= num_init_cases_refine
        counter[s][1] += num_init_cases_refine
        total_case_tracker[s][1] += num_init_cases_refine
        # region level output update
        # header: Day, GeoId, Susceptible, Infectious, Recovered
        region_level_output_str += '%d,%s,%d,%d,%d\n'%(simulation_day, s, counter[s][0], counter[s][1], counter[s][2])

        # case level output update
        # header: Day, from_GeoId, from_case, to_GeoId, to_case
        # simulation initialed: 000..0, -1
        simu_GeoId = '0' * len(s)
        for i in range(num_init_cases_refine):
            case_level_output_str += '%d,%s,%d,%s,%d\n'%(simulation_day,simu_GeoId, -1, s, i)

    if f_region is not None:
        f_region.write(region_level_output_str)

    if f_case is not None:
        f_case.write(case_level_output_str)

    return active_case, counter, total_case_tracker

def init_spread_from_src(pop_data, starts, num_init_cases, infectious_day, group_by_src, f_region, f_case):
    active_case = {}
    counter,total_case_tracker = init_counter(pop_data)
    region_level_output_str = 'Day,GeoId,Susceptible,Infectious,Recovered\n'
    case_level_output_str = 'Day,from_GeoId,from_case,to_GeoId,to_case\n'
    simulation_day = 0

    # random initiate spread in 5 regions
    init_case = {}
    for idx, s in enumerate(starts):
        num_init_case_s = num_init_cases[idx]
        src_df = group_by_src.get_group(s)
        for _ in range(num_init_case_s):
            des_cbg = get_random_des(src_df)
            if total_case_tracker[des_cbg][1] == total_case_tracker[des_cbg][0]: continue
            if des_cbg not in init_case: init_case[des_cbg] = 0
            init_case[des_cbg] += 1
            total_case_tracker[des_cbg][1] += 1
            counter[des_cbg][0] -= 1
            counter[des_cbg][1] += 1

    for cbg, case in init_case.items():
        active_case[cbg] = [[0] * infectious_day, [0] * infectious_day]
        active_case[cbg][0][0] = case

        region_level_output_str += '%d,%s,%d,%d,%d\n'%(simulation_day, cbg, counter[cbg][0], counter[cbg][1], counter[cbg][2])

        # case level output update
        # header: Day, from_GeoId, from_case, to_GeoId, to_case
        # simulation initialed: 000..0, -1
        simu_GeoId = '0' * len(cbg)
        for i in range(case):
            case_level_output_str += '%d,%s,%d,%s,%d\n'%(simulation_day,simu_GeoId, -1, cbg, i)

    if f_region is not None:
        f_region.write(region_level_output_str)

    if f_case is not None:
        f_case.write(case_level_output_str)

    return active_case, counter, total_case_tracker

def next_day(simulation_day, active_case, counter, total_case_tracker, group_by_des, group_by_src, infectious_day, infectious_rate, f_region, f_case):
    region_level_output_str = ''
    case_level_output_str = ''
    recovered_cases = {}
    new_cases = {}

    for cbg in list(active_case.keys()):
        cbg_des_df = group_by_src.get_group(cbg)
        cbg_active_case = active_case[cbg][0]
        cbg_case_idx_lower = active_case[cbg][1]
        cbg_active_case_num = 0

        for d in range(infectious_day-1, -1, -1):

            num_infectious = cbg_active_case[d]
            current_case_idx = cbg_case_idx_lower[d]
            cbg_active_case_num += num_infectious

            # collect recovered cases
            if d == infectious_day-1:
                if num_infectious != 0: recovered_cases[cbg] = num_infectious

            # update active case tracker
            if d != 0:
                cbg_active_case[d] = cbg_active_case[d-1]
                cbg_case_idx_lower[d] = cbg_case_idx_lower[d-1]
            else:
                cbg_active_case[d] = 0
                if cbg_active_case_num == 0: # remove the cbg from the active case tracker
                    del active_case[cbg]

            # Skip when no active case
            if num_infectious == 0: continue

            for idx in range(num_infectious):
                if rand.random() < infectious_rate[d]:
                    transec_cbg = get_random_des(cbg_des_df)
                    des_cbg = get_random_src(group_by_des.get_group(transec_cbg))
                    reduce_prob = total_case_tracker[des_cbg][1]/total_case_tracker[des_cbg][0]
                    if counter[des_cbg][0] == 0 or rand.random() < reduce_prob: continue # Assume spread to an already infected person
                    if des_cbg not in new_cases: new_cases[des_cbg] = 0
                    new_cases[des_cbg] += 1
                    total_case_tracker[des_cbg][1] += 1
                    counter[des_cbg][0] -= 1
                    counter[des_cbg][1] += 1

                    # update case level output
                    case_level_output_str += '%d,%s,%d,%s,%d\n'%(simulation_day, cbg, idx+current_case_idx, des_cbg, total_case_tracker[des_cbg][1]-1)


    # Spread finished
    # Update active case tracker
    for des_cbg, des_case in new_cases.items():
        if des_cbg not in active_case:
            active_case[des_cbg] = [[0] * infectious_day, [0] * infectious_day]
        active_case[des_cbg][0][0] = des_case
        active_case[des_cbg][1][0] = total_case_tracker[des_cbg][1] - des_case

        # Update region level output with new cases
        region_level_output_str += '%d,%s,%d,%d,%d\n'%(simulation_day, des_cbg, counter[des_cbg][0], counter[des_cbg][1], counter[des_cbg][2])

    # Update counter with recovered cases
    for cbg, case in recovered_cases.items():
        counter[cbg][1] -= case
        counter[cbg][2] += case

        # Update region level output with recovered cases
        region_level_output_str += '%d,%s,%d,%d,%d\n'%(simulation_day, cbg, counter[cbg][0], counter[cbg][1], counter[cbg][2])


    if f_region is not None:
        f_region.write(region_level_output_str)
    if f_case is not None:
        f_case.write(case_level_output_str)

    return region_level_output_str, case_level_output_str

def main(days_of_simulation, init_cbgs, num_init_cases, infection_chance_per_day, from_des, pop_data, group_by_des, group_by_src, fn_region, fn_case, simu_id, seed):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Simu #{simu_id} start.")
    start_time = time.time()
    init_random_seed(seed)
    f_region = open(fn_region%simu_id, 'w') if fn_region is not None else None
    f_case = open(fn_case%simu_id, 'w') if fn_case is not None else None
    infectious_day = len(infection_chance_per_day)
    if from_des:
        active_case, counter, total_case_tracker = init_spread_from_des(pop_data, init_cbgs, num_init_cases, infectious_day, f_region, f_case)
    else:
        active_case, counter, total_case_tracker = init_spread_from_src(pop_data, init_cbgs, num_init_cases, infectious_day, group_by_des, f_region, f_case)
    for simu_day in range(days_of_simulation):
        next_day(simu_day+1, active_case, counter, total_case_tracker, group_by_des, group_by_src, infectious_day, infection_chance_per_day, f_region, f_case)
    if f_region is not None: f_region.close()
    if f_case is not None: f_case.close()
    end_time = time.time()
    tot_case = 0
    tot_cbg = 0
    for cbg in total_case_tracker.keys():
        tot_case += total_case_tracker[cbg][1]
        if total_case_tracker[cbg][1] != 0: tot_cbg += 1
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Simu #{simu_id} finish.",
          f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]    -- Running time: {end_time-start_time:.4f} seconds for {days_of_simulation} days of simulation,"
          f" with {tot_case} total cases among {tot_cbg} regions.")