import pandas as pd
import numpy as np

from tqdm import tqdm


# HELPER FUNCTIONS
# Get a CBG where the infected case will visit
def get_random_des(src_df,random):
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


# Get  a CBG where the nealy infected agent originally from
def get_random_src(des_df,random):
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


# Initiate a counter
def initCounter(pop_data, N):
    counter = pd.DataFrame(dtype=np.int64)
    counter['day'] = [0] * N
    counter['cbg'] = pop_data['GeoId'].copy()
    counter['susceptible'] = pop_data['Population'].copy()
    counter['infectious'] = [0] * N
    counter['recovered'] = [0] * N
    return counter


# Initiate from Airports (destinations)
def initCase_from_des(counter, new_case_nums, new_case_airports, airport_cbg, group_by_des, f_spread, random):
    if new_case_airports is None:
        random.shuffle(airport_cbg)
        new_case_airports = [airport_cbg[i] for i in range(min(len(new_case_nums), len(airport_cbg)))]

    init_cases = {}
    for case_num, case_airport_cbg in zip(new_case_nums, new_case_airports):
        for i in range(case_num):
            case_cbg = get_random_src(group_by_des.get_group(case_airport_cbg),random)
            if case_cbg not in init_cases:
                init_cases[case_cbg] = 0
            init_cases[case_cbg] += 1

    index = len(counter)
    active_cases = []  # list of [cbg, num_day, case_id]
    if f_spread is not None: f_spread.write('Day, From, To\n')  # Spreading Tree

    for cbg, cases in init_cases.items():
        sus_num = counter[counter['cbg'] == cbg].iloc[-1]['susceptible']
        counter.loc[index] = [1, cbg, sus_num - cases, cases, 0]
        index += 1

        for i in range(cases):
            case_id = '%012d-%d'%(cbg, i+1)
            active_cases.append([cbg, 0, case_id])
            if f_spread is not None: f_spread.write('1, SIMU, %s\n'%case_id)
    return active_cases


# Initiate the disease
def initCase_from_src(counter, new_case_nums, new_case_CBGs, src_cbg_names, f_spread, random):
    if new_case_CBGs is None:
        random.shuffle(src_cbg_names)
        new_case_CBGs = [src_cbg_names[i] for i in range(len(new_case_nums), len(src_cbg_names))]

    index = len(counter)
    active_cases = []  # list of [cbg, num_day, case_id]
    if f_spread is not None: f_spread.write('Day, From, To\n')  # Spreading Tree

    for case_num, case_cbg in zip(new_case_nums, new_case_CBGs):
        sus_num = counter[counter['cbg'] == case_cbg].iloc[-1]['susceptible']
        case_num = min(sus_num, case_num)

        counter.loc[index] = [1, case_cbg, sus_num - case_num, case_num, 0]
        index += 1

        for i in range(case_num):
            case_id = '%012d-%d'%(case_cbg, i+1)
            active_cases.append([case_cbg, 0, case_id])
            if f_spread is not None: f_spread.write('1, SIMU, %s\n'%case_id)

    return active_cases


# Iteration
def nextDay(counter, active_cases, current_day, group_by_src, group_by_des, infection_chance_per_day,\
            f_spread, f_log, random):
    if (len(active_cases) == 0):
        if f_log is not None: f_log.write('Day#%d no more active cases\n' % current_day)

    new_active_cases = []
    i = 0
    index = len(counter)
    while i < len(active_cases):
        src_cbg, num_day, src_case_id = active_cases[i]
        if random.random() < infection_chance_per_day[num_day]:
            des_cbg = get_random_des(group_by_src.get_group(src_cbg),random)
            rev_src_cbg = get_random_src(group_by_des.get_group(des_cbg),random)

            rev_src_cbg_count = counter[counter['cbg'] == rev_src_cbg].iloc[-1]
            if rev_src_cbg_count['susceptible'] == 0:
                if f_log is not None: f_log.write(
                    'Day#%d %s try to infect %s, but full\n' % (current_day, active_cases[i], rev_src_cbg))
            else:  # activate a new case
                num_infectious = rev_src_cbg_count['infectious'] + 1
                num_recovered = rev_src_cbg_count['recovered']
                counter.loc[index] = [current_day, rev_src_cbg, rev_src_cbg_count['susceptible'] - 1,
                                      num_infectious, num_recovered]
                index += 1

                # collect new case
                des_case_id = '%012d-%d'%(rev_src_cbg, num_infectious + num_recovered)
                new_active_cases.append([rev_src_cbg, 0, des_case_id])
                if f_log is not None: f_log.write(
                    'Day#%d %s infected %s\n' % (current_day, active_cases[i], rev_src_cbg))

                # update spreading tree
                if f_spread is not None: f_spread.write('%d, %s, %s\n'%(current_day, src_case_id, des_case_id))
        else:
            if f_log is not None: f_log.write('Day#%d %s causes nothing\n' % (current_day, active_cases[i]))

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


def main(days_of_simulation, num_init_cases, list_init_cbg, infection_chance_per_day,
         pop_data, from_airport, airport_cbg, src_cbg_names, group_by_src, group_by_des, fn_simu, fn_spread, fn_log, simu_id,random):
    f_spread = None if fn_spread is None else open(fn_spread%simu_id, 'w')
    f_log = None if fn_log is None else open(fn_log%simu_id, 'w')
    N = len(pop_data)
    simu_counter = initCounter(pop_data, N)
    if from_airport:
        active_cases = initCase_from_des(simu_counter, num_init_cases, list_init_cbg, airport_cbg, group_by_des, f_spread, random)
    else:
        active_cases = initCase_from_src(simu_counter, num_init_cases,list_init_cbg, src_cbg_names, f_spread, random)
    for i in tqdm(range(2, days_of_simulation + 1)):
        nextDay(simu_counter, active_cases, i, group_by_src, group_by_des, infection_chance_per_day, f_spread, f_log,random)
    simu_counter.iloc[N:].to_csv(fn_simu % simu_id, index=False)
    if f_log is not None: f_log.close()
    if f_spread is not None: f_spread.close()
