import pandas as pd
import numpy as np
import random
import os
import time
import sys

# load source data
chunked_data = pd.read_csv('src_data/cbg2cbg_revise.csv', chunksize=100000)
chunk_list = []
for chunk in chunked_data:
    chunk_list.append(chunk)
transport_data = pd.concat(chunk_list)

pop_data = pd.read_csv('src_data/usa_population_revise.csv', dtype = int)
infection_chance_per_day=[0.2,0.3,0.2,0.1,0.1,0.1,0.1,0.1]
src_cbg_names = list(transport_data['poi_cbg_source'].unique())
n_src_CBG = len(src_cbg_names)

group_by_src = transport_data.groupby('poi_cbg_source')
group_by_des = transport_data.groupby('poi_cbg_destination')

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
    return src_df.loc[-1,'poi_cbg_destination']

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
    return des_df.loc[-1,'poi_cbg_source']

def initCounter():
    counter = pd.DataFrame()
    N =  len(pop_data)
    counter['day'] = [0] * N
    counter['cbg'] = pop_data['GeoId'].copy()
    counter['susceptible'] = pop_data['Population'].copy()
    counter['infectious'] = [0] * N
    counter['recovered'] = [0] * N
    return counter

def initCase(counter, new_case_nums = [1], new_case_CBGs = None):
    if new_case_CBGs is None:
        new_case_CBGs = []
        for i in range(len(new_case_nums)):
            new_case_CBGs.append(src_cbg_names[random.randint(0,n_src_CBG-1)])

    index = len(counter)
    active_cases = [] # list of [cbg, numday]
    for case_num, case_cbg in zip(new_case_nums,new_case_CBGs):
        sus_num = counter[counter['cbg'] == case_cbg].iloc[-1]['susceptible']
        case_num = min(sus_num,case_num)

        counter.loc[index] = [1, case_cbg, sus_num-case_num, case_num, 0]
        index += 1

        for _ in range(case_num):
            active_cases.append([case_cbg,0])

    return active_cases

def nextDay(counter, active_cases, current_day, log = False):
    if (len(active_cases)==0 and log):
        print('Day#%d no more active cases'%current_day)

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
                if log: print('Day#%d %s try to infect %s, but full'%(current_day,active_cases[i],rev_src_cbg))
            else: # activate a new case
                counter.loc[index] = [current_day, rev_src_cbg, rev_src_cbg_count['susceptible']-1, rev_src_cbg_count['infectious']+1, rev_src_cbg_count['recovered']]
                index += 1
                # collect new case
                new_active_cases.append([rev_src_cbg, 0])
                if log: print('Day#%d %s infected %s'%(current_day,active_cases[i],rev_src_cbg))
        else:
            if log: print('Day#%d %s causes nothing'%(current_day,active_cases[i]))

        active_cases[i][1] += 1
        if active_cases[i][1] == len(infection_chance_per_day):
            active_cases.pop(i)
            # one case recover
            src_cbg_count = counter[counter['cbg'] == src_cbg].iloc[-1]
            counter.loc[index] = [current_day, src_cbg, src_cbg_count['susceptible'], src_cbg_count['infectious']-1, src_cbg_count['recovered']+1]
            index += 1
        else:
            i += 1

        # print(i,len(active_cases))
    active_cases += new_active_cases
    return len(new_active_cases)

if __name__ == '__main__':
    log = False
    num_rum = 1
    num_cbg = 1
    num_cases = 10
    output_file = 'res'
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-log':
            log = True
        if sys.argv[i] == '-run':
            num_rum = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == '-cbg':
            num_cbg = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == '-cases':
            num_cases = int(sys.argv[i+1])
            i += 1
    output_file = 'res_%d_%d'%(num_cbg, num_cases)

    fout = open(output_file, 'w')
    fout.close()
    for i in range(num_rum):
        fout = open(output_file,'a')
        start = time.time()
        simu_counter = initCounter()
        active_cases = initCase(simu_counter, [num_cases] * num_cbg)
        total_cases = len(active_cases)
        for i in range (2,90):
            total_cases += nextDay(simu_counter,active_cases,i)
        end = time.time()
        fout.write('%d %.4f\n'%(total_cases,end-start))
        fout.close()
        del simu_counter
        active_cases.clear()
        time.sleep(0.1)