# -*- coding: utf-8 -*-
"""Rebuild everything in paper/ from the release, in order:
  1. select_examples.py     the example panels (rule in paper/EXAMPLE_PANELS.md)
  2. make_realisations.py   random-context realisations (regenerated) and the refitted gap-filling baselines (checked)
  3. checks.py              Results and Discussion checks
  4. discussion.py          recount with undefined scores as n.d., Figure 9, Figure 11, Tables D, ablation and S
  5. tables_export.py       Table_R1.xlsx and checks.xlsx
  6. figures.py             Figures R1, R2, R4 and D1 (R1 with photographs only when S1_PHOTO_DIR points to them)
Usage (from the repository root):  python paper/code/run_all.py        about 5 minutes on a desktop computer"""
import sys, subprocess, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [['select_examples.py'], ['make_realisations.py'], ['checks.py'], ['discussion.py'], ['tables_export.py'], ['figures.py', 'R1', 'R2', 'R4', 'D1']]
for st in STEPS:
    t0 = time.time()
    r = subprocess.run([sys.executable, '-B'] + st, cwd=str(HERE))
    print('%-4s %s (%.0f s)' % ('OK' if r.returncode == 0 else 'FAIL', ' '.join(st), time.time() - t0), flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)
print('paper/ rebuilt')
