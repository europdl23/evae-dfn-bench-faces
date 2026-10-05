# EVAE fracture-trace maps on open-pit bench faces: comparison with ADFNE and KDE

This repository holds the data and code of:

> Paudyal E, Tang Y, Lamei Ramandi H, Zhai H, Oh J, Yang S, Si G. Data-driven generative modelling of discrete fracture networks with geology-informed constraints. *International Journal of Rock Mechanics and Mining Sciences* (submitted).

It contains everything behind the comparison of three generators of 2D fracture-trace maps on the mapped bench faces of one open-pit wall:

* the traced data;
* the trained models;
* every generated realisation and its seed;
* the code, figures and tables, including the engineering inputs, the side checks and the sensitivity tests.

The three generators:

* **EVAE** is the learned generator: an enhanced variational autoencoder trained with geology-informed constraints.
* **ADFNE** and **KDE** are the established stochastic baselines. They use fitted distributions (a two-component trace-direction fit, fitted lengths and the mean trace count) and learn nothing.

All three use the same training windows and are tested on the same held-out windows. Every number can be recomputed from the files here, and every stored realisation can be regenerated bit for bit from its seed.

---

## 1. The study in plain words

* **The rock.** Seven bench faces of one pit wall were mapped by hand: 705 fracture traces.
* **Sampling windows.** The faces are cut into 50 sampling windows, each 20 m wide and the full face height.
* **Three tests.** Each test holds out some windows and asks a generator to fill them using only the other windows:
  * **hold-out test:** a window whose 8 surrounding windows are mapped (20 held-out windows, 4 folds);
  * **whole-bench test:** a whole bench face held out (50 windows, 7 folds);
  * **40 m-stretch test:** two adjacent window columns held out (50 windows, 4 folds).
* **Realisations.** For every held-out window each generator makes 24 realisations: 3 run seeds x 8.
  * The same seeds are used for all three generators.
  * The EVAE decodes each realisation from one of the 8 surrounding windows.
* **Trace-direction clusters.** On a face we see traces, not planes. The trace directions fall into 4 trace-direction clusters, C1 to C4 (about 125, 56, 27 and 89° on the face). Traces outside the clusters are "unclustered".
* **Comparison.** 15 network parameters and 38 error scores. Each score measures how far a realisation is from its held-out window.

Full definitions: `paper/SCORE_DEFINITIONS.md`. Method details: `docs/METHODS.md`.

---

## 2. Main results

**Held-out windows and EVAE in the three tests.**

| Parameter | Hold-out: held-out | EVAE | Whole-bench: held-out | EVAE | 40 m-stretch: held-out | EVAE |
|---|---|---|---|---|---|---|
| Median trace length (m) | 5.8 | 5.5 | 5.7 | 5.5 | 5.7 | 5.1 |
| 90th percentile length (m) | 13.9 | 11.8 | 12.4 | 12.1 | 12.4 | 11.4 |
| Intersections per 100 m² | 0.50 | 0.75 | 0.41 | 0.75 | 0.41 | 0.65 |
| Connections per trace | 0.73 | 0.90 | 0.68 | 1.00 | 0.68 | 0.87 |
| Spacing, nearest trace (m) | 3.1 | 4.1 | 3.0 | 4.1 | 3.0 | 4.0 |

* **Where the EVAE is closest to the held-out windows:** trace length and connectivity, in all three tests. In the hold-out test, ADFNE and KDE give median traces of 4.6 m and 5.2 m (mapped 5.8 m, EVAE 5.5 m) and 2.4 and 3.0 times the mapped intersection density (EVAE 1.5 times).
* **Trace directions are not significantly different between the generators.** All three are within about 1° of the held-out cluster directions.
* **Where the EVAE is worse:** its trace centres are spaced a little too far apart, it makes slightly fewer traces, and cluster C2 is about 4 percentage points too rare.
* **Paired tests over the held-out windows** (38 scores x 3 tests = 114 comparisons each; Holm over the two baselines; undefined scores left out, see "n.d." below):

| EVAE against | Better | No difference | Worse |
|---|---|---|---|
| ADFNE | 24 | 84 | 6 |
| KDE | 21 | 88 | 5 |

* **Clear winner in at least 2 of the 3 tests:** the EVAE on 7 scores (length distribution, median length, long traces, P21, intersections, connections per trace and node types); ADFNE and KDE on none.

**Ablation** (`docs/ABLATION.md`):

* **The geology-informed constraints matter.** Full EVAE against the EVAE without them: 25 better, 87 no difference, 2 worse. Without them, cluster C1 falls to 18-23 % of the traces (held-out 34-36 %).
* **Dual against single latent space:** no consistent difference in accuracy once the constraints are on (2 / 106 / 6); with the dual latent space, the constraints raise an error in only 2 of 114 comparisons.

**Undefined scores (n.d.).** Some scores cannot be computed for some realisations, for example a cluster score when a realisation has fewer than 2 traces of that cluster.

* These values are "n.d." and are left out of the medians, tests and intervals. This is the rule used in the paper.
* The first version of the study counted them as the worst possible value instead. With that rule the counts are: EVAE against ADFNE 32 / 70 / 12; against KDE 26 / 75 / 13; clear winners EVAE 8 scores, KDE 2; ablation 35 / 75 / 4. These are kept as a sensitivity check (`--penalty`, files ending in `_penalty`), and the paper reports them in its fourth limitation (Section 4.4).

---

## 3. What is in the repository

| Folder or file | Contents |
|---|---|
| `data/` | the 50 mapped sampling windows (`box_library/`, trace coordinates only, no photographs); the folds of the three tests (`splits/`); the trace-direction clusters of every fold; the fitted ADFNE and KDE parameters |
| `models/evae/` | the 45 trained EVAE models (15 folds x 3 run seeds), each with its training record |
| `models/ablation/` | the 135 ablation models (single latent with and without the geology-informed constraints; dual latent without them) |
| `networks/` | every realisation (17,280 files): `<test>/<generator>/f<fold>_<window>_s<run seed>_d<realisation>.csv`, one trace per row (x1, y1, x2, y2; 1 unit = 20 m) |
| `seeds/` | all seeds: the run seeds, the seed rule, the seed of every realisation, and the realisations shown in the figures |
| `src/` | the code: EVAE model and training, generators, trace-direction clusters, topology, figure style |
| `scripts/` | one script per step (Section 5) |
| `figures/`, `tables/` | quick-look figures and all result tables, including the full score tables of the three tests; `tables/final_tables.xlsx` has every comparison number in one Excel file |
| `paper/` | earlier figure versions, the tables and checks behind the paper's numbers, and the score definitions; see `paper/README.md` |
| `engineering/` | engineering inputs (equivalent moduli, deformability anisotropy, largest-cluster share, maximum persistence): code, tables, protocol, report |
| `paper_figures/` | code of the paper's figures, including the schematics (`schematics/`, with the drawn icons) |
| `side_check/` | BIC re-fit of the trace directions and the side check with the baselines given the four clusters |
| `sensitivity/` | the slot-limit, loss-weight and existence-threshold sensitivity tests (Appendix A, Table A2) |
| `docs/` | methods, results, ablation, data dictionary and reproducibility notes |
| `WINDOW_ID_MAPPING.csv` | window IDs of the paper (`W03-2`) against the file keys (`W03_C2`) |
| `CITATION.cff` | how to cite the data and code |

**Names in files and code.** Some older names are kept inside file and folder names because they are part of the seeds or of earlier documents. They mean:

| In the paper | In files, code and older documents | Meaning |
|---|---|---|
| sampling window (short: window) | `box` (files, code); "panel" (`docs/`, `paper/`) | a 20 m wide piece of one bench face, the full face height (20 m; 15.4 m on W00, 17.6 m on W06) |
| window ID **W03-2** | file key **W03_C2** | bench face W03, window column 2; `WINDOW_ID_MAPPING.csv` lists all 56 grid positions |
| hold-out, whole-bench, 40 m-stretch test | `S1`, `S2`, `S3`; "gap-filling", "new-bench", "new-stretch" | the three tests |
| held-out, surrounding, training, validation window | test, context, fitting, validation box (`data/splits/`) | roles of the windows in a fold |
| realisation; realisation index | `network` (files `networks/`); `draw` (`d00` to `d07`) | one generated trace map |
| trace direction θ | "orientation", `theta`, `orient_*` | the angle of a trace on the face, from the bench axis, 0 to 180° |
| trace-direction cluster C1 to C4 | "orientation cluster", `OC1` to `OC4`, `oc1_*` (`data/orientation_clusters/`) | the four learned clusters of trace directions |
| two trace-direction components (ADFNE and KDE) | "2-set fit", `sets[]` (`data/baseline_fits/`) | the baselines' two-component axial von Mises fit |
| geology-informed constraints | `guide` / `noguide` | the trace-direction distribution loss, the cluster-share loss and the geology-informed loss |
| EVAE | `geobg` (seed keys) | the enhanced variational autoencoder of the paper |
| ADFNE and KDE | `main` (seed keys) | the baselines |
| natural-variability reference | `Reference`; in `engineering/`: `Reference (fracture-removed)` | the 8 surrounding windows with the held-out fractures removed |
| not defined (n.d.) | `n.d.`, empty cells | a score that cannot be computed for a realisation |
| example window D, "difficult" | `"role": "hard"` in `paper/example_panels.json` | the example window chosen near the 90th percentile of the errors |
| trace-direction distribution, trace-direction clusters (score groups) | "Orientation distribution", "Orientation clusters" (`tables/stats_*.csv`) | score groups of the 38 error scores |

---

## 4. Where the paper's numbers come from

Counts of better / no difference / worse always use the n.d. rule. The `*_penalty.csv` files and `paper/tables/before_nd_rule/` hold the first-version rule.

| In the paper | Source in this repository |
|---|---|
| Table 2, hold-out test and generation modes | `data/splits/*.json`; rules in `src/study/study.py` and `docs/METHODS.md` |
| Table 3, network parameters, error scores and engineering inputs | `paper/SCORE_DEFINITIONS.md`; `scripts/statistical_tests.py`; `engineering/PROTOCOL_ENGINEERING.md` |
| Table 4, network parameters in the hold-out test | `tables/final_table_all.csv`, `paper/tables/Table_D_parameters.csv`; reference `paper/tables/Table_R1.csv`; topology and engineering rows `engineering/tables/Table_parameters_combined.csv`; test marks `tables/stats_decisions.csv` and `engineering/tables/engineering_tests.csv` |
| Table 5, component ablation | `tables/ablation_table.csv`, `paper/tables/Table_ablation_paper.csv`; counts `paper/tables/recount_ablation_counts.csv` |
| Counts of the EVAE against ADFNE and KDE, clear winners (Sections 3.6 and 4.1) | `tables/stats_decisions.csv`, `paper/tables/recount_EVAE_vs_baselines_counts.csv`, `recount_verdict.csv` |
| Natural-variability reference, representative generation, window-by-window agreement, memorisation (Section 3.4) | `paper/tables/check_natural_variability.csv`, `check_random_context.csv`, `check_panel_spearman.csv`, `check_memorisation.csv` |
| Benjamini-Hochberg correction, bootstrap intervals, per-seed analysis, refitted baselines (Sections 3.6 and 4.1) | `paper/tables/check_benjamini_hochberg*.csv`, `check_bootstrap_ci*.csv`, `check_per_seed_verdict*.csv`, `check_local_baselines*.csv` |
| Engineering inputs (Section 3.5, Fig. 7) | `engineering/tables/` |
| Two trace-direction components for ADFNE and KDE; baselines given the four clusters (Sections 2.5.3 and 3.6) | `side_check/tables/` |
| Table A1, EVAE layers | `src/model/` |
| Table A2, sensitivity tests | `sensitivity/nmax/`, `sensitivity/weight/`, `sensitivity/threshold/` |
| Table A3, the three tests against ADFNE and KDE | `tables/stats_decisions.csv`, `tables/stats_counts.csv` |
| Window grid, traces per window (Section 2.2) | `data/box_library/box_manifest.csv`, `data/box_library/boxes/*.json`, `WINDOW_ID_MAPPING.csv` |
| Figures 5 to 10 | `paper_figures/` (see its README); Figs. 1, 3 and 4 are schematics (`paper_figures/schematics/`); Fig. 2 needs the full mapped traces, which are not released |

---

## 5. Quick start

You need Python 3.10 or newer, and the Times New Roman font for the figures.

```bash
pip install -r requirements.txt
python scripts/verify_release.py              # checksums, splits, clusters, seeds: regenerates the example realisations
python scripts/make_figures.py --check        # quick-look figures and parameter tables, compared with tables/reference/
python scripts/statistical_tests.py --check   # EVAE vs ADFNE and KDE, 38 scores x 3 tests
python scripts/export_excel.py                # tables/final_tables.xlsx
python scripts/ablation_table.py --check      # the ablation table and tests
python paper/code/run_all.py                  # everything in paper/ (about 1 minute)
(cd paper_figures && python -B run_figures.py)  # the paper's data figures
```

`scripts/reproduce_all.sh` (Linux, Mac) or `scripts\reproduce_all.bat` (Windows) runs the first five steps. No GPU is needed. The engineering inputs, side checks and sensitivity tests have their own README files with their commands.

---

## 6. Going further

| Step | Command | Needs |
|---|---|---|
| Learn the trace-direction clusters again | `python scripts/fit_orientation_clusters.py` | Python |
| Retrain one EVAE | `python scripts/train_evae.py <S1/S2/S3> <fold> <run seed>` | PyTorch, about 2-3 minutes on a CPU |
| Regenerate realisations from their seeds | `python scripts/generate_networks.py evae S1 2` and `... baselines S1 2` | PyTorch; GNU Octave and ADFNE 1.5 for ADFNE (`--no-adfne` skips it) |
| Retrain or regenerate the ablation | `python scripts/ablation_run_all.py`, `python scripts/ablation_generate.py all` | PyTorch |
| Check all realisations | `python scripts/verify_release.py --full` | about 10 minutes (plus 1 hour for ADFNE) |

* **Where output goes.** Retrained models and regenerated realisations go to `work/`, never over the stored files.
* **ADFNE 1.5** is third-party software and is not included; `src/baselines/README.md` says how to install it.
* **Checked on 1 October 2026** (`docs/REPRODUCIBILITY.md`): every table recomputes identically; every example realisation regenerates bit for bit, for all three generators; a retrained EVAE gives a bit-identical model.

---

## 7. What is released, and what is not

**Released:** the traced data (2D trace end points in sampling-window coordinates, the window grid and the fold definitions), the code, and the outputs it produces from them (trained models, every realisation with its seed, the tables and the figures). For the sensitivity tests: the tables and every realisation, but not the retrained model checkpoints (about 590 MB).

**Not released:** photographs of the site and the bench-face images; the photogrammetric model; 3D and mine-grid coordinates; ADFNE 1.5 (third-party software). Some figure and schematic scripts need one of these inputs or the authors' original slide deck; they stop and say which input is missing. No released script reads or draws a photograph.

---

## 8. Limitations

* **One wall.** All data come from one wall of one pit. The windows touch each other, so they are not independent samples.
* **Reused test windows.** The two trace-direction losses and the rule for undefined scores were finalised after earlier tests on these windows (Section 4.4 of the paper).
* **Traces only.** Only 2D traces are compared; no 3D fracture planes are inferred.

---

## 9. How to cite and licence

* **The paper:** see the top of this file (journal details will be added on acceptance).
* **The data and code:** Paudyal E, Tang Y, Lamei Ramandi H, Zhai H, Oh J, Yang S, Si G. evae-dfn-bench-faces: data and code for "Data-driven generative modelling of discrete fracture networks with geology-informed constraints". GitHub, https://github.com/europdl23/evae-dfn-bench-faces. `CITATION.cff` holds both; GitHub shows them under "Cite this repository".
* **Code** (`src/`, `scripts/`, `paper/code/`, `engineering/code/`, `paper_figures/`, `side_check/code/` and the scripts in `sensitivity/`): MIT (`LICENSE`).
* **Data, models, realisations, tables and figures:** CC BY 4.0 (`LICENSE-DATA`).
