# -*- coding: utf-8 -*-
"""Run the whole ablation (docs/ABLATION.md):
  1. checks: the ablation code reproduces the released EVAE checkpoint (S1 fold 2, seed 1337) and the two no-guide
     checkpoints (S1 fold 0, seed 1337) byte for byte;
  2. train the arms that have no released models yet (--train ARM ...; by default single_guide), 5 runs in parallel;
  3. generate all arms (scripts/ablation_generate.py) and build the table (scripts/ablation_table.py).
Usage:  python scripts/ablation_run_all.py [--checks-only] [--skip-checks] [--train ARM ...] [--retrain-all]"""
import sys, json, subprocess, argparse, hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'src' / 'study'))
import study as C            # noqa: E402
import repo_paths as RP      # noqa: E402
import ablation as AB        # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--checks-only', action='store_true'); ap.add_argument('--skip-checks', action='store_true')
ap.add_argument('--train', nargs='*', default=['single_guide']); ap.add_argument('--retrain-all', action='store_true')
a = ap.parse_args()


def run(args):
    r = subprocess.run([sys.executable] + args, cwd=str(RP.REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    last = [l for l in r.stdout.splitlines() if l.startswith('DONE') or 'Error' in l or l.startswith('already')]
    return r.returncode, (last[-1] if last else r.stdout[-500:])


if not a.skip_checks:
    G = RP.WORK_DIR / 'ablation_checks'
    jobs = [('EVAE', 'S1', 2, 1337), ('single_noguide', 'S1', 0, 1337), ('dual_noguide', 'S1', 0, 1337)]
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda j: run(['scripts/ablation_train.py', j[0], j[1], str(j[2]), str(j[3]), '--out', str(G / ('%s_%s_f%d_s%d' % j))]), jobs))
    ok = True
    for j, (rc, msg) in zip(jobs, res):
        st = G / ('%s_%s_f%d_s%d' % j) / 'run_status.json'
        new = json.load(open(st))['checkpoint_sha256'] if st.exists() else None
        ref = json.load(open(AB.model_dir(j[0], j[1], j[2], j[3]) / 'run_status.json'))['checkpoint_sha256']
        same = new == ref; ok &= same
        print('%-4s check %-15s %s fold %d seed %d: %s' % ('OK' if same else 'FAIL', j[0], j[1], j[2], j[3], 'checkpoint identical' if same else msg))
    if not ok:
        sys.exit('checks failed: nothing trained')
    if a.checks_only:
        sys.exit(0)

lib = C.load_library()
arms = AB.TRAINED_HERE if a.retrain_all else a.train
jobs = [(arm, s, fi, sd) for arm in arms for s in C.SCHEMES for fi in range(len(C.folds(s, lib))) for sd in C.SEEDS]
out = (lambda j: str(AB.model_dir(*j))) if not a.retrain_all else (lambda j: str(RP.WORK_DIR / 'ablation_models_retrained' / j[0] / ('%s_f%d_s%d' % j[1:])))
with ThreadPoolExecutor(5) as ex:
    for j, (rc, msg) in zip(jobs, ex.map(lambda j: run(['scripts/ablation_train.py', j[0], j[1], str(j[2]), str(j[3]), '--out', out(j)]), jobs)):
        print('%s %s %s f%d s%d: %s' % ('OK  ' if rc == 0 else 'FAIL', j[0], j[1], j[2], j[3], msg), flush=True)
