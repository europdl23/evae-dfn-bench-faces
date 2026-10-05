# -*- coding: utf-8 -*-
"""Data access for Figs. 2 and 5 (copy of manuscript_revision_2026-10-01/code/figdata.py, final-paper version of
1 Oct 2026). Only the study's data module is used: cv_common (through abl_common) for the bench-face metadata
(bench_labelling_section1/to_map_metadata; no image is read), the 705 mapped traces (traces_all.json), the window library and the
folds of the three hold-out tests. Everything is READ ONLY: byte-code writing is off and nothing below creates a
folder or a file outside paper1_revision_IJRMMS_2026-10-01/out/figures (the old FIG/TAB folders are not created).
The fold splits, neighbouring windows and validation windows are checked against the geobg release in rev_fig5_holdout.py."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
CV = _RR.cv_study()
sys.path.insert(0, str(CV / 'ablation_2026-09-30' / 'code'))
import abl_common as A                                # noqa: E402  (imports cv_study_2026-09-30/code/cv_common.py, read only)
C = A.C
