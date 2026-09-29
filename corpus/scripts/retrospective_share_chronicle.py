import pandas as pd
import numpy as np
import ndjson
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from scipy import stats

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

DARK = '#333D29'


def modern_axes(ax, title, ylabel=None, xlabel=None):
    ax.set_title(title, fontweight='bold', fontsize=13, loc='left', pad=12)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#999999')
    ax.tick_params(axis='both', length=0, colors='#555555')
    ax.yaxis.grid(True, color='#E5E5E5', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def annotate_slope(ax, data, x_col, y_col, confidence=0.95):
    n = len(data)
    result = stats.linregress(data[x_col], data[y_col])
    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 2)
    margin = t_crit * result.stderr
    slope, ci_low, ci_high = result.slope, result.slope - margin, result.slope + margin
    ax.text(0.03, 0.96, f'{slope*100:+.3f} [{ci_low*100:+.3f}, {ci_high*100:+.3f}] pp/year (n={n})',
            transform=ax.transAxes, ha='left', va='top', fontsize=8, color='#555555')


# --- data pipeline: contemporary-start year per chronicle (Chronicles_metadata.xlsx) merged
# against dated, token-counted fragments (chronicling-events primitives) ---
meta = pd.read_excel(f'{base}/Chronicles_metadata.xlsx', sheet_name='Chronicles')
meta = meta[['Call_Number', 'contemporain_begin_integer']].dropna(subset=['contemporain_begin_integer'])
meta['contemporain_begin_integer'] = pd.to_numeric(meta['contemporain_begin_integer'], errors='coerce')
meta = meta.dropna(subset=['contemporain_begin_integer'])

with open(f'{EVENTS_BASE}/output/primitives_230807/primitives_corrected_monthly_clean.ndjson') as f:
    frags = ndjson.load(f)
frag_df = pd.DataFrame(frags)
frag_df['frag_year'] = pd.to_numeric(frag_df['clean_month'].str[:4], errors='coerce')

merged = frag_df.merge(meta, left_on='call_nr_clean', right_on='Call_Number', how='inner')
merged['is_retrospective'] = merged['frag_year'] < merged['contemporain_begin_integer']

per_chron = merged.groupby(['call_nr_clean', 'is_retrospective'])['n_tokens'].sum().unstack(fill_value=0)
per_chron = per_chron.rename(columns={False: 'contemporary_tokens', True: 'retrospective_tokens'})
for col in ['contemporary_tokens', 'retrospective_tokens']:
    if col not in per_chron.columns:
        per_chron[col] = 0
per_chron['retro_share'] = per_chron['retrospective_tokens'] / (per_chron['contemporary_tokens'] + per_chron['retrospective_tokens']) * 100
per_chron['year'] = per_chron.index.str[:4].astype(int)
per_chron = per_chron.reset_index()

print(f'n chronicles: {len(per_chron)}')
print(f"chronicles with any retrospective content: {(per_chron['retro_share'] > 0).sum()}")

fig, ax = plt.subplots(figsize=(7, 4))
sns.regplot(x='year', y='retro_share', data=per_chron, ax=ax, color=DARK,
            scatter_kws={'zorder': 3, 's': 30, 'alpha': 0.8}, line_kws={'linewidth': 2})
modern_axes(ax, 'Share of retrospective content per chronicle',
            ylabel='retrospective tokens (% of chronicle)', xlabel='')
annotate_slope(ax, per_chron, 'year', 'retro_share')
ax.set_ylim(-3, 100)

plt.savefig(f'{OUT}/retrospective_share_chronicle.pdf', bbox_inches='tight')
plt.close(fig)
print('ok: retrospective_share_chronicle.pdf')
