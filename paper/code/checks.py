# -*- coding: utf-8 -*-
"""Checks for Results and Discussion, all three tests, the 38 error scores of the release (scripts/statistical_tests.py).

Results
  natural-variability reference  the 8 neighbouring panels of each held-out panel (the EVAE's context panels, with
                                 every held-out fracture removed) scored against the held-out panel as if they were
                                 realisations; counts, length and crossing errors are per unit area (panels differ in
                                 height). Panel value = median over the 8. EVAE vs reference: paired two-sided Wilcoxon
                                 over panels, alpha 0.05.
  random context                 EVAE realisations from 8 random training panels instead of the neighbours (same
                                 models, same generator seeds); two-sided Wilcoxon, direction from the signed-rank sums.
  memorisation                   each realisation against its SOURCE neighbouring panel (the context panel of its draw),
                                 compared with the held-out panel against the same panel; plus the nearest training
                                 panel; near-copy = a trace with both end points within 0.5 m of a trace of the other panel.
  panel-to-panel agreement       Spearman correlation over the held-out panels of a test, held-out value vs EVAE median.
  Table R1                       15 parameters; held-out | reference | EVAE for each test.
Discussion
  per-seed verdict, Benjamini-Hochberg over all EVAE-vs-baseline comparisons, gap-filling baselines refitted on the 8
  neighbouring panels, bootstrap 95% CIs of the median paired difference (2,000 resamples of panels, seed 20261001).
Writes paper/tables/*.csv and checks.xlsx, Table_R1.csv/.xlsx."""
import math
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy.stats import wilcoxon, spearmanr, rankdata
import pr_common as P
import setbg as SB
import make_figures as MF
import statistical_tests as ST
import export_excel as EX

C = P.C
NAMES, GROUPS = ST.NAMES, ST.GROUPS
NEAR = 0.5                                            # m, near-copy tolerance for both end points


def nd_median(D, keys):
    """panel value = median over the realisations where the score is defined; undefined (inf: an empty realisation, or
    fewer than 2 members of a cluster that the held-out panel has) is excluded; no defined value = n.d. (NaN)"""
    return D.replace([np.inf, -np.inf], np.nan).groupby(keys)[NAMES].median().reset_index()


def ends_m(L):
    return np.asarray(L, float).reshape(-1, 4) * C.M


def end_dist(A, B):
    """n x m matrix: for each pair of traces, the larger of the two end-point distances (best of the two pairings), m"""
    a1, a2, b1, b2 = A[:, None, :2], A[:, None, 2:], B[None, :, :2], B[None, :, 2:]
    d = lambda p, q: np.sqrt(((p - q) ** 2).sum(-1))
    return np.minimum(np.maximum(d(a1, b1), d(a2, b2)), np.maximum(d(a1, b2), d(a2, b1)))


def copy_stats(La, Lb):
    """share of traces of La with a near-copy in Lb, and mean distance to the closest trace of Lb (m)"""
    A, B = ends_m(La), ends_m(Lb)
    if not len(A) or not len(B):
        return np.nan, np.nan
    D = end_dist(A, B).min(1)
    return float((D <= NEAR).mean()), float(D.mean())


def score_ref(Lg, ymg, Lr, ymr, model):
    """38 scores of a real neighbouring panel against the held-out panel; count-type errors per unit area"""
    s = ST.score(Lg, Lr, ymr, model)
    Lg, Lr = np.asarray(Lg, float).reshape(-1, 4), np.asarray(Lr, float).reshape(-1, 4)
    if not len(Lg) or not len(Lr):
        return s
    f = ymr / ymg                                    # area of held-out panel / area of neighbouring panel (same width)
    _, lg, tg = C.common.geom(Lg); _, lr, tr = C.common.geom(Lr)
    s['P20_relerr'] = abs(len(lg) * f - len(lr)) / len(lr)
    s['P21_relerr'] = abs(lg.sum() * f - lr.sum()) / max(lr.sum(), 1e-12)
    xg = len(C.common.crossings_xy(Lg)) if len(lg) > 1 else 0; xr = len(C.common.crossings_xy(Lr)) if len(lr) > 1 else 0
    s['P22_relerr'] = abs(xg * f - xr) / xr if xr else np.nan
    kg, kr = SB.classify(tg, model), SB.classify(tr, model)
    for j in range(min(model['K'], ST.KMAX)):
        r_ = (kr == j).sum()
        s['oc%d_count_relerr' % (j + 1)] = abs((kg == j).sum() * f - r_) / r_ if r_ else np.nan
    return s


def fold_job(job):
    s, fi = job
    lib = C.load_library(); sp = C.split(s, fi, lib); Pn = sp['panels']; model = C.cluster_model(s, fi)
    props, traces, scores, memo = [], [], [], []
    for b in sp['test']:
        real = Pn[b]; ym = real['y_max']; ctx = C.context(sp, b)
        # held-out, EVAE (release), reference (8 neighbouring panels), random context, local baselines (gap-filling)
        sets = {'Held-out': [(real['lines'], ym)],
                'EVAE': [(C.load_net(C.net_path(s, 'EVAE', fi, b, sd, d)), ym) for sd in C.SEEDS for d in range(C.NDRAW)],
                'Reference': [(Pn[k]['lines'], Pn[k]['y_max']) for k in ctx],
                'Random context': [(C.load_net(C.net_path(s, 'EVAE', fi, b, sd, d, root=P.NET / 'random_context')), ym) for sd in C.SEEDS for d in range(C.NDRAW)]}
        if s == 'S1':
            for m in ('ADFNE', 'KDE'):
                sets['%s (neighbours)' % m] = [(C.load_net(C.net_path(s, m, fi, b, sd, d, root=P.NET / 'local_baselines')), ym) for sd in C.SEEDS for d in range(C.NDRAW)]
        for m, LL in sets.items():
            pp = [MF.props(L, y, model) for L, y in LL]
            props.append(dict(scheme=s, fold=fi, box=b, method=m, **(pp[0] if m == 'Held-out' else pd.DataFrame(pp).median(numeric_only=True).to_dict())))
            if m in ('Held-out', 'EVAE', 'Reference'):
                for L, y in LL:
                    L = np.asarray(L, float).reshape(-1, 4)
                    if not len(L): continue
                    _, ln, th = C.common.geom(L)
                    traces.append(pd.DataFrame(dict(scheme=s, method=m, box=b, length=ln * C.M, theta=np.degrees(th),
                                                    oc=MF.canon(SB.classify(th, model), model), weight=1.0 / len(LL))))
            if m == 'Held-out':
                continue
            for k, (L, y) in enumerate(LL):
                sc = score_ref(L, y, real['lines'], ym, model) if m == 'Reference' else ST.score(L, real['lines'], ym, model)
                scores.append(dict(scheme=s, fold=fi, box=b, method=m, k=k, **sc))
        # memorisation: realisation vs its source neighbouring panel, held-out vs the same panel, nearest training panel
        fit = [k for k in sp['fit'] if len(Pn[k]['lines'])]
        def nearest_train(L):
            v = [copy_stats(L, Pn[k]['lines'])[0] for k in fit]; v = [x for x in v if x == x]
            return max(v) if v else np.nan
        ho = {k: copy_stats(real['lines'], Pn[k]['lines']) for k in ctx}
        ho_train = nearest_train(real['lines'])
        for i, sd in enumerate(C.SEEDS):
            for d in range(C.NDRAW):
                L = sets['EVAE'][i * C.NDRAW + d][0]; src = ctx[d % len(ctx)]
                sh, cd = copy_stats(L, Pn[src]['lines'])
                memo.append(dict(scheme=s, fold=fi, box=b, run_seed=sd, draw=d, source=src, real_copy_share_src=sh, real_dist_src_m=cd,
                                 heldout_copy_share_src=ho[src][0], heldout_dist_src_m=ho[src][1],
                                 real_copy_share_nearest_training=nearest_train(L), heldout_copy_share_nearest_training=ho_train))
    return props, pd.concat(traces), scores, memo


def wil(d):
    d = np.asarray(d, float)
    if len(d) < 3 or np.allclose(d, 0):
        return 1.0, 0.0, 0.0
    p = float(wilcoxon(d, zero_method='zsplit').pvalue)
    r = rankdata(np.abs(d)); wp = r[d > 0].sum() + r[d == 0].sum() / 2; wm = r[d < 0].sum() + r[d == 0].sum() / 2
    return p, wp, wm


def compare(BM, a, b, by_ranksum=False, alpha=0.05):
    """a against b, per test and score: two-sided Wilcoxon over panels; better = a has the smaller error"""
    out = []
    for s in C.SCHEMES:
        sub = BM[BM.scheme == s]
        for grp, names in GROUPS:
            for n in names:
                piv = sub.pivot_table(index='box', columns='method', values=n)
                if a not in piv or b not in piv: continue
                q = piv[[a, b]].replace([np.inf], 1e9).dropna(); d = (q[a] - q[b]).values
                p, wp, wm = wil(d); md = float(np.median(d)) if len(d) else np.nan
                neg = (wm > wp) if by_ranksum else (md < 0)
                out.append(dict(test=P.TEST[s], scheme=s, group=grp, score=n, first=a, second=b, n_panels=len(q), median_first=float(q[a].median()) if len(q) else np.nan,
                                median_second=float(q[b].median()) if len(q) else np.nan, median_diff=md, rank_sum_plus=wp, rank_sum_minus=wm, p=p,
                                result='no difference' if p >= alpha else ('better' if neg else 'worse')))
    return pd.DataFrame(out)


def counts(D, key='first'):
    rows = []
    for (s, a, b), g in D.groupby(['scheme', 'first', 'second'], sort=False):
        for grp in [x for x, _ in GROUPS] + ['All']:
            q = g if grp == 'All' else g[g.group == grp]; v = q.result.value_counts()
            rows.append(dict(test=P.TEST[s], first=a, second=b, group=grp, better=int(v.get('better', 0)), no_difference=int(v.get('no difference', 0)), worse=int(v.get('worse', 0))))
    return pd.DataFrame(rows)


def main():
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]
    with Pool(min(12, len(jobs))) as pool:
        res = pool.map(fold_job, jobs)
    PRp = pd.DataFrame([r for rr in res for r in rr[0]]); TR = pd.concat([r[1] for r in res], ignore_index=True)
    SC = pd.DataFrame([r for rr in res for r in rr[2]]); MEM = pd.DataFrame([r for rr in res for r in rr[3]])
    T = P.TAB
    PRp.to_csv(na_rep='n.d.', path_or_buf=T / 'panel_properties.csv', index=False); MEM.to_csv(na_rep='n.d.', path_or_buf=T / 'memorisation_realisations.csv', index=False)
    SC.replace([np.inf, -np.inf], np.nan).to_csv(na_rep='n.d.', path_or_buf=T / 'network_scores_checks.csv', index=False)
    BMn = nd_median(SC, ['scheme', 'fold', 'box', 'method'])
    # release scores of EVAE, ADFNE, KDE (24 realisations each)
    NS = pd.read_csv(P.RP.TABLES_DIR / 'stats_network_scores.csv', na_values=['n.d.'])
    BMr = nd_median(NS, ['scheme', 'fold', 'box', 'method'])
    BM = pd.concat([BMr, BMn[BMn.method != 'EVAE']], ignore_index=True)
    # check: the EVAE scores recomputed here equal the release table
    e1 = SC[SC.method == 'EVAE'].copy(); e1['run_seed'] = [C.SEEDS[k // C.NDRAW] for k in e1.k]; e1['draw'] = e1.k % C.NDRAW
    chk = e1.set_index(['scheme', 'box', 'run_seed', 'draw'])[NAMES].sort_index(); ref = NS[NS.method == 'EVAE'].set_index(['scheme', 'box', 'run_seed', 'draw'])[NAMES].sort_index()
    same = chk.shape == ref.shape and np.allclose(chk.replace([np.inf, -np.inf], np.nan).values, ref.replace([np.inf, -np.inf], np.nan).values, equal_nan=True)
    print('EVAE scores recomputed = release table:', same)
    BM.to_csv(na_rep='n.d.', path_or_buf=T / 'panel_score_medians.csv', index=False)

    # ---- Results checks
    NV = compare(BM, 'EVAE', 'Reference'); NV.to_csv(na_rep='n.d.', path_or_buf=T / 'check_natural_variability.csv', index=False)
    RC = compare(BM, 'EVAE', 'Random context', by_ranksum=True); RC.to_csv(na_rep='n.d.', path_or_buf=T / 'check_random_context.csv', index=False)
    CNT = pd.concat([counts(NV), counts(RC)]); CNT.to_csv(na_rep='n.d.', path_or_buf=T / 'check_counts.csv', index=False)
    pm = MEM.groupby(['scheme', 'box'])[[c for c in MEM.columns if c.startswith(('real_', 'heldout_'))]].median().reset_index()
    mrows = []
    for s in C.SCHEMES:
        q = pm[pm.scheme == s]; r = dict(test=P.TEST[s], panels=len(q))
        for a, b, lab in (('real_copy_share_src', 'heldout_copy_share_src', 'near-copy share, vs source panel'),
                          ('real_dist_src_m', 'heldout_dist_src_m', 'distance to closest trace of source panel (m)'),
                          ('real_copy_share_nearest_training', 'heldout_copy_share_nearest_training', 'near-copy share, nearest training panel')):
            x = q[[a, b]].dropna(); p, _, _ = wil((x[a] - x[b]).values)
            mrows.append(dict(test=P.TEST[s], measure=lab, realisation_median=float(x[a].median()), heldout_median=float(x[b].median()),
                              realisation_max=float(x[a].max()), heldout_max=float(x[b].max()), p_wilcoxon=p, n_panels=len(x)))
    MS = pd.DataFrame(mrows); MS.to_csv(na_rep='n.d.', path_or_buf=T / 'check_memorisation.csv', index=False)
    SP = []
    for s in C.SCHEMES:
        q = PRp[PRp.scheme == s]
        for k, lab in (('P20', 'Traces per 100 m²'), ('P21', 'P21 (m/m²)'), ('P22', 'Intersections per 100 m²'), ('CL', 'Connections per trace'),
                       ('nn_med', 'Spacing, nearest trace (m)'), ('len_med', 'Median trace length (m)'), ('OC1', 'Cluster 1 share')):
            real = q[q.method == 'Held-out'].set_index('box')[k]
            r = dict(test=P.TEST[s], parameter=lab)
            for m in ('EVAE', 'Reference', 'Random context'):
                g = q[q.method == m].set_index('box')[k].reindex(real.index); ok = g.notna() & real.notna()
                r['rho %s' % m] = float(spearmanr(real[ok], g[ok]).correlation) if ok.sum() > 3 and g[ok].nunique() > 1 else np.nan
            SP.append(r)
    SPd = pd.DataFrame(SP); SPd.to_csv(na_rep='n.d.', path_or_buf=T / 'check_panel_spearman.csv', index=False)
    # Table R1: held-out | reference | EVAE
    rows = []
    for key, lab, fmt in MF.TABP:
        r = dict(parameter=lab)
        for s in C.SCHEMES:
            for m in ('Held-out', 'Reference', 'EVAE'):
                r['%s %s' % (s, m)] = MF.table_value(TR, PRp, s, m, key)
        rows.append(r)
    TBL = pd.DataFrame(rows); TBL.to_csv(na_rep='n.d.', path_or_buf=T / 'Table_R1.csv', index=False)

    # ---- Discussion checks
    NSd = NS.copy()
    vrows = []
    for sd in C.SEEDS:
        bm = nd_median(NSd[NSd.run_seed == sd], ['scheme', 'box', 'method'])
        for grp, names in GROUPS:
            for n in names:
                rr = {s: ST.three_way(bm[bm.scheme == s].pivot_table(index='box', columns='method', values=n), ST.GEN) for s in C.SCHEMES}
                cw = {m: sum(1 for s in C.SCHEMES if rr[s] and rr[s]['winner'] == m and rr[s]['clear']) for m in ST.GEN}
                vrows.append(dict(run_seed=sd, group=grp, score=n, verdict=next((m for m in cw if cw[m] >= 2), 'no method')))
    PS = pd.DataFrame(vrows); PS.to_csv(na_rep='n.d.', path_or_buf=T / 'check_per_seed_verdict.csv', index=False)
    PSs = PS.groupby('run_seed').verdict.value_counts().unstack(fill_value=0); PSs.to_csv(na_rep='n.d.', path_or_buf=T / 'check_per_seed_verdict_summary.csv')
    allv = pd.read_csv(P.RP.TABLES_DIR / 'stats_verdict.csv')                 # n.d. rule (release default)
    bh = pd.concat([compare(BMr, 'EVAE', 'ADFNE'), compare(BMr, 'EVAE', 'KDE')], ignore_index=True)
    p = bh.p.values; o = np.argsort(p); m_ = len(p); q = np.empty(m_)
    q[o] = np.minimum.accumulate((p[o] * m_ / np.arange(1, m_ + 1))[::-1])[::-1]; bh['q_bh'] = np.minimum(q, 1.0)
    bh['result_bh'] = np.where(bh.q_bh >= 0.05, 'no difference', np.where(bh.median_diff < 0, 'better', 'worse'))
    bh.to_csv(na_rep='n.d.', path_or_buf=T / 'check_benjamini_hochberg.csv', index=False)
    BHs = bh.groupby('second').result_bh.value_counts().unstack(fill_value=0); BHs.to_csv(na_rep='n.d.', path_or_buf=T / 'check_benjamini_hochberg_summary.csv')
    LB = []
    for s in ('S1',):
        sub = BM[BM.scheme == s]
        for grp, names in GROUPS:
            for n in names:
                piv = sub.pivot_table(index='box', columns='method', values=n)
                for o_, r_ in ST.paired(piv, 'EVAE', ('ADFNE (neighbours)', 'KDE (neighbours)')).items():
                    LB.append(dict(test=P.TEST[s], group=grp, score=n, against=o_, **r_))
    LBd = pd.DataFrame(LB); LBd.to_csv(na_rep='n.d.', path_or_buf=T / 'check_local_baselines.csv', index=False)
    LBc = LBd.groupby(['against', 'group']).result.value_counts().unstack(fill_value=0).reset_index()
    LBa = LBd.groupby('against').result.value_counts().unstack(fill_value=0).reset_index().assign(group='All')
    LBc = pd.concat([LBc, LBa], ignore_index=True); LBc.to_csv(na_rep='n.d.', path_or_buf=T / 'check_local_baselines_counts.csv', index=False)
    rng = np.random.default_rng(20261001); bs = []
    for s in C.SCHEMES:
        sub = BMr[BMr.scheme == s]
        for grp, names in GROUPS:
            for n in names:
                piv = sub.pivot_table(index='box', columns='method', values=n)
                for b_ in ('ADFNE', 'KDE'):
                    x = piv[['EVAE', b_]].replace([np.inf], 1e9).dropna(); d = (x['EVAE'] - x[b_]).values
                    if len(d) < 3: continue
                    idx = rng.integers(0, len(d), size=(2000, len(d))); med = np.median(d[idx], axis=1)
                    lo, hi = np.percentile(med, [2.5, 97.5])
                    bs.append(dict(test=P.TEST[s], group=grp, score=n, against=b_, median_diff=float(np.median(d)), ci_low=float(lo), ci_high=float(hi),
                                   ci=('EVAE better' if hi < 0 else ('EVAE worse' if lo > 0 else 'includes 0'))))
    BS = pd.DataFrame(bs); BS.to_csv(na_rep='n.d.', path_or_buf=T / 'check_bootstrap_ci.csv', index=False)
    BSs = BS.groupby('against').ci.value_counts().unstack(fill_value=0); BSs.to_csv(na_rep='n.d.', path_or_buf=T / 'check_bootstrap_ci_summary.csv')

    # ---- print summary
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    print(CNT[CNT.group == 'All'].to_string(index=False))
    print(MS.round(3).to_string(index=False)); print(SPd.round(2).to_string(index=False))
    print('per-seed verdict\n', PSs, '\nall seeds', allv.verdict.value_counts().to_dict())
    print('BH\n', BHs); print('local baselines\n', LBc[LBc.group == 'All']); print('bootstrap\n', BSs)
    return TBL


if __name__ == '__main__':
    main()
