# -*- coding: utf-8 -*-
"""Shared settings for Figs. 2 and 5 and the graphical abstract of the REVISED Paper 1 (IJRMMS-D-26-00250); copy of
manuscript_revision_2026-10-01/code/rev_common.py, final-paper version of 1 Oct 2026 (work/GLOSSARY.md).
  - figure width = placement width 14.65 cm, so 12 pt text stays 12 pt on the page;
  - method colours: held-out black / dark grey, EVAE green #009E73, ADFNE #E69F00, KDE #56B4E9;
  - terminology (GLOSSARY): sampling window (window), held-out / neighbouring / training / validation window, window grid,
    window case, realisation, gap-filling / new-bench / new-stretch test, trace direction, trace-direction cluster.
Every figure is written to OUT (PNG 600 dpi + PDF) through figstyle.check_layout; plotted values go next to the figure in OUT.
Failed-check previews go to work/figcode/_scratch."""
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
from pathlib import Path
import matplotlib.pyplot as plt
import figstyle as S

OUT = _RR.OUT
VAL = OUT                                          # value files sit next to their figures (Figure_N_values.csv)
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW = _RR.SCRATCH; PREVIEW.mkdir(parents=True, exist_ok=True)
assert Path(S.__file__).resolve().parent == Path(__file__).resolve().parent, S.__file__   # the house check of figcode

W = 14.65 * S.CM                                   # placement width of the original manuscript
METHOD_COL = {'Mapped': '#000000', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}
SET_COL = S.SET_COL
TEST = {'S1': 'Hold-out test', 'S2': 'Whole-bench test', 'S3': '40 m-stretch test'}      # round 3 names (GLOSSARY Section 6)
TEST_SHORT = {'S1': 'Hold-out', 'S2': 'Whole bench', 'S3': '40 m stretch'}


def axes_cm(fig, x0, y_top, w, h):
    """axes placed in cm: left edge x0, top edge y_top measured down from the top of the figure"""
    FW, FH = fig.get_size_inches() * 2.54
    return fig.add_axes([x0 / FW, (FH - y_top - h) / FH, w / FW, h / FH])


def save(fig, name, allow=(12,)):
    """check_layout (mandatory), then PNG at 600 dpi and PDF into OUT; returns the check message and size in cm"""
    w, h = fig.get_size_inches() * 2.54
    probs = S.check_layout(fig, allow)
    if probs:                                     # keep a low-resolution preview for inspection, then fail
        fig.savefig(str(PREVIEW / (name + '_FAILED_preview.png')), dpi=150)
    msg = S.save(fig, str(OUT / name), allow_font_sizes=allow)
    print('%s: %s; %.2f x %.2f cm' % (name, msg, w, h))
    return w, h


def wid(key):
    """window ID of the paper (GLOSSARY 4b, 2 Oct 2026): release key W03_C2 -> W03-2 ("bench face W03, window column 2")"""
    face, col = str(key).split('_C')
    assert face[0] == 'W' and col.isdigit() and 1 <= int(col) <= 8, key
    return '%s-%s' % (face, col)
