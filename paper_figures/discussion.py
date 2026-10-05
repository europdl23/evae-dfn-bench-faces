# -*- coding: utf-8 -*-
"""ROUND 3 (3 Oct 2026): the pooled length histograms are now Supplementary Fig. S3 (Figure_S3; was Figure_S1); Figure_10
(ablation counts) is no longer a paper figure (PLAN_ROUND3 comment 13; its counts are in Table S5). Old header follows.
Discussion figures of the paper (copy of the release paper/code/discussion.py, final-paper version of 1 Oct 2026;
numbering of work/GLOSSARY.md Section 5). ONLY the figure parts are kept: the release script also recounts the tests and
writes the release tables (paper/tables), which this copy must never do. The counts are READ from the release recount
(paper/tables/recount_ablation_counts.csv, n.d. rule) and the realisations from the release realisation files (networks/), read only.

  Figure_10  release Fig_9_ablation_counts (old Fig. 9): ablation counts by score group, (a) full EVAE against EVAE without
             geology-informed constraints 25 / 87 / 2, (b) full EVAE against single-latent EVAE 2 / 106 / 6 (asserted).
             Labels (as rev_release_figs.py, FIXLIST_V2 G-02): legend "Full EVAE better / Not significantly different /
             Full EVAE worse"; x label "Score × test comparisons (38 scores × 3 tests = 114)"; titles "against"; x ticks
             0, 38, 76, 114.
  Figure_S1  release Fig_11_alt_length_histograms: pooled trace-length histograms of held-out, EVAE, ADFNE and KDE,
             medians 5.7, 5.4, 4.6, 5.2 m (asserted); 9.5 cm tall (release 11.5 cm). Labels: titles "Held-out windows,
             median 5.7 m" (was "Held-out, median ..."); legend "Held-out windows (outline)".
The old Fig. 11 box plots (release Fig_11_boxplots) are no longer a paper figure (GLOSSARY Section 5, decision 3).
Usage: python -B discussion.py [10] [S1]      (default: both)"""
import importlib.util
import numpy as np, pandas as pd
import pr_common as P
import matplotlib
matplotlib.use('Agg')
import figstyle_release as FS
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import statistical_tests as ST             # release scripts (read only): score groups, generator names

_rc = dict(plt.rcParams)
_spec = importlib.util.spec_from_file_location('house_figstyle', str(P.HERE / 'figstyle.py'))
HOUSE = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(HOUSE)
plt.rcParams.update(_rc)
plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic',
                     'mathtext.bf': 'Times New Roman:bold'})   # review F11: math in Times New Roman (was STIX)

C = P.C
GROUP_PAPER = {'Orientation distribution': 'Trace-direction distribution', 'Orientation clusters': 'Trace-direction clusters', 'Length': 'Trace length',
               'Density': 'Density and spacing', 'Topology': 'Topology', 'All': 'All'}


def save(fig, name):
    probs = HOUSE.check_layout(fig, P.SIZES)
    if probs:
        fig.savefig(str(P.SCRATCH / (name + '_FAILED_preview.png')), dpi=150)
        raise RuntimeError('%s:\n  ' % name + '\n  '.join(probs))
    w, h = fig.get_size_inches() * 2.54
    print('%s: %s; house check clean; %.2f x %.2f cm' % (name, FS.save(fig, str(P.OUT / name), allow_font_sizes=P.SIZES), w, h))


# ---------------------------------------------------------------- Figure 10: ablation counts by group (summed over the 3 tests)
def fig10():
    AC = pd.read_csv(P.TAB / 'recount_ablation_counts.csv')
    fig, axs = plt.subplots(2, 1, figsize=(P.W, 11.0 * P.CM))
    grp = [g for g, _ in ST.GROUPS] + ['All']
    for ax, (comp, title) in zip(axs, (('Geology-informed terms, dual latent', '(a) Full EVAE against EVAE without geology-informed constraints'),
                                      ('Dual vs single latent, with terms', '(b) Full EVAE against single-latent EVAE'))):
        q = AC[AC.comparison == comp].set_index('group').loc[grp]
        y = np.arange(len(grp))[::-1]; tot = (q.better + q.no_difference + q.worse).values
        ax.barh(y, q.better, color='#3A3A3A', height=0.62); ax.barh(y, q.no_difference, left=q.better, color='#D4D4D4', height=0.62)
        nz = q.worse.values > 0                                    # no zero-width bars (their edges would show as stray marks)
        ax.barh(y[nz], q.worse.values[nz], left=(q.better + q.no_difference).values[nz], color='white', edgecolor='k', hatch='////', lw=0.6, height=0.62)
        for yi, (b_, n_, w_), t_ in zip(y, q[['better', 'no_difference', 'worse']].values, tot):
            ax.text(t_ + 1.5, yi, '%d / %d / %d' % (b_, n_, w_), va='center', fontsize=10)
        ax.set_yticks(y); ax.set_yticklabels([GROUP_PAPER[g] for g in grp]); ax.set_xlim(0, 150); ax.set_xticks([0, 38, 76, 114])
        ax.set_title(title, loc='left', fontsize=12, pad=4); ax.spines[['top', 'right']].set_visible(False); ax.tick_params(axis='y', length=0)
    assert tuple(AC[(AC.comparison == 'Geology-informed terms, dual latent') & (AC.group == 'All')][['better', 'no_difference', 'worse']].iloc[0]) == (25, 87, 2)
    assert tuple(AC[(AC.comparison == 'Dual vs single latent, with terms') & (AC.group == 'All')][['better', 'no_difference', 'worse']].iloc[0]) == (2, 106, 6)
    axs[1].set_xlabel('Score × test comparisons (38 scores × 3 tests = 114)')
    fig.legend(handles=[Patch(fc='#3A3A3A', label='Full EVAE better'), Patch(fc='#D4D4D4', label='Not significantly different'),
                        Patch(fc='white', ec='k', hatch='////', label='Full EVAE worse')],
               loc='lower center', ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.07, 1, 1), h_pad=1.2)
    for ax in axs:                                     # the long titles start at the left margin of the figure
        pos = ax.get_position()
        ax.set_title(ax.get_title(loc='left'), loc='left', fontsize=12, pad=4, x=(0.01 - pos.x0) / pos.width)
    save(fig, 'Figure_10')
    out = AC[AC.comparison.isin(['Geology-informed terms, dual latent', 'Dual vs single latent, with terms'])].copy()
    out['group'] = out.group.map(GROUP_PAPER)
    out['comparison'] = out.comparison.map({'Geology-informed terms, dual latent': 'Full EVAE against EVAE without geology-informed constraints',
                                            'Dual vs single latent, with terms': 'Full EVAE against single-latent EVAE'})
    out.to_csv(P.OUT / 'Figure_10_values.csv', index=False)


# ---------------------------------------------------------------- Figure S1: pooled length histograms, 4 methods
def figS1():
    lib = C.load_library(); rows = []
    for s in C.SCHEMES:
        for fi, test in enumerate(C.folds(s, lib)):
            sp = C.split(s, fi, lib)
            for b in test:
                byname = {'Held-out': [sp['panels'][b]['lines']], **{m: [C.load_net(C.net_path(s, m, fi, b, sd, d)) for sd in C.SEEDS for d in range(C.NDRAW)] for m in ST.GEN}}
                for m, LL in byname.items():
                    for L in LL:
                        L = np.asarray(L, float).reshape(-1, 4)
                        if len(L): rows.append(pd.DataFrame(dict(method=m, length=C.common.geom(L)[1] * C.M, w=1.0 / len(LL))))
    TR = pd.concat(rows, ignore_index=True); lb = np.arange(0, 31, 1.0); ORD = ['Held-out', 'EVAE', 'ADFNE', 'KDE']
    TITLE = {'Held-out': 'Held-out windows', 'EVAE': 'EVAE', 'ADFNE': 'ADFNE', 'KDE': 'KDE'}
    hh = np.histogram(TR[TR.method == 'Held-out'].length, bins=lb, density=True)[0]
    fig, axs = plt.subplots(2, 2, figsize=(P.W, 9.5 * P.CM), sharex=True, sharey=True); hmax = 0
    meds = {}
    for ax, m in zip(axs.ravel(), ORD):
        a = TR[TR.method == m]; h = np.histogram(a.length, bins=lb, weights=a.w, density=True)[0]; hmax = max(hmax, h.max())
        ax.bar(lb[:-1] + 0.5, h, width=0.9, color=P.METHOD_COL[m], alpha=0.8)
        if m != 'Held-out': ax.step(lb, np.r_[hh, hh[-1]], where='post', color='k', lw=0.9)
        med = np.median(np.repeat(a.length.values, np.maximum(1, np.round(a.w.values * 24).astype(int)))); meds[m] = round(float(med), 1)
        ax.set_title('%s, median %.1f m' % (TITLE[m], med), fontsize=12, pad=4, color='k')   # review F8: black text (KDE sky blue low contrast)
        ax.set_xlim(0, 30); ax.set_xticks([0, 10, 20, 30])
    assert meds == {'Held-out': 5.7, 'EVAE': 5.4, 'ADFNE': 4.6, 'KDE': 5.2}, meds
    for ax in axs.ravel(): ax.set_ylim(0, hmax * 1.12)
    axs[0, 1].axvline(20, color='k', ls='--', lw=0.8); axs[0, 1].text(19.3, hmax * 1.07, 'decoder\nlimit', fontsize=10, ha='right', va='top')
    for ax in axs[1]: ax.set_xlabel('Trace length (m)')
    for ax in axs[:, 0]: ax.set_ylabel('Share per metre')
    fig.legend(handles=[Line2D([], [], color='k', lw=0.9, label='Held-out windows (outline)')], loc='lower center', frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.065, 1, 1), h_pad=0.8, w_pad=0.8)
    save(fig, 'Figure_S3')
    pd.DataFrame([dict(method=m, median_length_m=v, clipped_traces_weighted=round(float(TR[TR.method == m].w.sum()), 2)) for m, v in meds.items()]).to_csv(P.OUT / 'Figure_S3_values.csv', index=False)


if __name__ == '__main__':
    import sys
    for w_ in sys.argv[1:] or ['10', 'S1']:
        {'10': fig10, 'S1': figS1}[w_]()
