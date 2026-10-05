# -*- coding: utf-8 -*-
"""Shared setup for the engineering inputs (paper Sections 2.5.5 and 3.5, Fig. 9, Tables 3, S4 and S5).

Repository version of engineering_demo_2026-10-01/code/eng_common.py (1 October 2026). It is identical except for the
paths: the repository root is the folder holding `.repo-root` (or the folder named by EVAE_REPO), and a rerun writes
to work/engineering/ (git-ignored, or ENG_OUT_DIR), never over the stored tables in engineering/tables/.
Names in the code follow the release files: box = panel = sampling window, network = realisation,
S1 / S2 / S3 = gap-filling / new-bench / new-stretch test, trace-direction cluster C1-C4."""
import os, sys
from pathlib import Path

sys.dont_write_bytecode = True                         # leave no __pycache__ in the repository
HERE = Path(__file__).resolve().parents[1]             # engineering/


def _find_root(start):
    for d in [start] + list(start.parents):
        if (d / '.repo-root').exists():
            return d
    raise RuntimeError('repository root not found: no .repo-root marker above %s (or set EVAE_REPO)' % start)


REL = Path(os.environ['EVAE_REPO']).resolve() if os.environ.get('EVAE_REPO') else _find_root(HERE)
OUT = Path(os.environ.get('ENG_OUT_DIR', str(REL / 'work' / 'engineering')))
STORED = HERE / 'tables'                               # the tables as used in the paper (read only)
os.environ['S1_WORK_DIR'] = str(OUT / 'scratch')       # any scratch of the release code goes here
sys.path[:0] = [str(REL / 'scripts'), str(REL / 'src' / 'study'), str(REL / 'paper' / 'code')]
import study as C              # noqa: E402
import setbg as SB             # noqa: E402
from topology import topology  # noqa: E402

TAB, FIG = OUT / 'tables', OUT / 'figures'
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
TEST = {'S1': 'gap-filling', 'S2': 'new-bench', 'S3': 'new-stretch'}
GEN = ('EVAE', 'ADFNE', 'KDE')
P_CRIT = 5.6                                           # 2D percolation threshold of p = sum(l^2)/A (Robinson 1984; Bour and Davy 1997)
