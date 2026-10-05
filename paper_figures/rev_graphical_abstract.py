# -*- coding: utf-8 -*-
"""Graphical abstract (round 3, 3 Oct 2026: hold-out test only; values from Figure_7_values.csv (20 held-out windows) and
Figure_9_values.csv (median clipped length). Earlier: final-paper version of 2 Oct 2026; review D6 and MY_VIEW Section 3 D6: show the result, not one
realisation). No new computation: every plotted number is read from the audited value files of the paper figures.

Left: the study in three blocks (FACTS_GEOBG J2: trace length, intersections and connections per trace are the scores on
which the EVAE is "overall better"; most other scores not significantly different; no "connectivity", TASK B).
Right: mini versions of Fig. 9a and Fig. 9c for the EVAE, ADFNE and KDE: the difference from the held-out window over
the 20 held-out windows of the hold-out test, box = interquartile range, thick black line = median,
whiskers to 1.5 x the interquartile range (outliers not drawn), thin grey dashed line = held-out window (zero
difference); the median difference is printed under each method name. Source: out/figures/Figure_9_values.csv
(written by fig_engineering.py, which asserts the values against the release tables). Below: the median trace length
(clipped, hold-out test) from out/figures/Figure_9_values.csv.
The former right half (window A, one realisation of each method) is dropped: in that single realisation the EVAE was the
sparsest map and the farthest on median length, so it did not show the result (CHECKS_OF_REVIEW D6).
Method colours: EVAE #009E73, ADFNE #E69F00, KDE #56B4E9. 20 x 8 cm, PNG at 600 dpi (4724 x 1890 px, above the
1328 x 531 px minimum of the journal) + PDF. Plotted values to out/figures/Graphical_abstract_values.csv."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import figstyle as S
import rev_common as RC

COL = {'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}
GEN = ('EVAE', 'ADFNE', 'KDE')
V9 = pd.read_csv(RC.VAL / 'Figure_7_values.csv')
VS1 = pd.read_csv(RC.VAL / 'Figure_9_values.csv').set_index('method')
PARTS = [('len_med', 'Median trace length (m)', 2, [-4, -2, 0, 2]), ('P22', 'Intersections per 100 m²', 2, [-1, 0, 1, 2])]


def stats(measure, method):
    r = V9[(V9.measure == measure) & (V9.method == method)]
    assert len(r) == 1, (measure, method)
    r = r.iloc[0]
    assert int(r.n_window_cases) == 20 and int(r.n_windows) == 20, r
    return dict(med=r.median_difference, q1=r.q1, q3=r.q3, whislo=r.whisker_low, whishi=r.whisker_high, fliers=[], label=method)


def signed(x, nd):
    s = ('%+.' + str(nd) + 'f') % x
    return s.replace('-', '−')


FW, FH = 20.0, 8.0
fig = plt.figure(figsize=(FW * S.CM, FH * S.CM))
tx = fig.add_axes([0.0, 0.0, 0.335, 1.0]); tx.axis('off'); tx.set_xlim(0, 1); tx.set_ylim(0, 1)
tx.add_patch(FancyBboxPatch((0.04, 0.04), 0.92, 0.92, boxstyle='round,pad=0.01,rounding_size=0.03', fc='#F3F3F3', ec='0.3', lw=0.8))
tx.text(0.5, 0.92, 'Held-out 20 m sampling\nwindows of a mapped\nopen-pit wall', ha='center', va='top', fontweight='bold', linespacing=1.15)
tx.text(0.5, 0.665, '20 held-out windows, hold-out test;\nEVAE (local generation)\nagainst ADFNE and KDE', ha='center', va='top', linespacing=1.15)
tx.text(0.5, 0.42, 'Trace length, intersections and\nconnections per trace:\nEVAE closest\nMost other scores:\nnot significantly different',
        ha='center', va='top', linespacing=1.15)

rows = []
PW, PH, PTOP = 4.55, 3.05, 0.95                      # plot width, height, top edge (cm from the figure top)
X0 = [8.25, 14.85]                                   # left edges (cm); y label "Difference" to the left of each plot
for (k, title, nd, yt), x0 in zip(PARTS, X0):
    ax = RC.axes_cm(fig, x0, PTOP, PW, PH)
    st = [stats(k, m) for m in GEN]
    bp = ax.bxp(st, positions=[1, 2, 3], widths=0.55, patch_artist=True, showfliers=False,
                medianprops=dict(color='k', lw=2.2, solid_capstyle='butt', zorder=4),
                whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7), boxprops=dict(lw=0.7))
    for patch, m in zip(bp['boxes'], GEN):
        patch.set_facecolor(COL[m]); patch.set_alpha(0.85)
    ax.axhline(0, color='0.45', lw=0.8, ls=(0, (4, 2.5)), zorder=0.5)        # held-out window, behind the boxes
    ax.set_xlim(0.45, 3.55)
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels(['%s\n%s' % (m, signed(s_['med'], nd)) for m, s_ in zip(GEN, st)], linespacing=1.1)
    ax.tick_params(axis='x', length=0, pad=3)
    lo, hi = ax.get_ylim(); mm = max(abs(lo), abs(hi)); ax.set_ylim(min(lo, -0.08 * mm), max(hi, 0.08 * mm))
    ax.set_yticks(yt)
    ax.set_title(title, loc='left', pad=4)
    ax.set_ylabel('Difference', labelpad=2)
    for m, s_ in zip(GEN, st):
        rows.append(dict(part='difference from the held-out window, ' + title, method=m, n_window_cases=20, n_windows=20,
                         median_difference=s_['med'], q1=s_['q1'], q3=s_['q3'], whisker_low=s_['whislo'], whisker_high=s_['whishi'],
                         source='Figure_7_values.csv (measure %s)' % k))

med = {m: float(VS1.loc[m, 'median_length_m']) for m in ('Mapped', 'EVAE', 'ADFNE', 'KDE')}
for m, v in med.items():
    rows.append(dict(part='median clipped trace length, hold-out test (m)', method=m, median_difference=np.nan,
                     pooled_median_length_m=v, source='Figure_9_values.csv'))
x_mid = (X0[0] - 1.3 + X0[1] + PW) / 2 / FW
fig.text(x_mid, 0.45 / FH, 'Differences from the held-out window, 20 held-out windows\n'
         'Median clipped trace length: mapped windows %.1f m,\n'
         'EVAE %.1f m, ADFNE %.1f m, KDE %.1f m' % (med['Mapped'], med['EVAE'], med['ADFNE'], med['KDE']),
         ha='center', va='bottom', linespacing=1.15)
fig.legend(handles=[Line2D([], [], color='0.45', lw=0.8, ls=(0, (4, 2.5)), label='Held-out window'),
                    Line2D([], [], color='k', lw=2.2, label='Median')],
           loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(x_mid, 2.2 / FH), handlelength=1.8, columnspacing=1.5, borderaxespad=0)
RC.save(fig, 'Graphical_abstract')
pd.DataFrame(rows).to_csv(RC.VAL / 'Graphical_abstract_values.csv', index=False, float_format='%.4f')
print(pd.DataFrame(rows).to_string(index=False))
