# -*- coding: utf-8 -*-
"""Repository paths for the schematic figures (Figs. 1, 3 and 4); added for the repository, the scripts import it as _SP.

Figs. 1, 3 and 4 are drawn in PowerPoint. build_all.py edits the authors' original slide deck with python-pptx and
export_figs.py exports the three figure slides through PowerPoint (Windows). The icons placed on the slides are drawn
by the make_icons*.py scripts from the traced data; the icons of the revised paper are in schematics/icons/.

Inputs that are NOT in the repository (each needed only by the scripts named):
  EVAE_SCHEMATICS_DECK   the authors' original deck Ppt_edit_figures.pptx (build_all.py). It is not released: its
                         unused slides hold photographs of the site, which build_all.py removes from the revised deck.
  EVAE_MANUSCRIPT_CODE   the authors' figure module fig_common (make_icons.py, make_icons_fig3_inputs.py)
  EVAE_CV_STUDY          the study folder with the full mapped traces (make_icons_geobg.py, make_icons_nophoto.py,
                         through figdata.py; see ../repo_root.py)
Outputs go to work/paper_figures/schematics/ (git-ignored); a rerun never writes over schematics/icons/.
Set SCHEMATICS_ICONS to a folder of regenerated icons to build the deck from those instead of the released icons.
No script reads or draws a photograph of the site.
"""
import os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_FIGURES = HERE.parent
sys.path.insert(0, str(PAPER_FIGURES))
import repo_root as _RR                                   # noqa: E402  (repository root, figure output folder)

REPO = _RR.REPO
WORK = REPO / 'work' / 'paper_figures' / 'schematics'
ICON_OUT = Path(os.environ.get('SCHEMATICS_ICON_OUT', str(WORK / 'icons')))      # where make_icons*.py write
ICONS = Path(os.environ.get('SCHEMATICS_ICONS', str(HERE / 'icons')))            # what build_fig*.py place
FIG_OUT = _RR.OUT                                                                   # Figure_1/3/4 .png and .pdf
DECK = FIG_OUT / 'Ppt_edit_figures_REVISED.pptx'                                    # the revised deck (three slides)
EXPORT = WORK / 'export'
for _d in (WORK, ICON_OUT, EXPORT):
    _d.mkdir(parents=True, exist_ok=True)


def _need(var, what):
    v = os.environ.get(var)
    if not v or not Path(v).exists():
        raise SystemExit('%s is not in the repository: set %s (see schematics/schem_paths.py).' % (what, var))
    return Path(v)


def original_deck():
    """the authors' original deck (not released; its unused slides hold photographs of the site)"""
    return _need('EVAE_SCHEMATICS_DECK', "The authors' original slide deck")


def manuscript_code():
    """the folder of the authors' figure module fig_common (not released)"""
    return _need('EVAE_MANUSCRIPT_CODE', "The authors' figure module fig_common")
