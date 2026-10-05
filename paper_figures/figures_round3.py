# -*- coding: utf-8 -*-
"""Round-3 data figures (PLAN_ROUND3_AUTHOR_COMMENTS_2026-10-03, Sections C and H), main hold-out test only
(release S1: 20 held-out windows, 4 folds), terms of GLOSSARY.md round 3. 14.65 cm wide, Times New Roman 12 pt
(10 pt ticks, values and legends), PNG 600 dpi + PDF into out/figures, every figure through the house check
(figstyle.check_layout with the GLOSSARY term check), the release check (figstyle_release) and, where texts sit in a
plot, the no-text-on-points check (helpers of figures.py).

  Figure_5   example windows A to D (round3_common.EXAMPLES, all in the hold-out test): window map, and for each window
             the mapped traces and one EVAE realisation (local generation; run seed 1337, first realisation), traces
             coloured by trace-direction cluster (old Fig. 6 drawing).
  Figure_6   trace directions (roses, 10° bins) and clipped trace lengths (1 m bins) of the 20 held-out windows:
             (a, c) local generation, (b, d) representative generation, each against the mapped windows (outline);
             24 realisations per window weighted 1/24 (old Fig. 7 drawing, one test).
  Figure_8   example windows A to D: mapped, EVAE, ADFNE, KDE (run seed 1337, first realisation), crossings (X) and
             T-ends (Y) marked (release topology rules: crossing of two traces; uncensored end within 0.3 m of another
             trace); trace and intersection counts in the titles (old Fig. 11 drawing).
  Figure_9   trace-direction roses and length histograms: EVAE, ADFNE, KDE, each against the mapped windows.
  Figure_10  connectivity: (a) intersections per 100 m² and (b) connections per trace, window values of the 20
             held-out windows (generators: median of 24 realisations; box plots), (c) node types: shares of free ends
             (I), T-ends (Y) and crossings (X) pooled over all maps of each method.
  Figure_S2  window-by-window agreement (old Fig. 8; all three tests, renamed: hold-out test, whole-bench test,
             40 m-stretch test).
Data (read only): release realisations and tables; work/round3_data (round3_compute.py: traces, node counts, window
values, all checked against the release). Values next to each figure (Figure_N_values.csv).
Usage: python -B figures_round3.py [5] [6] [8] [9] [10] [S2]"""
import sys, importlib.util
import numpy as np, pandas as pd
import figures as F                         # helpers and release imports (pr_common, figstyle_release, house check)
import round3_common as R3
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D

P = F.P; C = F.C; LIB = F.LIB
TR = pd.read_csv(R3.DATA / 'round3_traces.csv'); TR = TR[TR.scheme == 'S1']
NODES = pd.read_csv(R3.DATA / 'round3_node_counts.csv'); NODES = NODES[NODES.scheme == 'S1']
WV = pd.read_csv(R3.DATA / 'round3_window_values.csv'); WV = WV[WV.scheme == 'S1']
MLAB = {'Held-out': 'Mapped', 'EVAE': 'EVAE', 'Representative': 'EVAE, representative', 'ADFNE': 'ADFNE', 'KDE': 'KDE'}
COL = {'Held-out': '#333333', 'EVAE': '#009E73', 'Representative': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}
R3.check_examples()


def ex_data(e):
    b, fi = e['box'], e['fold']; sp = C.split('S1', fi, LIB)
    return sp['panels'][b]['lines'], LIB[b]['y_max']


# ---------------------------------------------------------------- Figure 5
def fig5():
    fig = plt.figure(figsize=(P.W, 16.0 * P.CM))
    outer = fig.add_gridspec(2, 1, height_ratios=[0.85, 2.3], hspace=0.62 / ((0.85 + 2.3) / 2))
    gs_ex = outer[1].subgridspec(2, 5, width_ratios=[1, 1, 0.22, 1, 1], hspace=0.3, wspace=0.1)
    ax = fig.add_subplot(outer[0])
    man = pd.read_csv(P.RP.BOX_LIBRARY_DIR / 'box_manifest.csv'); pick = {e['box']: e['label'] for e in R3.EXAMPLES}
    grid = np.ones((7, 8, 3))
    for _, r in man.iterrows():
        grid[r['row_index'], r['col'] - 1] = (0.2, 0.2, 0.2) if r['box'] in pick else ((0.9, 0.9, 0.9) if r['usable'] else (1, 1, 1))
    ax.imshow(grid, extent=(0, 8, 7, 0), interpolation='nearest', aspect=0.45)
    for x in range(9): ax.axvline(x, color='white', lw=1.5)
    for y in range(8): ax.axhline(y, color='white', lw=1.5)
    for b, lab in pick.items():
        r = man[man.box == b].iloc[0]; ax.text(r['col'] - 0.5, r['row_index'] + 0.5, lab, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    ax.set_xlim(0, 8); ax.set_ylim(7, 0)
    ax.set_xticks(np.arange(8) + 0.5); ax.set_xticklabels([str(i) for i in range(1, 9)]); ax.set_yticks(np.arange(7) + 0.5)
    ax.set_yticklabels(['W%02d' % i for i in range(7)]); ax.tick_params(length=0, pad=2); [s_.set_visible(False) for s_ in ax.spines.values()]
    ax.set_xlabel('Window column (white cells: not used)'); ax.set_ylabel('Bench face')
    vals = []
    for i, e in enumerate(R3.EXAMPLES):
        b, fi = e['box'], e['fold']; real, ym = ex_data(e); gen = C.load_net(C.net_path('S1', 'EVAE', fi, b, 1337, 0))
        a1 = fig.add_subplot(gs_ex[i // 2, 3 * (i % 2)]); a2 = fig.add_subplot(gs_ex[i // 2, 3 * (i % 2) + 1])
        for a_, L in ((a1, real), (a2, gen)):
            a_.add_patch(Rectangle((0, 0), C.M, ym * C.M, fill=False, ec='#999999', lw=0.6)); F.draw_traces(a_, L, 'S1', fi)
        F.panel_axes(a1, ym); F.panel_axes(a2, ym, ticks=False); a1.set_anchor('N'); a2.set_anchor('N')
        n1, n2 = len(np.asarray(real).reshape(-1, 4)), len(np.asarray(gen).reshape(-1, 4))
        a1.set_title('Mapped, %d traces' % n1, fontsize=10, pad=2); a2.set_title('EVAE, %d traces' % n2, fontsize=10, pad=2)
        a1.annotate('%s  %s%s' % (e['label'], P.wid(b), ' (difficult)' if e['role'] == 'difficult' else ''), xy=(1.06, 1), xycoords='axes fraction',
                    xytext=(-14 * (i % 2), 15), textcoords='offset points', ha='center', va='bottom', fontsize=12)
        vals.append(dict(window=e['label'], window_id=P.wid(b), fold=fi + 1, mapped_traces=n1, evae_traces=n2, run_seed=1337, realisation=1))
    fig.legend(handles=[Line2D([], [], color=c, lw=2) for c in P.CLU_COL], labels=P.CLU_LABEL, loc='lower center', ncol=5, frameon=False,
               fontsize=10, bbox_to_anchor=(0.5, 0.0), title='Trace-direction cluster', title_fontsize=10, handlelength=0.9, handletextpad=0.35, columnspacing=0.4)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.97, bottom=0.11)
    F.save(fig, 'Figure_5')
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_5_values.csv', index=False)


# ---------------------------------------------------------------- roses and length histograms (Figs. 6 and 9)
BINS = np.radians(np.arange(0, 361, 10)); CEN = BINS[:-1] + np.radians(5); LB = np.arange(0, 31, 1.0)


def rose(a):
    th = np.radians(np.r_[a.theta.values, a.theta.values + 180]); w = np.r_[a.weight.values, a.weight.values]
    h, _ = np.histogram(th, bins=BINS, weights=w); return h / h.sum()


def lenhist(a):
    return np.histogram(a.length, bins=LB, weights=a.weight, density=True)[0]


def roses_lengths(methods, titles, name, alphas):
    n = len(methods)
    fig = plt.figure(figsize=(P.W, (10.6 if n == 3 else 11.6) * P.CM)); gs = fig.add_gridspec(2, n, height_ratios=[1.15, 1], hspace=0.45, wspace=0.35)
    hh = rose(TR[TR.method == 'Held-out']); lr = lenhist(TR[TR.method == 'Held-out'])
    rmax = max([rose(TR[TR.method == m]).max() for m in methods] + [hh.max()]) * 1.08
    hmax = 0; vals = []
    for j, (m, t) in enumerate(zip(methods, titles)):
        ax = fig.add_subplot(gs[0, j], projection='polar'); he = rose(TR[TR.method == m])
        ax.bar(CEN, he, width=np.radians(10), color=COL[m], alpha=alphas[j], edgecolor='w', linewidth=0.3)
        ax.plot(np.r_[CEN, CEN[0]], np.r_[hh, hh[0]], color='k', lw=0.9)
        ax.set_theta_zero_location('E'); ax.set_theta_direction(-1); ax.set_ylim(0, rmax); ax.set_yticklabels([])
        ax.set_xticks(np.radians(np.arange(0, 360, 45))); ax.set_xticklabels(['%d°' % d for d in range(0, 360, 45)], fontsize=10)
        ax.tick_params(axis='x', pad=3.5); ax.grid(lw=0.3); ax.set_title(t, fontsize=12, pad=16)
        axl = fig.add_subplot(gs[1, j]); a = TR[TR.method == m]; h = lenhist(a)
        axl.bar(LB[:-1] + 0.5, h, width=0.9, color=COL[m], alpha=alphas[j])
        axl.step(LB, np.r_[lr, lr[-1]], where='post', color='k', lw=0.9); axl.axvline(20, color='k', ls='--', lw=0.8)
        hmax = max(hmax, h.max(), lr.max()); axl.set_xlim(0, 30); axl.set_xticks([0, 10, 20, 30]); axl.set_xlabel('Trace length (m)')
        if j == 0: axl.set_ylabel('Share per metre')
        w = a.weight.values; L = a.length.values; o = np.argsort(L); cw = np.cumsum(w[o]) / w.sum()
        vals.append(dict(method=MLAB[m], weighted_clipped_traces=round(float(w.sum()), 3), median_length_m=round(float(L[o][np.searchsorted(cw, 0.5)]), 3),
                         share_longer_than_20m=round(float(w[L > 20].sum() / w.sum()), 4), max_length_m=round(float(L.max()), 2),
                         rose_max_share=round(float(he.max()), 4)))
    for ax in fig.axes:
        if ax.name != 'polar':
            ax.set_ylim(0, hmax * 1.45); ax.text(19.3, hmax * 1.4, 'decoder\nlimit', fontsize=10, va='top', ha='right')
    a = TR[TR.method == 'Held-out']; vals.append(dict(method='Mapped', weighted_clipped_traces=float(a.weight.sum()), median_length_m=round(float(np.median(a.length)), 3),
                                                      share_longer_than_20m=round(float((a.length > 20).mean()), 4), max_length_m=round(float(a.length.max()), 2),
                                                      rose_max_share=round(float(hh.max()), 4)))
    return fig, vals


def fig6():
    fig, vals = roses_lengths(['EVAE', 'Representative'], ['(a) Local generation', '(b) Representative generation'], 'Figure_6', [0.75, 0.4])
    for ax, t in zip([a for a in fig.axes if a.name != 'polar'], ['(c) Local generation', '(d) Representative generation']):
        ax.set_title(t, fontsize=12, pad=4)
    fig.legend(handles=[Patch(fc=COL['EVAE'], alpha=0.75, label='EVAE, local (24 realisations per window)'),
                        Patch(fc=COL['EVAE'], alpha=0.4, label='EVAE, representative (24 per window)'),
                        Line2D([], [], color='k', lw=0.9, label='Mapped held-out windows (20)')],
               loc='lower center', ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0), columnspacing=1.0)
    fig.subplots_adjust(left=0.12, right=0.93, top=0.84, bottom=0.23, hspace=0.75)
    F.save(fig, 'Figure_6')
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_6_values.csv', index=False)


def fig9():
    fig, vals = roses_lengths(['EVAE', 'ADFNE', 'KDE'], ['EVAE', 'ADFNE', 'KDE'], 'Figure_9', [0.75, 0.75, 0.75])
    fig.legend(handles=[Patch(fc=COL[m], alpha=0.75, label=m) for m in ('EVAE', 'ADFNE', 'KDE')] +
               [Line2D([], [], color='k', lw=0.9, label='Mapped held-out windows')],
               loc='lower center', ncol=4, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0), columnspacing=1.0)
    fig.subplots_adjust(left=0.1, right=0.95, top=0.84, bottom=0.2)
    F.save(fig, 'Figure_9')
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_9_values.csv', index=False)


# ---------------------------------------------------------------- Figure 8
def nodes_xy(L, ym):
    """crossing points (X) and T-end points (Y), release topology rules (topology.py: TOL 0.3 m, EDGE 0.1 m), metres"""
    import topology as TP
    L = np.asarray(L, float).reshape(-1, 4); n = len(L)
    if n < 2:
        return np.zeros((0, 2)), np.zeros((0, 2))
    X = np.asarray(C.common.crossings_xy(L), float).reshape(-1, 4)[:, 2:4] * C.M   # rows (i, j, x, y)
    Lm = L * C.M; W, H = C.M, ym * C.M
    E = np.vstack([Lm[:, :2], Lm[:, 2:]]); own = np.r_[np.arange(n), np.arange(n)]
    inside = (E[:, 0] > TP.EDGE) & (E[:, 0] < W - TP.EDGE) & (E[:, 1] > TP.EDGE) & (E[:, 1] < H - TP.EDGE)
    D = TP._pt_seg(E, Lm[:, :2], Lm[:, 2:]); D[np.arange(2 * n), own] = np.inf
    Y = E[inside & (D.min(1) <= TP.TOL)]
    tp = TP.topology(L, ym); assert tp['n_X'] == len(X) and tp['n_Y'] == len(Y), (tp, len(X), len(Y))
    return X, Y


def fig8():
    data = []
    for e in R3.EXAMPLES:
        real, ym = ex_data(e)
        data.append((e, ym, {'Held-out': real, **{m: C.load_net(C.net_path('S1', m, e['fold'], e['box'], 1337, 0)) for m in C.METHODS}}))
    fig, axs = plt.subplots(len(data), 4, figsize=(P.W, 19.0 * P.CM), gridspec_kw=dict(height_ratios=[d[1] for d in data]))
    order = ['Held-out', 'EVAE', 'ADFNE', 'KDE']; vals = []
    for i, (e, ym, nets) in enumerate(data):
        for j, m in enumerate(order):
            ax = axs[i, j]; L = np.asarray(nets[m], float).reshape(-1, 4)
            for x1, y1, x2, y2 in L * C.M:
                ax.plot([x1, x2], [y1, y2], color='0.25', lw=0.8, solid_capstyle='round', zorder=2)
            X, Y = nodes_xy(L, ym)
            if len(Y): ax.scatter(Y[:, 0], Y[:, 1], s=13, marker='^', fc='white', ec='#CC3311', lw=0.9, zorder=3)
            if len(X): ax.scatter(X[:, 0], X[:, 1], s=13, marker='o', fc='#CC3311', ec='#CC3311', lw=0.5, zorder=4)
            ax.add_patch(Rectangle((0, 0), C.M, ym * C.M, fill=False, ec=COL[m] if m != 'Held-out' else '#333333', lw=1.4))
            F.panel_axes(ax, ym, yticks=(j == 0))
            if j > 0: ax.set_xticks([10, 20])
            ax.set_title('%d traces\n%d intersection%s' % (len(L), len(X), '' if len(X) == 1 else 's'), fontsize=10, pad=2, color='k', linespacing=1.1)
            vals.append(dict(window=e['label'], window_id=P.wid(e['box']), method=MLAB[m], run_seed=1337, realisation=1, traces=len(L),
                             intersections_X=len(X), t_ends_Y=len(Y), intersections_per_100m2=round(100 * len(X) / (400 * ym), 3)))
            if i == 0:
                ax.annotate(MLAB[m], xy=(0.5, 1), xycoords='axes fraction', xytext=(0, 30), textcoords='offset points', ha='center', va='bottom', fontsize=12)
            if j == 0:
                ax.set_ylabel('%s  %s%s' % (e['label'], P.wid(e['box']), '\n(difficult)' if e['role'] == 'difficult' else ''), fontsize=12, linespacing=1.3)
            if i == len(data) - 1: ax.set_xlabel('Along the wall (m)', fontsize=10)
    fig.legend(handles=[Line2D([], [], ls='', marker='o', ms=4.5, mfc='#CC3311', mec='#CC3311', label='Intersection (crossing, X)'),
                        Line2D([], [], ls='', marker='^', ms=4.5, mfc='white', mec='#CC3311', mew=0.9, label='T-end (Y)')],
               loc='lower center', ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.035, 1, 1), h_pad=0.4, w_pad=0.3)
    F.save(fig, 'Figure_8', extra=(F.legend_inside,))
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_8_values.csv', index=False)


# ---------------------------------------------------------------- Figure 10
def fig10():
    ORDm = ['Held-out', 'EVAE', 'ADFNE', 'KDE']
    fig = plt.figure(figsize=(P.W, 7.6 * P.CM)); gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.15], wspace=0.55)
    vals = []
    for j, (k, t) in enumerate((('P22', '(a) Intersections\nper 100 m²'), ('CL', '(b) Connections\nper trace'))):
        ax = fig.add_subplot(gs[0, j]); data = [WV[WV.method == m][k].dropna().values for m in ORDm]
        bp = ax.boxplot(data, tick_labels=['Mapped', 'EVAE', 'ADFNE', 'KDE'], patch_artist=True, widths=0.6, showfliers=False, whis=1.5,
                        medianprops=dict(color='k', lw=2.0, solid_capstyle='butt'), whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7), boxprops=dict(lw=0.7))
        for patch, m in zip(bp['boxes'], ORDm):
            patch.set_facecolor(COL[m] if m != 'Held-out' else '#BBBBBB'); patch.set_alpha(0.85)
        ax.set_title(t, fontsize=12, loc='left', pad=4); ax.tick_params(axis='x', labelsize=10, rotation=90, length=0); ax.tick_params(axis='y', labelsize=10)
        ax.set_ylim(0, None)
        for m, d in zip(ORDm, data):
            q1, med, q3 = np.percentile(d, [25, 50, 75])
            vals.append(dict(part='ab'[j], measure=k, method=MLAB[m], n_windows=len(d), median=round(float(med), 4), q1=round(float(q1), 4), q3=round(float(q3), 4)))
    ax = fig.add_subplot(gs[0, 2]); left = np.zeros(4); NC = {'n_I': ('Free end (I)', '#DDDDDD'), 'n_Y': ('T-end (Y)', '#888888'), 'n_X': ('Crossing (X)', '#CC3311')}
    tot = {m: NODES[NODES.method == m][['n_I', 'n_Y', 'n_X']].sum() for m in ORDm}
    for c, (lab, col) in NC.items():
        sh = np.array([tot[m][c] / tot[m].sum() for m in ORDm])
        ax.barh(np.arange(4), sh, left=left, color=col, ec='k', lw=0.5, height=0.6, label=lab); left += sh
        for m, v in zip(ORDm, sh):
            vals.append(dict(part='c', measure='share of nodes, ' + lab, method=MLAB[m], n_nodes=int(tot[m].sum()), count=int(tot[m][c]), median=round(float(v), 4)))
    ax.set_yticks(np.arange(4)); ax.set_yticklabels(['Mapped', 'EVAE', 'ADFNE', 'KDE'], fontsize=10); ax.invert_yaxis()
    ax.set_xlim(0, 1); ax.set_xticks([0, 0.5, 1]); ax.tick_params(axis='x', labelsize=10); ax.set_xlabel('Share of nodes', fontsize=10)
    ax.set_title('(c) Node types', fontsize=12, loc='left', pad=4)
    fig.legend(handles=[Patch(fc=col, ec='k', lw=0.5, label=lab) for lab, col in NC.values()], loc='lower center', ncol=3, frameon=False, fontsize=10,
               bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.36)
    F.save(fig, 'Figure_10', extra=(F.legend_inside,))
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_10_values.csv', index=False)


# ---------------------------------------------------------------- Figure S2 (old Fig. 8, all three tests renamed)
def figS2():
    """old Fig. 8 drawn by figures.fig8 (all three tests, round-3 test names from pr_common), saved as Figure_S2"""
    orig_save = F.save
    F.save = lambda fig, name, extra=(F.check_points, F.legend_inside): orig_save(fig, 'Figure_S2', extra)
    try:
        F.fig8()
    finally:
        F.save = orig_save


if __name__ == '__main__':
    what = sys.argv[1:] or ['5', '6', '8', '9', '10', 'S2']
    for w_ in what:
        {'5': fig5, '6': fig6, '8': fig8, '9': fig9, '10': fig10, 'S2': figS2}[w_]()
