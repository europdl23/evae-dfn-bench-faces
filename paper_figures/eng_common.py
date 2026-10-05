# -*- coding: utf-8 -*-
"""Shared setup for Fig. 9 (engineering inputs); copy of engineering_demo_2026-10-01/code/eng_common.py, final-paper
version of 1 Oct 2026. The engineering demonstration (engineering_demo_2026-10-01/tables) and the geobg release
(SECTION1_EVAE_ADFNE_KDE_RELEASE_2026-10-01) are used READ ONLY: byte-code writing is off, the release scratch is
redirected to work/figcode/_scratch and the figure is written to paper1_revision_IJRMMS_2026-10-01/out/figures.
Terms follow work/GLOSSARY.md: held-out / neighbouring window, window case, realisation, gap-filling / new-bench /
new-stretch test, trace-direction cluster C1 to C4, natural-variability reference."""
import os, sys
from pathlib import Path

sys.dont_write_bytecode = True                         # leave no __pycache__ in the release or the demonstration
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
HERE = Path(__file__).resolve().parent                 # work/figcode
ENG = (_RR.REPO / 'engineering')
REL = _RR.REPO
os.environ['S1_WORK_DIR'] = str(_RR.SCRATCH)     # any scratch of the release code goes here
TAB = ENG / 'tables'                                   # read only
FIG = _RR.OUT
TEST = {'S1': 'gap-filling', 'S2': 'new-bench', 'S3': 'new-stretch'}
GEN = ('EVAE', 'ADFNE', 'KDE')
REFERENCE = 'Reference (fracture-removed)'             # the paper's natural-variability reference (equals the release reference)
