# -*- coding: utf-8 -*-
"""Decision 3 (MY_VIEW_ON_FINAL_REVIEW Section 8, option b): LABELLED SIDE CHECK, ADFNE and KDE given the four learned
trace-direction clusters (and the unclustered component), recounted under the CURRENT undefined-score (n.d.) rule with
the SAME scorer and tests as the paper's main comparison. No new generation: the existing cluster-informed realisations
of the study (cv_study networks/<test>/bgbase/ADFNE and KDE, 2,880 each; PROTOCOL_SETS_BG.md Section 3, code
cv_generate.py 'base <test> bgbase <fold>' with cv_common.fit_baseline_stats_bg) are scored against the held-out windows
and compared with the paper's EVAE realisations (release networks/<test>/EVAE).

Same as the main comparison (paper/code/discussion.py recount, scripts/statistical_tests.py score):
  scorer         statistical_tests.score (38 error scores, five groups), the fold's learned cluster model
                 (data/orientation_clusters, C1-C4 in the reference order 125, 56, 27, 89 deg);
  n.d. rule      inf (fewer than 2 members of a cluster the held-out window has) and NaN are excluded; window value =
                 median over the realisations where the score is defined (checks.nd_median);
  tests          paired two-sided Wilcoxon (zsplit) over held-out windows, Holm over the two baselines, alpha 0.05,
                 fewer than 3 windows = no difference (discussion.holm_tests); 38 scores x 3 tests = 114 comparisons;
  verdict        statistical_tests.three_way over (EVAE, ADFNE-cl, KDE-cl), "overall better" = clear winner in >= 2 tests.
The functions are copied verbatim from the release and are SELF-TESTED: applied to the release realisation scores of
the main comparison they must reproduce paper/tables/recount_EVAE_vs_baselines.csv row by row (24 / 84 / 6 and
21 / 88 / 5) and the verdict EVAE 7 / ADFNE 0 / KDE 0 / no method 31; the EVAE scores recomputed here must equal the
release table tables/stats_network_scores.csv.
Provenance checks (all asserted): file inventory 2,880 per baseline, exactly the release window cases, seeds and draws;
the study's cluster models and box library are byte-identical to the release's; the cluster-informed fit has K + 1 = 5
classes in every fold; one KDE realisation per fold regenerated in memory (not saved, not scored) from the
cluster-informed fit with its recorded generator seed equals the stored file bit for bit (new-bench fold 4: with the
clusters in setbg's weight order, as at generation time; the release file holds the same clusters re-stored in the
reference order, 'order_note'); the study's EVAE realisations
(geobg) equal the release EVAE files.
The old side-check counts (first-version rule, different scorer) are NOT used anywhere.
Outputs (../tables/): sidecheck_baselines_with_clusters_scores.csv (realisation scores), _panel_medians.csv, _tests.csv,
_counts.csv, _verdict.csv, _summary.json, _log.txt. Read-only on the release and the study networks."""
# Repository copy (2 October 2026): only the paths were changed (repository root, outputs to work/side_check).
import sys, os, math, json, filecmp, zlib
sys.dont_write_bytecode = True
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy.stats import wilcoxon, rankdata

def _repo_root():                                       # repository version: the folder holding .repo-root (or EVAE_REPO)
    if os.environ.get('EVAE_REPO'):
        return Path(os.environ['EVAE_REPO']).resolve()
    for d in Path(__file__).resolve().parents:
        if (d / '.repo-root').exists():
            return d
    raise RuntimeError('repository root not found: no .repo-root marker (or set EVAE_REPO)')


REL = _repo_root()
CV = Path(os.environ.get('EVAE_CV_STUDY', str(Path(__file__).resolve().parents[1])))   # repository: side_check/ holds networks/<test>/bgbase/; main() also needs the study folder (not released) for its provenance checks
LIB_CV = Path(os.environ.get('EVAE_STUDY_BOX_LIBRARY', str(REL / 'data' / 'box_library')))   # the study's copy of the box library (byte-identical)
OUT = Path(os.environ.get('SIDE_CHECK_OUT', str(REL / 'work' / 'side_check')))
OUT.mkdir(parents=True, exist_ok=True)   # repository: a rerun never writes over side_check/tables
os.environ.setdefault('S1_WORK_DIR', str(REL / 'work' / 'side_check' / 'scratch'))
sys.path[:0] = [str(REL / 'scripts'), str(REL / 'src' / 'study'), str(REL / 'src'), str(REL / 'src' / 'evaluation')]
import study as C                  # noqa: E402
import setbg as SB                 # noqa: E402
import statistical_tests as ST     # noqa: E402

NAMES, GROUPS = ST.NAMES, ST.GROUPS
TEST = {'S1': 'gap-filling', 'S2': 'new-bench', 'S3': 'new-stretch'}
GROUP_PAPER = {'Orientation distribution': 'Trace-direction distribution', 'Orientation clusters': 'Trace-direction clusters',
               'Length': 'Trace length', 'Density': 'Density and spacing', 'Topology': 'Topology', 'All': 'All'}
BL = {'ADFNE-cl': 'ADFNE', 'KDE-cl': 'KDE'}           # side-check method -> study network folder
METHODS3 = ('EVAE', 'ADFNE-cl', 'KDE-cl')


def cv_net(scheme, m, fi, b, sd, d):
    return CV / 'networks' / scheme / 'bgbase' / BL[m] / ('f%d_%s_s%d_d%02d.csv' % (fi, b, sd, d))


# ---------------------------------------------------------------- verbatim from the release (paper/code)
def nd_median(D, keys):                                   # checks.py lines 36-40
    return D.replace([np.inf, -np.inf], np.nan).groupby(keys)[NAMES].median().reset_index()


def wil(d):                                               # checks.py wil
    d = np.asarray(d, float)
    if len(d) < 3 or np.allclose(d, 0):
        return 1.0, 0.0, 0.0
    p = float(wilcoxon(d, zero_method='zsplit').pvalue)
    r = rankdata(np.abs(d)); wp = r[d > 0].sum() + r[d == 0].sum() / 2; wm = r[d < 0].sum() + r[d == 0].sum() / 2
    return p, wp, wm


def holm_tests(BM, pairs, schemes=C.SCHEMES):             # discussion.py holm_tests
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
                    out.append(dict(test=TEST[s], scheme=s, group=grp, score=n, comparison=name, first=a, second=b, n_panels=nb, median_diff=md, p=p, p_holm=ph,
                                    result='no difference' if (ph >= 0.05 or nb < 3) else ('better' if md < 0 else 'worse')))
    return pd.DataFrame(out)


def count(D, by='comparison'):                            # discussion.py count
    rows = []
    for c_, g in D.groupby(by, sort=False):
        for grp in [x for x, _ in ST.GROUPS] + ['All']:
            q = g if grp == 'All' else g[g.group == grp]; v = q.result.value_counts()
            rows.append({by: c_, 'group': grp, 'better': int(v.get('better', 0)), 'no_difference': int(v.get('no difference', 0)), 'worse': int(v.get('worse', 0))})
    return pd.DataFrame(rows)


def verdict(BM, methods):                                 # discussion.py verdict, methods as argument
    out = []
    for grp, names in ST.GROUPS:
        for n in names:
            rr = {s: ST.three_way(BM[BM.scheme == s].pivot_table(index='box', columns='method', values=n), methods) for s in C.SCHEMES}
            cw = {m: sum(1 for s in C.SCHEMES if rr[s] and rr[s]['winner'] == m and rr[s]['clear']) for m in methods}
            out.append(dict(group=grp, score=n, **{'%s_winner' % TEST[s]: ('%s (%s)' % (rr[s]['winner'], 'clear' if rr[s]['clear'] else 'tie')) if rr[s] else 'n.d.' for s in C.SCHEMES},
                            verdict=next((m for m in cw if cw[m] >= 2), 'no method')))
    return pd.DataFrame(out)


# ---------------------------------------------------------------- cluster-informed fit (cv_common.fit_baseline_stats_bg, verbatim)
def fit_baseline_stats_bg(fit_panels, model):
    lines = np.vstack([p['lines'] for p in fit_panels]); cen, lens, angs = C.common.geom(lines)
    lab = SB.classify(angs, model); mean_ymax = float(np.mean([p['y_max'] for p in fit_panels])); sets = []
    for k in range(model['K'] + 1):
        use = lab == k
        if use.sum() < 3:
            continue
        counts = [int((SB.classify(C.common.geom(p['lines'])[2], model) == k).sum()) if len(p['lines']) else 0 for p in fit_panels]
        sets.append({'set': k, 'centre_deg': math.degrees(float(C.axial_mean(angs[use]))),
                     'kappa_dir': C.common.kappa_directional_from_axial(angs[use]), 'length_fit': C.common.trunc_exp_fit(lens[use]),
                     'mean_count': float(np.mean(counts)), 'angles': angs[use], 'lengths': lens[use], 'centres': cen[use]})
    return {'sets': sets, 'mean_ymax': mean_ymax}


# ---------------------------------------------------------------- per fold
def fold_job(job):
    s, fi = job
    lib = C.load_library(); sp = C.split(s, fi, lib); model = C.cluster_model(s, fi); rows = []; prov = {}
    # provenance: the cluster-informed fit and one KDE realisation regenerated in memory (first window, run seed 1337, draw 0)
    b0 = sp['test'][0]; sd0 = C.SEEDS[0]
    S0 = C.load_net(cv_net(s, 'KDE-cl', fi, b0, sd0, 0))
    # setbg.fit stores the clusters by weight (largest first); the release files hold them in the reference order
    # (125, 56, 27, 89 deg; 'order_note'). The study generated the baselines before that re-ordering, so the class
    # order (and with it the random-number sequence of the KDE) is tried in both orders; the clusters are the same.
    o = list(np.argsort(-np.asarray(model['w_sets'])))
    m_w = dict(model, mu2=[model['mu2'][i] for i in o], kappa2=[model['kappa2'][i] for i in o], w_sets=[model['w_sets'][i] for i in o],
               centres_deg=[model['centres_deg'][i] for i in o])
    match = 'none'
    for lab_, mm in (('reference order', model), ('weight order', m_w)):
        st = fit_baseline_stats_bg([sp['panels'][k] for k in sp['fit']], mm)
        L0 = np.asarray(C.generators.generate_kde(st, sp['panels'][b0]['y_max'], C.gen_seed('KDE', s, 'bgbase', fi, b0, sd0, 0)), float).reshape(-1, 4)
        if L0.shape == S0.shape and np.array_equal(L0, S0):
            match = lab_; break
    prov = dict(scheme=s, fold=fi, classes=len(st['sets']), K=model['K'], reference_order_is_weight_order=bool(o == list(range(model['K']))),
                class_mean_counts=[round(x['mean_count'], 2) for x in st['sets']],
                kde_regenerated_equals_file=match != 'none', kde_match_order=match)
    for b in sp['test']:
        real = sp['panels'][b]
        for m in ('EVAE',) + tuple(BL):
            for sd in C.SEEDS:
                for d in range(C.NDRAW):
                    p = C.net_path(s, 'EVAE', fi, b, sd, d) if m == 'EVAE' else cv_net(s, m, fi, b, sd, d)
                    L = C.load_net(p)
                    if m == 'EVAE':
                        prov.setdefault('evae_equals_study_geobg', True)
                        q = CV / 'networks' / s / 'geobg' / 'EVAE' / p.name
                        prov['evae_equals_study_geobg'] &= q.exists() and filecmp.cmp(p, q, shallow=False)
                    rows.append(dict(scheme=s, fold=fi, box=b, method=m, run_seed=sd, draw=d, n=len(L), **ST.score(L, real['lines'], real['y_max'], model)))
    return rows, prov


def main():
    log = []
    def say(x=''):
        print(x); log.append(str(x))
    say('sidecheck_baselines_with_clusters.py: LABELLED SIDE CHECK, ADFNE and KDE given the four learned clusters (n.d. rule, release scorer and tests)')
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]

    # ---- inventory: exactly the release window cases, seeds and draws
    exp = {m: set() for m in BL}
    for s, fi in jobs:
        for b in C.folds(s, lib)[fi]:
            for sd in C.SEEDS:
                for d in range(C.NDRAW):
                    for m in BL:
                        exp[m].add(cv_net(s, m, fi, b, sd, d))
    for m, folder in BL.items():
        have = set()
        for s in C.SCHEMES:
            have |= {p for p in (CV / 'networks' / s / 'bgbase' / folder).glob('*.csv')}
        have = {Path(str(p)) for p in have}; expn = {Path(str(p)) for p in exp[m]}
        say('inventory %s: %d files in the study folders, %d expected window-case/seed/draw files, all present: %s, extras: %d'
            % (m, len(have), len(expn), expn <= have, len(have - expn)))
        assert len(have) == 2880 and have == expn
    # ---- identical inputs
    same_models = all(filecmp.cmp(CV / 'work' / 'setbg' / ('%s_f%d.json' % j), REL / 'data' / 'orientation_clusters' / ('%s_f%d.json' % j), shallow=False) for j in jobs)
    same_lib = filecmp.cmp(LIB_CV / 'box_manifest.csv', REL / 'data' / 'box_library' / 'box_manifest.csv', shallow=False) and all(
        filecmp.cmp(p, REL / 'data' / 'box_library' / 'boxes' / p.name, shallow=False) for p in (LIB_CV / 'boxes').glob('*.json'))
    logs = [json.load(open(CV / 'work' / 'logs' / ('gen_base_%s_bgbase_f%d.json' % j))) for j in jobs]
    say('study cluster models (work/setbg) byte-identical to release data/orientation_clusters: %s' % same_models)
    say('study box library byte-identical to release data/box_library: %s' % same_lib)
    say('study generation logs: variant bgbase in %d of 15 folds; networks per log %d' % (sum(g['variant'] == 'bgbase' for g in logs), sum(g['networks'] for g in logs)))
    assert same_models and same_lib and all(g['variant'] == 'bgbase' for g in logs) and sum(g['networks'] for g in logs) == 2880

    # ---- score
    with Pool(min(12, len(jobs))) as pool:
        res = pool.map(fold_job, jobs)
    df = pd.DataFrame([r for rr, _ in res for r in rr]); prov = pd.DataFrame([p for _, p in res])
    say('cluster-informed fit: classes per fold (K + 1 = 5 expected) %s; KDE realisation regenerated in memory = stored file in %d of 15 folds (%s); release EVAE files = study geobg files in %d of 15 folds'
        % (sorted(prov.classes.unique().tolist()), prov.kde_regenerated_equals_file.sum(),
           '; '.join('%s f%d: %s' % (r.scheme, r.fold, r.kde_match_order) for r in prov.itertuples() if r.kde_match_order != 'reference order') or 'all in the reference order',
           prov.evae_equals_study_geobg.sum()))
    say('folds whose stored cluster order differs from the weight order: %s' % ['%s f%d' % (r.scheme, r.fold) for r in prov.itertuples() if not r.reference_order_is_weight_order])
    assert (prov.classes == 5).all() and prov.kde_regenerated_equals_file.all() and prov.evae_equals_study_geobg.all()
    say('realisations scored: %s' % df.method.value_counts().to_dict())
    say('empty realisations: %s; traces per realisation (min / median / max): %s' % (
        df[df.n == 0].method.value_counts().to_dict(), {m: (int(g.n.min()), float(g.n.median()), int(g.n.max())) for m, g in df.groupby('method')}))

    # ---- self-test 1: EVAE scores recomputed = release table (n.d. rule)
    NS = pd.read_csv(REL / 'tables' / 'stats_network_scores.csv', na_values=['n.d.'])
    e1 = df[df.method == 'EVAE'].replace([np.inf, -np.inf], np.nan).set_index(['scheme', 'box', 'run_seed', 'draw'])[NAMES].sort_index()
    e0 = NS[NS.method == 'EVAE'].set_index(['scheme', 'box', 'run_seed', 'draw'])[NAMES].sort_index()
    ok1 = e1.shape == e0.shape and np.allclose(e1.values, e0.values, equal_nan=True)
    say('self-test 1, EVAE scores recomputed here = release tables/stats_network_scores.csv: %s' % ok1); assert ok1
    # ---- self-test 2: the copied tests reproduce the paper's main recount and verdict
    BMr = nd_median(NS, ['scheme', 'fold', 'box', 'method'])
    Dm = holm_tests(BMr, [('EVAE vs ADFNE', 'EVAE', 'ADFNE'), ('EVAE vs KDE', 'EVAE', 'KDE')])
    ref = pd.read_csv(REL / 'paper' / 'tables' / 'recount_EVAE_vs_baselines.csv')
    ok2 = list(Dm.result) == list(ref.result) and np.allclose(Dm.p_holm.values, ref.p_holm.values) and len(Dm) == 228
    Vm = verdict(BMr, ST.GEN).verdict.value_counts().to_dict()
    cm = count(Dm); say('self-test 2, main recount reproduced row by row (228 rows): %s; All: %s; verdict %s' % (
        ok2, cm[cm.group == 'All'][['comparison', 'better', 'no_difference', 'worse']].values.tolist(), Vm))
    assert ok2 and Vm == {'no method': 31, 'EVAE': 7}

    # ---- the side check
    sc = df[df.method != 'EVAE'].replace([np.inf, -np.inf], np.nan)
    OUT.mkdir(exist_ok=True)
    sc.to_csv(OUT / 'sidecheck_baselines_with_clusters_scores.csv', index=False, na_rep='n.d.')
    BMc = nd_median(df, ['scheme', 'fold', 'box', 'method'])
    BMc.to_csv(OUT / 'sidecheck_baselines_with_clusters_panel_medians.csv', index=False, na_rep='n.d.')
    nd_cells = {m: int(g[NAMES].isna().sum().sum()) for m, g in BMc.groupby('method')}
    say('undefined window-score cells (of 4,560 per method): %s' % nd_cells)
    D = holm_tests(BMc, [('EVAE vs ADFNE-cl', 'EVAE', 'ADFNE-cl'), ('EVAE vs KDE-cl', 'EVAE', 'KDE-cl')])
    D['group_paper'] = D.group.map(GROUP_PAPER)
    D.to_csv(OUT / 'sidecheck_baselines_with_clusters_tests.csv', index=False, na_rep='n.d.')
    CN = count(D); CN['group_paper'] = CN.group.map(GROUP_PAPER)
    bt = count(D.assign(ct=D.comparison + ' | ' + D.test), by='ct'); bt = bt[bt.group == 'All']
    CN.to_csv(OUT / 'sidecheck_baselines_with_clusters_counts.csv', index=False)
    V = verdict(BMc, METHODS3); V.to_csv(OUT / 'sidecheck_baselines_with_clusters_verdict.csv', index=False)
    say('')
    say('RESULT (better / no difference / worse = EVAE error lower / not significantly different / higher; 114 comparisons each)')
    for c_ in ('EVAE vs ADFNE-cl', 'EVAE vs KDE-cl'):
        q = CN[CN.comparison == c_]
        say('  %s: ' % c_ + '; '.join('%s %d / %d / %d' % (r.group_paper, r.better, r.no_difference, r.worse) for r in q.itertuples()))
        say('     by test: ' + '; '.join('%s %d / %d / %d' % (r.ct.split(' | ')[1], r.better, r.no_difference, r.worse) for r in bt[bt.ct.str.startswith(c_ + ' |')].itertuples()))
        for res_ in ('worse', 'better'):
            rr = D[(D.comparison == c_) & (D.result == res_)]
            say('     EVAE %s (%d): %s' % (res_, len(rr), '; '.join('%s %s' % (r.test, r.score) for r in rr.itertuples())))
    vv = V.verdict.value_counts().to_dict()
    say('  "overall better" verdict (EVAE / ADFNE-cl / KDE-cl / no method): %d / %d / %d / %d' % tuple(vv.get(k, 0) for k in METHODS3 + ('no method',)))
    for m in METHODS3:
        say('     %s scores: %s' % (m, ', '.join(V[V.verdict == m].score)))
    for s in C.SCHEMES:
        col = '%s_winner' % TEST[s]
        say('     clear wins %s: %s' % (TEST[s], {m: int((V[col] == '%s (clear)' % m).sum()) for m in METHODS3}))
    summ = dict(counts={c_: {GROUP_PAPER[r.group]: [r.better, r.no_difference, r.worse] for r in CN[CN.comparison == c_].itertuples()} for c_ in ('EVAE vs ADFNE-cl', 'EVAE vs KDE-cl')},
                by_test={r.ct: [r.better, r.no_difference, r.worse] for r in bt.itertuples()},
                verdict={k: int(vv.get(k, 0)) for k in METHODS3 + ('no method',)},
                verdict_scores={m: V[V.verdict == m].score.tolist() for m in METHODS3},
                nd_cells=nd_cells, provenance=prov.to_dict('records'))
    json.dump(summ, open(OUT / 'sidecheck_baselines_with_clusters_summary.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    (OUT / 'sidecheck_baselines_with_clusters_log.txt').write_text('\n'.join(log) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
