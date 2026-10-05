# Score the weight variants vs the paper model (released S1 EVAE realisations) with the release scorer (n.d. rule);
# write Table_weights.csv/.md, Table_weights_tests.csv, outputs/tests_per_score.csv. Adapted from nmax_sensitivity score_nmax.py.
_REPO = __import__('pathlib').Path(__file__).resolve().parents[2]   # repository root (sensitivity/<test>/ lies two levels down)
import sys, json, math
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
W = Path(__file__).resolve().parent
REL = (_REPO)
sys.path[:0] = [str(W / 'code' / 'scripts'), str(W / 'code' / 'src' / 'study')]
import os; os.environ['S1_WORK_DIR'] = str(W / 'work')
import study as C, setbg as SB
import statistical_tests as ST
import make_figures as MF
VAR = ['A_half', 'A_double', 'B_half', 'B_double', 'C_half', 'C_double', 'D_half', 'D_double']
ROOT = {v: W / 'networks' / v for v in VAR}; ROOT['Paper'] = REL / 'networks'; ALL = ['Paper'] + VAR; O = W / 'outputs'


def job(fi):
    lib = C.load_library(); sp = C.split('S1', fi, lib); model = C.cluster_model('S1', fi); sc, pr, tr = [], [], []
    for b in sp['test']:
        real = sp['panels'][b]; ym = real['y_max']
        nets = {'Held-out': [real['lines']]}
        for v in ALL:
            nets[v] = [C.load_net(C.net_path('S1', 'EVAE', fi, b, sd, d, root=ROOT[v])) for sd in C.SEEDS for d in range(C.NDRAW)]
        for m, Ls in nets.items():
            P = [MF.props(L, ym, model) for L in Ls]
            pr.append(dict(scheme='S1', fold=fi, box=b, method=m, **(P[0] if m == 'Held-out' else pd.DataFrame(P).median(numeric_only=True).to_dict())))
            for i, L in enumerate(Ls):
                L = np.asarray(L, float).reshape(-1, 4)
                if m != 'Held-out':
                    sc.append(dict(fold=fi, box=b, method=m, k=i, n=len(L), **ST.score(L, real['lines'], ym, model)))
                if not len(L): continue
                _, ln, th = C.common.geom(L)
                tr.append(pd.DataFrame(dict(scheme='S1', method=m, box=b, length=ln * C.M, theta=np.degrees(th), oc=MF.canon(SB.classify(th, model), model), weight=1.0 / len(Ls))))
    return sc, pr, pd.concat(tr)


def paired2(piv, ref, others):
    res = {}
    for o in others:
        sub = piv[[o, ref]].dropna(); d = (sub[o] - sub[ref]).values
        p = 1.0 if len(d) < 3 or np.allclose(d, 0) else float(wilcoxon(d, zero_method='zsplit').pvalue)
        res[o] = (p, float(np.median(d)) if len(d) else np.nan, len(sub))
    ps = sorted((res[o][0], o) for o in others); hol, run = {}, 0.0
    for i, (p, o) in enumerate(ps):
        run = max(run, min(1.0, p * (len(ps) - i))); hol[o] = run
    return {o: dict(n_windows=res[o][2], median_diff=res[o][1], p_raw=res[o][0], p_holm=hol[o],
                    result='no difference' if hol[o] >= 0.05 else ('better' if res[o][1] < 0 else 'worse')) for o in others}


if __name__ == '__main__':
    with Pool(4) as pool:
        R = pool.map(job, range(4))
    S = pd.DataFrame([r for x in R for r in x[0]]).replace([np.inf, -np.inf], np.nan)     # n.d. rule
    PR = pd.DataFrame([r for x in R for r in x[1]]); TR = pd.concat([x[2] for x in R])
    S.to_csv(O / 'scores_per_realisation.csv', index=False, na_rep='n.d.'); PR.to_csv(O / 'properties_per_window.csv', index=False)
    BM = S.groupby(['fold', 'box', 'method'])[ST.NAMES + ['n']].median().reset_index(); BM.to_csv(O / 'scores_window_medians.csv', index=False, na_rep='n.d.')
    dec = []
    for grp, names in ST.GROUPS:
        for n in names:
            piv = BM.pivot_table(index='box', columns='method', values=n)
            for o, r in paired2(piv, 'Paper', VAR).items():
                dec.append(dict(group=grp, score=n, variant=o, median_paper=piv['Paper'].median(), median_variant=piv[o].median(), **r))
    D = pd.DataFrame(dec); D.to_csv(O / 'tests_per_score.csv', index=False)
    rows = []
    for cmp_ in VAR:
        for grp in [g for g, _ in ST.GROUPS] + ['All']:
            q = D[D.variant == cmp_]; q = q if grp == 'All' else q[q.group == grp]; v = q.result.value_counts()
            rows.append(dict(variant=cmp_, group=grp, better=int(v.get('better', 0)), no_difference=int(v.get('no difference', 0)), worse=int(v.get('worse', 0)), scores=len(q)))
    CT = pd.DataFrame(rows); CT.to_csv(W / 'Table_weights_tests.csv', index=False)
    print(CT.to_string(index=False)); print(D[D.result != 'no difference'].to_string(index=False))
    PR.to_pickle(O / 'PR.pkl'); TR.to_pickle(O / 'TR.pkl')
    import make_table; make_table.main()
