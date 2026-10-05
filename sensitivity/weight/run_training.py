# Train the 96 weight-variant models (8 variants x S1 folds 0-3 x 3 run seeds), 6 at a time, interleaved across variants.
# Plus one baseline check model (release weights, S1 f0 s1337) to confirm the code edits are no-ops.
_REPO = __import__('pathlib').Path(__file__).resolve().parents[2]   # repository root (sensitivity/<test>/ lies two levels down)
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
W = Path(__file__).resolve().parent
VARIANTS = {
    'A_half': {'WS_EVW_PHYS': '0.0025'}, 'A_double': {'WS_EVW_PHYS': '0.01'},
    'B_half': {'WS_EVGEO_W': '0.5', 'WS_EVBG_W': '0.5'}, 'B_double': {'WS_EVGEO_W': '2.0', 'WS_EVBG_W': '2.0'},
    'C_half': {'WS_EVW_INT': '0.15', 'WS_EVW_SP': '0.1'}, 'C_double': {'WS_EVW_INT': '0.6', 'WS_EVW_SP': '0.4'},
    'D_half': {'WS_EVFIX_WQ': '0.5'}, 'D_double': {'WS_EVFIX_WQ': '2.0'},
}
jobs = [('BASE_check', 0, 1337)] + [(v, f, s) for f in range(4) for s in (1337, 20260903, 7) for v in VARIANTS]
REL_MODELS = str(_REPO / 'models' / 'evae')
def run(j):
    v, f, s = j
    out = W / 'models' / v / ('S1_f%d_s%d' % (f, s))
    if (out / 'run_status.json').exists():
        return 'skip %s' % (j,)
    env = {k: x for k, x in os.environ.items() if not k.startswith('WS_')}
    env.update(S1_WORK_DIR=str(W / 'work'), S1_MODELS_DIR=REL_MODELS, PYTHONDONTWRITEBYTECODE='1', **VARIANTS.get(v, {}))
    with open(W / 'logs' / ('train_%s_f%d_s%d.log' % (v, f, s)), 'w') as lf:
        r = subprocess.run([sys.executable, str(W / 'code' / 'scripts' / 'train_evae.py'), 'S1', str(f), str(s), '--nmax', '120', '--out', str(out)],
                           stdout=lf, stderr=subprocess.STDOUT, env=env)
    return '%s rc=%d' % (j, r.returncode)
if __name__ == '__main__':
    env = dict(os.environ, S1_WORK_DIR=str(W / 'work'))
    subprocess.run([sys.executable, '-c', 'import sys; sys.path.insert(0, r"%s"); import study as C; [C.write_fold_data("S1", f) for f in range(4)]' % (W / 'code' / 'src' / 'study')], env=env, check=True)
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(run, jobs):
            print(r, flush=True)
