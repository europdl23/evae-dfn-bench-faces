# -*- coding: utf-8 -*-
"""Fig. E1: engineering inputs per held-out panel, pooled over the 120 panel cases, held-out / EVAE / ADFNE / KDE
(the style of the paper's Fig. 11: 14.65 cm wide, Times New Roman 12/10 pt, release layout check)."""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import eng_common as E
import figstyle as FS
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

CM = 1 / 2.54; W = 14.65 * CM; SIZES = (12, 10)
ORD = ['Held-out', 'EVAE', 'ADFNE', 'KDE']
PAR = [('p', '(a) Percolation parameter p', '%.2f'), ('E_along', '(b) E/E0 along the bench', '%.2f'),
       ('E_down', '(c) E/E0 down the face', '%.2f'), ('aniso', '(d) Deformability anisotropy', '%.2f'),
       ('k_max_C1', '(e) Maximum persistence, C1', '%.2f'), ('k_max_C2', '(f) Maximum persistence, C2', '%.2f')]


def check_points(fig):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); probs = []
    for ax in fig.axes:
        for t in ax.texts:
            if not t.get_visible() or not t.get_text().strip(): continue
            bb = t.get_window_extent(r)
            for col in ax.collections:
                xy = col.get_offset_transform().transform(col.get_offsets())
                if len(xy) and np.any((xy[:, 0] > bb.x0 - 4) & (xy[:, 0] < bb.x1 + 4) & (xy[:, 1] > bb.y0 - 4) & (xy[:, 1] < bb.y1 + 4)):
                    probs.append('%r sits on points' % t.get_text()[:30])
    return probs


def main():
    PV = pd.read_csv(E.TAB / 'engineering_panel_values.csv', na_values=['n.d.'])
    fig, axs = plt.subplots(3, 2, figsize=(W, 20.0 * CM))
    for ax, (k, lab, fmt) in zip(axs.ravel(), PAR):
        data = [PV[PV.method == m][k].dropna().values for m in ORD]; ref = np.median(data[0])
        ticks = ['Held-out\n%s' % (fmt % ref)] + ['%s\n%s\n(%+.0f%%)' % (m, fmt % np.median(d), 100 * (np.median(d) - ref) / ref) for m, d in zip(ORD[1:], data[1:])]
        bp = ax.boxplot(data, tick_labels=[t_.replace('(-', '(−') for t_ in ticks], patch_artist=True, widths=0.55, showfliers=False,
                        medianprops=dict(color='k', lw=1.3), whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7), boxprops=dict(lw=0.7))
        for patch, m in zip(bp['boxes'], ORD):
            patch.set_facecolor(FS.METHOD_COL[m]); patch.set_alpha(0.8)
        ax.axhline(ref, color='k', ls='--', lw=0.8); ax.tick_params(axis='x', length=0, pad=3)
        ax.set_title(lab, fontsize=12, pad=4)
        if k == 'p':                                    # all networks lie below the 2D percolation threshold
            ax.axhline(E.P_CRIT, color='0.45', ls=':', lw=1.0); lo, hi = ax.get_ylim(); ax.set_ylim(lo, E.P_CRIT * 1.12)
            ax.text(4.45, E.P_CRIT * 1.035, 'threshold ≈ 5.6', fontsize=10, ha='right', va='bottom', color='0.3')
    fig.legend(handles=[Line2D([], [], color='k', ls='--', lw=0.8, label='Held-out median (120 held-out panels; per panel, median of 24 realisations)')],
               loc='lower center', frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.035, 1, 1), h_pad=0.8, w_pad=1.5)
    pr = check_points(fig)
    if pr:
        raise RuntimeError('\n'.join(pr))
    print(FS.save(fig, str(E.FIG / 'Fig_E1_engineering'), allow_font_sizes=SIZES))


if __name__ == '__main__':
    main()
