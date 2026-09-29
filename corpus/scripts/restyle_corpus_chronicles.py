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

# --- minimal data pipeline (mirrors count_chronicles.ipynb cells 4, 12, 14 -- these three
# figures only need the corpus metadata table, not the XML/token-counting cells) ---
corpus = pd.read_excel(f'{base}/Status definitieve corpus_2.xlsx', sheet_name='Alle kronieken')
corpus = corpus[['Batch', 'Call Number', 'Transcriptie klaar', 'Geannoteerd', 'Geannoteerd (bronnen van informatie)', 'Datums genormaliseerd']]
corpus = corpus[corpus['Call Number'].isna() == False]
corpus = corpus[corpus['Transcriptie klaar'].isin(['Ja', 'n.v.t.'])]
corpus['year'] = corpus['Call Number'].str[:4].astype(int)
corpus['call_nr_clean'] = corpus['Call Number'].str[:14]
corpus['cut'] = pd.cut(corpus['year'], np.arange(1475, 1925, 25))
corpus['cut'] = corpus['cut'].astype(str)
corpus['cut'] = corpus['cut'].str[1:-1]
corpus['cut'] = corpus['cut'].str.replace(', ', '–')

corpus_annotated = corpus[corpus['Geannoteerd'] == 'Ja']
df_annotated = corpus_annotated.groupby('cut')[['Call Number', 'call_nr_clean']].nunique().reset_index()

df_full = corpus.groupby('cut')[['Call Number', 'call_nr_clean']].nunique().reset_index()

corpus_sources = corpus[corpus['Geannoteerd (bronnen van informatie)'].isin(['Ja', 'gedeelte'])]
df_sources = corpus_sources.groupby('cut')[['Call Number', 'call_nr_clean']].nunique().reset_index()


def modern_bar(df, title, ylabel, out_name, y_locator=None, legend_anchor=(1.0, 1.0)):
    fig, axs = plt.subplots(figsize=(7, 4))
    x = np.arange(len(df))

    axs.bar(x, df['Call Number'], width=0.6, color='#C2C5AA', zorder=3)
    axs.bar(x, df['call_nr_clean'], width=0.3, color='#333D29', zorder=3)

    axs.set_title(title, fontweight='bold', fontsize=13, loc='left', pad=12)
    axs.set_ylabel(ylabel)
    axs.set_xlabel('')
    axs.set_xticks(x)
    # rotation_mode='anchor' pivots each label around its own tick position (ha='right' anchor)
    # instead of its bounding-box center, so rotated labels sit centered under their bar
    axs.set_xticklabels(labels=df['cut'], rotation=45, ha='right', rotation_mode='anchor')
    if y_locator is not None:
        axs.yaxis.set_major_locator(plt.MultipleLocator(y_locator))

    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)
    axs.spines['bottom'].set_color('#999999')
    axs.tick_params(axis='both', length=0, colors='#555555')

    axs.yaxis.grid(True, color='#E5E5E5', linewidth=0.8, zorder=0)
    axs.set_axisbelow(True)

    axs.legend(['chronicle volumes', 'chronicles'], frameon=False, loc='upper left', bbox_to_anchor=legend_anchor)

    plt.savefig(f'{OUT}/{out_name}', bbox_inches='tight')
    plt.close(fig)
    print(f'ok: {out_name}')


modern_bar(df_full, 'Full Corpus', 'number of documents', 'full_corpus_chronicles.pdf', y_locator=10, legend_anchor=(0, 0.95))
modern_bar(df_annotated, 'Topic Corpus', 'number of documents', 'topic_corpus_chronicles.pdf', legend_anchor=(0, 0.95))
modern_bar(df_sources, 'Source Corpus', 'number of documents', 'source_corpus_chronicles.pdf', y_locator=3, legend_anchor=(0, 0.93))
