# -*- coding: utf-8 -*-
"""Paper figures built from the release drawing code (copy of the release paper/code/figures.py, final-paper version of
1 Oct 2026; numbering of work/GLOSSARY.md Section 5). 14.65 cm wide, Times New Roman 12 pt (10 pt ticks, values and
legends), PNG 600 dpi + PDF into out/figures. Every figure passes the release layout check (figstyle_release: fonts,
sizes, no overlaps, no text on data or on other plots, figure legends off the plots), the house check
(figstyle.check_layout) and, where texts sit inside a plot, the no-text-on-points check.

The data are the release files, read only (paper/example_panels.json, paper/tables, the realisation files in networks/, data); the plotted values
are those of the release figures. Changes against the release drawings are label strings only (GLOSSARY terms):

  Figure_6           release Fig_R1_examples drawing WITHOUT photographs (author decision of 2 Oct 2026: the mine
                     operator does not permit photographs; the photograph branch was removed): window map with the
                     example windows A to D and, for each, the held-out traces (grey window outline) and one EVAE
                     realisation (run seed 1337, first realisation), traces by trace-direction cluster.
                     Labels (GLOSSARY 4b, 2 Oct 2026): x axis "Window column (white cells: not used)" with columns 1 to 8,
                     titles with window IDs W03-2 etc. and "(difficult)" for window D; legend "C1 (about 125°)" ...
                     "Unclustered traces" (was "C1 (~125°)" ... "unclustered"), rebuilt on one line with tighter spacing.
  Figure_7           release Fig_R2_geometry: legend "EVAE (24 realisations per window case)" and "Held-out windows".
  Figure_8           release Fig_R4_panel_by_panel (as rev_release_figs.py: title "$P_{21}$ (m/m²)", gap-filling points on
                     top): x label "Held-out window"; y label "EVAE, median of 24".
  Figure_11          release Fig_D1_comparison: row labels "A  W03-2 / gap-filling test" (test names in full, the difficult
                     window on a third line, "(difficult)"; GLOSSARY 4b window IDs).
Usage: python -B figures.py [6] [7] [8] [11]       (default: all)"""
import json, importlib.util
import numpy as np, pandas as pd
import pr_common as P
import matplotlib
matplotlib.use('Agg')
import figstyle_release as FS              # release figure style (Times New Roman) and layout check (copy)
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
import setbg as SB                         # release src/study (read only)
import make_figures as MF                  # release scripts (read only)

_rc = dict(plt.rcParams)
_spec = importlib.util.spec_from_file_location('house_figstyle', str(P.HERE / 'figstyle.py'))
HOUSE = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(HOUSE)
plt.rcParams.update(_rc)
plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic',
                     'mathtext.bf': 'Times New Roman:bold'})   # review F11: math in Times New Roman (was STIX)

C = P.C
EX = json.load(open(P.PR / 'example_panels.json'))['panels']
LIB = C.load_library()
P21 = r'$P_{21}$ (m/m²)'


def check_points(fig):
    """texts inside a plot must not sit on scatter points"""
    fig.canvas.draw(); r = fig.canvas.get_renderer(); probs = []
    for ax in fig.axes:
        for t in ax.texts:
            if not t.get_visible() or not t.get_text().strip(): continue
            bb = t.get_window_extent(r).expanded(1.0, 1.0)
            for col in ax.collections:
                xy = col.get_offset_transform().transform(col.get_offsets())
                if len(xy) and np.any((xy[:, 0] > bb.x0 - 4) & (xy[:, 0] < bb.x1 + 4) & (xy[:, 1] > bb.y0 - 4) & (xy[:, 1] < bb.y1 + 4)):
                    probs.append('%r sits on scatter points' % t.get_text()[:30])
    return probs


def legend_inside(fig):
    """figure legends must stay inside the figure width and hold no '~'"""
    fig.canvas.draw(); r = fig.canvas.get_renderer(); W = fig.bbox.width; probs = []
    for lg in fig.legends:
        bb = lg.get_window_extent(r)
        if bb.x0 < 0 or bb.x1 > W:
            probs.append('legend runs outside the figure (%.0f to %.0f of %.0f px)' % (bb.x0, bb.x1, W))
        if any('~' in t.get_text() for t in lg.get_texts()):
            probs.append('legend still holds "~"')
    return probs


def save(fig, name, extra=(check_points, legend_inside)):
    probs = [p for chk in extra for p in chk(fig)] + HOUSE.check_layout(fig, P.SIZES)
    if probs:
        fig.savefig(str(P.SCRATCH / (name + '_FAILED_preview.png')), dpi=150)
        raise RuntimeError('%s:\n  ' % name + '\n  '.join(probs))
    w, h = fig.get_size_inches() * 2.54
    msg = FS.save(fig, str(P.OUT / name), allow_font_sizes=P.SIZES)          # release check again, then PNG 600 dpi + PDF
    print('%s: %s; house check clean; %.2f x %.2f cm' % (name, msg, w, h))


def cluster_of(L, s, fi):
    L = np.asarray(L, float).reshape(-1, 4)
    if not len(L): return np.zeros(0, int)
    m = C.cluster_model(s, fi); return MF.canon(SB.classify(C.common.geom(L)[2], m), m)


def draw_traces(ax, L, s, fi, stroke=False):
    L = np.asarray(L, float).reshape(-1, 4); k = cluster_of(L, s, fi)
    for (x1, y1, x2, y2), c in zip(L * C.M, k):
        ln, = ax.plot([x1, x2], [y1, y2], color=P.CLU_COL[c], lw=1.0, solid_capstyle='round')
        if stroke: ln.set_path_effects([pe.Stroke(linewidth=1.9, foreground='white'), pe.Normal()])


def panel_axes(ax, ym, ticks=True, yticks=True):
    ax.set_xlim(-0.4, C.M + 0.4); ax.set_ylim(ym * C.M + 0.4, -0.4); ax.set_aspect('equal')
    ax.set_xticks([0, 10, 20] if ticks else []); ax.set_yticks([t for t in (0, 10, 20) if t <= ym * C.M + 1e-6] if (ticks and yticks) else [])
    ax.tick_params(length=2, pad=1.5)
    for sp_ in ax.spines.values(): sp_.set_visible(False)


# ---------------------------------------------------------------- Figure 6 (release fig_r1)
FIG6_ROW_GAP, FIG6_HEIGHT_CM = 0.3, 16.0      # VL-10: row gap 0.3 of a row height (A/B to C/D); height was 17.2 cm


def fig6():
    fig = plt.figure(figsize=(P.W, FIG6_HEIGHT_CM * P.CM))
    # review VL-10 (2 Oct 2026): the map keeps a clear gap above the examples, the gap
    # between the A/B and C/D rows is smaller (FIG6_ROW_GAP of a row height), and the window pairs are top-aligned
    outer = fig.add_gridspec(2, 1, height_ratios=[0.85, 2 + FIG6_ROW_GAP], hspace=0.62 / ((0.85 + 2 + FIG6_ROW_GAP) / 2))
    gs_ex = outer[1].subgridspec(2, 5, width_ratios=[1, 1, 0.22, 1, 1], hspace=FIG6_ROW_GAP, wspace=0.1)
    # window map: 8 window columns x 7 bench faces, drawn as an image; example windows dark and lettered
    ax = fig.add_subplot(outer[0])
    man = pd.read_csv(P.RP.BOX_LIBRARY_DIR / 'box_manifest.csv'); pick = {e['panel']: e['label'] for e in EX}
    grid = np.ones((7, 8, 3))
    for _, r in man.iterrows():
        grid[r['row_index'], r['col'] - 1] = (0.2, 0.2, 0.2) if r['box'] in pick else ((0.9, 0.9, 0.9) if r['usable'] else (1, 1, 1))
    ax.imshow(grid, extent=(0, 8, 7, 0), interpolation='nearest', aspect=0.45)
    for x in range(9): ax.axvline(x, color='white', lw=1.5)
    for y in range(8): ax.axhline(y, color='white', lw=1.5)
    for b, lab in pick.items():
        r = man[man.box == b].iloc[0]; ax.text(r['col'] - 0.5, r['row_index'] + 0.5, lab, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    ax.set_xlim(0, 8); ax.set_ylim(7, 0)
    ax.set_xticks(np.arange(8) + 0.5); ax.set_xticklabels([str(i) for i in range(1, 9)]); ax.set_yticks(np.arange(7) + 0.5); ax.set_yticklabels(['W%02d' % i for i in range(7)])
    ax.tick_params(length=0, pad=2); [s_.set_visible(False) for s_ in ax.spines.values()]
    ax.set_xlabel('Window column (white cells: not used)'); ax.set_ylabel('Bench face')
    for i, e in enumerate(EX):
        s, fi, b = e['scheme'], e['fold'], e['panel']; ym = LIB[b]['y_max']; sp = C.split(s, fi, LIB)
        real = sp['panels'][b]['lines']; gen = C.load_net(C.net_path(s, 'EVAE', fi, b, 1337, 0))
        a1 = fig.add_subplot(gs_ex[i // 2, 3 * (i % 2)]); a2 = fig.add_subplot(gs_ex[i // 2, 3 * (i % 2) + 1])
        a1.add_patch(Rectangle((0, 0), C.M, ym * C.M, fill=False, ec='#999999', lw=0.6))     # held-out window outline
        draw_traces(a1, real, s, fi)
        draw_traces(a2, gen, s, fi); a2.add_patch(Rectangle((0, 0), C.M, ym * C.M, fill=False, ec='#999999', lw=0.6))
        panel_axes(a1, ym); panel_axes(a2, ym, ticks=False)
        a1.set_anchor('N'); a2.set_anchor('N')     # review VL-10: the shorter B pair (17.6 m) top-aligned with A
        a1.set_title('Held-out, %d traces' % len(np.asarray(real).reshape(-1, 4)), fontsize=10, pad=2)
        a2.set_title('EVAE, %d traces' % len(np.asarray(gen).reshape(-1, 4)), fontsize=10, pad=2)
        a1.annotate('%s  %s test, %s%s' % (e['label'], e['test'].capitalize(), P.wid(b), ' (difficult)' if e['role'] == 'hard' else ''), xy=(1.06, 1), xycoords='axes fraction',
                    xytext=(-14 * (i % 2), 15), textcoords='offset points', ha='center', va='bottom', fontsize=12)
    fig.legend(handles=[Line2D([], [], color=c, lw=2) for c in P.CLU_COL], labels=P.CLU_LABEL,
               loc='lower center', ncol=5, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0), title='Trace-direction cluster', title_fontsize=10,
               handlelength=0.9, handletextpad=0.35, columnspacing=0.4)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.97, bottom=0.11)
    save(fig, 'Figure_6')


# ---------------------------------------------------------------- Figure 7 (release fig_r2)
def pooled():
    rows = []
    for s in C.SCHEMES:
        for fi, test in enumerate(C.folds(s, LIB)):
            sp = C.split(s, fi, LIB)
            for b in test:
                byname = {'Held-out': [sp['panels'][b]['lines']], 'EVAE': [C.load_net(C.net_path(s, 'EVAE', fi, b, sd, d)) for sd in C.SEEDS for d in range(C.NDRAW)]}
                for m, LL in byname.items():
                    for L in LL:
                        L = np.asarray(L, float).reshape(-1, 4)
                        if len(L):
                            _, ln, th = C.common.geom(L); rows.append(pd.DataFrame(dict(scheme=s, method=m, length=ln * C.M, theta=np.degrees(th), w=1.0 / len(LL))))
    return pd.concat(rows, ignore_index=True)


def fig7():
    TR = pooled()
    fig = plt.figure(figsize=(P.W, 10.6 * P.CM)); gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1], hspace=0.45, wspace=0.35)
    bins = np.radians(np.arange(0, 361, 10)); cen = bins[:-1] + np.radians(5); lb = np.arange(0, 31, 1.0)

    def rose(a):
        th = np.radians(np.r_[a.theta.values, a.theta.values + 180]); w = np.r_[a.w.values, a.w.values]
        h, _ = np.histogram(th, bins=bins, weights=w); return h / h.sum()
    rmax = max(rose(TR[(TR.scheme == s) & (TR.method == m)]).max() for s in C.SCHEMES for m in ('Held-out', 'EVAE')) * 1.08
    hmax = 0
    for j, s in enumerate(C.SCHEMES):
        ax = fig.add_subplot(gs[0, j], projection='polar')
        he, hh = rose(TR[(TR.scheme == s) & (TR.method == 'EVAE')]), rose(TR[(TR.scheme == s) & (TR.method == 'Held-out')])
        ax.bar(cen, he, width=np.radians(10), color=P.METHOD_COL['EVAE'], alpha=0.75, edgecolor='w', linewidth=0.3)
        ax.plot(np.r_[cen, cen[0]], np.r_[hh, hh[0]], color='k', lw=0.9)
        ax.set_theta_zero_location('E'); ax.set_theta_direction(-1); ax.set_ylim(0, rmax); ax.set_yticklabels([])
        ax.set_xticks(np.radians(np.arange(0, 360, 45))); ax.set_xticklabels(['%d°' % d for d in range(0, 360, 45)], fontsize=10)
        ax.tick_params(axis='x', pad=3.5); ax.grid(lw=0.3)   # review F10: 135°, 180°, 225° clear of the circle
        ax.set_title(P.TEST_T[s], fontsize=12, pad=16)
    axs = [fig.add_subplot(gs[1, j]) for j in range(3)]
    for j, (ax, s) in enumerate(zip(axs, C.SCHEMES)):
        a = TR[(TR.scheme == s) & (TR.method == 'EVAE')]; h = np.histogram(a.length, bins=lb, weights=a.w, density=True)[0]
        r = TR[(TR.scheme == s) & (TR.method == 'Held-out')]; hr = np.histogram(r.length, bins=lb, density=True)[0]
        ax.bar(lb[:-1] + 0.5, h, width=0.9, color=P.METHOD_COL['EVAE'], alpha=0.75)
        ax.step(lb, np.r_[hr, hr[-1]], where='post', color='k', lw=0.9)
        ax.axvline(20, color='k', ls='--', lw=0.8); hmax = max(hmax, h.max(), hr.max())
        ax.set_xlim(0, 30); ax.set_xticks([0, 10, 20, 30]); ax.set_xlabel('Trace length (m)')
        if j == 0: ax.set_ylabel('Share per metre')
    for ax in axs:
        ax.set_ylim(0, hmax * 1.45)
        ax.text(19.3, hmax * 1.4, 'decoder\nlimit', fontsize=10, va='top', ha='right')
    fig.legend(handles=[Patch(fc=P.METHOD_COL['EVAE'], alpha=0.75, label='EVAE (24 realisations per window case)'), Line2D([], [], color='k', lw=0.9, label='Held-out windows')],
               loc='lower center', ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.1, right=0.95, top=0.84, bottom=0.2)
    save(fig, 'Figure_7')
    vals = []
    for s in C.SCHEMES:
        for m in ('Held-out', 'EVAE'):
            a = TR[(TR.scheme == s) & (TR.method == m)]
            vals.append(dict(test=P.TEST[s], method=m, traces_or_weighted_traces=round(float(a.w.sum()), 3),
                             share_longer_than_20m=round(float(a.w[a.length > 20].sum() / a.w.sum()), 4), max_length_m=round(float(a.length.max()), 2)))
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_7_values.csv', index=False)


# ---------------------------------------------------------------- Figure 8 (release fig_r4, rev_release_figs.py fig8)
def fig8():
    PR = pd.read_csv(P.TAB / 'panel_properties.csv'); SP = pd.read_csv(P.TAB / 'check_panel_spearman.csv')
    PAR = [('P21', P21, 'P21 (m/m²)'), ('P22', 'Intersections per 100 m²', 'Intersections per 100 m²'),
           ('CL', 'Connections per trace', 'Connections per trace'), ('nn_med', 'Spacing, nearest trace (m)', 'Spacing, nearest trace (m)')]
    # review F7: white edge on the gap-filling circles so that they do not merge with the new-bench squares into black squares
    MK = {'S1': dict(marker='o', fc='k', ec='white'), 'S2': dict(marker='s', fc='white', ec='k'), 'S3': dict(marker='^', fc='#9A9A9A', ec='#555555')}
    ZO = {'S1': 3.2, 'S2': 3.0, 'S3': 3.1}                                     # gap-filling points on top
    fig, axs = plt.subplots(2, 2, figsize=(P.W, 14.2 * P.CM))
    for ax, (k, lab, sp_lab) in zip(axs.ravel(), PAR):
        lo, hi = np.inf, -np.inf
        for s in ('S2', 'S3', 'S1'):                                           # gap-filling drawn last
            q = PR[PR.scheme == s]; x = q[q.method == 'Held-out'].set_index('box')[k]; y = q[q.method == 'EVAE'].set_index('box')[k].reindex(x.index)
            ok = x.notna() & y.notna(); ax.scatter(x[ok], y[ok], s=14, lw=0.6, zorder=ZO[s], **MK[s]); lo = min(lo, x[ok].min(), y[ok].min()); hi = max(hi, x[ok].max(), y[ok].max())
        pad = 0.05 * (hi - lo); lo_, hi_ = lo - pad, hi + pad; top = hi_ + 0.62 * (hi_ - lo_)   # review F7: points at 0 not clipped
        ax.plot([lo_, top], [lo_, top], color='#888888', ls='--', lw=0.8, zorder=1)
        ax.set_xlim(lo_, hi_ + 0.25 * (hi_ - lo_)); ax.set_ylim(lo_, top)
        rho = SP[SP.parameter.str.startswith(sp_lab.split(' (')[0].split(',')[0])]
        assert len(rho) == 3, (sp_lab, len(rho))
        txt = '\n'.join(('%s ρ = %.2f' % (P.TEST[s].capitalize(), rho[rho.test == P.REL_TEST[s]]['rho EVAE'].iloc[0])).replace('= -', '= −') for s in C.SCHEMES)
        ax.text(0.03, 0.97, txt, transform=ax.transAxes, fontsize=10, va='top', ha='left')
        ax.set_title(lab, fontsize=12, pad=4); ax.set_xlabel('Mapped held-out window'); ax.set_ylabel('EVAE, median of 24')
    fig.legend(handles=[Line2D([], [], ls='', markersize=5, markeredgewidth=0.6, label=P.TEST_T[s], **{'marker': MK[s]['marker'], 'markerfacecolor': MK[s]['fc'], 'markeredgecolor': MK[s]['ec']})
                        for s in C.SCHEMES] + [Line2D([], [], color='#888888', ls='--', lw=0.8, label='1:1')],
               loc='lower center', ncol=4, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0), columnspacing=1.2, handletextpad=0.4)
    fig.tight_layout(rect=(0, 0.06, 1, 1), h_pad=1.2, w_pad=1.6)
    save(fig, 'Figure_8')


# ---------------------------------------------------------------- Figure 11 (release fig_d1)
def fig11():
    data = []
    for e in EX:
        s, fi, b = e['scheme'], e['fold'], e['panel']; sp = C.split(s, fi, LIB); ym = LIB[b]['y_max']
        data.append((e, ym, {'Held-out': sp['panels'][b]['lines'], **{m: C.load_net(C.net_path(s, m, fi, b, 1337, 0)) for m in C.METHODS}}))
    fig, axs = plt.subplots(len(data), 4, figsize=(P.W, 17.8 * P.CM), gridspec_kw=dict(height_ratios=[d[1] for d in data]))
    order = ['Held-out', 'EVAE', 'ADFNE', 'KDE']; vals = []
    for i, (e, ym, nets) in enumerate(data):
        for j, m in enumerate(order):
            ax = axs[i, j]; L = np.asarray(nets[m], float).reshape(-1, 4) * C.M
            for x1, y1, x2, y2 in L:
                ax.plot([x1, x2], [y1, y2], color='k', lw=0.8, solid_capstyle='round')
            ax.add_patch(Rectangle((0, 0), C.M, ym * C.M, fill=False, ec=P.METHOD_COL[m], lw=1.4))
            panel_axes(ax, ym, yticks=(j == 0))
            if j > 0:                                     # review F8: no '0' next to the '20' of the column to the left
                ax.set_xticks([10, 20])
            # review F8: labels in black (the KDE sky blue on white is low contrast); the method colour stays on the frame
            ax.set_title('%d traces' % len(L), fontsize=10, pad=2, color='k')
            vals.append(dict(window=e['label'], window_id=P.wid(e['panel']), release_key=e['panel'], test=e['test'], method=m, run_seed=1337, realisation=1, traces=len(L)))
            if i == 0:
                ax.annotate(m, xy=(0.5, 1), xycoords='axes fraction', xytext=(0, 15), textcoords='offset points', ha='center', va='bottom', fontsize=12,
                            color='k')
            if j == 0:
                ax.set_ylabel('%s  %s\n%s test%s' % (e['label'], P.wid(e['panel']), e['test'], '\n(difficult)' if e['role'] == 'hard' else ''), fontsize=12, linespacing=1.3)
            if i == len(data) - 1: ax.set_xlabel('Along the wall (m)', fontsize=10)
    fig.tight_layout(h_pad=0.5, w_pad=0.3)
    save(fig, 'Figure_11')
    pd.DataFrame(vals).to_csv(P.OUT / 'Figure_11_values.csv', index=False)


if __name__ == '__main__':
    import sys
    what = sys.argv[1:] or ['6', '7', '8', '11']
    for w_ in what:
        {'6': fig6, '7': fig7, '8': fig8, '11': fig11}[w_]()
    left = [p for p in P.SCRATCH.rglob('*') if p.is_file() and not p.name.endswith('_FAILED_preview.png')]
    print('release scratch files written:', left or 'none')
