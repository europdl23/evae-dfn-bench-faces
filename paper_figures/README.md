# Figure code of the paper

This folder holds the code that draws the data figures of the revised paper (IJRMMS-D-26-00250), numbered as in the paper (Figs. 1 to 10). Every figure reads only the repository's data, realisations and tables. It is written at 14.65 cm width (the placement width), Times New Roman 12 pt with 10 pt ticks, as PNG (600 dpi) and PDF. A values file (`Figure_N_values.csv`) next to each figure holds every plotted number.

Before saving, each figure passes a layout check (`figstyle.check_layout`, and `figstyle_release` for the figures drawn with the release code): fonts and sizes, no overlapping text, nothing outside the figure.

## Run

```bash
cd paper_figures
python -B run_figures.py          # about 3 minutes
```

The figures go to `work/paper_figures/`, which git ignores; set `REV_FIG_OUT` to write them elsewhere. You need Python 3.10 or newer, the packages in `requirements.txt`, and the Times New Roman font.

## What is drawn from the repository alone

| Paper figure | Script | Data read |
|---|---|---|
| Fig. 5: example windows A to D, held-out traces and one EVAE realisation | `figures_round3.py 5` | `paper/example_panels.json`, `data/`, `networks/` |
| Fig. 6: trace directions and lengths, local and representative generation | `figures_round3.py 6` | `networks/`, `data/` |
| Fig. 7: engineering inputs, differences from the held-out window | `fig_engineering.py` | `engineering/tables/`, `paper/tables/panel_properties.csv`, `tables/final_properties.csv` |
| Fig. 8: example windows A to D, EVAE, ADFNE and KDE, with intersections and T-ends | `figures_round3.py 8` | `paper/example_panels.json`, `networks/` |
| Fig. 9: trace directions and lengths, EVAE, ADFNE and KDE | `figures_round3.py 9` | `networks/`, `data/` |
| Fig. 10: connectivity and node types | `figures_round3.py 10` | `networks/`, `data/` |
| (not in the paper) window-by-window agreement and pooled length histograms | `figures_round3.py S2`, `discussion.py S1` | `paper/tables/`, `networks/` |

`round3_compute.py` computes the values that these figures plot; `run_figures.py` runs it first. All realisations shown are the first realisation of each window case: run seed 1337, realisation 0, for every generator. They were not selected.

## What needs inputs that are not in the repository

| Paper figure | Script | Missing input |
|---|---|---|
| Fig. 2: the mapped wall and the window roles | `rev_fig2_wall.py` | the full mapped traces of the wall. Their end points carry mine-grid coordinates, which are not released. |
| Figs. 1, 3 and 4 | `schematics/` (see below) | the authors' original slide deck, which is not released |

`run_figures.py` skips these steps and says so. With the input available, set `EVAE_CV_STUDY` (the study folder), and `run_figures.py` runs them too. The graphical abstract script (`rev_graphical_abstract.py`) reads values files of an earlier figure set and is not run by `run_figures.py`.

No figure shows a photograph of the site. The photographs, the photogrammetric model and the mine-grid coordinates are not released.

## Schematic figures (Figs. 1, 3 and 4): `schematics/`

Figs. 1, 3 and 4 are drawn in PowerPoint. The scripts edit the authors' slide deck with python-pptx and export the three figure slides through PowerPoint (Windows only).

| Step | Script | What it does | Needs (not in the repository) |
|---|---|---|---|
| 1 | `make_icons.py`, `make_icons_fig3_inputs.py` | Step 2 sketches of Fig. 1; the input, output and loss icons of Figs. 3 and 4 | the authors' figure module (`EVAE_MANUSCRIPT_CODE`) |
| 2 | `make_icons_geobg.py` | Fig. 1 Steps 3 and 4 (example window A = W03-2, its 8 neighbouring windows, the three tests); the cluster-share icon of Fig. 4 | the study folder (`EVAE_CV_STUDY`) |
| 3 | `make_icons_nophoto.py` | Fig. 1 Step 1, drawn: a bench profile of an open pit, a traces-only crop, the window grid | the study folder (`EVAE_CV_STUDY`) |
| 4 | `build_all.py` (with `build_fig1.py`, `build_fig3.py`, `build_fig4.py`, `pp.py`) | places the icons and text on the three figure slides and removes every other slide and unused picture | the original deck (`EVAE_SCHEMATICS_DECK`) |
| 5 | `export_figs.py` | exports Figs. 1, 3 and 4 as PNG and PDF | PowerPoint |
| check | `check_fit.py`, `check_media.py`, `dump_slide_texts.py` | text fit and fonts; no photograph in the deck or the figures; the figure texts for the term check | the revised deck from step 4 |

The icons of the revised paper are in `schematics/icons/` (with the plotted values in `icons_geobg_values.json`). They are drawn graphics: sketches, plots, and traces drawn from the traced data. None is a photograph; each was measured by `check_media.py`'s photo test and looked at. The icon scripts write to `work/paper_figures/schematics/icons/` and never over `schematics/icons/`. To build the deck from regenerated icons, set `SCHEMATICS_ICONS` to that folder. All paths are set in `schematics/schem_paths.py`.

The original deck is not released, because its unused slides hold photographs of the site. `build_all.py` removes those slides, and `check_media.py` confirms that the revised deck holds no photograph. No script reads or draws a photograph.

## Names

Names in the figures follow the paper: sampling window, held-out window, realisation, trace direction, trace-direction cluster C1 to C4, and window IDs written W03-2 (bench face W03, window column 2). The code keeps the file keys of the repository (`box` for a window, `network` for a realisation, `S1`/`S2`/`S3` for the gap-filling, new-bench and new-stretch tests, and window files such as `W03_C2`). `WINDOW_ID_MAPPING.csv` in the repository root lists every window under both IDs.

## Files

* `run_figures.py`: builds every figure above.
* `repo_root.py`: finds the repository root (marker `.repo-root`) and the output folder.
* `pr_common.py`, `geobg_common.py`, `rev_common.py`, `eng_common.py`, `figdata.py`: shared data access and settings.
* `figstyle.py`, `figstyle_release.py`: style and layout checks.
* `figures.py`, `discussion.py`, `fig_engineering.py`, `rev_fig2_site.py`, `rev_fig5_holdout.py`, `rev_graphical_abstract.py`, `select_examples.py`: the figures.
* `schematics/`: Figs. 1, 3 and 4 (scripts and drawn icons; see above).

These are copies of the scripts that drew the submitted figures. The only change is that absolute paths were replaced by repository paths, through `repo_root.py` (and `schematics/schem_paths.py`).
