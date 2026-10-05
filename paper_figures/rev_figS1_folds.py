# -*- coding: utf-8 -*-
"""Supplementary Fig. S1 of round 3 (PLAN_ROUND3 H4: the complete fold map and the trace-length histogram moved out of
Fig. 2). (a) to (c): the window grid (window columns 1 to 8 x bench faces W00 to W06) with the held-out windows of
every fold (one cividis shade per fold, fold number in each cell) for the hold-out test (release S1) and the two
robustness tests, the whole-bench test (S2) and the 40 m-stretch test (S3); example windows A to D of the main text
(hold-out test, round3_common.EXAMPLES) outlined and lettered in (a). (d) lengths of the 705 mapped traces (2 m bins)
with the median. Drawing of (a) to (c) as the old Fig. 5 (rev_fig5_holdout.py); (d) as the old Fig. 2c.
Values to out/figures/Figure_S1_values.csv (role of every window in every test) and Figure_S1_lengths.json."""
import csv, json, math, glob
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
import figstyle as S
import figdata as D
import rev_common as RC
import round3_common as R3
C = D.C

boxes = C.load_library()
man = list(csv.DictReader(open(C.LIB / 'box_manifest.csv')))
FOLD_COL = [mcolors.to_hex(plt.get_cmap('cividis')(x)) for x in np.linspace(0.0, 1.0, 7)]
FOLD_TXT = ['white' if 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2] < 0.5 else 'black' for c in (mcolors.to_rgb(f) for f in FOLD_COL)]
UNUSED = dict(fc='white', hatch='////', ec='0.45')
FW, FH = RC.W / S.CM, 12.7
fig = plt.figure(figsize=(FW * S.CM, FH * S.CM))


def box_cm(x0, y_top, w, h):
    return fig.add_axes([x0 / FW, (FH - y_top - h) / FH, w / FW, h / FH])


G = 4.25
axs = [box_cm(1.05, 1.15, G, G * 7 / 8), box_cm(1.05 + G + 0.4, 1.15, G, G * 7 / 8), box_cm(1.05 + 2 * (G + 0.4), 1.15, G, G * 7 / 8)]


def cell(ax, m, **kw):
    x, y = int(m['col']) - 1, int(m['row_index'])
    ax.add_patch(Rectangle((x + 0.06, y + 0.06), 0.88, 0.88, lw=0.6, **kw))


TITLES = ('(a) Hold-out test\n4 folds', '(b) Whole-bench test\n7 folds', '(c) 40 m-stretch test\n4 folds')
NAMES = {'S1': 'hold-out test', 'S2': 'whole-bench test', 'S3': '40 m-stretch test'}
lett = {e['box']: e['label'] for e in R3.EXAMPLES}
rec = []
for ax, s, t in zip(axs, C.SCHEMES, TITLES):
    F = C.folds(s, boxes); where = {b: i for i, f in enumerate(F) for b in f}
    for m in man:
        b = m['box']
        if m['usable'] != 'True':
            cell(ax, m, **UNUSED); role = 'not used'
        elif b in where:
            k = where[b]; cell(ax, m, fc=FOLD_COL[k], ec='0.3'); role = 'held out, fold %d' % (k + 1)
            if not (s == 'S1' and b in lett):
                ax.text(int(m['col']) - 0.5, int(m['row_index']) + 0.53, str(k + 1), ha='center', va='center', color=FOLD_TXT[k], fontsize=10)
        else:
            cell(ax, m, fc='white', ec='0.3'); role = 'never held out'
        if s == 'S1' and b in lett:
            assert where[b] == [e['fold'] for e in R3.EXAMPLES if e['box'] == b][0]
            x, y = int(m['col']) - 1, int(m['row_index'])
            ax.add_patch(Rectangle((x + 0.06, y + 0.06), 0.88, 0.88, fc='none', ec='k', lw=2.0))
            ax.text(x + 0.5, y + 0.53, lett[b], ha='center', va='center', fontweight='bold', fontsize=10, color=FOLD_TXT[where[b]])
        rec.append(dict(test=NAMES[s], window=RC.wid(b), release_key=b, role=role, example=lett.get(b, '') if s == 'S1' else ''))
    ax.set_xlim(0, 8); ax.set_ylim(7, 0); ax.set_aspect('equal')
    ax.set_xticks(np.arange(8) + 0.5); ax.set_xticklabels([str(i) for i in range(1, 9)])
    ax.set_xlabel('Window column', labelpad=1, fontsize=10)
    ax.set_yticks(np.arange(7) + 0.5); ax.set_yticklabels(C.ORDER if s == 'S1' else [])
    ax.tick_params(length=0, pad=2, labelsize=10); ax.set_title(t, loc='left', fontsize=12)
    for sp_ in ax.spines.values():
        sp_.set_visible(False)

# (d) lengths of the 705 traces
T = json.load(open(C.TRACES))['traces']
L = np.array([tr['length_m'] for tr in T]); lb = np.arange(0, 44, 2)
hl, _ = np.histogram(L, bins=lb)
axd = box_cm(1.75, 7.15, 5.0, 4.2)
axd.stairs(hl / hl.sum(), lb, fill=True, color='0.75', lw=0)
axd.axvline(np.median(L), color='k', lw=1.2, ls='--')
axd.set_xlim(0, 42); axd.set_xticks([0, 10, 20, 30, 40]); axd.set_ylim(0, None); axd.tick_params(labelsize=10)
axd.set_xlabel('Trace length (m)', fontsize=10); axd.set_ylabel('Share of traces', fontsize=10)
axd.set_title('(d) Lengths of the 705 mapped traces', loc='left', fontsize=12)
leg = [Patch(fc=FOLD_COL[i], ec='0.3', lw=0.6, label='Held-out windows, fold %d' % (i + 1)) for i in range(7)] + \
      [Patch(fc='white', ec='0.3', lw=0.6, label='Never held out'), Patch(lw=0.6, label='Not used (inner berm)', **UNUSED),
       Patch(fc='white', ec='k', lw=2.0, label='Example windows A to D'), Line2D([], [], color='k', lw=1.2, ls='--', label='Median length (d)')]
fig.legend(handles=leg, loc='upper left', ncol=1, frameon=False, bbox_to_anchor=(8.2 / FW, 1 - 6.95 / FH), fontsize=10,
           alignment='left', handlelength=1.4, handletextpad=0.4, labelspacing=0.35, columnspacing=0.8, borderaxespad=0, borderpad=0)
RC.save(fig, 'Figure_S1', allow=(12, 10))
pd.DataFrame(rec).to_csv(RC.VAL / 'Figure_S1_values.csv', index=False)
json.dump(dict(traces=len(L), median_m=float(np.median(L)), p90_m=float(np.percentile(L, 90)), max_m=float(L.max()),
               bin_lo=lb[:-1].tolist(), share=(hl / hl.sum()).tolist()), open(RC.VAL / 'Figure_S1_lengths.json', 'w'), indent=1)
print('median length %.2f m, n %d' % (np.median(L), len(L)))
