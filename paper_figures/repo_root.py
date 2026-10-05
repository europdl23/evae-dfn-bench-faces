# -*- coding: utf-8 -*-
"""Repository paths for the paper figure code (added for the repository; the figure scripts import it as _RR).

The repository root is the folder holding the marker file `.repo-root`, found by walking up from this file
(or the folder named by the environment variable EVAE_REPO). Figures go to work/paper_figures/ (git-ignored) unless
REV_FIG_OUT names another folder. One input is NOT in the repository and is only needed for some figures:

  EVAE_CV_STUDY  the authors' study folder with the full mapped traces of the wall (Figs. 2 and 5)

No figure uses a photograph of the site; the photographs are not released.
"""
import os
from pathlib import Path


def _find_root(start):
    for d in [start] + list(start.parents):
        if (d / '.repo-root').exists():
            return d
    raise RuntimeError('repository root not found: no .repo-root marker above %s (or set EVAE_REPO)' % start)


REPO = Path(os.environ['EVAE_REPO']).resolve() if os.environ.get('EVAE_REPO') else _find_root(Path(__file__).resolve().parent)
OUT = Path(os.environ.get('REV_FIG_OUT', str(REPO / 'work' / 'paper_figures')))
SCRATCH = REPO / 'work' / 'paper_figures' / '_scratch'
OUT.mkdir(parents=True, exist_ok=True)
SCRATCH.mkdir(parents=True, exist_ok=True)


def cv_study():
    """the authors' study folder (not released); needed only for Figs. 2 and 5"""
    v = os.environ.get('EVAE_CV_STUDY')
    if not v or not Path(v).exists():
        raise SystemExit('This figure needs the full mapped traces of the wall, which are not in the repository '
                         '(their end points carry mine-grid coordinates). Set EVAE_CV_STUDY to the study folder.')
    return Path(v)
