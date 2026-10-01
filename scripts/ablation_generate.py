# -*- coding: utf-8 -*-
"""Generate the held-out test boxes for the ablation arms: 3 run seeds x 8 draws = 24 networks per test box, posterior
sampling around the 8 nearest non-test boxes (as the EVAE). Every arm uses the EVAE's own generator seeds, so the
arms and the EVAE share the same seeds draw for draw.

Usage:  python scripts/ablation_generate.py <arm|all> [--out DIR]
        python scripts/ablation_generate.py check      the ablation generator on the EVAE models must reproduce
                                                      networks/<scheme>/EVAE of fold S1-2 byte for byte
Default output: networks/<scheme>/<arm>/ (the released ablation networks)."""
import sys, csv, argparse
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'study'))
import study as C            # noqa: E402
import repo_paths as RP      # noqa: E402
import ablation as AB        # noqa: E402


def gen_fold(arm, scheme, fi, out=None):
    lib = C.load_library(); sp = C.split(scheme, fi, lib); P = sp['panels']; single = AB.ARMS[arm][1]; n = fb = 0
    for seed in C.SEEDS:
        model, dev = AB.load_model(AB.model_dir(arm, scheme, fi, seed) / 'checkpoint.pt', single)
        for b in sp['test']:
            post = C.aggregate_posterior(model, dev, P, C.context(sp, b))
            for d in range(C.NDRAW):
                L, f = AB.generate(model, dev, P[b]['y_max'], AB.generator_seed(scheme, fi, b, seed, d), post, d, single)
                C.save_net(AB.net_path(arm, scheme, fi, b, seed, d, root=out), L); n += 1; fb += f
    return n, fb


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('arm'); ap.add_argument('--out', default=None); a = ap.parse_args()
    lib = C.load_library()
    if a.arm == 'check':
        out = RP.WORK_DIR / 'ablation_generation_check'
        gen_fold('EVAE', 'S1', 2, out)
        files = sorted((RP.NETWORKS_DIR / 'S1' / 'EVAE').glob('f2_*.csv'))
        diff = [f.name for f in files if not np.array_equal(C.load_net(f), C.load_net(out / 'S1' / 'EVAE' / f.name))]
        print('CHECK ablation generator on the EVAE models, fold S1-2: %d networks, %d different' % (len(files), len(diff)))
        sys.exit(1 if diff or not files else 0)
    arms = AB.TRAINED_HERE if a.arm == 'all' else [a.arm]
    rows = []
    for arm in arms:
        tot = fbt = 0
        for s in C.SCHEMES:
            for fi in range(len(C.folds(s, lib))):
                n, fb = gen_fold(arm, s, fi, a.out); tot += n; fbt += fb
        print('generated', arm, tot, 'networks; top-10 fallback fired', fbt, 'times', flush=True)
    # seed table of the ablation networks (all arms, the EVAE included, share these seeds)
    if a.out is None and a.arm == 'all':
        for s in C.SCHEMES:
            for fi, test in enumerate(C.folds(s, lib)):
                for b in test:
                    for sd in C.SEEDS:
                        for d in range(C.NDRAW):
                            rows.append(dict(scheme=s, fold=fi, box=b, run_seed=sd, draw=d, generator_seed=AB.generator_seed(s, fi, b, sd, d),
                                             seed_key='EVAE|%s|geobg|%d|%s|%d|%d' % (s, fi, b, sd, d),
                                             arms='single_noguide, single_guide, dual_noguide, EVAE',
                                             file_name='f%d_%s_s%d_d%02d.csv' % (fi, b, sd, d)))
        with open(RP.SEEDS_DIR / 'ablation_network_seeds.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        print('seeds/ablation_network_seeds.csv', len(rows), 'rows')
