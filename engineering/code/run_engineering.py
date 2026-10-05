# -*- coding: utf-8 -*-
"""Step 1c: compute the engineering measures (PROTOCOL_ENGINEERING.md) for every held-out panel of the three tests:
held-out, the 8 neighbouring panels (intact = primary reference; fracture-removed = sensitivity), and the 24 saved
realisations of EVAE, ADFNE and KDE. Also the release's 15 parameters for the intact reference (combined table) and,
as a replication check, for held-out and the generators. Writes tables/engineering_*.csv."""
from multiprocessing import Pool
import numpy as np, pandas as pd
import eng_common as E
import eng_metrics as M

C = E.C
VALS = ['n', 'p', 'rho', 'E_along', 'E_down', 'aniso', 'soft_dir_deg', 'span', 'largest_share', 'term_share', 'pX',
        'k_mean_C1', 'k_mean_C2', 'k_max_C1', 'k_max_C2']
# the 10 tested measures: (key, error type)
TESTED = [('E_along', 'abs'), ('E_down', 'abs'), ('aniso', 'abs'), ('p', 'rel'), ('span', 'abs'), ('largest_share', 'abs'),
          ('k_mean_C1', 'abs'), ('k_mean_C2', 'abs'), ('k_max_C1', 'abs'), ('k_max_C2', 'abs')]


def values(L, ym, model, dirs):
    L = np.asarray(L, float).reshape(-1, 4)
    if not len(L):                                     # empty network: undefined for every measure (release n.d. rule)
        return dict({k: np.nan for k in VALS}, n=0)
    return M.measures(L, ym, model, dirs)


def scores(vg, vh):
    out = {}
    for k, kind in TESTED:
        g, h = vg.get(k, np.nan), vh.get(k, np.nan)
        if g != g or h != h or vg['n'] == 0:
            out[k] = np.nan
        elif kind == 'rel':
            out[k] = abs(g - h) / h if h > 0 else np.nan
        else:
            out[k] = abs(g - h)
    return out


def fold_job(job):
    import make_figures as MF
    s, fi = job
    lib = C.load_library(); sp = C.split(s, fi, lib); Pn = sp['panels']; model = C.cluster_model(s, fi)
    dirs = M.cluster_dirs(model)
    vals, scs, props, traces = [], [], [], []
    for b in sp['test']:
        real = Pn[b]; ym = real['y_max']; ctx = C.context(sp, b)
        sets = {'Held-out': [(real['lines'], ym)],
                'Reference': [(lib[k]['lines'], lib[k]['y_max']) for k in ctx],
                'Reference (fracture-removed)': [(Pn[k]['lines'], Pn[k]['y_max']) for k in ctx]}
        for m in E.GEN:
            sets[m] = [(C.load_net(C.net_path(s, m, fi, b, sd, d)), ym) for sd in C.SEEDS for d in range(C.NDRAW)]
        vh = values(real['lines'], ym, model, dirs)
        for m, LL in sets.items():
            for k_, (L, y) in enumerate(LL):
                v = vh if m == 'Held-out' else values(L, y, model, dirs)
                vals.append(dict(scheme=s, fold=fi, box=b, method=m, k=k_, **v))
                if m != 'Held-out':
                    scs.append(dict(scheme=s, fold=fi, box=b, method=m, k=k_, **scores(v, vh)))
                # release parameters (for the combined table) and pooled traces, as make_figures.fold_job
                props.append(dict(scheme=s, fold=fi, box=b, method=m, k=k_, **MF.props(L, y, model)))
                L_ = np.asarray(L, float).reshape(-1, 4)
                if len(L_):
                    _, ln, th = C.common.geom(L_)
                    traces.append(pd.DataFrame(dict(scheme=s, method=m, box=b, length=ln * C.M, theta=np.degrees(th),
                                                    oc=MF.canon(E.SB.classify(th, model), model), weight=1.0 / len(LL))))
    return vals, scs, props, pd.concat(traces, ignore_index=True)


if __name__ == '__main__':
    lib = C.load_library(); jobs = [(s, f) for s in C.SCHEMES for f in range(len(C.folds(s, lib)))]
    with Pool(min(12, len(jobs))) as pool:
        res = pool.map(fold_job, jobs)
    V = pd.DataFrame([r for rr, _, _, _ in res for r in rr]); S = pd.DataFrame([r for _, rr, _, _ in res for r in rr])
    Pp = pd.DataFrame([r for _, _, rr, _ in res for r in rr]); TR = pd.concat([t for _, _, _, t in res], ignore_index=True)
    V.to_csv(E.TAB / 'engineering_network_values.csv', index=False, na_rep='n.d.')
    S.to_csv(E.TAB / 'engineering_network_scores.csv', index=False, na_rep='n.d.')
    Pp.to_csv(E.TAB / 'engineering_network_props.csv', index=False, na_rep='n.d.')
    TR.to_csv(E.TAB / 'engineering_pooled_traces.csv', index=False)
    print('networks:', V.groupby('method').size().to_dict())
    print('empty networks:', V[V.n == 0].groupby('method').size().to_dict())
