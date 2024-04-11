# %%
import ndjson
import numpy as np
import pandas as pd
import sys
from top2vec import Top2Vec
from tqdm import tqdm

# %%
#load model
model = Top2Vec.load('name-model')

# load primitives
with open('../data/primitives_corrected_monthly_clean.ndjson') as f: # of primitives_annotated
    data = ndjson.load(f)

# filter events longer than 50 characters, and without date
data_filtered = []
for item in data:
    if item['len_text'] > 50:
        if item['len_text'] <= 5000:
            if isinstance(item['date'],list):
                if len(item['date']) > 0:
                    data_filtered.append(item)

#%%
#select most dominant topic per document
rows = []

for item in tqdm(data_filtered, total=len(data_filtered)):
    d_dict = {}
    d_dict['doc_id'] = item['id']
    d_dict['clean_month'] = item['clean_month']
    d_dict['call_nr_clean'] = item['call_nr_clean']
    for i in range(0,5):
        d_dict[f'topic_id_{i}'] = model.get_documents_topics([item['id']], num_topics=5)[0][0][i]
        d_dict[f'topic_score_{i}'] = model.get_documents_topics([item['id']], num_topics=5)[1][0][i]
    rows.append(d_dict)
    
dfje = pd.DataFrame(rows)
#%%
#save
with open('../data/primitive_topic_top5.ndjson', 'w') as fout:
	ndjson.dump(dfje.to_dict('records'), fout)

#%%
#groupby and save
dfje.groupby(['call_nr_clean', 'topic_id_0'])['topic_id_0'].count().to_csv('../models/230807/call_nr_topic_id.csv')
dfje.groupby(['topic_id_0', 'call_nr_clean'])['call_nr_clean'].count().to_csv('../models/230807/topic_id_call_nr.csv')

#%%
#find and save all cossims per document
rows = []

for item in tqdm(data_filtered, total=len(data_filtered)):
    d_dict = {}
    d_dict['doc_id'] = item['id']
    d_dict['clean_month'] = item['clean_month']
    d_dict['call_nr_clean'] = item['call_nr_clean']
    a, b, c, d = model.get_documents_topics([d_dict['doc_id']], reduced=False, num_topics=436)
    sorted_indices = np.argsort(a)
    d_dict['cossims'] = b[0, sorted_indices][0]
    rows.append(d_dict)
    
df = pd.DataFrame(rows)
split_df = pd.DataFrame(df['cossims'].tolist())
df2 = pd.concat([df, split_df], axis=1).drop(columns=['cossims'])

with open('../data/cossims_corrected.ndjson', 'w') as fout:
	ndjson.dump(df2.to_dict('records'), fout)
# %%
