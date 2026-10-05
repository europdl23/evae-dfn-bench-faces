# Build Table_weights.csv/.md: one row per variant (weights, counts vs the paper model, key parameters), plus held-out and paper rows.
import sys, os
from pathlib import Path
import pandas as pd
W = Path(__file__).resolve().parent
sys.path[:0] = [str(W / 'code' / 'scripts'), str(W / 'code' / 'src' / 'study')]
os.environ['S1_WORK_DIR'] = str(W / 'work')
WTS = {'Held-out': None, 'Paper': (0.005, 1.0, 1.0, 0.3, 0.2, 1.0),
       'A_half': (0.0025, 1.0, 1.0, 0.3, 0.2, 1.0), 'A_double': (0.01, 1.0, 1.0, 0.3, 0.2, 1.0),
       'B_half': (0.005, 0.5, 0.5, 0.3, 0.2, 1.0), 'B_double': (0.005, 2.0, 2.0, 0.3, 0.2, 1.0),
       'C_half': (0.005, 1.0, 1.0, 0.15, 0.1, 1.0), 'C_double': (0.005, 1.0, 1.0, 0.6, 0.4, 1.0),
       'D_half': (0.005, 1.0, 1.0, 0.3, 0.2, 0.5), 'D_double': (0.005, 1.0, 1.0, 0.3, 0.2, 2.0)}
WN = ['w_geology', 'w_direction', 'w_cluster_share', 'w_intersection', 'w_spacing', 'w_loglength']
KEYS = [('len_med', 'median_length_m', 1), ('len_p90', 'p90_length_m', 1), ('n100', 'P20_per100m2', 2), ('P21', 'P21_m_per_m2', 3),
        ('P22', 'intersections_per100m2', 2), ('CL', 'connections_per_trace', 2), ('nn_med', 'spacing_m', 1), ('share1', 'C1_share_pct', 0), ('share2', 'C2_share_pct', 0)]


def main():
    import make_figures as MF
    PR = pd.read_pickle(W / 'outputs' / 'PR.pkl'); TR = pd.read_pickle(W / 'outputs' / 'TR.pkl')
    CT = pd.read_csv(W / 'Table_weights_tests.csv'); CT = CT[CT.group == 'All'].set_index('variant')
    rows = []
    for m, w in WTS.items():
        r = dict(row={'Held-out': 'Held-out windows', 'Paper': 'Paper model (release)'}.get(m, m))
        r.update({n: ('' if w is None else x) for n, x in zip(WN, w or [None] * 6)})
        if m in CT.index:
            r.update(better=int(CT.loc[m, 'better']), no_difference=int(CT.loc[m, 'no_difference']), worse=int(CT.loc[m, 'worse']))
        else:
            r.update(better='', no_difference='', worse='')
        for k, lab, dp in KEYS:
            r[lab] = round(float(MF.table_value(TR, PR, 'S1', m, k)), dp)
        rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(W / 'Table_weights.csv', index=False)
    with open(W / 'Table_weights.md', 'w', encoding='utf-8') as f:
        f.write('Gap-filling test (S1), 20 held-out windows x 24 realisations. Counts = 38 error scores vs the paper model '
                '(paired two-sided Wilcoxon over windows, Holm over 8 variants, n.d. rule). Parameters as the paper\'s Table D.\n\n')
        f.write('| ' + ' | '.join(T.columns) + ' |\n|' + '---|' * len(T.columns) + '\n')
        for _, r in T.iterrows(): f.write('| ' + ' | '.join(str(x) for x in r.values) + ' |\n')
    print(T.to_string(index=False))


if __name__ == '__main__':
    main()
