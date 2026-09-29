import pandas as pd
import numpy as np
import ndjson
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f'{os.path.dirname(base)}/figures'
EVENTS_BASE = '/Users/alielassche/Documenten/GitHub/chronicling-events'

for _font_path in [
    os.path.expanduser("~/Library/Fonts/RobotoCondensed-Regular.ttf"),
    os.path.expanduser("~/Library/Fonts/RobotoCondensed-Bold.ttf"),
]:
    fm.fontManager.addfont(_font_path)

plt.rcParams['font.size'] = 11
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = 'Roboto Condensed'

SHORT_SPAN_THRESHOLD = 100  # years; a described period this short or shorter plausibly fits one
                             # chronicler's own lifetime, so a missing contemporain_begin_integer is
                             # treated as "no retrospective gap" rather than "not yet coded"

# --- Topic Corpus membership (mirrors count_chronicles.ipynb: Geannoteerd == 'Ja') ---
corpus = pd.read_excel(f'{base}/Status definitieve corpus_2.xlsx', sheet_name='Alle kronieken')
corpus = corpus[['Batch', 'Call Number', 'Transcriptie klaar', 'Geannoteerd']]
corpus = corpus[corpus['Call Number'].isna() == False]
corpus = corpus[corpus['Transcriptie klaar'].isin(['Ja', 'n.v.t.'])]
corpus['call_nr_clean'] = corpus['Call Number'].str[:14]
topic_corpus_set = set(corpus.loc[corpus['Geannoteerd'] == 'Ja', 'call_nr_clean'].unique())
# 1841_Zier_Bloo in the fragment data is 1851_Zier_Bloo in the Topic Corpus list -- a known rename
# (established earlier in this project), not a genuine exclusion
RENAME_ALIASES = {'1841_Zier_Bloo': '1851_Zier_Bloo'}

# --- per-chronicle classification of when contemporary (eyewitness) writing began ---
meta = pd.read_excel(f'{base}/Chronicles_metadata.xlsx', sheet_name='Chronicles')
meta['contemporain_begin_integer'] = pd.to_numeric(meta['contemporain_begin_integer'], errors='coerce')
meta['span'] = meta['described_period_end'] - meta['described_period_begin']

meta['effective_begin'] = meta['contemporain_begin_integer']
short_missing = meta['contemporain_begin_integer'].isna() & (meta['span'] <= SHORT_SPAN_THRESHOLD)
meta.loc[short_missing, 'effective_begin'] = meta.loc[short_missing, 'described_period_begin']
# remaining NaNs (long span but uncoded, or no metadata at all) are treated as fully contemporary --
# i.e. their described_period_begin doubles as effective_begin, so none of their content is flagged
# retrospective. A deliberate simplifying assumption, not a data-backed classification for these chronicles.

meta_lookup = meta.set_index('Call_Number')['effective_begin']

# --- all dated, token-counted fragments ---
with open(f'{EVENTS_BASE}/output/primitives_230807/primitives_corrected_monthly_clean.ndjson') as f:
    frags = ndjson.load(f)
frag_df = pd.DataFrame(frags)
frag_df['frag_year'] = pd.to_numeric(frag_df['clean_month'].str[:4], errors='coerce')
frag_df = frag_df[frag_df['frag_year'] <= 1900]  # drops 29 fragments (of 85,680) with clearly erroneous parsed dates

frag_df['call_nr_clean'] = frag_df['call_nr_clean'].replace(RENAME_ALIASES)
n_before_filter = frag_df['call_nr_clean'].nunique()
frag_df = frag_df[frag_df['call_nr_clean'].isin(topic_corpus_set)]
print(f'restricted to Topic Corpus: {n_before_filter} -> {frag_df["call_nr_clean"].nunique()} chronicles')

frag_df['effective_begin'] = frag_df['call_nr_clean'].map(meta_lookup)
n_assumed_contemporary = frag_df.loc[frag_df['effective_begin'].isna(), 'call_nr_clean'].nunique()
frag_df['effective_begin'] = frag_df['effective_begin'].fillna(frag_df['frag_year'])  # assumed contemporary: never retrospective
frag_df['is_retrospective'] = frag_df['frag_year'] < frag_df['effective_begin']

n_total_chronicles = frag_df['call_nr_clean'].nunique()
print(f'chronicles with fragment data: {n_total_chronicles} '
      f'({n_total_chronicles - n_assumed_contemporary} classified via metadata, '
      f'{n_assumed_contemporary} assumed fully contemporary)')

# --- bin by described year, matching this corpus's 25-year convention, starting at 1475 ---
frag_df = frag_df[frag_df['frag_year'] >= 1475]
bin_edges = list(np.arange(1475, 1925, 25))
frag_df['cut'] = pd.cut(frag_df['frag_year'], bin_edges)

per_bin = frag_df.groupby('cut', observed=True).agg(
    total_tokens=('n_tokens', 'sum'),
    retrospective_tokens=('n_tokens', lambda s: s[frag_df.loc[s.index, 'is_retrospective']].sum()),
).reset_index()
per_bin['retro_share'] = np.where(per_bin['total_tokens'] > 0,
                                   per_bin['retrospective_tokens'] / per_bin['total_tokens'] * 100, np.nan)

per_bin['label'] = [f'{int(iv.left)}–{int(iv.right)}' for iv in per_bin['cut']]

fig, ax2 = plt.subplots(figsize=(7, 4))
x = np.arange(len(per_bin))

ax2.bar(x, per_bin['retro_share'], width=0.6, color='#333D29', zorder=3)
ax2.set_title('Retrospective share of content in Topic Corpus', fontweight='bold', fontsize=13, loc='left', pad=12)
ax2.set_ylabel('retrospective tokens (%)')
ax2.set_ylim(0, 100)

ax2.set_xlabel('')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.spines['bottom'].set_color('#999999')
ax2.tick_params(axis='both', length=0, colors='#555555')
ax2.yaxis.grid(True, color='#E5E5E5', linewidth=0.8, zorder=0)
ax2.set_axisbelow(True)

ax2.set_xticks(x)
ax2.set_xticklabels(labels=per_bin['label'], rotation=45, ha='right', rotation_mode='anchor')

plt.savefig(f'{OUT}/retrospective_tokens_per_year.pdf', bbox_inches='tight')
plt.close(fig)
print('ok: retrospective_tokens_per_year.pdf')
print(per_bin[['label', 'total_tokens', 'retrospective_tokens', 'retro_share']].to_string())
