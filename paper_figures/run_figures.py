# -*- coding: utf-8 -*-
"""ROUND 3 (3 Oct 2026, PLAN_ROUND3 Section C): numbering Fig. 2 wall + window roles (rev_fig2_wall.py), Fig. 5 example
windows, Fig. 6 local and representative generation, Fig. 8 four methods with intersections, Fig. 9 roses and lengths,
Fig. 10 connectivity, Fig. S2 window by window (figures_round3.py), Fig. 7 engineering inputs (fig_engineering.py),
Fig. S1 fold map and lengths (rev_figS1_folds.py); values from round3_compute.py. Old header follows.
Rebuild every data figure of the final revised paper (IJRMMS-D-26-00250) into out/figures, numbering of
work/GLOSSARY.md Section 5. Figures 1, 3 and 4 (schematics) come from the revised PowerPoint and are NOT built here.

  select_examples.py           check: the example windows A to D equal the release paper/example_panels.json (writes _scratch only)
  rev_fig2_site.py             Figure_2   site and window grid, trace-direction clusters (bench faces drawn, no photograph)
  rev_fig5_holdout.py          Figure_5   hold-out tests
  figures.py 6 7 8 11          Figure_6 (example windows, no photograph), Figure_7, Figure_8, Figure_11
  fig_engineering.py           Figure_9   engineering inputs, differences from the held-out window
  discussion.py 10 S1          Figure_10  ablation counts, Figure_S1 length histograms
  rev_graphical_abstract.py    Graphical_abstract (mini Figs. 9a and 9c from Figure_9_values.csv, pooled medians from Figure_S1_values.csv)

Every figure passes figstyle.check_layout (house check with the GLOSSARY term check); the figures drawn with the
release code also pass the release check (figstyle_release). The release (SECTION1_EVAE_ADFNE_KDE_RELEASE_2026-10-01),
the engineering demonstration (engineering_demo_2026-10-01) and the study data (bench_labelling_section1) are only read.
No figure shows a photograph of the site (author decision of 2 Oct 2026: the mine operator does not permit photographs).
Usage: python -B run_figures.py        (about 3 minutes)"""
import subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = [['round3_compute.py'], ['rev_fig2_wall.py'], ['rev_figS1_folds.py'], ['figures_round3.py', '5', '6', '8', '9', '10', 'S2'],
           ['fig_engineering.py'], ['discussion.py', 'S1']]   # round 3 (discussion.py S1 writes Figure_S3); the graphical abstract (rev_graphical_abstract.py) still reads the round-2 value files: NOT rebuilt
# Repository version: steps whose inputs are not in the repository run only when their folder is given.
#   EVAE_CV_STUDY  the authors' study folder with the full mapped traces (every script that imports figdata: Figs. 2, 5)
# No figure uses a photograph (author decision of 2 Oct 2026: the photographs are not released).
import os as _os
_cv = bool(_os.environ.get('EVAE_CV_STUDY'))
_keep = []
for _s in SCRIPTS:
    if not _cv and 'import figdata' in (HERE / _s[0]).read_text(encoding='utf-8'):
        print('%-34s skipped (needs EVAE_CV_STUDY, not in the repository)' % ' '.join(_s)); continue
    _keep.append(_s)
SCRIPTS = _keep
failed = []
for s in SCRIPTS:
    t = time.time()
    r = subprocess.run([sys.executable, '-B'] + s, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    lines = [x for x in r.stdout.splitlines() if 'clean' in x or 'identical' in x]
    print('%-34s %s  (%.0f s)' % (' '.join(s), (('\n' + ' ' * 36).join(lines) or 'done') if r.returncode == 0 else 'FAILED', time.time() - t), flush=True)
    if r.returncode:
        failed.append(s[0]); print(r.stderr[-2000:])
sys.exit(1 if failed else 0)
