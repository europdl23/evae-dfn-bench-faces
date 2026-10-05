# -*- coding: utf-8 -*-
"""ROUND 3 (3 Oct 2026, PLAN_ROUND3 Section C): this figure is now Fig. 7 and shows the HOLD-OUT TEST ONLY (release S1,
20 held-out windows; the robustness tests are in the Supplement); labels "surrounding windows", "Mapped held-out window".
Old header follows. Fig. 9: engineering inputs as differences from the held-out window (copy of engineering_demo_2026-10-01/code/
fig_engineering.py, rebuilt per work/ADVICE_engineering_placement.md Section 4 item 10 and the final-paper task;
numbering of work/GLOSSARY.md Section 5).

For every window case (a held-out window in one test; 120 window cases from 50 windows: 20 gap-filling, 50 new-bench,
50 new-stretch, pooled) and every method, the value of the method minus the value of the held-out window:
  natural-variability reference = the 8 neighbouring windows with the held-out fractures removed (median over the 8),
  EVAE, ADFNE, KDE              = median over the 24 realisations of the window case.
Six measures (one plot each): (a) median trace length (m), (b) P21 (m/m²), (c) intersections per 100 m²,
(d) E/E0 along the bench, (e) largest-cluster share, (f) maximum persistence k_max of cluster C1 (title
"(f) Maximum persistence, C1"; the symbol k_max is given in the caption).
y label "Difference" (method minus held-out window, in the unit of the title). Boxes: interquartile range, median line, whiskers to 1.5 x the interquartile range, outliers not drawn (as the old
Fig. 11). Median = plain thick black line (no white halo; review D5, 2 Oct 2026); the held-out window (zero difference)
= thin grey dashed line drawn behind the boxes. Colours: reference mid grey #9A9A9A, EVAE
#009E73, ADFNE #E69F00, KDE #56B4E9.

Data (read only): engineering_demo_2026-10-01/tables/engineering_panel_values.csv (window-case values of P21,
intersections, E/E0 along the bench, largest-cluster share, k_max C1 for Held-out, Reference (fracture-removed), EVAE,
ADFNE, KDE) and engineering_network_props.csv (median trace length per realisation; window-case value = median over the
realisations, as engineering_panel_values). Checks (asserted): the reference, held-out and EVAE window-case values of
median length, P21 and intersections equal the release paper/tables/panel_properties.csv; ADFNE and KDE equal the
release tables/final_properties.csv; 120 window cases from 50 windows; no undefined value.
Every plotted summary (median, quartiles, whisker ends, n) goes to out/figures/Figure_7_values.csv.
Usage: python -B fig_engineering.py"""
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
import importlib.util
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import eng_common as E
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

_spec = importlib.util.spec_from_file_location('figstyle_release', str(E.HERE / 'figstyle_release.py'))
FS = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(FS)          # release style and layout check (copy)
_rc = dict(plt.rcParams)
_spec = importlib.util.spec_from_file_location('house_figstyle', str(E.HERE / 'figstyle.py'))
HOUSE = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(HOUSE)    # house check + GLOSSARY term check
plt.rcParams.update(_rc)
plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic',
                     'mathtext.bf': 'Times New Roman:bold'})   # review F11: math in Times New Roman (was STIX)

CM = 1 / 2.54; W = 14.65 * CM; SIZES = (12, 10)
ORD = [E.REFERENCE, 'EVAE', 'ADFNE', 'KDE']
TICK = {E.REFERENCE: 'Reference', 'EVAE': 'EVAE', 'ADFNE': 'ADFNE', 'KDE': 'KDE'}
COL = {E.REFERENCE: '#9A9A9A', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}
PAR = [('len_med', '(a) Median trace length (m)'), ('P21', r'(b) $P_{21}$ (m/m²)'), ('P22', '(c) Intersections per 100 m²'),
       ('E_along', r'(d) $E/E_0$ along the bench'), ('largest_share', '(e) Largest-cluster share'),
       ('k_max_C1', '(f) Maximum persistence, C1')]
KEY = ['scheme', 'fold', 'box']


def load():
    PV = pd.read_csv(E.TAB / 'engineering_panel_values.csv', na_values=['n.d.'])
    PR = pd.read_csv(E.TAB / 'engineering_network_props.csv', usecols=KEY + ['method', 'len_med', 'P21', 'P22'])
    PRp = PR.groupby(KEY + ['method']).median(numeric_only=True).reset_index()
    V = PV.merge(PRp[KEY + ['method', 'len_med']], on=KEY + ['method'], how='left')
    # consistency with the engineering table itself (P21, intersections were taken from the realisation medians)
    chk = PV.merge(PRp, on=KEY + ['method'], suffixes=('', '_p'))
    assert np.allclose(chk.P21, chk.P21_p) and np.allclose(chk.P22, chk.P22_p)
    # consistency with the release (read only)
    rel = pd.read_csv(E.REL / 'paper' / 'tables' / 'panel_properties.csv')
    for m_e, m_r in ((E.REFERENCE, 'Reference'), ('Held-out', 'Held-out'), ('EVAE', 'EVAE')):
        a = V[V.method == m_e].set_index(['scheme', 'box']); b = rel[rel.method == m_r].set_index(['scheme', 'box'])
        for k in ('len_med', 'P21', 'P22'):
            j = a[[k]].join(b[[k]], rsuffix='_r', how='inner'); assert len(j) == 120 and np.allclose(j[k], j[k + '_r']), (m_e, k)
    fp = pd.read_csv(E.REL / 'tables' / 'final_properties.csv').replace({'Real': 'Held-out'})
    for m in ('ADFNE', 'KDE', 'Held-out', 'EVAE'):
        a = V[V.method == m].set_index(['scheme', 'box']); b = fp[fp.method == m].set_index(['scheme', 'box'])
        for k in ('len_med', 'P21', 'P22'):
            j = a[[k]].join(b[[k]], rsuffix='_r', how='inner'); assert len(j) == 120 and np.allclose(j[k], j[k + '_r']), (m, k)
    V = V[V.scheme == 'S1']                            # round 3: the hold-out test only (release S1, 20 held-out windows)
    H = V[V.method == 'Held-out'].set_index(KEY)
    assert len(H) == 20 and H.reset_index().box.nunique() == 20
    D = {}
    for m in ORD:
        X = V[V.method == m].set_index(KEY).reindex(H.index)
        D[m] = X[[k for k, _ in PAR]] - H[[k for k, _ in PAR]]
        assert not D[m].isna().any().any(), m
    return H, D


def main():
    H, D = load()
    fig, axs = plt.subplots(3, 2, figsize=(W, 15.5 * CM))
    rows = []
    for ax, (k, lab) in zip(axs.ravel(), PAR):
        data = [D[m][k].values for m in ORD]
        bp = ax.boxplot(data, tick_labels=[TICK[m] for m in ORD], patch_artist=True, widths=0.55, showfliers=False, whis=1.5,
                        medianprops=dict(color='k', lw=2.2, solid_capstyle='butt', zorder=4),   # review D5: plain thick median, no halo
                        whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7), boxprops=dict(lw=0.7))
        for patch, m in zip(bp['boxes'], ORD):
            patch.set_facecolor(COL[m]); patch.set_alpha(0.85)
        ax.axhline(0, color='0.45', lw=0.8, ls=(0, (4, 2.5)), zorder=0.5)   # held-out window: thin grey dashed, behind the boxes
        ax.tick_params(axis='x', length=0, pad=3)
        ax.set_title(lab, fontsize=12, pad=4, loc='left')
        lo, hi = ax.get_ylim(); m_ = max(abs(lo), abs(hi)); ax.set_ylim(min(lo, -0.08 * m_), max(hi, 0.08 * m_))
        for m, d, wl, wh in zip(ORD, data, bp['whiskers'][0::2], bp['whiskers'][1::2]):
            q1, med, q3 = np.percentile(d, [25, 50, 75])
            rows.append(dict(measure=k, method=TICK[m] if m != E.REFERENCE else 'Natural-variability reference', n_window_cases=len(d),
                             n_windows=D[m].reset_index().box.nunique(), held_out_median=float(np.median(H[k])),
                             median_difference=float(med), q1=float(q1), q3=float(q3),
                             whisker_low=float(wl.get_ydata()[1]), whisker_high=float(wh.get_ydata()[1]),
                             share_below_zero=float(np.mean(d < 0)), share_above_zero=float(np.mean(d > 0))))
    for ax in axs[:, 0]:
        ax.set_ylabel('Difference')
    fig.align_ylabels(axs[:, 0])                       # review F9: (a), (c), (e) labels aligned
    fig.legend(handles=[Patch(fc=COL[E.REFERENCE], alpha=0.85, ec='k', lw=0.7, label='Reference: natural-variability reference (surrounding windows, held-out fractures removed)'),
                        Line2D([], [], color='0.45', lw=0.8, ls=(0, (4, 2.5)), label='Mapped held-out window (zero difference)'),
                        Line2D([], [], color='k', lw=2.2, label='Median of the 20 held-out windows')],
               loc='lower center', ncol=1, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0), handlelength=1.6, labelspacing=0.3)
    fig.tight_layout(rect=(0, 0.10, 1, 1), h_pad=0.9, w_pad=1.5)
    probs = HOUSE.check_layout(fig, SIZES)
    if probs:
        fig.savefig(str(_RR.SCRATCH / 'Figure_7_FAILED_preview.png'), dpi=150)
        raise RuntimeError('Figure_7:\n  ' + '\n  '.join(probs))
    w, h = fig.get_size_inches() / CM
    print('Figure_7: %s; house check clean; %.2f x %.2f cm' % (FS.save(fig, str(E.FIG / 'Figure_7'), allow_font_sizes=SIZES), w, h))
    VAL = pd.DataFrame(rows)
    VAL.to_csv(E.FIG / 'Figure_7_values.csv', index=False, float_format='%.4f')
    pd.set_option('display.width', 250)
    print(VAL.round(3).to_string(index=False))


if __name__ == '__main__':
    main()
