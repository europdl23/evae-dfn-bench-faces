# Train the 36 models (N_max 50/120/200 x S1 folds 0-3 x run seeds), 5 at a time, interleaved across variants.
import subprocess, sys, os, itertools
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
W = Path(__file__).resolve().parent
jobs = [(n, f, s) for f in range(4) for s in (1337, 20260903, 7) for n in (50, 120, 200)]
def run(j):
    n, f, s = j
    out = W / 'models' / ('N%d' % n) / ('S1_f%d_s%d' % (f, s))
    if (out / 'run_status.json').exists():
        return 'skip %s' % (j,)
    env = dict(os.environ, S1_WORK_DIR=str(W / 'work'), PYTHONDONTWRITEBYTECODE='1')
    with open(W / 'logs' / ('train_N%d_f%d_s%d.log' % (n, f, s)), 'w') as lf:
        r = subprocess.run([sys.executable, str(W / 'code' / 'scripts' / 'train_evae.py'), 'S1', str(f), str(s), '--nmax', str(n), '--out', str(out)],
                           stdout=lf, stderr=subprocess.STDOUT, env=env)
    return '%s rc=%d' % (j, r.returncode)
# write fold data once first (avoid races)
env = dict(os.environ, S1_WORK_DIR=str(W / 'work'))
subprocess.run([sys.executable, '-c', 'import sys; sys.path.insert(0, r"%s"); import study as C; [C.write_fold_data("S1", f) for f in range(4)]' % (W / 'code' / 'src' / 'study')], env=env, check=True)
with ThreadPoolExecutor(5) as ex:
    for r in ex.map(run, jobs):
        print(r, flush=True)
