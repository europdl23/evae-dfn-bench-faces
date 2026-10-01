# -*- coding: utf-8 -*-
"""Discussion set (paper/): undefined scores are n.d. (excluded from panel medians, tests and CIs).

  recount       EVAE vs ADFNE and KDE (Holm over the 2 baselines) and the three-way verdict, from the release
                realisation scores, with the n.d. rule; old vs new counts in tables/changes_nd.csv
  ablation      the 4 ablation comparisons (Holm over the 4, as in the protocol) with the n.d. rule;
                Fig_9_ablation_counts: (a) full EVAE vs EVAE without geology-informed terms, (b) full EVAE vs
                single-latent EVAE; Table_ablation_paper.csv/.xlsx (gap-filling test first)
  Fig_11_boxplots, Fig_11_alt_length_histograms   paper versions, held-out / EVAE / ADFNE / KDE
  Table_D_parameters.csv/.xlsx    15 parameters, held-out / EVAE / ADFNE / KDE, all 3 tests
  Table_S_scores.csv/.xlsx        38 scores x 3 tests: medians, Holm result, BH q, bootstrap CI vs ADFNE and vs KDE
Run after checks.py."""
from multiprocessing import Pool
import numpy as np, pandas as pd
import pr_common as P
import matplotlib
matplotlib.use('Agg')
import figstyle as FS
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import statistical_tests as ST
import export_excel as EX
import ablation as AB
import make_figures as MF
from checks import nd_median, wil
from xl import book, sheet

C = P.C; T = P.TAB; NAMES = ST.NAMES
GROUP_PAPER = {'Orientation distribution': 'Trace-direction distribution', 'Orientation clusters': 'Trace-direction clusters', 'Length': 'Trace length',
               'Density': 'Density and spacing', 'Topology': 'Topology', 'All': 'All'}
ARM_PAPER = {'single_noguide': 'Single-latent EVAE without geology-informed terms', 'single_guide': 'Single-latent EVAE',
             'dual_noguide': 'EVAE without geology-informed terms', 'EVAE': 'Full EVAE'}
EDGES = [('Geology-informed terms, single latent', 'single_guide', 'single_noguide'), ('Geology-informed terms, dual latent', 'EVAE', 'dual_noguide'),
         ('Dual vs single latent, with terms', 'EVAE', 'single_guide'), ('Dual vs single latent, without terms', 'dual_noguide', 'single_noguide')]


def score_name(n):
    s = EX.score_name(n)
    return s.replace('Orientation distribution', 'Trace-direction distribution').replace('Cluster ', 'Trace-direction cluster ').replace('Cluster shares', 'Trace-direction cluster shares')


def save(fig, name):
    print(name, FS.save(fig, str(P.FIG / name), allow_font_sizes=P.SIZES))


# ------------------------------------------------------------------ ablation scores
def abl_job(job):
    s, fi = job
    sp = C.split(s, fi, C.load_library()); model = C.cluster_model(s, fi); rows = []
    for b in sp['test']:
        real = sp['panels'][b]
        for arm in AB.TRAINED_HERE:
            for sd in C.SEEDS:
                for d in range(C.NDRAW):
                    rows.append(dict(scheme=s, fold=fi, box=b, method=arm, run_seed=sd, draw=d,
                                     **ST.score(C.load_net(AB.net_path(arm, s, fi, b, sd, d)), real['lines'], real['y_max'], model)))
    return rows


def holm_tests(BM, pairs, schemes=C.SCHEMES):
    """per test and score: two-sided Wilcoxon for each (name, a, b), Holm over the pairs; n.d. panels dropped"""
    out = []
    for s in schemes:
        sub = BM[BM.scheme == s]
        for grp, names in ST.GROUPS:
            for n in names:
                piv = sub.pivot_table(index='box', columns='method', values=n, dropna=False)
                res = []
                for name, a, b in pairs:
                    q = piv[[a, b]].dropna() if a in piv and b in piv else pd.DataFrame(columns=[a, b]); d = (q[a] - q[b]).values
                    p, _, _ = wil(d); res.append([name, a, b, p, float(np.median(d)) if len(d) else np.nan, len(q)])
                order = sorted(range(len(res)), key=lambda i: res[i][3]); run = 0.0
                for r_, i in enumerate(order):
                    run = max(run, min(1.0, res[i][3] * (len(res) - r_))); res[i].append(run)
                for name, a, b, p, md, nb, ph in res:
                    out.append(dict(test=P.TEST[s], scheme=s, group=grp, score=n, comparison=name, first=a, second=b, n_panels=nb, median_diff=md, p=p, p_holm=ph,
                                    result='no difference' if (ph >= 0.05 or nb < 3) else ('better' if md < 0 else 'worse')))
    return pd.DataFrame(out)


def count(D, by='comparison'):
    rows = []
    for c_, g in D.groupby(by, sort=False):
        for grp in [x for x, _ in ST.GROUPS] + ['All']:
            q = g if grp == 'All' else g[g.group == grp]; v = q.result.value_counts()
            rows.append({by: c_, 'group': grp, 'better': int(v.get('better', 0)), 'no_difference': int(v.get('no difference', 0)), 'worse': int(v.get('worse', 0))})
    return pd.DataFrame(rows)


def verdict(BM):
    out = []
    for grp, names in ST.GROUPS:
        for n in names:
            rr = {s: ST.three_way(BM[BM.scheme == s].pivot_table(index='box', columns='method', values=n), ST.GEN) for s in C.SCHEMES}
            cw = {m: sum(1 for s in C.SCHEMES if rr[s] and rr[s]['winner'] == m and rr[s]['clear']) for m in ST.GEN}
            out.append(dict(group=grp, score=n, **{'%s_winner' % P.TEST[s]: ('%s (%s)' % (rr[s]['winner'], 'clear' if rr[s]['clear'] else 'tie')) if rr[s] else 'n.d.' for s in C.SCHEMES},
                            verdict=next((m for m in cw if cw[m] >= 2), 'no method')))
    return pd.DataFrame(out)


def main():
    NS = pd.read_csv(P.RP.TABLES_DIR / 'stats_network_scores.csv', na_values=['n.d.'])
    BMr = nd_median(NS, ['scheme', 'fold', 'box', 'method']); BMr.to_csv(T / 'panel_scores_EVAE_ADFNE_KDE_nd.csv', index=False, na_rep='n.d.')
    changes = []
    # ---------------- recount EVAE vs ADFNE / KDE
    D = holm_tests(BMr, [('EVAE vs ADFNE', 'EVAE', 'ADFNE'), ('EVAE vs KDE', 'EVAE', 'KDE')]); D.to_csv(T / 'recount_EVAE_vs_baselines.csv', index=False, na_rep='n.d.')
    CN = count(D); CN.to_csv(T / 'recount_EVAE_vs_baselines_counts.csv', index=False)
    old = pd.read_csv(P.RP.TABLES_DIR / 'stats_counts_penalty.csv')          # first version: undefined = worst value
    for _, r in CN.iterrows():
        o = old[(old.against == r.comparison.split(' vs ')[1]) & (old.group == r.group.replace('Orientation clusters', 'Orientation clusters'))]
        o = o.iloc[0] if len(o) else None
        changes.append(dict(summary='EVAE vs baselines (Holm over 2)', item='%s | %s' % (r.comparison, GROUP_PAPER[r.group]),
                            old='%d / %d / %d' % (o.better, o.no_difference, o.worse) if o is not None else '', new='%d / %d / %d' % (r.better, r.no_difference, r.worse)))
    V = verdict(BMr); V.to_csv(T / 'recount_verdict.csv', index=False)
    vo = pd.read_csv(P.RP.TABLES_DIR / 'stats_verdict_penalty.csv').verdict.value_counts().to_dict(); vn = V.verdict.value_counts().to_dict()
    changes.append(dict(summary='Three-way verdict (clear in >= 2 tests)', item='EVAE / ADFNE / KDE / no method', old='%d / %d / %d / %d' % tuple(vo.get(k, 0) for k in ('EVAE', 'ADFNE', 'KDE', 'no method')),
                        new='%d / %d / %d / %d' % tuple(vn.get(k, 0) for k in ('EVAE', 'ADFNE', 'KDE', 'no method'))))
    # ---------------- ablation
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]
    with Pool(min(12, len(jobs))) as pool:
        AS = pd.DataFrame([r for rr in pool.map(abl_job, jobs) for r in rr])
    AS = pd.concat([AS, NS[NS.method == 'EVAE'][AS.columns]], ignore_index=True); AS.replace([np.inf, -np.inf], np.nan).to_csv(T / 'ablation_network_scores.csv', index=False, na_rep='n.d.')
    BMa = nd_median(AS, ['scheme', 'fold', 'box', 'method'])
    AD = holm_tests(BMa, EDGES); AD.to_csv(T / 'recount_ablation.csv', index=False, na_rep='n.d.')
    AC = count(AD); AC.to_csv(T / 'recount_ablation_counts.csv', index=False)
    oa = pd.read_csv(P.RP.TABLES_DIR / 'ablation_tests_counts_penalty.csv')
    for _, r in AC.iterrows():
        o = oa[(oa.edge == r.comparison) & (oa.group == r.group)].iloc[0]
        changes.append(dict(summary='Ablation (Holm over 4)', item='%s | %s' % (r.comparison, GROUP_PAPER[r.group]), old='%d / %d / %d' % (o.better, o.no_difference, o.worse),
                            new='%d / %d / %d' % (r.better, r.no_difference, r.worse)))
    # Results-check summaries recounted by checks.py (first-version copies in tables/before_nd_rule/)
    for f, key in (('check_counts.csv', ['test', 'second', 'group']),):
        a, b = pd.read_csv(T / 'before_nd_rule' / f), pd.read_csv(T / f)
        m = a.merge(b, on=key + ['first'], suffixes=('_old', '_new'))
        for _, r in m[m.group == 'All'].iterrows():
            changes.append(dict(summary='EVAE vs %s' % ('natural-variability reference' if r.second == 'Reference' else 'random context'), item=r.test,
                                old='%d / %d / %d' % (r.better_old, r.no_difference_old, r.worse_old), new='%d / %d / %d' % (r.better_new, r.no_difference_new, r.worse_new)))
    for f, idx, lab in (('check_per_seed_verdict_summary.csv', 'run_seed', 'Per-seed verdict, run seed %s (EVAE / KDE / no method)'),):
        a, b = pd.read_csv(T / 'before_nd_rule' / f).set_index(idx), pd.read_csv(T / f).set_index(idx)
        for sd in b.index:
            g = lambda x: '%d / %d / %d' % tuple(int(x.get(k, 0)) for k in ('EVAE', 'KDE', 'no method'))
            changes.append(dict(summary='Per-seed verdict', item='run seed %s' % sd, old=g(a.loc[sd]), new=g(b.loc[sd])))
    for f, idx, cols, lab in (('check_benjamini_hochberg_summary.csv', 'second', ['better', 'no difference', 'worse'], 'Benjamini-Hochberg'),
                              ('check_bootstrap_ci_summary.csv', 'against', ['EVAE better', 'includes 0', 'EVAE worse'], 'Bootstrap 95% CI (better / includes 0 / worse)')):
        a, b = pd.read_csv(T / 'before_nd_rule' / f).set_index(idx), pd.read_csv(T / f).set_index(idx)
        for k in b.index:
            changes.append(dict(summary=lab, item='EVAE vs %s' % k, old=' / '.join(str(int(a.loc[k].get(c, 0))) for c in cols), new=' / '.join(str(int(b.loc[k].get(c, 0))) for c in cols)))
    a, b = pd.read_csv(T / 'before_nd_rule' / 'check_local_baselines_counts.csv'), pd.read_csv(T / 'check_local_baselines_counts.csv')
    for ag in b.against.unique():
        x, y = a[(a.against == ag) & (a.group == 'All')].iloc[0], b[(b.against == ag) & (b.group == 'All')].iloc[0]
        changes.append(dict(summary='Gap-filling baselines refitted on 8 neighbouring panels', item='EVAE vs %s' % ag,
                            old='%d / %d / %d' % (x.better, x['no difference'], x.worse), new='%d / %d / %d' % (y.better, y['no difference'], y.worse)))
    CH = pd.DataFrame(changes); CH['changed'] = np.where(CH.old != CH.new, 'yes', 'no'); CH.to_csv(T / 'changes_nd.csv', index=False)

    # ---------------- Fig 9: ablation counts by group (summed over the 3 tests)
    fig, axs = plt.subplots(2, 1, figsize=(P.W, 11.0 * P.CM))
    grp = [g for g, _ in ST.GROUPS] + ['All']
    for ax, (comp, title) in zip(axs, (('Geology-informed terms, dual latent', '(a) Full EVAE vs EVAE without geology-informed terms'),
                                      ('Dual vs single latent, with terms', '(b) Full EVAE vs single-latent EVAE'))):
        q = AC[AC.comparison == comp].set_index('group').loc[grp]
        y = np.arange(len(grp))[::-1]; tot = (q.better + q.no_difference + q.worse).values
        ax.barh(y, q.better, color='#3A3A3A', height=0.62); ax.barh(y, q.no_difference, left=q.better, color='#D4D4D4', height=0.62)
        nz = q.worse.values > 0                                    # no zero-width bars (their edges would show as stray marks)
        ax.barh(y[nz], q.worse.values[nz], left=(q.better + q.no_difference).values[nz], color='white', edgecolor='k', hatch='////', lw=0.6, height=0.62)
        for yi, (b_, n_, w_), t_ in zip(y, q[['better', 'no_difference', 'worse']].values, tot):
            ax.text(t_ + 1.5, yi, '%d / %d / %d' % (b_, n_, w_), va='center', fontsize=10)
        ax.set_yticks(y); ax.set_yticklabels([GROUP_PAPER[g] for g in grp]); ax.set_xlim(0, 150); ax.set_xticks([0, 30, 60, 90, 114])
        ax.set_title(title, loc='left', fontsize=12, pad=4); ax.spines[['top', 'right']].set_visible(False); ax.tick_params(axis='y', length=0)
    axs[1].set_xlabel('Score x test comparisons (38 scores x 3 tests = 114)')
    fig.legend(handles=[Patch(fc='#3A3A3A', label='Full EVAE better'), Patch(fc='#D4D4D4', label='No difference'), Patch(fc='white', ec='k', hatch='////', label='Full EVAE worse')],
               loc='lower center', ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.07, 1, 1), h_pad=1.2)
    save(fig, 'Fig_9_ablation_counts')

    # ---------------- ablation table, paper version (gap-filling first)
    AT = pd.read_csv(P.RP.TABLES_DIR / 'ablation_table.csv')
    cols = [('Held-out', 'held-out')] + [(a, ARM_PAPER[a]) for a in AB.ORDER]
    head = ['Parameter', 'Unit'] + ['%s test: %s' % (P.TEST[s], lab) for s in C.SCHEMES for _, lab in cols]
    fm = [f for _, _, f in EX.ROWS]
    rows = [[p, u] + [round(float(AT.iloc[i]['%s %s' % (s, m)]), EX.DEC[f]) for s in C.SCHEMES for m, _ in cols] for i, (p, u, f) in enumerate(EX.ROWS)]
    pd.DataFrame(rows, columns=head).to_csv(T / 'Table_ablation_paper.csv', index=False)
    wb = book(); sheet(wb, 'Ablation table', head, rows, fm, [38, 18] + [16] * 15, 'C2')
    ac = AC.copy(); ac['group'] = ac.group.map(GROUP_PAPER)
    sheet(wb, 'Comparison counts', ['Comparison', 'Group', 'First-named better', 'No difference', 'First-named worse'], ac[['comparison', 'group', 'better', 'no_difference', 'worse']].values.tolist(),
          None, [40, 30, 16, 14, 16])
    sheet(wb, 'Notes', ['Notes'], [[n] for n in ['Full EVAE = dual latent with geology-informed terms. Without geology-informed terms = the released geology term, the trace-direction term and the trace-direction-cluster term all off. Single-latent EVAE = one joint latent code read by every decoder head.',
                                                 'Same data, folds, run seeds (1337, 20260903, 7), draws and generator seeds for every column. Values as in Table D.',
                                                 'Comparison counts: paired two-sided Wilcoxon over held-out panels, Holm over the 4 ablation comparisons, alpha 0.05; undefined scores (n.d.) excluded. Sum of 38 scores x 3 tests.']], None, [170])
    wb.save(T / 'Table_ablation_paper.xlsx'); EX._freeze(T / 'Table_ablation_paper.xlsx')

    # ---------------- Table D: 15 parameters x 4 methods x 3 tests
    TD = pd.read_csv(P.RP.TABLES_DIR / 'final_table_all.csv')
    cols = [('Held-out', 'held-out'), ('EVAE', 'EVAE'), ('ADFNE', 'ADFNE'), ('KDE', 'KDE')]
    head = ['Parameter', 'Unit'] + ['%s test: %s' % (P.TEST[s], lab) for s in C.SCHEMES for _, lab in cols]
    rows = [[p, u] + [round(float(TD.iloc[i]['%s %s' % (s, m)]), EX.DEC[f]) for s in C.SCHEMES for m, _ in cols] for i, (p, u, f) in enumerate(EX.ROWS)]
    pd.DataFrame(rows, columns=head).to_csv(T / 'Table_D_parameters.csv', index=False)
    wb = book(); sheet(wb, 'Table D', head, rows, fm, [38, 18] + [13] * 12, 'C2')
    sheet(wb, 'Notes', ['Notes'], [[n] for n in ['Held-out panels of the gap-filling (20), new-bench (50) and new-stretch (50) tests. EVAE = learned; ADFNE and KDE = fitted distributions on the training panels of each fold.',
                                                 'Per held-out panel the median over its 24 realisations; per test the median over panels. Median length, 90th percentile length, cluster shares, directions and spreads over all traces of the test (each realisation weighted 1/24).',
                                                 'Cluster = trace-direction cluster (learned on the training panels of each fold).']], None, [170])
    wb.save(T / 'Table_D_parameters.xlsx'); EX._freeze(T / 'Table_D_parameters.xlsx')

    # ---------------- Table S: 38 scores x 3 tests vs ADFNE and KDE
    BH = pd.read_csv(T / 'check_benjamini_hochberg.csv', na_values=['n.d.']); BS = pd.read_csv(T / 'check_bootstrap_ci.csv', na_values=['n.d.'])
    med = BMr.groupby(['scheme', 'method'])[NAMES].median()
    rows = []
    for s in C.SCHEMES:
        for grp, names in ST.GROUPS:
            for n in names:
                r = {'Test': P.TEST[s], 'Group': GROUP_PAPER[grp], 'Score (error; smaller = closer to held-out)': score_name(n)}
                for m in ST.GEN:
                    v = med.loc[(s, m), n] if (s, m) in med.index else np.nan
                    r['Median %s' % m] = 'n.d.' if v != v else round(float(v), 4)
                for b_ in ('ADFNE', 'KDE'):
                    d = D[(D.scheme == s) & (D.score == n) & (D.second == b_)].iloc[0]
                    h = BH[(BH.scheme == s) & (BH.score == n) & (BH.second == b_)]
                    c = BS[(BS.test == P.TEST[s]) & (BS.score == n) & (BS.against == b_)]
                    r['vs %s: panels' % b_] = int(d.n_panels)
                    r['vs %s: Holm p' % b_] = round(float(d.p_holm), 4)
                    r['vs %s: Holm result' % b_] = {'better': 'EVAE better', 'worse': 'EVAE worse'}.get(d.result, 'no difference')
                    r['vs %s: BH q' % b_] = round(float(h.q_bh.iloc[0]), 4) if len(h) else 'n.d.'
                    r['vs %s: median difference [95%% CI]' % b_] = ('%.3f [%.3f, %.3f]' % (c.median_diff.iloc[0], c.ci_low.iloc[0], c.ci_high.iloc[0])) if len(c) else 'n.d.'
                rows.append(r)
    TS = pd.DataFrame(rows); TS.to_csv(T / 'Table_S_scores.csv', index=False)
    wb = book(); sheet(wb, 'Table S', list(TS.columns), TS.values.tolist(), None, [12, 26, 44] + [11] * 3 + [10, 10, 14, 10, 24] * 2, 'D2')
    sheet(wb, 'Notes', ['Notes'], [[n] for n in ['Each score is an error of a realisation against its held-out panel (smaller = closer); panel value = median over the realisations where the score is defined. n.d. = not defined (an empty realisation, or fewer than 2 members of a trace-direction cluster that the held-out panel has); n.d. values are excluded from medians, tests and intervals.',
                                                 'Median = median over the held-out panels of the test. Holm: paired two-sided Wilcoxon over panels (zero-split), Holm over the 2 baselines, alpha 0.05. BH q: Benjamini-Hochberg over all 228 EVAE-vs-baseline comparisons.',
                                                 'Median difference = EVAE minus baseline over panels (negative = EVAE closer); 95% CI by bootstrap over panels (2,000 resamples, seed 20261001).',
                                                 'Score definitions: paper/SCORE_DEFINITIONS.md.']], None, [170])
    wb.save(T / 'Table_S_scores.xlsx'); EX._freeze(T / 'Table_S_scores.xlsx')

    # ---------------- Fig 11: box plots and length histograms, 4 methods (pooled over the 3 tests)
    PR = pd.read_csv(P.RP.TABLES_DIR / 'final_properties.csv').replace({'Real': 'Held-out'}); ORD = ['Held-out', 'EVAE', 'ADFNE', 'KDE']
    PAR = [('P20', 'Traces per 100 m²', '%.2f'), ('len_med', 'Median trace length (m)', '%.1f'), ('P21', 'P21 (m/m²)', '%.3f'),
           ('P22', 'Intersections per 100 m²', '%.2f'), ('CL', 'Connections per trace', '%.2f'), ('nn_med', 'Spacing, nearest trace (m)', '%.1f')]
    fig, axs = plt.subplots(3, 2, figsize=(P.W, 20.0 * P.CM))
    for ax, (k, lab, fmt) in zip(axs.ravel(), PAR):
        data = [PR[PR.method == m][k].dropna().values for m in ORD]; ref = np.median(data[0])
        ticks = ['Held-out\n%s' % (fmt % ref)] + ['%s\n%s\n(%+.0f%%)' % (m, fmt % np.median(d), 100 * (np.median(d) - ref) / ref) for m, d in zip(ORD[1:], data[1:])]
        bp = ax.boxplot(data, tick_labels=[t_.replace('(-', '(−') for t_ in ticks], patch_artist=True, widths=0.55,
                        showfliers=False, medianprops=dict(color='k', lw=1.3), whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7), boxprops=dict(lw=0.7))
        for patch, m in zip(bp['boxes'], ORD): patch.set_facecolor(P.METHOD_COL[m]); patch.set_alpha(0.8)
        ax.axhline(ref, color='k', ls='--', lw=0.8); ax.tick_params(axis='x', length=0, pad=3)
        ax.set_title(lab, fontsize=12, pad=4)
    fig.legend(handles=[Line2D([], [], color='k', ls='--', lw=0.8, label='Held-out median (120 held-out panels; per panel, median of 24 realisations)')],
               loc='lower center', frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.035, 1, 1), h_pad=0.8, w_pad=1.5)
    save(fig, 'Fig_11_boxplots')
    lib = C.load_library(); rows = []
    for s in C.SCHEMES:
        for fi, test in enumerate(C.folds(s, lib)):
            sp = C.split(s, fi, lib)
            for b in test:
                sets = {'Held-out': [sp['panels'][b]['lines']], **{m: [C.load_net(C.net_path(s, m, fi, b, sd, d)) for sd in C.SEEDS for d in range(C.NDRAW)] for m in ST.GEN}}
                for m, LL in sets.items():
                    for L in LL:
                        L = np.asarray(L, float).reshape(-1, 4)
                        if len(L): rows.append(pd.DataFrame(dict(method=m, length=C.common.geom(L)[1] * C.M, w=1.0 / len(LL))))
    TR = pd.concat(rows, ignore_index=True); lb = np.arange(0, 31, 1.0)
    hh = np.histogram(TR[TR.method == 'Held-out'].length, bins=lb, density=True)[0]
    fig, axs = plt.subplots(2, 2, figsize=(P.W, 11.5 * P.CM), sharex=True, sharey=True); hmax = 0
    for ax, m in zip(axs.ravel(), ORD):
        a = TR[TR.method == m]; h = np.histogram(a.length, bins=lb, weights=a.w, density=True)[0]; hmax = max(hmax, h.max())
        ax.bar(lb[:-1] + 0.5, h, width=0.9, color=P.METHOD_COL[m], alpha=0.8)
        if m != 'Held-out': ax.step(lb, np.r_[hh, hh[-1]], where='post', color='k', lw=0.9)
        med = np.median(np.repeat(a.length.values, np.maximum(1, np.round(a.w.values * 24).astype(int))))
        ax.set_title('%s, median %.1f m' % (m, med), fontsize=12, pad=4, color='k' if m == 'Held-out' else P.METHOD_COL[m])
        ax.set_xlim(0, 30); ax.set_xticks([0, 10, 20, 30])
    for ax in axs.ravel(): ax.set_ylim(0, hmax * 1.12)
    axs[0, 1].axvline(20, color='k', ls='--', lw=0.8); axs[0, 1].text(19.3, hmax * 1.07, 'decoder\nlimit', fontsize=10, ha='right', va='top')
    for ax in axs[1]: ax.set_xlabel('Trace length (m)')
    for ax in axs[:, 0]: ax.set_ylabel('Share per metre')
    fig.legend(handles=[Line2D([], [], color='k', lw=0.9, label='Held-out (outline)')], loc='lower center', frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.06, 1, 1), h_pad=0.8, w_pad=0.8)
    save(fig, 'Fig_11_alt_length_histograms')
    pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70)
    print(CH[CH.changed == 'yes'].to_string(index=False))


if __name__ == '__main__':
    main()
