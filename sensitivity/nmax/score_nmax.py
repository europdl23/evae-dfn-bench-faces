# Score the N_max variants with the release scorer (n.d. rule) and write Table_Nmax.csv/.md, Table_Nmax_tests.csv.
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
VAR = ['N50', 'N120', 'N200']; O = W / 'outputs'


def job(fi):
    lib = C.load_library(); sp = C.split('S1', fi, lib); model = C.cluster_model('S1', fi); sc, pr, tr = [], [], []
    for b in sp['test']:
        real = sp['panels'][b]; ym = real['y_max']
        nets = {'Held-out': [real['lines']]}
        for v in VAR:
            nets[v] = [C.load_net(C.net_path('S1', 'EVAE', fi, b, sd, d, root=W / 'networks' / v)) for sd in C.SEEDS for d in range(C.NDRAW)]
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
            for o, r in paired2(piv, 'N120', ('N50', 'N200')).items():
                dec.append(dict(group=grp, score=n, comparison='%s vs N120' % o, median_N50=piv['N50'].median(), median_N120=piv['N120'].median(), median_N200=piv['N200'].median(), **r))
    D = pd.DataFrame(dec); D.to_csv(O / 'tests_per_score.csv', index=False)
    rows = []
    for cmp_ in ('N50 vs N120', 'N200 vs N120'):
        for grp in [g for g, _ in ST.GROUPS] + ['All']:
            q = D[D.comparison == cmp_]; q = q if grp == 'All' else q[q.group == grp]; v = q.result.value_counts()
            rows.append(dict(comparison=cmp_.replace('N', 'N_max '), group=grp, better=int(v.get('better', 0)), no_difference=int(v.get('no difference', 0)), worse=int(v.get('worse', 0)), scores=len(q)))
    CT = pd.DataFrame(rows); CT.to_csv(W / 'Table_Nmax_tests.csv', index=False)
    print(CT.to_string(index=False)); print(D[D.result != 'no difference'].to_string(index=False))
    KEYS = [('len_med', 'Median trace length', 'm', 1), ('len_p90', '90th percentile trace length', 'm', 1), ('n100', 'Trace count P20', 'traces per 100 m2', 2),
            ('P21', 'Trace intensity P21', 'm/m2', 3), ('P22', 'Intersections', 'per 100 m2', 2), ('CL', 'Connections per trace', '-', 2),
            ('nn_med', 'Spacing: nearest trace', 'm', 1), ('share1', 'Cluster C1 (~125 deg) share', '%', 0), ('share2', 'Cluster C2 (~56 deg) share', '%', 0),
            ('share3', 'Cluster C3 (~27 deg) share', '%', 0), ('share4', 'Cluster C4 (~89 deg) share', '%', 0),
            ('dir1', 'Cluster C1 direction', 'deg', 0), ('dir2', 'Cluster C2 direction', 'deg', 0), ('sd1', 'Cluster C1 spread', 'deg', 1), ('sd2', 'Cluster C2 spread', 'deg', 1)]
    cols = [('Held-out', 'Held-out'), ('N50', 'N_max 50'), ('N120', 'N_max 120'), ('N200', 'N_max 200')]
    T = pd.DataFrame([dict(Parameter=lab, Unit=u, **{c: round(float(MF.table_value(TR, PR, 'S1', m, k)), dp) for m, c in cols}) for k, lab, u, dp in KEYS])
    T.to_csv(W / 'Table_Nmax.csv', index=False)
    with open(W / 'Table_Nmax.md', 'w', encoding='utf-8') as f:
        f.write('Gap-filling test (20 held-out windows, 24 realisations each). Per-window median over realisations, then median over windows; '
                'median length, 90th percentile and cluster shares/directions/spreads from all pooled traces (each realisation weighted 1/24).\n\n')
        f.write('| ' + ' | '.join(T.columns) + ' |\n|' + '---|' * len(T.columns) + '\n')
        for _, r in T.iterrows(): f.write('| ' + ' | '.join(str(x) for x in r.values) + ' |\n')
    print(T.to_string(index=False))
