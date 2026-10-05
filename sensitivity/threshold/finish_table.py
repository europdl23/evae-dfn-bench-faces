# Append traces per realisation, slots passing, fallback use and test counts to Table_threshold.csv/.md.
import pandas as pd
from pathlib import Path
W = Path(__file__).resolve().parent; T = pd.read_csv(W / 'Table_threshold.csv'); PR = pd.read_csv(W / 'outputs/properties_per_window.csv')
S = {t: pd.read_csv(W / ('outputs/slots_%s.csv' % t)) for t in ('T04', 'T05', 'T06')}
c = list(T.columns)
import os, sys, numpy as np
os.environ['S1_WORK_DIR'] = str(W / 'work'); sys.path.insert(0, str(W / 'code/src/study')); import study as C
lib = C.load_library(); hn = np.mean([len(C.split('S1', f, lib)['panels'][b]['lines']) for f in range(4) for b in C.split('S1', f, lib)['test']])
T.loc[len(T)] = ['Traces per realisation (mean; held-out = traces per window)', '-', round(float(hn), 2)] + [round(S[t].traces.mean(), 2) for t in S]
T.loc[len(T)] = ['Slots passing threshold (mean)', '-', float('nan')] + [round(S[t].slots_passing.mean(), 2) for t in S]
T.loc[len(T)] = ['Realisations using fallback (of 480)', '-', float('nan')] + [int(S[t].fallback.sum()) for t in S]
K = pd.read_csv(W / 'Table_threshold_tests.csv'); K = K[K.group == 'All']
T.loc[len(T)] = ['38 scores vs 0.5: better / n.s. / worse', '-', ''] + ['%d / %d / %d' % tuple(K[K.comparison.str.startswith('threshold 0.4')][['better', 'no_difference', 'worse']].values[0]), 'reference', '%d / %d / %d' % tuple(K[K.comparison.str.startswith('threshold 0.6')][['better', 'no_difference', 'worse']].values[0])]
T.to_csv(W / 'Table_threshold.csv', index=False)
with open(W / 'Table_threshold.md', 'w', encoding='utf-8') as f:
    f.write('Gap-filling test (S1), released EVAE checkpoints, 20 held-out windows x 24 realisations; only the existence threshold changes '
            '(fallback: top 10 logits if fewer than 2 slots pass, unchanged). Per-window median over realisations, then median over windows; '
            'median length, 90th percentile and cluster shares/directions/spreads from pooled traces. Tests: paired two-sided Wilcoxon over 20 windows, Holm over 2 comparisons. n.a. = not applicable.\n\n')
    f.write('| ' + ' | '.join(T.columns) + ' |\n|' + '---|' * len(T.columns) + '\n')
    for _, r in T.iterrows(): f.write('| ' + ' | '.join('n.a.' if (isinstance(x, float) and x != x) or x == '' else str(x) for x in r.values) + ' |\n')
print(T.to_string(index=False))
