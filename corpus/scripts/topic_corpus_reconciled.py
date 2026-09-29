import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f'{os.path.dirname(base)}/figures'

for _font_path in [
    os.path.expanduser("~/Library/Fonts/RobotoCondensed-Regular.ttf"),
    os.path.expanduser("~/Library/Fonts/RobotoCondensed-Bold.ttf"),
]:
    fm.fontManager.addfont(_font_path)

plt.rcParams['font.size'] = 11
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = 'Roboto Condensed'

# the code (chronicling-events) was built against pre-correction end dates for these three;
# the metadata sheet has since been corrected -- map the code's names to the corrected ones
RENAME_ALIASES = {'1841_Zier_Bloo': '1851_Zier_Bloo', '1606_Gron_Anon': '1535_Gron_Anon', '1787_Gent_Anon': '1750_Gent_Anon'}

# --- the real Topic Corpus: exactly the 126 chronicles actually used in the topic-modeling analysis ---
GITHUB_ROOT = os.path.dirname(os.path.dirname(base))
events_set = set(pd.read_csv(
    f'{GITHUB_ROOT}/chronicling-events/output/primitives_230807/result_cv_topics_absolute.csv',
    sep=';', index_col=0)['call_nr_clean'].unique())
real_topic_corpus = {RENAME_ALIASES.get(c, c) for c in events_set}
print(f'real Topic Corpus: {len(real_topic_corpus)} chronicles')

# --- volumes: from the metadata sheet, plus the one chronicle (1750_Brus_Anon) missing from the
# consolidated "Alle kronieken" sheet but present in the raw "Batch 4" sheet ---
corpus = pd.read_excel(f'{base}/Status definitieve corpus_2.xlsx', sheet_name='Alle kronieken')
corpus = corpus[['Batch', 'Call Number', 'Transcriptie klaar', 'Geannoteerd']]
corpus = corpus[corpus['Call Number'].isna() == False]
corpus = corpus[corpus['Transcriptie klaar'].isin(['Ja', 'n.v.t.'])]

batch4 = pd.read_excel(f'{base}/Status definitieve corpus_2.xlsx', sheet_name='Batch 4')
missing_row = batch4[batch4['Call Number'] == '1750_Brus_Anon'][['Call Number']].copy()
missing_row['Batch'] = 4
missing_row['Transcriptie klaar'] = 'Ja'
missing_row['Geannoteerd'] = 'Ja'
corpus = pd.concat([corpus, missing_row], ignore_index=True)

corpus['call_nr_clean'] = corpus['Call Number'].str[:14]
corpus['call_nr_clean'] = corpus['call_nr_clean'].replace(RENAME_ALIASES)
corpus['year'] = corpus['call_nr_clean'].str[:4].astype(int)
corpus['cut'] = pd.cut(corpus['year'], np.arange(1475, 1925, 25))
corpus['cut'] = corpus['cut'].astype(str).str[1:-1].str.replace(', ', '–')

corpus_topic = corpus[corpus['call_nr_clean'].isin(real_topic_corpus)]
n_chronicles_found = corpus_topic['call_nr_clean'].nunique()
print(f'chronicles matched in metadata sheet (incl. Batch 4 addition): {n_chronicles_found} / {len(real_topic_corpus)}')
missing = real_topic_corpus - set(corpus_topic['call_nr_clean'])
if missing:
    print(f'WARNING -- still missing from metadata sheet entirely: {sorted(missing)}')

df_topic = corpus_topic.groupby('cut')[['Call Number', 'call_nr_clean']].nunique().reset_index()
n_volumes = corpus_topic['Call Number'].nunique()
print(f'total volumes: {n_volumes}')

# --- tokens: events_grouped.csv (XML full-text token counts) covers the real Topic Corpus completely
# once the same three renames are applied; it also carries one extra chronicle (1820_Rhen_Vree) that
# is not part of the real 126 and is dropped here ---
tokens_df = pd.read_csv(f'{base}/events_grouped.csv', index_col=0)
tokens_df['call_nr_clean'] = tokens_df['call_nr_clean'].replace(RENAME_ALIASES)
tokens_df = tokens_df[tokens_df['call_nr_clean'].isin(real_topic_corpus)]
missing_tokens = real_topic_corpus - set(tokens_df['call_nr_clean'])
print(f'chronicles with token data: {tokens_df["call_nr_clean"].nunique()} / {len(real_topic_corpus)} '
      f'(missing: {sorted(missing_tokens) if missing_tokens else "none"})')
print(f'total tokens: {tokens_df["tokens"].sum():,}')

# === figure: same style as the original topic_corpus_chronicles.pdf ===
fig, axs = plt.subplots(figsize=(7, 4))
x = np.arange(len(df_topic))

axs.bar(x, df_topic['Call Number'], width=0.6, color='#C2C5AA', zorder=3)
axs.bar(x, df_topic['call_nr_clean'], width=0.3, color='#333D29', zorder=3)

axs.set_title('Topic Corpus', fontweight='bold', fontsize=13, loc='left', pad=12)
axs.set_ylabel('number of documents')
axs.set_xlabel('')
axs.set_xticks(x)
axs.set_xticklabels(labels=df_topic['cut'], rotation=45, ha='right', rotation_mode='anchor')

axs.spines['top'].set_visible(False)
axs.spines['right'].set_visible(False)
axs.spines['left'].set_visible(False)
axs.spines['bottom'].set_color('#999999')
axs.tick_params(axis='both', length=0, colors='#555555')

axs.yaxis.grid(True, color='#E5E5E5', linewidth=0.8, zorder=0)
axs.set_axisbelow(True)

axs.legend(['chronicle volumes', 'chronicles'], frameon=False, loc='upper left', bbox_to_anchor=(0, 0.95))

plt.savefig(f'{OUT}/topic_corpus_chronicles.pdf', bbox_inches='tight')
plt.close(fig)
print('ok: topic_corpus_chronicles.pdf (regenerated from the real 126-chronicle Topic Corpus)')
