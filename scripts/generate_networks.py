# -*- coding: utf-8 -*-
"""Generate the networks of the held-out test boxes of one fold: 3 run seeds x 8 draws = 24 per box and method.

  EVAE   posterior sampling around the 8 nearest non-test boxes (one context box per draw), released checkpoints
  ADFNE  ADFNE 1.5 under GNU Octave, fitted distributions (needs ADFNE, see src/baselines/README.md)
  KDE    kernel-density generator, fitted distributions (SciPy only)

Every network has its own generator seed, crc32 of 'METHOD|scheme|variant|fold|box|run seed|draw'
(seeds/network_seeds.csv). The same run seeds and draws are used for all three methods.

Usage:  python scripts/generate_networks.py evae      <S1|S2|S3> <fold> [--out DIR] [--models DIR]
        python scripts/generate_networks.py baselines <S1|S2|S3> <fold> [--out DIR] [--no-adfne]
Output goes to work/networks_regenerated/ unless --out is given, so the released networks/ are never overwritten."""
import sys, json, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'study'))
import study as C            # noqa: E402
import repo_paths as RP      # noqa: E402

DEFAULT_OUT = RP.WORK_DIR / 'networks_regenerated'


def evae(scheme, fi, out=DEFAULT_OUT, models=RP.MODELS_DIR, boxes=None, seeds=C.SEEDS, draws=range(C.NDRAW)):
    lib = C.load_library(); sp = C.split(scheme, fi, lib); P = sp['panels']; n = 0
    for seed in seeds:
        model, dev = C.generators.load_evae(str(Path(models) / ('%s_f%d_s%d' % (scheme, fi, seed)) / 'checkpoint.pt'))
        for b in (boxes or sp['test']):
            post = C.aggregate_posterior(model, dev, P, C.context(sp, b))
            for d in draws:
                L = C.generate(model, dev, P[b]['y_max'], C.network_seed('EVAE', scheme, fi, b, seed, d), post, d)
                C.save_net(C.net_path(scheme, 'EVAE', fi, b, seed, d, root=out), L); n += 1
    return n


def baselines(scheme, fi, out=DEFAULT_OUT, adfne=True, boxes=None, seeds=C.SEEDS, draws=range(C.NDRAW)):
    """ADFNE and KDE with the standard fitted distributions: 2-set orientation fit, fitted lengths, mean count,
    from the fitting boxes of this fold only (never a test box)."""
    lib = C.load_library(); sp = C.split(scheme, fi, lib); P = sp['panels']; n = 0
    stats = C.generators.fit_baseline_stats([P[k] for k in sp['fit']], C.family_rule(sp))
    for b in (boxes or sp['test']):
        if adfne:
            jobs = [(C.network_seed('ADFNE', scheme, fi, b, seed, d), 's%d_d%02d' % (seed, d)) for seed in seeds for d in draws]
            res = C.adfne_batch(stats, P[b]['y_max'], jobs, '%s_f%d_%s' % (scheme, fi, b))
        for seed in seeds:
            for d in draws:
                if adfne:
                    C.save_net(C.net_path(scheme, 'ADFNE', fi, b, seed, d, root=out), res['s%d_d%02d' % (seed, d)]); n += 1
                L = C.generators.generate_kde(stats, P[b]['y_max'], C.network_seed('KDE', scheme, fi, b, seed, d))
                C.save_net(C.net_path(scheme, 'KDE', fi, b, seed, d, root=out), L); n += 1
    return n


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('evae', 'baselines')); ap.add_argument('scheme', choices=C.SCHEMES); ap.add_argument('fold', type=int)
    ap.add_argument('--out', default=str(DEFAULT_OUT)); ap.add_argument('--models', default=str(RP.MODELS_DIR)); ap.add_argument('--no-adfne', action='store_true')
    a = ap.parse_args()
    n = evae(a.scheme, a.fold, a.out, a.models) if a.what == 'evae' else baselines(a.scheme, a.fold, a.out, adfne=not a.no_adfne)
    print('generated', a.what, a.scheme, 'fold', a.fold, 'networks', n, '->', a.out)
