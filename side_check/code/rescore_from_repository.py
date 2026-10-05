# -*- coding: utf-8 -*-
"""Recompute the labelled side check (ADFNE and KDE given the four learned trace-direction clusters) from the
repository alone. Added for the repository; sidecheck_baselines_with_clusters.py is the script as run by the authors,
whose provenance checks also need the study folder (not released).

  1. scores every realisation in side_check/networks/<test>/bgbase/<ADFNE|KDE>/ with the release scorer
     (scripts/statistical_tests.py score, the fold's cluster model in data/orientation_clusters) against its held-out
     window, and compares the scores with side_check/tables/sidecheck_baselines_with_clusters_scores.csv;
  2. recomputes the window medians, the paired tests (Holm over the two baselines), the counts and the verdict with the
     functions of sidecheck_baselines_with_clusters.py, with the EVAE realisations of networks/ scored in the same
     run (as the authors' script does; they equal tables/stats_network_scores.csv), and compares them with the stored
     tables.
Writes only to work/side_check/ (git-ignored). Usage: python rescore_from_repository.py   (about 1 minute)"""
import sys
sys.dont_write_bytecode = True
from multiprocessing import Pool
from pathlib import Path
import numpy as np, pandas as pd
import sidecheck_baselines_with_clusters as SC

C, ST, NAMES = SC.C, SC.ST, SC.NAMES
STORED = Path(__file__).resolve().parents[1] / 'tables'
KEYS = ['scheme', 'fold', 'box', 'method', 'run_seed', 'draw']


def job(j):
    s, fi = j
    lib = C.load_library(); sp = C.split(s, fi, lib); model = C.cluster_model(s, fi); rows = []
    for b in sp['test']:
        real = sp['panels'][b]
        for m in ('EVAE',) + tuple(SC.BL):
            for sd in C.SEEDS:
                for d in range(C.NDRAW):
                    L = C.load_net(C.net_path(s, 'EVAE', fi, b, sd, d) if m == 'EVAE' else SC.cv_net(s, m, fi, b, sd, d))
                    rows.append(dict(scheme=s, fold=fi, box=b, method=m, run_seed=sd, draw=d, n=len(L),
                                     **ST.score(L, real['lines'], real['y_max'], model)))
    return rows


def same(a, b, cols):
    return a.shape == b.shape and np.allclose(a[cols].values.astype(float), b[cols].values.astype(float), equal_nan=True, rtol=1e-12, atol=1e-12)


def main():
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]
    with Pool(min(12, len(jobs))) as pool:
        df = pd.DataFrame([r for rr in pool.map(job, jobs) for r in rr])
    new = df[df.method != 'EVAE'].replace([np.inf, -np.inf], np.nan).sort_values(KEYS).reset_index(drop=True)
    old = pd.read_csv(STORED / 'sidecheck_baselines_with_clusters_scores.csv', na_values=['n.d.']).sort_values(KEYS).reset_index(drop=True)
    ok1 = new[KEYS].astype(str).equals(old[KEYS].astype(str)) and same(new, old, ['n'] + NAMES)
    print('1. realisation scores (%d realisations) = stored scores: %s' % (len(new), ok1))

    NS = pd.read_csv(SC.REL / 'tables' / 'stats_network_scores.csv', na_values=['n.d.'])
    e1 = df[df.method == 'EVAE'].replace([np.inf, -np.inf], np.nan).sort_values(KEYS).reset_index(drop=True)
    e0 = NS[NS.method == 'EVAE'].sort_values(KEYS).reset_index(drop=True)
    print('   EVAE scores recomputed here = release tables/stats_network_scores.csv: %s' % same(e1, e0, NAMES))
    BM = SC.nd_median(df, ['scheme', 'fold', 'box', 'method'])
    D = SC.holm_tests(BM, [('EVAE vs ADFNE-cl', 'EVAE', 'ADFNE-cl'), ('EVAE vs KDE-cl', 'EVAE', 'KDE-cl')])
    CN = SC.count(D); V = SC.verdict(BM, SC.METHODS3)
    T0 = pd.read_csv(STORED / 'sidecheck_baselines_with_clusters_tests.csv')
    C0 = pd.read_csv(STORED / 'sidecheck_baselines_with_clusters_counts.csv')
    V0 = pd.read_csv(STORED / 'sidecheck_baselines_with_clusters_verdict.csv')
    ok2 = list(D.result) == list(T0.result) and np.allclose(D.p_holm.values, T0.p_holm.values)
    ok3 = CN[['comparison', 'group', 'better', 'no_difference', 'worse']].values.tolist() == C0[['comparison', 'group', 'better', 'no_difference', 'worse']].values.tolist()
    ok4 = list(V.verdict) == list(V0.verdict)
    print('2. tests (%d rows) = stored: %s; counts = stored: %s; verdict = stored: %s' % (len(D), ok2, ok3, ok4))
    SC.OUT.mkdir(parents=True, exist_ok=True)
    new.to_csv(SC.OUT / 'rescored_scores.csv', index=False, na_rep='n.d.'); CN.to_csv(SC.OUT / 'rescored_counts.csv', index=False)
    for c_ in ('EVAE vs ADFNE-cl', 'EVAE vs KDE-cl'):
        r = CN[(CN.comparison == c_) & (CN.group == 'All')].iloc[0]
        print('   %s, all 38 scores x 3 tests: better %d / no difference %d / worse %d' % (c_, r.better, r.no_difference, r.worse))
    sys.exit(0 if ok1 and ok2 and ok3 and ok4 else 1)


if __name__ == '__main__':
    main()
