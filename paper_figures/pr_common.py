# -*- coding: utf-8 -*-
"""Shared setup for the paper figures built from the release code (copy of the release paper/code/pr_common.py,
final-paper version of 1 Oct 2026).

The geobg release (SECTION1_EVAE_ADFNE_KDE_RELEASE_2026-10-01) is used READ ONLY: its modules are imported with
byte-code writing off, its scratch directory is redirected to work/figcode/_scratch, its tables, realisations and
example windows are only read. Every figure is written to paper1_revision_IJRMMS_2026-10-01/out/figures.
Terms follow work/GLOSSARY.md: sampling window (window), held-out / neighbouring / training / validation window,
window case, realisation, gap-filling / new-bench / new-stretch test, trace direction, trace-direction cluster."""
import os, sys
from pathlib import Path

sys.dont_write_bytecode = True                       # leave no __pycache__ in the release folders
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
HERE = Path(__file__).resolve().parent
REL = _RR.REPO
PR = REL / 'paper'                                   # release paper/ (read only: example_panels.json, tables)
SCRATCH = _RR.SCRATCH; SCRATCH.mkdir(exist_ok=True)
os.environ['S1_WORK_DIR'] = str(SCRATCH)             # any scratch of the release code goes here, not into the release
sys.path[:0] = [str(REL / 'scripts'), str(REL / 'src' / 'study')]
import study as C            # noqa: E402
import repo_paths as RP      # noqa: E402

TAB, NET = PR / 'tables', PR / 'networks'            # read only
OUT = _RR.OUT
FIG = OUT
CM = 1 / 2.54
W = 14.65 * CM                                       # figure width = placement width
SIZES = (12, 10)                                     # 12 pt text, 10 pt ticks and values
TEST = {'S1': 'hold-out test', 'S2': 'whole-bench test', 'S3': '40 m-stretch test'}        # round 3 names (GLOSSARY Section 6)
TEST_T = {'S1': 'Hold-out test', 'S2': 'Whole-bench test', 'S3': '40 m-stretch test'}
# test names as written in the release tables (column 'test'), read from the release so that no old name is a literal here
import pandas as _pd  # noqa: E402
REL_TEST = dict(zip(C.SCHEMES, _pd.read_csv(TAB / 'check_panel_spearman.csv').test.unique()))
CLU_COL = ['#0072B2', '#D55E00', '#CC79A7', '#F0E442', '#8C8C8C']   # C1..C4, unclustered traces (grey)
METHOD_COL = {'Held-out': '#333333', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9', 'Reference': '#9A9A9A'}
REF = [125.0, 56.0, 27.0, 89.0]
CLU_LABEL = ['C1 (about 125°)', 'C2 (about 56°)', 'C3 (about 27°)', 'C4 (about 89°)', 'Unclustered traces']


def wid(key):
    """window ID of the paper (GLOSSARY 4b, 2 Oct 2026): release key W03_C2 -> W03-2 ("bench face W03, window column 2")"""
    face, col = str(key).split('_C')
    assert face[0] == 'W' and col.isdigit() and 1 <= int(col) <= 8, key
    return '%s-%s' % (face, col)
