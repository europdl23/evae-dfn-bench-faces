# -*- coding: utf-8 -*-
"""Shared settings of the round-3 figures (PLAN_ROUND3_AUTHOR_COMMENTS_2026-10-03, Sections B, C, H; GLOSSARY.md round 3).

Terms: hold-out test (release scheme S1, 20 held-out windows, 4 folds) = the ONLY test of the main text;
local generation (EVAE from the 8 surrounding windows) = the proposed method; representative generation (EVAE from 8
randomly chosen mapped windows of the wall; release paper/networks/random_context) = control mode; robustness tests
(Supplement only): whole-bench test (release S2) and 40 m-stretch test (release S3), where the 8 windows are the
"nearest available mapped windows".

Example windows of the main text (Figs. 5 and 8), one rule fixed before drawing, applied to the hold-out test only
(the release rule of select_examples.py restricted to S1): typical windows = the three windows whose standardised EVAE
error vector (direction W1, length W1, count error, cluster-share error; window value = median of 24 realisations,
release tables/stats_box_medians.csv) is closest to the vector of medians, in order of distance (A, B, C); difficult
window D = the window whose mean standardised error is closest to the 90th percentile. Result (round3 run of 3 Oct 2026):
A W03-2 (distance 0.709, fold 3), B W04-6 (0.830, fold 1), C W03-3 (0.847, fold 4), D W02-2 (difficult, fold 1).
A and D are the release windows A and D; B and C replace the release's robustness-test windows.
Realisation shown = run seed 1337, first realisation, every method (not selected)."""
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
import json
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'work' / 'round3_data'
OUT = _RR.OUT
MCOL = {'Mapped': '#000000', 'EVAE': '#009E73', 'Representative': '#7FCDB6', 'ADFNE': '#E69F00', 'KDE': '#56B4E9',
        'Reference': '#9A9A9A'}
EXAMPLES = [dict(label='A', box='W03_C2', fold=2, role='typical'), dict(label='B', box='W04_C6', fold=0, role='typical'),
            dict(label='C', box='W03_C3', fold=3, role='typical'), dict(label='D', box='W02_C2', fold=0, role='difficult')]


def check_examples():
    """re-apply the rule and assert the four windows (no figure is drawn before this passes)"""
    import pr_common as P
    SC = ['orient_w1_deg', 'len_w1_m', 'P20_relerr', 'cluster_share_tv']
    B = pd.read_csv(P.RP.TABLES_DIR / 'stats_box_medians.csv', na_values=['n.d.'])
    q = B[(B.method == 'EVAE') & (B.scheme == 'S1')].set_index('box')[SC].astype(float)
    z = (q - q.mean()) / q.std(ddof=0)
    dist = np.sqrt(((z - z.median()) ** 2).sum(1)).sort_values(kind='stable')
    typ = list(dist.index[:3]); mz = z.mean(1); p90 = float(np.percentile(mz, 90))
    hard = next(k for k in (mz - p90).abs().sort_values(kind='stable').index if k not in typ)
    lib = P.C.load_library()
    got = [(b, P.C.fold_of('S1', b, lib)) for b in typ + [hard]]
    assert got == [(e['box'], e['fold']) for e in EXAMPLES], got
    out = dict(rule=__doc__.split('Example windows', 1)[1].split('Realisation shown')[0].strip(),
               windows=[dict(e, distance_to_median=round(float(dist[e['box']]), 3), mean_z=round(float(mz[e['box']]), 3),
                             errors={k: round(float(q.loc[e['box'], k]), 4) for k in SC}) for e in EXAMPLES], p90_mean_z=round(p90, 3))
    DATA.mkdir(exist_ok=True)
    json.dump(out, open(DATA / 'example_windows_round3.json', 'w'), indent=1)
    return out
