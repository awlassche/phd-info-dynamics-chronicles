import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITHUB_ROOT = os.path.dirname(os.path.dirname(base))
OUT = f'{os.path.dirname(base)}/figures'

for _font_path in [
    os.path.expanduser("~/Library/Fonts/RobotoCondensed-Regular.ttf"),
    os.path.expanduser("~/Library/Fonts/RobotoCondensed-Bold.ttf"),
]:
    fm.fontManager.addfont(_font_path)
plt.rcParams['font.size'] = 11
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = 'Roboto Condensed'

# unlike the Topic Corpus, sources_clpl's 'doc' column is already the true volume-level identifier
# (verified: tokens_total genuinely differs per doc within a doc_author, not a repeated chronicle
# total), so no separate fragment-level join is needed here to recover which volumes were really used
EXCLUDE = ['1575_Antw_Ulle', '1602_Brus_Pott']
sources_clpl = pd.read_csv(f'{GITHUB_ROOT}/chronicling-sources/output/sources_clpl/sources_clpl_2022_del.csv', sep=';', index_col=0)
sources_clpl = sources_clpl[~sources_clpl['doc_author'].isin(EXCLUDE)].copy()

n_chronicles = sources_clpl['doc_author'].nunique()
n_volumes = sources_clpl['doc'].nunique()
n_tokens = sources_clpl['tokens_total'].sum()
print(f'Source Corpus: {n_chronicles} chronicles, {n_volumes} volumes, {n_tokens:,} tokens')
assert n_chronicles == 64 and n_volumes == 83

sources_clpl['cut'] = pd.cut(sources_clpl['year'], np.arange(1475, 1925, 25))
sources_clpl['cut'] = sources_clpl['cut'].astype(str).str[1:-1].str.replace(', ', '–')

df_source = sources_clpl.groupby('cut')[['doc', 'doc_author']].nunique().reset_index()
df_source = df_source.rename(columns={'doc': 'Call Number', 'doc_author': 'call_nr_clean'})

fig, axs = plt.subplots(figsize=(7, 4))
x = np.arange(len(df_source))
axs.bar(x, df_source['Call Number'], width=0.6, color='#C2C5AA', zorder=3)
axs.bar(x, df_source['call_nr_clean'], width=0.3, color='#333D29', zorder=3)
axs.set_title('Source Corpus', fontweight='bold', fontsize=13, loc='left', pad=12)
axs.set_ylabel('number of documents')
axs.set_xlabel('')
axs.set_xticks(x)
axs.set_xticklabels(labels=df_source['cut'], rotation=45, ha='right', rotation_mode='anchor')
axs.yaxis.set_major_locator(plt.MultipleLocator(3))
axs.spines['top'].set_visible(False)
axs.spines['right'].set_visible(False)
axs.spines['left'].set_visible(False)
axs.spines['bottom'].set_color('#999999')
axs.tick_params(axis='both', length=0, colors='#555555')
axs.yaxis.grid(True, color='#E5E5E5', linewidth=0.8, zorder=0)
axs.set_axisbelow(True)
axs.legend(['chronicle volumes', 'chronicles'], frameon=False, loc='upper left', bbox_to_anchor=(0, 0.93))
plt.savefig(f'{OUT}/source_corpus_chronicles.pdf', bbox_inches='tight')
plt.close(fig)
print('ok: source_corpus_chronicles.pdf')
