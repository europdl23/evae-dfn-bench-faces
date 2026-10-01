# -*- coding: utf-8 -*-
"""Example panels, one rule for Results and Discussion (written before any figure is drawn).

Per test, the EVAE errors of every held-out panel (panel value = median over its 24 realisations, from the release
table tables/stats_box_medians.csv) on four scores: trace-direction W1 (orient_w1_deg), trace-length W1 (len_w1_m),
trace-count error (P20_relerr) and trace-direction-cluster share error (cluster_share_tv). Each score is standardised
within the test (z = (x - mean) / sd over the test's panels).
  typical panel = the panel whose standardised error vector is closest (Euclidean) to the vector of per-score medians;
                  tests are taken in the order gap-filling, new-bench, new-stretch, and a panel already chosen is skipped
                  (the next closest is taken);
  hard panel    = gap-filling test: the panel whose mean standardised error is closest to the 90th percentile of the
                  mean standardised errors of that test (a panel already chosen is skipped).
Realisation shown = run seed 1337, draw 0 for every method (the first realisation, not selected).
Writes paper/example_panels.json and EXAMPLE_PANELS.md."""
import json
import numpy as np, pandas as pd
import pr_common as P

SC = ['orient_w1_deg', 'len_w1_m', 'P20_relerr', 'cluster_share_tv']
B = pd.read_csv(P.RP.TABLES_DIR / 'stats_box_medians.csv', na_values=['n.d.']); B = B[B.method == 'EVAE']
lib = P.C.load_library(); chosen, rows, info = [], [], {}
for s in P.C.SCHEMES:
    q = B[B.scheme == s].set_index('box')[SC].astype(float)
    z = (q - q.mean()) / q.std(ddof=0)
    dist = np.sqrt(((z - z.median()) ** 2).sum(1)).sort_values(kind='stable')
    info[s] = dict(z=z, dist=dist, mean=z.mean(1))
    b = next(k for k in dist.index if k not in [c['panel'] for c in chosen])
    chosen.append(dict(role='typical', test=P.TEST[s], scheme=s, panel=b, fold=P.C.fold_of(s, b, lib), distance_to_median=round(float(dist[b]), 3),
                       mean_z=round(float(z.mean(1)[b]), 3), errors={k: round(float(q.loc[b, k]), 4) for k in SC}))
s = 'S1'; mz = info[s]['mean']; p90 = float(np.percentile(mz, 90))
b = next(k for k in (mz - p90).abs().sort_values(kind='stable').index if k not in [c['panel'] for c in chosen])
q = B[B.scheme == s].set_index('box')[SC]
chosen.append(dict(role='hard', test='gap-filling', scheme=s, panel=b, fold=P.C.fold_of(s, b, lib), mean_z=round(float(mz[b]), 3), p90_mean_z=round(p90, 3),
                   errors={k: round(float(q.loc[b, k]), 4) for k in SC}))
for c, lab in zip(chosen, 'ABCD'):
    c['label'] = lab
    c['realisation'] = dict(run_seed=1337, draw=0, generator_seed={m: P.C.network_seed(m, c['scheme'], c['fold'], c['panel'], 1337, 0) for m in P.C.METHODS})
json.dump(dict(rule=__doc__.split('\n\n', 1)[1].strip(), panels=chosen), open(P.PR / 'example_panels.json', 'w'), indent=1)
med = {s: B[B.scheme == s][SC].median().round(3).to_dict() for s in P.C.SCHEMES}
md = ['# Example panels (one rule for Results and Discussion)', '',
      '**Rule (fixed before drawing).** For each test, every held-out panel gets four EVAE errors, each the median over its 24 realisations:',
      '', '* trace-direction W1;', '* trace-length W1;', '* trace-count error;', '* trace-direction-cluster share error.', '',
      'Each error is standardised within the test.', '',
      '* **Typical panel:** the panel whose standardised errors are closest to the test medians. Tests are taken in the order gap-filling, new-bench, new-stretch; a panel already chosen is skipped.',
      '* **Hard panel:** one gap-filling panel, at the 90th percentile of the mean standardised error.',
      '* **Realisation shown:** run seed 1337, draw 0 for every method (EVAE, ADFNE, KDE). It is the first realisation, not selected.', '',
      '| Label | Role | Test | Panel | Fold | Direction W1 (°) | Length W1 (m) | Count error | Cluster-share error | Generator seeds (EVAE / ADFNE / KDE) |',
      '|---|---|---|---|---|---|---|---|---|---|']
for c in chosen:
    e = c['errors']; g = c['realisation']['generator_seed']
    md.append('| %s | %s | %s | %s | %d | %.2f | %.2f | %.2f | %.3f | %d / %d / %d |' % (c['label'], c['role'], c['test'], c['panel'], c['fold'], e['orient_w1_deg'],
              e['len_w1_m'], e['P20_relerr'], e['cluster_share_tv'], g['EVAE'], g['ADFNE'], g['KDE']))
md += ['', 'Test medians of the four errors (for comparison):', '']
for s in P.C.SCHEMES:
    m = med[s]
    md.append('* %s: direction W1 %.2f°, length W1 %.2f m, count error %.2f, cluster-share error %.3f.' % (P.TEST_T[s], m['orient_w1_deg'], m['len_w1_m'], m['P20_relerr'], m['cluster_share_tv']))
md += ['', 'Code: `paper/code/select_examples.py`; values from `tables/stats_box_medians.csv` of the release.']
(P.PR / 'EXAMPLE_PANELS.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
for c in chosen:
    print(c['label'], c['role'], c['test'], c['panel'], 'fold', c['fold'], c['errors'])
