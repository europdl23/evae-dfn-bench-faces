# -*- coding: utf-8 -*-
"""Figures and tables of the final comparison, computed from the stored networks (no training and no Octave needed).

  figures/Figure_1_plain_comparison   held-out traces | EVAE | ADFNE | KDE, one test box per scheme; the SAME run seed
                                      (1337) and draw (0) for every method (seeds/figure_networks.json)
  figures/Figure_2_rose_0_360         orientation roses over 0-360 deg, all held-out test boxes; black outline = held-out
  figures/Figure_3_length_histograms  trace-length histograms, all held-out test boxes; black outline = held-out
  figures/Figure_4_boxplots           per-box values; dashed line = held-out median; medians and % difference written
  tables/final_properties.csv         per test box: held-out value and the median over the 24 networks of each method
  tables/final_table_all.csv          parameters per scheme for held-out, EVAE, ADFNE, KDE
  tables/final_table_heldout_vs_EVAE.csv
  (all table numbers in one Excel file: scripts/export_excel.py -> tables/final_tables.xlsx)

Usage:  python scripts/make_figures.py            write everything
        python scripts/make_figures.py --check    also compare the recomputed tables with tables/reference/"""
import sys, json, math
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'study'))
import study as C            # noqa: E402
import setbg as SB           # noqa: E402
from topology import topology  # noqa: E402
import repo_paths as RP      # noqa: E402

ORDER = ['Held-out', 'EVAE', 'ADFNE', 'KDE']
GEN = ['EVAE', 'ADFNE', 'KDE']
COL = {'Held-out': '#333333', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}
REF = [125.0, 56.0, 27.0, 89.0]   # names of the orientation clusters across folds (matched by direction, not by size)
FIGSEL = json.load(open(RP.SEEDS_DIR / 'figure_networks.json'))


def canon(lab, model):
    from scipy.optimize import linear_sum_assignment
    c = np.asarray(model['centres_deg']); d = np.abs((c[:, None] - np.asarray(REF)[None] + 90) % 180 - 90)
    r, k = linear_sum_assignment(d); mp = {int(i): int(j) for i, j in zip(r, k)}; mp[model['K']] = len(REF)      # unclustered -> 4
    return np.array([mp.get(int(x), len(REF)) for x in lab], int)


def props(L, ym, model):
    """one network: count, intensity, intersections, lengths, spacing, topology, orientation-cluster shares"""
    L = np.asarray(L, float).reshape(-1, 4); area = ym * C.M * C.M
    out = dict(n=len(L), P20=len(L) / area * 100)
    if not len(L):
        return out
    c, ln, th = C.common.geom(L); lab = SB.classify(th, model); tp = topology(L, ym)
    xs = len(C.common.crossings_xy(L)) if len(L) > 1 else 0
    out.update(P21=ln.sum() * C.M / area, P22=xs / area * 100, len_med=float(np.median(ln)) * C.M, len_p90=float(np.percentile(ln, 90)) * C.M,
               nn_med=float(np.median(C.common.nn_distances(c))) * C.M if len(L) > 1 else np.nan, CL=tp['CL'], pI=tp['pI'], pY=tp['pY'], pX=tp['pX'],
               unclustered=float((lab == model['K']).mean()), **{'OC%d' % (k + 1): float((lab == k).mean()) for k in range(model['K'])})
    return out


def fold_job(job):
    """per test box of one fold: properties (box rows) and every trace (pooled rows, weight 1/number of networks)"""
    s, fi = job
    lib = C.load_library(); sp = C.split(s, fi, lib); model = C.cluster_model(s, fi); rows, traces = [], []
    for b in sp['test']:
        real = sp['panels'][b]; ym = real['y_max']
        nets = {'Held-out': [real['lines']]}
        for m in GEN:
            nets[m] = [C.load_net(C.net_path(s, m, fi, b, sd, d)) for sd in C.SEEDS for d in range(C.NDRAW)]
        for m, Ls in nets.items():
            P = [props(L, ym, model) for L in Ls]
            rows.append(dict(scheme=s, fold=fi, box=b, method=m, **(P[0] if m == 'Held-out' else pd.DataFrame(P).median(numeric_only=True).to_dict())))
            for L in Ls:
                L = np.asarray(L, float).reshape(-1, 4)
                if not len(L): continue
                _, ln, th = C.common.geom(L)
                traces.append(pd.DataFrame(dict(scheme=s, method=m, box=b, length=ln * C.M, theta=np.degrees(th),
                                                oc=canon(SB.classify(th, model), model), weight=1.0 / len(Ls))))
    return rows, pd.concat(traces)


def axial_mean_deg(a):
    z = np.exp(2j * np.radians(a)).mean(); return (math.degrees(np.angle(z)) / 2) % 180


def axial_sd_deg(a):
    R = abs(np.exp(2j * np.radians(a)).mean()); return math.degrees(math.sqrt(-2 * math.log(max(R, 1e-9))) / 2)


TABP = [('n100', 'Traces per 100 m2', '%.2f'), ('len_med', 'Median trace length (m)', '%.1f'), ('len_p90', 'Long traces: 90th percentile length (m)', '%.1f'),
        ('P21', 'Trace intensity P21 (m/m2)', '%.3f'), ('P22', 'Intersections per 100 m2', '%.2f'), ('CL', 'Connections per trace', '%.2f'),
        ('nn_med', 'Spacing: nearest trace (m)', '%.1f'),
        ('share1', 'Orientation cluster 1 (~125 deg): share (%)', '%.0f'), ('share2', 'Orientation cluster 2 (~56 deg): share (%)', '%.0f'),
        ('share3', 'Orientation cluster 3 (~27 deg): share (%)', '%.0f'), ('share4', 'Orientation cluster 4 (~89 deg): share (%)', '%.0f'),
        ('dir1', 'Orientation cluster 1: direction (deg)', '%.0f'), ('dir2', 'Orientation cluster 2: direction (deg)', '%.0f'),
        ('sd1', 'Orientation cluster 1: spread (deg)', '%.1f'), ('sd2', 'Orientation cluster 2: spread (deg)', '%.1f')]


def table_value(TR, PR, s, m, key):
    a = TR[(TR.scheme == s) & (TR.method == m)]; p = PR[(PR.scheme == s) & (PR.method == m)]
    w = np.maximum(1, np.round(a.weight.values * 24).astype(int)); L = np.repeat(a.length.values, w); A = np.repeat(a.theta.values, w); K = np.repeat(a.oc.values, w)
    if key == 'n100': return p.P20.median()
    if key == 'len_med': return np.median(L)
    if key == 'len_p90': return np.percentile(L, 90)
    if key in ('P21', 'P22', 'CL', 'nn_med'): return p[key].median()
    k = int(key[-1]) - 1
    if key.startswith('share'): return 100 * (K == k).mean()
    if key.startswith('dir'): return axial_mean_deg(A[K == k])
    if key.startswith('sd'): return axial_sd_deg(A[K == k])


# ---------------------------------------------------------------- figures, drawn at print size (16 cm wide)
# Text: 12 pt for titles and axis labels, 10 pt for tick labels, values and legends, 8 pt for notes (src/study/figstyle.py).
def _label(m):
    return 'Held-out' if m == 'Held-out' else m


def figure_1(lib, FS, plt, Rectangle, FIG):
    """held-out traces | EVAE | ADFNE | KDE; one test box per scheme; the same run seed and draw for every method"""
    sel = FIGSEL['boxes']; seed, draw = FIGSEL['run_seed'], FIGSEL['draw']
    data = []
    for e in sel:
        s, b = e['scheme'], e['box']; fi = C.fold_of(s, b, lib); sp = C.split(s, fi, lib); real = sp['panels'][b]
        data.append((s, b, real['y_max'], {'Held-out': real['lines'], **{m: C.load_net(C.net_path(s, m, fi, b, seed, draw)) for m in GEN}}))
    fig, axs = plt.subplots(len(sel), 4, figsize=(FS.FULL_W, 14.6 * FS.CM), gridspec_kw=dict(height_ratios=[d[2] for d in data]))
    for i, (s, b, ym, nets) in enumerate(data):
        for j, m in enumerate(ORDER):
            ax = axs[i, j]; L = np.asarray(nets[m], float).reshape(-1, 4) * C.M
            for x1, y1, x2, y2 in L:
                ax.plot([x1, x2], [y1, y2], color='k', lw=0.9, solid_capstyle='round')
            ax.add_patch(Rectangle((0, 0), C.M, ym * C.M, fill=False, ec=COL[m], lw=1.6))
            ax.set_xlim(-0.6, C.M + 0.6); ax.set_ylim(ym * C.M + 0.6, -0.6); ax.set_aspect('equal')
            ax.set_xticks([0, 10, 20]); ax.set_yticks([t for t in (0, 10, 20) if t <= ym * C.M + 1e-6])
            ax.tick_params(labelsize=8, length=2)
            for sp_ in ax.spines.values(): sp_.set_visible(False)
            ax.set_title('%d traces' % len(L), fontsize=10, color='k' if m == 'Held-out' else COL[m], pad=3)
            if i == 0:                                      # column header, 12 pt, above the trace count
                ax.annotate(_label(m), xy=(0.5, 1), xycoords='axes fraction', xytext=(0, 19), textcoords='offset points',
                            ha='center', va='bottom', fontsize=12, color='k' if m == 'Held-out' else COL[m])
            if j == 0: ax.set_ylabel('%s, box %s\nDepth (m)' % (s, b), fontsize=12, linespacing=1.5)
            if i == len(data) - 1: ax.set_xlabel('Along the wall (m)', fontsize=10)
    fig.text(0.5, 0.004, 'Generated networks: run seed %d, draw %d for every method (seeds/figure_networks.json).' % (seed, draw),
             ha='center', va='bottom', fontsize=8)
    fig.tight_layout(rect=(0, 0.025, 1, 1), h_pad=0.6, w_pad=0.4)
    print('Figure 1', FS.save(fig, str(FIG / 'Figure_1_plain_comparison')))


def figure_2(TR, FS, plt, FIG):
    """orientation roses over 0-360 deg (each trace at theta and theta + 180), held-out outline on every panel"""
    from matplotlib.lines import Line2D
    bins = np.radians(np.arange(0, 361, 10)); cen = bins[:-1] + np.radians(5)

    def rose(m):
        a = TR[TR.method == m]; th = np.radians(np.r_[a.theta.values, a.theta.values + 180]); w = np.r_[a.weight.values, a.weight.values]
        h, _ = np.histogram(th, bins=bins, weights=w); return h / h.sum()
    hr = rose('Held-out'); rmax = max(rose(m).max() for m in ORDER) * 1.08
    fig = plt.figure(figsize=(FS.FULL_W, 17.0 * FS.CM))
    for j, m in enumerate(ORDER):
        ax = fig.add_subplot(2, 2, j + 1, projection='polar'); h = rose(m)
        ax.bar(cen, h, width=np.radians(10), color=COL[m], alpha=0.85, edgecolor='w', linewidth=0.4)
        if m != 'Held-out':
            ax.plot(np.r_[cen, cen[0]], np.r_[hr, hr[0]], color='k', lw=1.0)
        ax.set_theta_zero_location('E'); ax.set_theta_direction(-1); ax.set_ylim(0, rmax); ax.set_yticklabels([])
        ax.set_xticks(np.radians(np.arange(0, 360, 30))); ax.set_xticklabels(['%d°' % d for d in range(0, 360, 30)], fontsize=10)
        ax.tick_params(axis='x', pad=1); ax.grid(lw=0.4)
        ax.set_title(_label(m), fontsize=12, pad=14, color='k' if m == 'Held-out' else COL[m])
    fig.legend(handles=[Line2D([], [], color='k', lw=1.0, label='Held-out, drawn as an outline on the EVAE, ADFNE and KDE roses')],
               loc='lower center', bbox_to_anchor=(0.5, 0.035), frameon=False, fontsize=10)
    fig.text(0.5, 0.004, 'All held-out test boxes. 0° = along the bench; angles clockwise as seen on the face.', ha='center', va='bottom', fontsize=8)
    fig.tight_layout(rect=(0, 0.075, 1, 1), h_pad=1.2)
    print('Figure 2', FS.save(fig, str(FIG / 'Figure_2_rose_0_360')))


def figure_3(TR, FS, plt, FIG):
    """length histograms, held-out outline on every panel, pooled median dashed"""
    from matplotlib.lines import Line2D
    lb = np.arange(0, 21, 1.0); hh = np.histogram(TR[TR.method == 'Held-out'].length, bins=lb, density=True)[0]
    fig, axs = plt.subplots(2, 2, figsize=(FS.FULL_W, 12.6 * FS.CM), sharex=True, sharey=True)
    for ax, m in zip(axs.ravel(), ORDER):
        a = TR[TR.method == m]; h = np.histogram(a.length, bins=lb, weights=a.weight, density=True)[0]
        ax.bar(lb[:-1] + 0.5, h, width=0.9, color=COL[m], alpha=0.85)
        if m != 'Held-out':
            ax.step(lb, np.r_[hh, hh[-1]], where='post', color='k', lw=1.0)
        med = np.median(np.repeat(a.length.values, np.maximum(1, np.round(a.weight.values * 24).astype(int))))
        ax.axvline(med, color='k', ls='--', lw=1.0)
        ax.set_title('%s, median %.1f m' % (_label(m), med), fontsize=12, color='k' if m == 'Held-out' else COL[m], pad=4)
        ax.set_xlim(0, 20); ax.set_xticks([0, 5, 10, 15, 20])
    for ax in axs[1]: ax.set_xlabel('Trace length (m)', fontsize=12)
    for ax in axs[:, 0]: ax.set_ylabel('Share per metre', fontsize=12)
    fig.legend(handles=[Line2D([], [], color='k', lw=1.0, label='Held-out (outline)'), Line2D([], [], color='k', ls='--', lw=1.0, label='Median')],
               loc='lower center', ncol=2, bbox_to_anchor=(0.5, 0.03), frameon=False, fontsize=10)
    fig.text(0.5, 0.004, 'All held-out test boxes; each generated network weighted 1/24 so every box counts the same.', ha='center', va='bottom', fontsize=8)
    fig.tight_layout(rect=(0, 0.085, 1, 1), h_pad=0.8, w_pad=0.8)
    print('Figure 3', FS.save(fig, str(FIG / 'Figure_3_length_histograms')))


def figure_4(PR, FS, plt, FIG):
    """per-box values; dashed line = held-out median; median and % difference from held-out under each box"""
    from matplotlib.lines import Line2D
    PR = PR.copy(); PR['n100'] = PR['P20']
    PAR = [('n100', 'Traces per 100 m²', '%.2f'), ('len_med', 'Median trace length (m)', '%.1f'), ('P21', 'Trace intensity P21 (m/m²)', '%.3f'),
           ('P22', 'Intersections per 100 m²', '%.2f'), ('CL', 'Connections per trace', '%.2f'), ('nn_med', 'Spacing, nearest trace (m)', '%.1f')]
    fig, axs = plt.subplots(3, 2, figsize=(FS.FULL_W, 21.5 * FS.CM))
    for ax, (k, lab, fmt) in zip(axs.ravel(), PAR):
        data = [PR[PR.method == m][k].dropna().values for m in ORDER]
        ref = np.median(data[0])
        ticks = []
        for m, d in zip(ORDER, data):
            md = np.median(d)
            ticks.append('%s\n%s' % (_label(m), fmt % md) if m == 'Held-out' else '%s\n%s\n(%+.0f%%)' % (m, fmt % md, 100 * (md - ref) / ref if ref else 0))
        bp = ax.boxplot(data, tick_labels=ticks, patch_artist=True, widths=0.55, showfliers=False, medianprops=dict(color='k', lw=1.4),
                        whiskerprops=dict(lw=0.8), capprops=dict(lw=0.8), boxprops=dict(lw=0.8))
        for patch, m in zip(bp['boxes'], ORDER): patch.set_facecolor(COL[m]); patch.set_alpha(0.8)
        ax.axhline(ref, color='k', ls='--', lw=0.9)
        for tl in ax.get_xticklabels():
            tl.set_fontsize(10)
            if tl.get_text().startswith('EVAE'): tl.set_fontweight('bold')
        ax.tick_params(axis='x', length=0, pad=3)
        ax.set_title(lab, fontsize=12, pad=4)
    fig.legend(handles=[Line2D([], [], color='k', ls='--', lw=0.9, label='Held-out median')], loc='lower center', bbox_to_anchor=(0.5, 0.022),
               frameon=False, fontsize=10)
    fig.text(0.5, 0.003, '120 held-out test-box cases. Box value = median over 24 networks. Under each box: median and difference from held-out.',
             ha='center', va='bottom', fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=1.0, w_pad=1.5)
    print('Figure 4', FS.save(fig, str(FIG / 'Figure_4_boxplots')))


def main(check=False):
    import matplotlib
    matplotlib.use('Agg')
    import figstyle as FS                        # Times New Roman, 12 pt, layout check
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    FIG, T = RP.FIGURES_DIR, RP.TABLES_DIR; FIG.mkdir(exist_ok=True); T.mkdir(exist_ok=True)
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]
    with Pool(min(12, len(jobs))) as pool:
        res = pool.map(fold_job, jobs)
    PR = pd.DataFrame([r for rr, _ in res for r in rr]); TR = pd.concat([t for _, t in res], ignore_index=True)
    PR.to_csv(T / 'final_properties.csv', index=False)

    figure_1(lib, FS, plt, Rectangle, FIG)
    figure_2(TR, FS, plt, FIG)
    figure_3(TR, FS, plt, FIG)
    figure_4(PR, FS, plt, FIG)

    # ---------------- tables
    rows = []
    for key, lab, fmt in TABP:
        r = dict(parameter=lab)
        for s in C.SCHEMES:
            for m in ORDER:
                r['%s %s' % (s, m)] = table_value(TR, PR, s, m, key)
        rows.append(r)
    TBL = pd.DataFrame(rows); TBL.to_csv(T / 'final_table_all.csv', index=False)
    T1 = TBL[['parameter'] + ['%s %s' % (s, m) for s in C.SCHEMES for m in ('Held-out', 'EVAE')]]; T1.to_csv(T / 'final_table_heldout_vs_EVAE.csv', index=False)
    md = ['| Parameter | ' + ' | '.join('%s held-out | %s EVAE' % (s, s) for s in C.SCHEMES) + ' |', '|---' * 7 + '|']
    for (key, lab, fmt), r in zip(TABP, rows):
        md.append('| %s | ' % lab + ' | '.join('%s | %s' % (fmt % r['%s Held-out' % s], fmt % r['%s EVAE' % s]) for s in C.SCHEMES) + ' |')
    md += ['', '| Parameter | Held-out S1 / S2 / S3 | EVAE S1 / S2 / S3 | ADFNE S1 / S2 / S3 | KDE S1 / S2 / S3 |', '|---|---|---|---|---|']
    for (key, lab, fmt), r in zip(TABP, rows):
        md.append('| %s | ' % lab + ' | '.join(' / '.join(fmt % r['%s %s' % (s, m)] for s in C.SCHEMES) for m in ORDER) + ' |')
    (T / 'final_tables.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    pd.set_option('display.width', 250); print(TBL.round(3).to_string(index=False))
    if check:
        ok = True
        for f in ('final_properties.csv', 'final_table_all.csv', 'final_table_heldout_vs_EVAE.csv'):
            a = pd.read_csv(T / f); b = pd.read_csv(RP.TABLES_DIR / 'reference' / f).replace({'Real': 'Held-out'})
            num = a.select_dtypes('number').columns
            same = a.shape == b.shape and np.allclose(a[num].values, b[num].values, rtol=1e-9, atol=1e-12, equal_nan=True)
            print('CHECK %-34s %s' % (f, 'identical' if same else 'DIFFERENT')); ok &= same
        if not ok:
            sys.exit(1)


if __name__ == '__main__':
    main(check='--check' in sys.argv)
