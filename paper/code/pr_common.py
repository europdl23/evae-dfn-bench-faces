# -*- coding: utf-8 -*-
"""Shared setup for the paper versions (paper/). Uses the release code read-only; writes only inside
paper/. Terms follow the paper: panel (held-out / neighbouring / training), realisation, gap-filling /
new-bench / new-stretch test, geology-informed constraints, trace-direction cluster."""
import os, sys
from pathlib import Path

sys.dont_write_bytecode = True                       # leave no __pycache__ in the release folders
PR = Path(__file__).resolve().parents[1]             # paper/
REL = PR.parent                                      # the release
os.environ.setdefault('S1_WORK_DIR', str(PR / 'work'))   # any scratch of the release code goes here, not into the release
sys.path[:0] = [str(REL / 'scripts'), str(REL / 'src' / 'study')]
import study as C            # noqa: E402
import repo_paths as RP      # noqa: E402

FIG, TAB, NET = PR / 'figures', PR / 'tables', PR / 'networks'
for d in (FIG, TAB, NET):
    d.mkdir(exist_ok=True)
CM = 1 / 2.54
W = 14.65 * CM                                       # figure width
SIZES = (12, 10)                                     # 12 pt text, 10 pt ticks and values
TEST = {'S1': 'gap-filling', 'S2': 'new-bench', 'S3': 'new-stretch'}
TEST_T = {'S1': 'Gap-filling test', 'S2': 'New-bench test', 'S3': 'New-stretch test'}
CLU_COL = ['#0072B2', '#D55E00', '#CC79A7', '#F0E442', '#8C8C8C']   # C1..C4, unclustered (grey)
METHOD_COL = {'Held-out': '#333333', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}
REF = [125.0, 56.0, 27.0, 89.0]
