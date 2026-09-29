import pandas as pd
import os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITHUB_ROOT = os.path.dirname(os.path.dirname(base))

# code (chronicling-events / chronicling-sources) name -> corrected metadata-sheet name, for
# chronicles later re-dated; the metadata sheet is authoritative, but for two of the topic renames
# and none of the source renames it still carries the old, superseded row alongside the corrected one
TOPIC_RENAMES = {'1841_Zier_Bloo': '1851_Zier_Bloo', '1606_Gron_Anon': '1535_Gron_Anon', '1787_Gent_Anon': '1750_Gent_Anon'}
TOPIC_SUPERSEDED_ROWS = {'1606_Gron_Anon', '1787_Gent_Anon'}  # old-named rows still lingering in the sheet itself

SOURCE_RENAMES = {
    '1604_Bosc_Anon': '1609_Bosc_Anon', '1687_Rott_Waer': '1690_Rott_Anon',
    '1791_Purm_Louw': '1796_Purm_Louw', '1794_Hoor_Veli': '1838_Hoor_Anon',
    '1841_Zier_Bloo': '1851_Zier_Bloo',
    '1648_Rott_Waer': '1648_Rott_Anon', '1658_Rott_Waer': '1658_Rott_Anon',
    '1672_Amst_Wate': '1672_Amst_Anon', '1716_Jisp_anon': '1716_Jisp_Gert',
    '1745_Kort_Putt': '1745_Kort_Anon', '1793_Bred_anon': '1793_Bred_Ouko',
    '1643_Antw_anon': '1643_Antw_Bate', '1574_Antw_EykP': '1574_Antw_Ano2',
}

# --- real corpora, as actually used in analysis ---
events_set = set(pd.read_csv(
    f'{GITHUB_ROOT}/chronicling-events/output/primitives_230807/result_cv_topics_absolute.csv',
    sep=';', index_col=0)['call_nr_clean'].unique())
real_topic_corpus = {TOPIC_RENAMES.get(c, c) for c in events_set}
assert len(real_topic_corpus) == 126, f'expected 126, got {len(real_topic_corpus)}'

sources_clpl = pd.read_csv(f'{GITHUB_ROOT}/chronicling-sources/output/sources_clpl/sources_clpl_2022_del.csv', sep=';', index_col=0)
real_source_corpus_raw = set(sources_clpl['doc_author'].unique()) - {'1575_Antw_Ulle', '1602_Brus_Pott'}
real_source_corpus = {SOURCE_RENAMES.get(c, c) for c in real_source_corpus_raw}
assert len(real_source_corpus) == 64, f'expected 64, got {len(real_source_corpus)}'

# --- load full metadata sheet, add the one row missing entirely (1750_Brus_Anon, present only in
# the raw "Batch 4" sheet, never merged into "Alle kronieken") ---
corpus = pd.read_excel(f'{base}/Status definitieve corpus_2.xlsx', sheet_name='Alle kronieken')
batch4 = pd.read_excel(f'{base}/Status definitieve corpus_2.xlsx', sheet_name='Batch 4')
missing_row = batch4[batch4['Call Number'] == '1750_Brus_Anon'][['Call Number']].copy()
for col in corpus.columns:
    if col not in missing_row.columns:
        missing_row[col] = pd.NA
missing_row['Batch'] = 4
missing_row['Transcriptie klaar'] = 'Ja'
missing_row['Geannoteerd'] = 'Ja'
missing_row['Geannoteerd (bronnen van informatie)'] = 'nee'  # not part of the Source Corpus
corpus = pd.concat([corpus, missing_row], ignore_index=True)
corpus = corpus[corpus['Call Number'].isna() == False].reset_index(drop=True)

corpus['call_nr_clean'] = corpus['Call Number'].astype(str).str[:14]

# a row's own call_nr_clean is only "superseded" for Topic Corpus purposes if it's one of the two
# old-named rows still lingering in the sheet AND the corrected row also exists in the sheet
superseded_topic_mask = corpus['call_nr_clean'].isin(TOPIC_SUPERSEDED_ROWS)


def norm(s):
    # matches on the first-14-characters chronicle prefix, case-insensitively -- absorbs both the
    # volume-suffix (e.g. "..._04") and the stray capitalization differences found between the
    # code output and the metadata sheet
    return s[:14].lower()


real_topic_corpus_norm = {norm(c) for c in real_topic_corpus}
real_source_corpus_norm = {norm(c) for c in real_source_corpus}
TOPIC_RENAMES_NORM = {norm(k): norm(v) for k, v in TOPIC_RENAMES.items()}
SOURCE_RENAMES_NORM = {norm(k): norm(v) for k, v in SOURCE_RENAMES.items()}


def topic_corpus_final(row):
    if superseded_topic_mask.loc[row.name]:
        return 'Nee (superseded -- see corrected entry under the re-dated name)'
    key = norm(row['call_nr_clean'])
    canonical = TOPIC_RENAMES_NORM.get(key, key)
    return 'Ja' if canonical in real_topic_corpus_norm else 'Nee'


def source_corpus_final(row):
    key = norm(row['call_nr_clean'])
    canonical = SOURCE_RENAMES_NORM.get(key, key)
    return 'Ja' if canonical in real_source_corpus_norm else 'Nee'


corpus['Topic_Corpus_final'] = corpus.apply(topic_corpus_final, axis=1)
corpus['Source_Corpus_final'] = corpus.apply(source_corpus_final, axis=1)

n_topic = corpus.loc[corpus['Topic_Corpus_final'] == 'Ja', 'call_nr_clean'].nunique()
n_source = corpus.loc[corpus['Source_Corpus_final'] == 'Ja', 'call_nr_clean'].nunique()
print(f'Topic_Corpus_final == Ja: {n_topic} unique chronicles (target: 126)')
print(f'Source_Corpus_final == Ja: {n_source} unique chronicles (target: 64)')
assert n_topic == 126 and n_source == 64, 'reconciliation did not close -- do not save until this passes'

out_path = f'{base}/Status definitieve corpus_RECONCILED.xlsx'
with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
    corpus.to_excel(writer, sheet_name='Alle kronieken (reconciled)', index=False)
    notes = pd.DataFrame([
        {'chronicle (code/pre-correction name)': k, 'canonical name (metadata sheet)': v, 'applies to': 'Topic Corpus'}
        for k, v in TOPIC_RENAMES.items()
    ] + [
        {'chronicle (code/pre-correction name)': k, 'canonical name (metadata sheet)': v, 'applies to': 'Source Corpus'}
        for k, v in SOURCE_RENAMES.items()
    ])
    notes.to_excel(writer, sheet_name='Renames applied', index=False)
print(f'saved: {out_path}')
