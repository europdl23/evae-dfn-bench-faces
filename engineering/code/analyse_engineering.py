# -*- coding: utf-8 -*-
"""Steps 1c-2: tests of the engineering measures (PROTOCOL_ENGINEERING.md) and the combined parameter table.
Reads tables/engineering_network_*.csv (run_engineering.py); release tables read only."""
import math
import numpy as np, pandas as pd
from scipy.stats import wilcoxon, rankdata, spearmanr
import eng_common as E
import statistical_tests as ST
import make_figures as MF
from run_engineering import TESTED

C = E.C; T = E.TAB
GEN = list(E.GEN); REFS = ['Reference', 'Reference (fracture-removed)']
NAME = {'E_along': 'Equivalent modulus along the bench, E/E0', 'E_down': 'Equivalent modulus down the face, E/E0',
        'aniso': 'Deformability anisotropy index', 'p': 'Percolation parameter p', 'span': 'Spanning cluster (share)',
        'largest_share': 'Largest connected cluster (share of trace length)', 'k_mean_C1': 'Mean persistence, cluster C1',
        'k_mean_C2': 'Mean persistence, cluster C2', 'k_max_C1': 'Maximum persistence, cluster C1', 'k_max_C2': 'Maximum persistence, cluster C2'}
GROUP = {'E_along': 'Deformability', 'E_down': 'Deformability', 'aniso': 'Deformability', 'p': 'Connectivity', 'span': 'Connectivity',
         'largest_share': 'Connectivity', 'k_mean_C1': 'Persistence', 'k_mean_C2': 'Persistence', 'k_max_C1': 'Persistence', 'k_max_C2': 'Persistence'}
KEYS = [k for k, _ in TESTED]


def read(name):
    return pd.read_csv(T / name, na_values=['n.d.'])


def wil(d):
    d = np.asarray(d, float)
    if len(d) < 3 or np.allclose(d, 0):
        return 1.0, 0.0, 0.0
    p = float(wilcoxon(d, zero_method='zsplit').pvalue)
    r = rankdata(np.abs(d)); return p, r[d > 0].sum() + r[d == 0].sum() / 2, r[d < 0].sum() + r[d == 0].sum() / 2


def panel_agg(D, keys):
    """panel value = median over networks where defined; the binary spanning measure = mean"""
    g = D.groupby(['scheme', 'fold', 'box', 'method'])
    out = g[[k for k in keys if k != 'span']].median()
    if 'span' in keys:
        out['span'] = g['span'].mean()
    return out.reset_index()


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); q = np.empty(n); run = 1.0
    for i in range(n - 1, -1, -1):
        run = min(run, p[o[i]] * n / (i + 1)); q[o[i]] = run
    return q


def main():
    V, S, PR = read('engineering_network_values.csv'), read('engineering_network_scores.csv'), read('engineering_network_props.csv')
    TR = pd.read_csv(T / 'engineering_pooled_traces.csv')

    # ---------------- replication check: the release's 15 parameters for held-out and the generators
    TD = pd.read_csv(E.REL / 'paper' / 'tables' / 'Table_D_parameters.csv')
    PRp = PR.groupby(['scheme', 'fold', 'box', 'method']).median(numeric_only=True).reset_index()
    keymap = dict(zip([t[1] for t in MF.TABP], [t[0] for t in MF.TABP]))
    rows_label = {'Trace count (P20)': 'n100', 'Median trace length': 'len_med', 'Long traces: 90th percentile length': 'len_p90',
                  'Trace intensity (P21)': 'P21', 'Intersections': 'P22', 'Connections per trace': 'CL', 'Spacing: nearest trace': 'nn_med',
                  'Orientation cluster 1 (~125°): share': 'share1', 'Orientation cluster 2 (~56°): share': 'share2',
                  'Orientation cluster 3 (~27°): share': 'share3', 'Orientation cluster 4 (~89°): share': 'share4',
                  'Orientation cluster 1: direction': 'dir1', 'Orientation cluster 2: direction': 'dir2',
                  'Orientation cluster 1: spread': 'sd1', 'Orientation cluster 2: spread': 'sd2'}
    bad = 0
    for _, r in TD.iterrows():
        key = rows_label[r.Parameter]; fmt = dict((t[0], t[2]) for t in MF.TABP)[key]
        for s in C.SCHEMES:
            for m, col in (('Held-out', 'held-out'), ('EVAE', 'EVAE'), ('ADFNE', 'ADFNE'), ('KDE', 'KDE')):
                mine = MF.table_value(TR, PRp, s, m, key); rec = float(r['%s test: %s' % (E.TEST[s], col)])
                if abs(float(fmt % mine) - rec) > 1e-9:
                    bad += 1; print('REPLICATION MISMATCH', r.Parameter, s, m, fmt % mine, rec)
    print('replication of Table_D_parameters: %s' % ('all %d values match' % (len(TD) * 12) if not bad else '%d mismatches' % bad))

    # ---------------- panel values and panel scores
    PV = panel_agg(V, ['n', 'p', 'rho', 'E_along', 'E_down', 'aniso', 'span', 'largest_share', 'term_share', 'pX',
                       'k_mean_C1', 'k_mean_C2', 'k_max_C1', 'k_max_C2'])
    sd_ = V.groupby(['scheme', 'fold', 'box', 'method'])['soft_dir_deg'].apply(lambda a: MF.axial_mean_deg(a.dropna().values) if a.notna().any() else np.nan)
    PV = PV.merge(sd_.reset_index(), on=['scheme', 'fold', 'box', 'method'])
    PV = PV.merge(PRp[['scheme', 'fold', 'box', 'method', 'P21', 'P22']], on=['scheme', 'fold', 'box', 'method'], how='left')
    PV.to_csv(T / 'engineering_panel_values.csv', index=False, na_rep='n.d.')
    PS = panel_agg(S, KEYS); PS.to_csv(T / 'engineering_panel_scores.csv', index=False, na_rep='n.d.')

    # ---------------- tests
    dec, ver, ref, bs = [], [], [], []
    rng = np.random.default_rng(20261001)
    for k in KEYS:
        tw = {}
        for s in C.SCHEMES:
            piv = PS[PS.scheme == s].pivot_table(index='box', columns='method', values=k)
            for o, r in ST.paired(piv, 'EVAE', ('ADFNE', 'KDE')).items():
                x = piv[['EVAE', o]].dropna(); d = (x['EVAE'] - x[o]).values
                p_raw = 1.0 if len(d) < 3 or np.allclose(d, 0) else float(wilcoxon(d, zero_method='zsplit').pvalue)
                dec.append(dict(test=E.TEST[s], scheme=s, group=GROUP[k], measure=k, name=NAME[k], against=o, n_panels=r['n_boxes'],
                                median_EVAE=float(x['EVAE'].median()), median_baseline=float(x[o].median()), median_diff=r['median_diff'],
                                p_raw=p_raw, p_holm=r['p_holm'], result=r['result']))
                if len(d) >= 3:
                    idx = rng.integers(0, len(d), size=(2000, len(d))); med = np.median(d[idx], axis=1); lo, hi = np.percentile(med, [2.5, 97.5])
                    bs.append(dict(test=E.TEST[s], measure=k, against=o, median_diff=float(np.median(d)), ci_low=float(lo), ci_high=float(hi),
                                   ci=('EVAE better' if hi < 0 else ('EVAE worse' if lo > 0 else 'includes 0'))))
            tw[s] = ST.three_way(piv, GEN)
            for rf in REFS:
                q = piv[['EVAE', rf]].dropna(); d = (q['EVAE'] - q[rf]).values; p, wp, wm = wil(d); md = float(np.median(d)) if len(d) else np.nan
                ref.append(dict(test=E.TEST[s], measure=k, name=NAME[k], reference=rf, n_panels=len(q), median_EVAE=float(q['EVAE'].median()),
                                median_reference=float(q[rf].median()), median_diff=md, p=p,
                                result='no difference' if p >= 0.05 else ('better' if md < 0 else 'worse')))
        cw = {m: sum(1 for s in C.SCHEMES if tw[s] and tw[s]['winner'] == m and tw[s]['clear']) for m in GEN}
        ver.append(dict(measure=k, name=NAME[k], **{'%s winner' % E.TEST[s]: ('%s (%s)' % (tw[s]['winner'], 'clear' if tw[s]['clear'] else 'tie')) if tw[s] else 'n/a'
                                                    for s in C.SCHEMES}, verdict=next((m for m in cw if cw[m] >= 2), 'no method')))
    D = pd.DataFrame(dec); D['q_bh'] = bh(D.p_raw.values)
    D['result_bh'] = np.where(D.q_bh >= 0.05, 'no difference', np.where(D.median_diff < 0, 'better', 'worse'))
    D.to_csv(T / 'engineering_tests.csv', index=False)
    pd.DataFrame(ver).to_csv(T / 'engineering_verdict.csv', index=False)
    RF = pd.DataFrame(ref); RF.to_csv(T / 'engineering_reference.csv', index=False)
    BS = pd.DataFrame(bs); BS.to_csv(T / 'engineering_bootstrap.csv', index=False)
    cnt = []
    for ag in ('ADFNE', 'KDE'):
        for grp in ['Deformability', 'Connectivity', 'Persistence', 'All']:
            q = D[D.against == ag]; q = q if grp == 'All' else q[q.group == grp]
            for col, lab in (('result', 'Holm'), ('result_bh', 'BH')):
                v = q[col].value_counts()
                cnt.append(dict(against=ag, group=grp, correction=lab, better=int(v.get('better', 0)), no_difference=int(v.get('no difference', 0)), worse=int(v.get('worse', 0))))
        v = BS[BS.against == ag].ci.value_counts()
        cnt.append(dict(against=ag, group='All', correction='bootstrap CI', better=int(v.get('EVAE better', 0)), no_difference=int(v.get('includes 0', 0)), worse=int(v.get('EVAE worse', 0))))
    for rf in REFS:
        v = RF[RF.reference == rf].result.value_counts()
        cnt.append(dict(against=rf, group='All', correction='none (alpha 0.05)', better=int(v.get('better', 0)), no_difference=int(v.get('no difference', 0)), worse=int(v.get('worse', 0))))
    CN = pd.DataFrame(cnt); CN.to_csv(T / 'engineering_counts.csv', index=False)

    # ---------------- what is and is not a restatement of P21 (held-out panels, all 120 panel cases)
    H = PV[PV.method == 'Held-out']; sp = []
    for k in ['p', 'rho', 'E_along', 'E_down', 'aniso', 'span', 'largest_share', 'k_mean_C1', 'k_mean_C2', 'k_max_C1', 'k_max_C2']:
        x = H[['P21', k]].dropna(); r, pv = spearmanr(x.P21, x[k]); sp.append(dict(measure=k, name=NAME.get(k, 'Crack density rho'), spearman_with_P21=r, p=pv, n=len(x)))
    pd.DataFrame(sp).to_csv(T / 'engineering_spearman_P21.csv', index=False)

    # ---------------- combined parameter table
    combined(PV, PRp, TR, D)
    pd.set_option('display.width', 250)
    print(D.pivot_table(index='name', columns=['test', 'against'], values='result', aggfunc='first').to_string())
    print(pd.DataFrame(ver).to_string(index=False)); print(CN.to_string(index=False))


# ---------------------------------------------------------------- combined table
ROWS = [  # (group, key, label, unit, format, source)
    ('Trace direction', 'share1', 'Cluster C1 (~125°): share', '%', '%.0f', 'rel'), ('Trace direction', 'share2', 'Cluster C2 (~56°): share', '%', '%.0f', 'rel'),
    ('Trace direction', 'share3', 'Cluster C3 (~27°): share', '%', '%.0f', 'rel'), ('Trace direction', 'share4', 'Cluster C4 (~89°): share', '%', '%.0f', 'rel'),
    ('Trace direction', 'dir1', 'Cluster C1: direction', '°', '%.0f', 'rel'), ('Trace direction', 'dir2', 'Cluster C2: direction', '°', '%.0f', 'rel'),
    ('Trace direction', 'sd1', 'Cluster C1: spread', '°', '%.1f', 'rel'), ('Trace direction', 'sd2', 'Cluster C2: spread', '°', '%.1f', 'rel'),
    ('Length', 'len_med', 'Median trace length', 'm', '%.1f', 'rel'), ('Length', 'len_p90', '90th-percentile trace length', 'm', '%.1f', 'rel'),
    ('Intensity and spacing', 'n100', 'Trace density (P20)', 'per 100 m²', '%.2f', 'rel'), ('Intensity and spacing', 'P21', 'Trace intensity (P21)', 'm/m²', '%.3f', 'rel'),
    ('Intensity and spacing', 'nn_med', 'Spacing to the nearest trace', 'm', '%.1f', 'rel'),
    ('Connectivity and termination', 'P22', 'Intersections', 'per 100 m²', '%.2f', 'rel'), ('Connectivity and termination', 'CL', 'Connections per trace', '-', '%.2f', 'rel'),
    ('Connectivity and termination', 'term_share', 'T-end share (ends stopping on another trace)', '-', '%.2f', 'new'),
    ('Connectivity and termination', 'pX', 'Crossing share of nodes', '-', '%.2f', 'new'),
    ('Connectivity and termination', 'p', 'Percolation parameter p (threshold about 5.6)', '-', '%.2f', 'new'),
    ('Connectivity and termination', 'span', 'Panels with a spanning cluster', 'share', '%.2f', 'new'),
    ('Connectivity and termination', 'largest_share', 'Largest connected cluster', 'share of length', '%.2f', 'new'),
    ('Engineering inputs', 'E_along', 'Equivalent modulus along the bench, E/E0', '-', '%.2f', 'new'),
    ('Engineering inputs', 'E_down', 'Equivalent modulus down the face, E/E0', '-', '%.2f', 'new'),
    ('Engineering inputs', 'aniso', 'Deformability anisotropy index', '-', '%.2f', 'new'),
    ('Engineering inputs', 'soft_dir_deg', 'Softest loading direction (from the bench axis)', '°', '%.0f', 'new'),
    ('Engineering inputs', 'k_mean_C1', 'Mean persistence, C1', '-', '%.3f', 'new'), ('Engineering inputs', 'k_mean_C2', 'Mean persistence, C2', '-', '%.3f', 'new'),
    ('Engineering inputs', 'k_max_C1', 'Maximum persistence, C1', '-', '%.2f', 'new'), ('Engineering inputs', 'k_max_C2', 'Maximum persistence, C2', '-', '%.2f', 'new')]
# release error score behind each release row (recount_EVAE_vs_baselines.csv, n.d. rule) and our tests for the new rows
SCORE = {'share1': 'oc1_share_err', 'share2': 'oc2_share_err', 'share3': 'oc3_share_err', 'share4': 'oc4_share_err', 'dir1': 'oc1_centre_err_deg',
         'dir2': 'oc2_centre_err_deg', 'sd1': 'oc1_spread_err_deg', 'sd2': 'oc2_spread_err_deg', 'len_med': 'len_med_err_m', 'len_p90': 'len_p90_err_m',
         'n100': 'P20_relerr', 'P21': 'P21_relerr', 'nn_med': 'nn_w1_m', 'P22': 'P22_relerr', 'CL': 'CL_err', 'term_share': 'term_share_err', 'pX': 'node_tv'}
METH = ['Held-out', 'Reference', 'EVAE', 'ADFNE', 'KDE']
SYM = {'better': '+', 'no difference': '=', 'worse': '−'}


def test_value(PV, PRp, TR, s, m, key):
    """test-level value: release rows as make_figures.table_value; new rows = median over panels (spanning: mean)"""
    if key in dict((t[0], 1) for t in MF.TABP):
        return MF.table_value(TR, PRp, s, m, key)
    a = PV[PV.method == m] if s is None else PV[(PV.scheme == s) & (PV.method == m)]
    if key == 'soft_dir_deg':                          # axial mean, shown in (-90, 90] from the along-bench axis
        return (MF.axial_mean_deg(a[key].dropna().values) + 90) % 180 - 90
    return a[key].mean() if key == 'span' else a[key].median()


def combined(PV, PRp, TR, D):
    RC = pd.read_csv(E.REL / 'paper' / 'tables' / 'recount_EVAE_vs_baselines.csv')
    TRall = TR.assign(scheme='ALL'); PRall = PRp.assign(scheme='ALL'); PVall = PV.assign(scheme='ALL')
    out_rows, md_rows, pooled_rows = [], [], []
    for grp, key, lab, unit, fmt, src in ROWS:
        r = dict(Group=grp, Parameter=lab, Unit=unit); mdr = [grp, lab, unit]
        for s in C.SCHEMES:
            vals = {m: test_value(PV, PRp, TR, s, m, key) for m in METH}
            fv = {m: float(fmt % vals[m]) for m in METH if vals[m] == vals[m]}      # compare the printed values
            gens = {m: fv[m] for m in GEN if m in fv}
            if key in ('dir1', 'dir2', 'soft_dir_deg'):
                dist = {m: abs((v - fv['Held-out'] + 90) % 180 - 90) for m, v in gens.items()}
            else:
                dist = {m: abs(v - fv['Held-out']) for m, v in gens.items()}
            best = min(dist.values()) if dist else None
            close = [m for m in dist if abs(dist[m] - best) < 1e-9]
            for m in METH:
                r['%s: %s' % (E.TEST[s], m)] = float(fmt % vals[m]) if vals[m] == vals[m] else np.nan
            vr = test_value(PV, PRp, TR, s, 'Reference (fracture-removed)', key)
            r['%s: Reference (fracture-removed)' % E.TEST[s]] = float(fmt % vr) if vr == vr else np.nan
            r['%s: closest' % E.TEST[s]] = ', '.join(close)
            # significance: EVAE vs ADFNE / KDE
            res = []
            for o in ('ADFNE', 'KDE'):
                if key in SCORE:
                    q = RC[(RC.scheme == s) & (RC.score == SCORE[key]) & (RC.second == o)]
                    res.append(SYM.get(q.result.iloc[0], '?') if len(q) else 'n/a')
                elif key in KEYS:
                    q = D[(D.scheme == s) & (D.measure == key) & (D.against == o)]; res.append(SYM[q.result.iloc[0]])
                else:
                    res.append('')
            r['%s: EVAE vs ADFNE/KDE' % E.TEST[s]] = '/'.join(res) if any(res) else ''
            cells = []
            for m in METH:
                txt = (fmt % vals[m]) if vals[m] == vals[m] else 'n.d.'
                cells.append('**%s**' % txt if m in close else txt)
            mdr += cells + [r['%s: EVAE vs ADFNE/KDE' % E.TEST[s]]]
        out_rows.append(r); md_rows.append(mdr)
        # pooled over the 120 panel cases (one set of columns) with the test-by-test significance summary
        pv = {m: test_value(PVall, PRall, TRall, 'ALL', m, key) for m in METH}
        fp = {m: float(fmt % pv[m]) for m in METH if pv[m] == pv[m]}
        gens = {m: fp[m] for m in GEN if m in fp}
        dist = {m: (abs((v - fp['Held-out'] + 90) % 180 - 90) if key in ('dir1', 'dir2', 'soft_dir_deg') else abs(v - fp['Held-out'])) for m, v in gens.items()}
        bst = min(dist.values()) if dist else None
        cl = ', '.join(m for m in dist if abs(dist[m] - bst) < 1e-9)
        sig = r['gap-filling: EVAE vs ADFNE/KDE'], r['new-bench: EVAE vs ADFNE/KDE'], r['new-stretch: EVAE vs ADFNE/KDE']
        vr = test_value(PVall, PRall, TRall, 'ALL', 'Reference (fracture-removed)', key)
        pooled_rows.append(dict(Group=grp, Parameter=lab, Unit=unit, **{m: float(fmt % pv[m]) if pv[m] == pv[m] else np.nan for m in METH},
                                **{'Reference (fracture-removed)': float(fmt % vr) if vr == vr else np.nan},
                                closest=cl, **{'EVAE vs ADFNE/KDE, %s' % E.TEST[s]: x for s, x in zip(C.SCHEMES, sig)}))
    TB = pd.DataFrame(out_rows); TB.to_csv(T / 'Table_parameters_combined.csv', index=False)
    TP = pd.DataFrame(pooled_rows); TP.to_csv(T / 'Table_parameters_combined_pooled.csv', index=False)
    # markdown versions
    head = ['Group', 'Parameter', 'Unit']
    for s in C.SCHEMES:
        head += ['%s: %s' % (E.TEST[s], m) for m in METH] + ['%s: EVAE vs ADFNE/KDE' % E.TEST[s]]
    L = ['# Combined parameter table (held-out | natural-variability reference | EVAE | ADFNE | KDE)', '',
         'Values: median over the held-out panels of the test (per panel, a generator value is the median of its 24 realisations; the reference value is the median of the 8 INTACT neighbouring panels). Rows taken from the release (trace direction, length, intensity, spacing, intersections, connections) are computed exactly as `paper/tables/Table_D_parameters.csv` (replicated value for value). **Bold** = the generator value closest to the held-out value (ties bolded). Significance (EVAE vs ADFNE / vs KDE): + EVAE closer, = no significant difference, − EVAE further (paired Wilcoxon over panels, Holm over the two baselines, alpha 0.05; release rows from the release error score of that parameter, `recount_EVAE_vs_baselines.csv`, n.d. rule; new rows from `engineering_tests.csv`). The spacing row uses the spacing-distribution score; the crossing-share row uses the node-type score.', '',
         '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    L += ['| ' + ' | '.join(map(str, r)) + ' |' for r in md_rows]
    L += ['', '## Pooled over the 120 panel cases (compact version for the main text)', '',
          '| Group | Parameter | Unit | Held-out | Reference | EVAE | ADFNE | KDE | EVAE vs ADFNE/KDE: gap-filling, new-bench, new-stretch |', '|---|---|---|---|---|---|---|---|---|']
    FMT = {lab: fmt for _, _, lab, _, fmt, _ in ROWS}
    for _, r in TP.iterrows():
        cells = []
        for m in METH:
            txt = (FMT[r.Parameter] % r[m]) if r[m] == r[m] else 'n.d.'
            cells.append('**%s**' % txt if m in str(r.closest).split(', ') else txt)
        sig = '; '.join(x for x in (r['EVAE vs ADFNE/KDE, gap-filling'], r['EVAE vs ADFNE/KDE, new-bench'], r['EVAE vs ADFNE/KDE, new-stretch']) if x)
        L.append('| %s | %s | %s | %s | %s |' % (r.Group, r.Parameter, r.Unit, ' | '.join(cells), sig))
    (T / 'Table_parameters_combined.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    try:
        with pd.ExcelWriter(T / 'Table_parameters_combined.xlsx') as xw:
            TP.to_excel(xw, sheet_name='Pooled (main text)', index=False); TB.to_excel(xw, sheet_name='By test (supplement)', index=False)
    except Exception as e:
        print('xlsx not written:', e)


if __name__ == '__main__':
    main()
