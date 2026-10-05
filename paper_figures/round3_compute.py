# -*- coding: utf-8 -*-
"""Round 3 (plan PLAN_ROUND3_AUTHOR_COMMENTS_2026-10-03, Sections E and H8): NO RETRAINING. Read-only calculation on
SAVED realisations of the release (SECTION1_EVAE_ADFNE_KDE_RELEASE_2026-10-01) with the release and engineering code.

Per realisation (24 per window case) and per window case:
  all tests: Held-out, Reference (fracture-removed; the 8 surrounding / nearest available mapped windows),
             Representative (representative generation = EVAE from 8 randomly chosen mapped windows of the wall,
             release paper/networks/random_context);
  main hold-out test (release S1) also: EVAE (local generation), ADFNE, KDE.
  Release parameters (make_figures.props), engineering measures (engineering_demo eng_metrics.measures), node counts
  (release topology: I free ends, Y T-ends, X crossings).
Window value = median over the 24 realisations (spanning: mean; softest direction: axial mean); test value = release
make_figures.table_value / engineering test_value rules (median over windows; spanning: mean).
Checks (asserted): window values equal release paper/tables/panel_properties.csv (Representative = 'Random context',
EVAE, Held-out, Reference) and engineering_demo tables/engineering_panel_values.csv (S1: EVAE, ADFNE, KDE, Held-out,
Reference (fracture-removed)).
Output (work/round3_data): round3_realisation_values.csv, round3_window_values.csv, round3_test_values.csv,
round3_node_counts.csv, round3_traces.csv.
Usage: python -B round3_compute.py      (a few minutes, 12 processes)"""
import os, sys
from pathlib import Path
from multiprocessing import Pool
sys.dont_write_bytecode = True
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
HERE = Path(__file__).resolve().parent
ENGD = (_RR.REPO / 'engineering')
REL = _RR.REPO
os.environ['S1_WORK_DIR'] = str(_RR.SCRATCH)
sys.path[:0] = [str(REL / 'scripts'), str(REL / 'src' / 'study'), str(REL / 'paper' / 'code'), str(ENGD / 'code')]
import numpy as np, pandas as pd
import study as C
import setbg as SB
from topology import topology
OUT = HERE.parent / 'work' / 'round3_data'; OUT.mkdir(parents=True, exist_ok=True)
RC_ROOT = REL / 'paper' / 'networks' / 'random_context'
ENGV = ['n', 'p', 'rho', 'E_along', 'E_down', 'aniso', 'soft_dir_deg', 'span', 'largest_share', 'term_share', 'pX',
        'k_mean_C1', 'k_mean_C2', 'k_max_C1', 'k_max_C2']
ENGK = ['p', 'E_along', 'E_down', 'aniso', 'largest_share', 'term_share', 'pX', 'k_max_C1', 'k_max_C2', 'k_mean_C1', 'k_mean_C2']


def job(a):
    import make_figures as MF
    import eng_metrics as M
    s, fi = a
    lib = C.load_library(); sp = C.split(s, fi, lib); Pn = sp['panels']; model = C.cluster_model(s, fi); dirs = M.cluster_dirs(model)
    rows, nodes, traces = [], [], []
    for b in sp['test']:
        real = Pn[b]; ym = real['y_max']; ctx = C.context(sp, b)
        sets = {'Held-out': [(real['lines'], ym)], 'Reference': [(Pn[k]['lines'], Pn[k]['y_max']) for k in ctx],
                'Representative': [(C.load_net(C.net_path(s, 'EVAE', fi, b, sd, d, root=RC_ROOT)), ym) for sd in C.SEEDS for d in range(C.NDRAW)]}
        if s == 'S1':
            for m in ('EVAE', 'ADFNE', 'KDE'):
                sets[m] = [(C.load_net(C.net_path(s, m, fi, b, sd, d)), ym) for sd in C.SEEDS for d in range(C.NDRAW)]
        for m, LL in sets.items():
            for k, (L, y) in enumerate(LL):
                L = np.asarray(L, float).reshape(-1, 4)
                pr = MF.props(L, y, model)
                ev = M.measures(L, y, model, dirs) if len(L) else {kk: np.nan for kk in ENGV}
                tp = topology(L, y)
                rows.append(dict(scheme=s, fold=fi, box=b, method=m, k=k, **pr, **{'eng_' + kk: ev.get(kk, np.nan) for kk in ENGV}))
                nodes.append(dict(scheme=s, fold=fi, box=b, method=m, k=k, area_m2=400.0 * y, n_traces=len(L), n_I=tp['n_I'], n_Y=tp['n_Y'], n_X=tp['n_X']))
                if len(L):
                    _, ln, th = C.common.geom(L)
                    traces.append(pd.DataFrame(dict(scheme=s, method=m, box=b, length=ln * C.M, theta=np.degrees(th),
                                                    oc=MF.canon(SB.classify(th, model), model), weight=1.0 / len(LL))))
    return rows, nodes, pd.concat(traces, ignore_index=True)


if __name__ == '__main__':
    import make_figures as MF
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]
    with Pool(min(12, len(jobs))) as pool:
        res = pool.map(job, jobs)
    R = pd.DataFrame([r for rr in res for r in rr[0]]); N = pd.DataFrame([r for rr in res for r in rr[1]])
    TR = pd.concat([r[2] for r in res], ignore_index=True)
    R.to_csv(OUT / 'round3_realisation_values.csv', index=False); N.to_csv(OUT / 'round3_node_counts.csv', index=False)
    TR.to_csv(OUT / 'round3_traces.csv', index=False)
    K = ['scheme', 'fold', 'box', 'method']
    num = [c for c in R.columns if c not in K + ['k']]
    W = R.groupby(K)[[c for c in num if c not in ('eng_span', 'eng_soft_dir_deg')]].median().reset_index()
    W = W.merge(R.groupby(K)['eng_span'].mean().reset_index(), on=K)
    sd_ = R.groupby(K)['eng_soft_dir_deg'].apply(lambda a: MF.axial_mean_deg(a.dropna().values) if a.notna().any() else np.nan).reset_index()
    W = W.merge(sd_, on=K)
    W.to_csv(OUT / 'round3_window_values.csv', index=False)
    # ---- checks against the release and the engineering demonstration
    PP = pd.read_csv(REL / 'paper' / 'tables' / 'panel_properties.csv', na_values=['n.d.']).replace({'Random context': 'Representative'})
    bad = 0; nchk = 0
    for col in ['P20', 'P21', 'P22', 'len_med', 'len_p90', 'nn_med', 'CL', 'pI', 'pY', 'pX', 'OC1', 'OC2', 'OC3', 'OC4']:
        for m in ('Representative', 'EVAE', 'Held-out', 'Reference'):
            a = W[W.method == m].set_index(['scheme', 'box'])[col]; b = PP[PP.method == m].set_index(['scheme', 'box'])[col].reindex(a.index)
            nchk += 1
            if not np.allclose(a.values, b.values, equal_nan=True, rtol=1e-9, atol=1e-12):
                bad += 1; print('MISMATCH panel_properties', m, col)
    EV = pd.read_csv(ENGD / 'tables' / 'engineering_panel_values.csv', na_values=['n.d.'])
    for col in ['p', 'E_along', 'E_down', 'aniso', 'largest_share', 'term_share', 'pX', 'k_max_C1', 'k_max_C2', 'k_mean_C1', 'k_mean_C2', 'span']:
        for m, me in (('EVAE', 'EVAE'), ('ADFNE', 'ADFNE'), ('KDE', 'KDE'), ('Held-out', 'Held-out'), ('Reference', 'Reference (fracture-removed)')):
            a = W[(W.method == m) & (W.scheme == 'S1')].set_index('box')['eng_' + col]
            b = EV[(EV.method == me) & (EV.scheme == 'S1')].set_index('box')[col].reindex(a.index)
            nchk += 1
            if not np.allclose(a.values, b.values, equal_nan=True, rtol=1e-9, atol=1e-12):
                bad += 1; print('MISMATCH engineering', m, col)
    print('checks: %d column comparisons, %s' % (nchk, 'all equal' if not bad else '%d mismatches' % bad))
    # ---- test values (release rules)
    rows = []
    for s in C.SCHEMES:
        for m in W[W.scheme == s].method.unique():
            r = dict(scheme=s, method=m, n_windows=int(((W.scheme == s) & (W.method == m)).sum()))
            for key, lab, fmt in MF.TABP:
                r[key] = MF.table_value(TR, W, s, m, key)
            a = W[(W.scheme == s) & (W.method == m)]
            for kk in ENGK:
                r[kk] = a['eng_' + kk].median()
            r['span'] = a['eng_span'].mean()
            r['soft_dir_deg'] = (MF.axial_mean_deg(a['eng_soft_dir_deg'].dropna().values) + 90) % 180 - 90
            nn = N[(N.scheme == s) & (N.method == m)]
            r.update(nodes_I=int(nn.n_I.sum()), nodes_Y=int(nn.n_Y.sum()), nodes_X=int(nn.n_X.sum()), n_maps=len(nn))
            rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(OUT / 'round3_test_values.csv', index=False)
    pd.set_option('display.width', 250); print(T.round(3).T.to_string())
    if bad:
        sys.exit(1)
