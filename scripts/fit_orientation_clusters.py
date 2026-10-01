# -*- coding: utf-8 -*-
"""Learn the orientation clusters of every fold from its fitting boxes only (held-out fractures removed).

Model (src/study/setbg.py): a mixture of K axial von Mises clusters on 2-theta plus one uniform component for the
traces outside every cluster ('unclustered'), fitted by EM (seed 20261001, 10 restarts); K in 1..4 chosen by BIC.
A cluster is a tight group: concentration >= 8 on 2-theta (about +-20 deg on the face). The clusters are then listed
in a fixed direction order (about 125, 56, 27, 89 deg) so that cluster 1..4 means the same direction in every fold.

Usage:  python scripts/fit_orientation_clusters.py            fit and compare with data/orientation_clusters/
        python scripts/fit_orientation_clusters.py --write    also overwrite data/orientation_clusters/"""
import sys, json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'study'))
import study as C            # noqa: E402
import setbg as SB           # noqa: E402
import repo_paths as RP      # noqa: E402

REF = [125.0, 56.0, 27.0, 89.0]


def to_reference_order(m):
    from scipy.optimize import linear_sum_assignment
    c = np.asarray(m['centres_deg']); d = np.abs((c[:, None] - np.asarray(REF)[None] + 90) % 180 - 90)
    r, k = linear_sum_assignment(d); o = [int(r[list(k).index(j)]) for j in sorted(k)]
    for key in ('mu2', 'kappa2', 'w_sets', 'centres_deg'):
        m[key] = [m[key][i] for i in o]
    return m


def main(write=False):
    lib = C.load_library(); worst = 0.0
    for s in C.SCHEMES:
        for fi in range(len(C.folds(s, lib))):
            sp = C.split(s, fi, lib)
            th = np.concatenate([C.common.geom(sp['panels'][k]['lines'])[2] for k in sp['fit'] if len(sp['panels'][k]['lines'])])
            m = to_reference_order(SB.fit(th))
            ref = json.load(open(RP.CLUSTERS_DIR / ('%s_f%d.json' % (s, fi))))
            dev = max(abs(a - b) for key in ('mu2', 'kappa2', 'w_sets', 'centres_deg') for a, b in zip(m[key], ref[key])) if m['K'] == ref['K'] else np.inf
            dev = max(dev, abs(m['w_bg'] - ref['w_bg'])); worst = max(worst, dev)
            print('%s fold %d: K=%d, centres %s deg, weights %s, unclustered %.2f | max difference to stored %.1e'
                  % (s, fi, m['K'], [round(x) for x in m['centres_deg']], [round(x, 2) for x in m['w_sets']], m['w_bg'], dev))
            if write:
                SB.save(m, RP.CLUSTERS_DIR / ('%s_f%d.json' % (s, fi)))
    print('CHECK orientation clusters', 'identical to stored (max difference %.1e)' % worst if worst < 1e-6 else 'DIFFERENT (max %.3g)' % worst)
    return worst < 1e-6


if __name__ == '__main__':
    sys.exit(0 if main(write='--write' in sys.argv) else 1)
