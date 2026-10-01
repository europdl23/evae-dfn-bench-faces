# -*- coding: utf-8 -*-
"""Check the release.

  1. every file listed in MANIFEST_SHA256.txt is present and unchanged;
  2. the fold splits recompute from the box library (data/splits);
  3. the orientation clusters refit from the fitting boxes to the stored values (data/orientation_clusters);
  4. the networks of Figure 1 regenerate bit for bit from their seeds: EVAE and KDE always, ADFNE when ADFNE 1.5 is
     installed (src/baselines/README.md);
  5. with --full: every EVAE and KDE network (and ADFNE when installed) of all 120 test-box cases is regenerated
     and compared (about 10 minutes for EVAE and KDE on a desktop CPU; ADFNE about 1 hour).

Usage:  python scripts/verify_release.py [--full] [--skip-manifest]"""
import sys, json, hashlib, shutil, os
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'src' / 'study')]
import study as C                      # noqa: E402
import repo_paths as RP                # noqa: E402
import generate_networks as G          # noqa: E402
import fit_orientation_clusters as FOC  # noqa: E402

FULL = '--full' in sys.argv
ok_all = True


def report(name, ok, detail=''):
    global ok_all
    ok_all &= bool(ok)
    print('%-4s %s %s' % ('OK' if ok else 'FAIL', name, detail))


def same(a, b):
    A = C.load_net(a); B = C.load_net(b)
    return A.shape == B.shape and np.array_equal(A, B)


# 1. manifest
if '--skip-manifest' not in sys.argv:
    bad, n = [], 0
    for line in open(RP.REPO_ROOT / 'MANIFEST_SHA256.txt', encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        h, rel = line.rstrip('\n').split('  ', 1); n += 1
        p = RP.REPO_ROOT / rel
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append(rel)
    report('manifest', not bad, '%d files checked%s' % (n, '' if not bad else '; changed or missing: ' + ', '.join(bad[:10])))

# 2. splits
lib = C.load_library(); nf = {s: len(C.folds(s, lib)) for s in C.SCHEMES}
try:
    for s in C.SCHEMES:
        for fi in range(nf[s]):
            C.split(s, fi, lib, check=True)
    report('splits', True, '%d folds recomputed and equal to data/splits' % sum(nf.values()))
except AssertionError as e:
    report('splits', False, str(e))

# 3. orientation clusters
report('orientation clusters', FOC.main(write=False))

# 4. / 5. networks
adfne_ok = (Path(os.environ['ADFNE_ROOT']) / 'ADFNE1.5').exists()
OUT = RP.WORK_DIR / 'verify_networks'
shutil.rmtree(OUT, ignore_errors=True)
sel = json.load(open(RP.SEEDS_DIR / 'figure_networks.json'))
for e in sel['boxes']:
    s, fi, b = e['scheme'], e['fold'], e['box']
    G.evae(s, fi, OUT, boxes=[b], seeds=(sel['run_seed'],), draws=[sel['draw']])
    G.baselines(s, fi, OUT, adfne=adfne_ok, boxes=[b], seeds=(sel['run_seed'],), draws=[sel['draw']])
    for m in (('EVAE', 'ADFNE', 'KDE') if adfne_ok else ('EVAE', 'KDE')):
        f = C.net_path(s, m, fi, b, sel['run_seed'], sel['draw'])
        report('Figure 1 network %s %s %s' % (s, b, m), same(C.net_path(s, m, fi, b, sel['run_seed'], sel['draw'], root=OUT), f),
               'seed %d (%s)' % (e['networks'][m]['generator_seed'], e['networks'][m]['seed_key']))
# ablation arms: the same three boxes, the same run seed and draw, regenerated from the ablation models
import ablation as AB                  # noqa: E402
for e in sel['boxes']:
    s, fi, b = e['scheme'], e['fold'], e['box']; sd, d = sel['run_seed'], sel['draw']
    sp = C.split(s, fi, lib)
    for arm in AB.TRAINED_HERE:
        single = AB.ARMS[arm][1]
        model, dev = AB.load_model(AB.model_dir(arm, s, fi, sd) / 'checkpoint.pt', single)
        post = C.aggregate_posterior(model, dev, sp['panels'], C.context(sp, b))
        L, _ = AB.generate(model, dev, sp['panels'][b]['y_max'], AB.generator_seed(s, fi, b, sd, d), post, d, single)
        p = AB.net_path(arm, s, fi, b, sd, d, root=OUT); C.save_net(p, L)
        report('ablation network %s %s %s' % (s, b, arm), same(p, AB.net_path(arm, s, fi, b, sd, d)), 'seed %d (EVAE seed, shared by all arms)' % AB.generator_seed(s, fi, b, sd, d))
if not adfne_ok:
    print('SKIP ADFNE networks: ADFNE 1.5 not found at %s (see src/baselines/README.md)' % (Path(os.environ['ADFNE_ROOT']) / 'ADFNE1.5'))
if FULL:
    shutil.rmtree(OUT, ignore_errors=True)
    for s in C.SCHEMES:
        for fi in range(nf[s]):
            G.evae(s, fi, OUT); G.baselines(s, fi, OUT, adfne=adfne_ok)
    for m in (('EVAE', 'ADFNE', 'KDE') if adfne_ok else ('EVAE', 'KDE')):
        files = sorted((RP.NETWORKS_DIR).glob('S*/%s/*.csv' % m))
        diff = [f.name for f in files if not same(OUT / f.parent.parent.name / m / f.name, f)]
        report('all %s networks' % m, not diff, '%d regenerated, %d different' % (len(files), len(diff)))
print('\nRELEASE CHECK', 'PASSED' if ok_all else 'FAILED')
sys.exit(0 if ok_all else 1)
