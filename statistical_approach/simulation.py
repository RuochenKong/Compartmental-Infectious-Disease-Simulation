import numpy as np
import pandas as pd
import random
import time

random.seed(42)
np.random.seed(42)

num_init_cases = 100
infectious_rate = [0.1,0.2,0.3,0.3,0.2,0.1,0.1]
infectious_day = len(infectious_rate)

spread_prob_df = pd.concat([pd.read_csv('../spread_probability_top30/%d.csv'%i) for i in range(1,5)],ignore_index=True)
spread_prob_df['from'] = spread_prob_df['from'].apply(lambda x: '%012d'%x)
spread_prob_df['to'] = spread_prob_df['to'].apply(lambda x: '%012d'%x)
spread_prob_df = spread_prob_df[['from', 'to', 'prob']].reset_index(drop = True)
spread_prob_grouped_df = spread_prob_df.groupby('from')
pop_data = pd.read_csv('../src_data/usa_population_revise.csv', dtype ={'GeoId':str, 'Population':np.int64})

def init_counter():
    counter = {}
    total_infected_tracker = {}
    N = len(pop_data)
    for i in range(N):
        cbg = pop_data.loc[i,'GeoId']
        pop = int(pop_data.loc[i,'Population'])
        counter[cbg] = [pop, 0, 0] # S, I, R
        total_infected_tracker[cbg] = [pop, 0] # population, total infected
    return counter, total_infected_tracker

def get_random_des(des_prob_df):
    rand_val = random.random()
    cumprob = des_prob_df['prob'].cumsum()
    for des, prob in zip(des_prob_df['to'], cumprob):
        if rand_val < prob: return des
    return des_prob_df.loc[-1,'to']

starts = ['250092524002', '361190111013', '270530257013', '360650228002', '261635154001']
active_case = {}
counter,total_case_tracker = init_counter()
region_level_output_str = 'Day,GeoId,Susceptible,Infectious,Recovered\n'
case_level_output_str = 'Day,from_GeoId,from_case,to_GeoId,to_case\n'
simulation_day = 0
# random initiate spread in 5 regions
for s in starts:
    num_init_cases_refine = min(counter[s][0], num_init_cases)
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


def next_day(simulation_day):
    region_level_output_str = ''
    case_level_output_str = ''
    recovered_cases = {}
    new_cases = {}
    for cbg in list(active_case.keys()):

        des_prob_df = spread_prob_grouped_df.get_group(cbg)
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

            # calculate the number of expected new cases in infectious day 'd'
            expected_new_case = num_infectious * infectious_rate[d]

            new_case_by_day = {}
            actual_new_case = 0
            if expected_new_case < 30:
                if num_infectious < 30: # naive approach
                    for idx in range(num_infectious):
                        if random.random() < infectious_rate[d]:
                            des_cbg = get_random_des(des_prob_df)
                            reduce_prob = total_case_tracker[des_cbg][1]/total_case_tracker[des_cbg][0]
                            if counter[des_cbg][0] == 0 or random.random() < reduce_prob: continue # Assume spread to an already infected person
                            if des_cbg not in new_cases: new_cases[des_cbg] = 0
                            new_cases[des_cbg] += 1
                            total_case_tracker[des_cbg][1] += 1
                            counter[des_cbg][0] -= 1
                            counter[des_cbg][1] += 1

                            # update case level output
                            case_level_output_str += '%d,%s,%d,%s,%d\n'%(simulation_day, cbg, idx+current_case_idx, des_cbg, total_case_tracker[des_cbg][1]-1)

                else: # normal distribution on number of new cases, then naive approach for destinations
                    actual_new_case = np.random.normal(expected_new_case, expected_new_case * (1-infectious_rate[d]))
                    actual_new_case = max(0,int(actual_new_case))
                    failed_spread = 0
                    for _ in range(actual_new_case):
                        des_cbg = get_random_des(des_prob_df)
                        reduce_prob = total_case_tracker[des_cbg][1]/total_case_tracker[des_cbg][0]
                        if counter[des_cbg][0] == 0 or random.random() < reduce_prob: # Assume spread to an already infected person
                            failed_spread += 1
                            continue
                        if des_cbg not in new_case_by_day:
                            new_case_by_day[des_cbg] = 0
                        new_case_by_day[des_cbg] += 1
                        total_case_tracker[des_cbg][1] += 1
                        counter[des_cbg][0] -= 1
                        counter[des_cbg][1] += 1
                    actual_new_case -= failed_spread

            else: # calculate the expected number of new cases, then use normal/Poisson distribution for destinations
                for des_idx in des_prob_df.index:
                    des_cbg = des_prob_df.loc[des_idx,'to']
                    des_susceptible = counter[des_cbg][0]
                    if des_susceptible == 0: continue # No susceptible population

                    des_prob = des_prob_df.loc[des_idx,'prob']
                    reduce_prob = total_case_tracker[des_cbg][1]/total_case_tracker[des_cbg][0]
                    expected_new_case_in_des = expected_new_case * des_prob * (1-reduce_prob)

                    if expected_new_case_in_des < 5: # Poisson distribution
                        actual_new_case_in_des = np.random.poisson(expected_new_case_in_des)
                    else: # Normal distribution
                        actual_new_case_in_des = np.random.normal(expected_new_case_in_des, expected_new_case_in_des* (1-des_prob))
                        actual_new_case_in_des = max(0,int(actual_new_case_in_des))
                    actual_new_case_in_des = min(des_susceptible, actual_new_case_in_des)
                    if actual_new_case_in_des == 0: continue # No spread happens

                    actual_new_case += actual_new_case_in_des
                    if des_cbg not in new_case_by_day:
                        new_case_by_day[des_cbg] = 0
                    new_case_by_day[des_cbg] += actual_new_case_in_des
                    total_case_tracker[des_cbg][1] += actual_new_case_in_des
                    counter[des_cbg][0] -= actual_new_case_in_des
                    counter[des_cbg][1] += actual_new_case_in_des

            sidx = 0
            src_case_idx = np.random.choice(num_infectious, size = actual_new_case, replace = False) + current_case_idx if actual_new_case else None
            for des_cbg, des_case in new_case_by_day.items(): # Update new case counter
                if des_cbg not in new_cases: new_cases[des_cbg] = 0
                new_cases[des_cbg] += des_case
                # Update case level output
                if actual_new_case == 0: continue # Skip for naive approach
                des_start_idx = total_case_tracker[des_cbg][1] - des_case
                for des_idx in range(des_case):
                    case_level_output_str += '%d,%s,%d,%s,%d\n'%(simulation_day,cbg,src_case_idx[sidx],des_cbg,des_start_idx+des_idx)
                    sidx += 1

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

    return region_level_output_str, case_level_output_str

days_of_simulation = 180
start_time = time.time()
for day in range(180):
    next_day(day+1)
end_time = time.time()
tot_case = 0
for cbg in total_case_tracker.keys():
    tot_case += total_case_tracker[cbg][1]
print(f"Running time: {end_time-start_time:.4f} seconds for {days_of_simulation} days of simulation,"
      f" with {tot_case} total cases")
