import pandas as pd


chunked_data = pd.read_csv('src_data/cbg2cbg_revise.csv', chunksize=100000)
chunk_list = []
for chunk in chunked_data:
    chunk_list.append(chunk)
transport_data = pd.concat(chunk_list)
group_by_src = transport_data.groupby('poi_cbg_source')
group_by_des = transport_data.groupby('poi_cbg_destination')

def cal_spread_probs(src_cbg_df):
    probs = {}
    des_cbgs = list(src_cbg_df['poi_cbg_destination'])
    des_probs = list(src_cbg_df['des_prob'])
    src_cbg = src_cbg_df['poi_cbg_source'].iloc[0]
    for des_cbg, des_prob in zip(des_cbgs, des_probs):
        des_prob_df = group_by_des.get_group(des_cbg)
        rev_src_cbg = list(des_prob_df['poi_cbg_source'])
        rev_src_prob = list(des_prob_df['src_prob'])
        for c,p in zip(rev_src_cbg,rev_src_prob):
            if c not in probs: probs[c] = 0
            probs[c] += des_prob * p

    probs = pd.DataFrame(probs.items(), columns = ['to', 'prob'])
    probs['from'] = len(probs) * [src_cbg]
    probs = probs[['from', 'to', 'prob']]
    return probs

results = group_by_src[transport_data.columns.tolist()].apply(cal_spread_probs).reset_index(drop=True)

results.to_csv('src_data/spread_probability.csv', index=False)