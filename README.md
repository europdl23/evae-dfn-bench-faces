# EVAE fracture-trace networks on open-pit bench faces: comparison with ADFNE and KDE

This repository holds everything behind the comparison of three generators of 2D fracture-trace networks on the mapped
bench faces of one open-pit wall:

* the data;
* the trained models;
* every generated realisation and its seed;
* the code, figures and tables.

The three generators:

* **EVAE** is the learned generator: a variational autoencoder trained with geology-informed terms.
* **ADFNE** and **KDE** are the standard baselines. They use fitted distributions (a 2-set direction fit, fitted
  lengths and the mean trace count) and learn nothing.

All three use the same training panels and are tested on the same held-out panels. Every number can be recomputed from
the files here, and every stored realisation can be regenerated bit for bit from its seed.

---

## 1. The study in plain words

* **The rock.** Seven bench faces of one pit wall were mapped by hand on orthophotos: 705 fracture traces.
* **Panels.** The faces are cut into 50 panels, each 20 m wide and the full face height.
* **Three tests.** Each test hides some panels (the held-out panels) and asks a generator to fill them using only the
  other panels:
  * **gap-filling test:** a panel whose 8 neighbours are known (20 held-out panels);
  * **new-bench test:** a whole bench face held out (50);
  * **new-stretch test:** a stretch of two panel columns held out (50).
* **Realisations.** For every held-out panel each generator makes 24 realisations: 3 run seeds x 8 draws.
  * The same seeds are used for all three generators.
  * The EVAE draws its realisations from the 8 neighbouring panels.
* **Trace-direction clusters.** On a face we see traces, not planes. The trace directions fall into 4
  trace-direction clusters (about 125, 56, 27 and 89° on the face). Traces outside the clusters are "unclustered".
* **Comparison.** 15 parameters (count, length, intensity, intersections, connections, spacing, cluster shares,
  directions and spreads) and 38 error scores. Each score measures how far a realisation is from its held-out panel.

Full definitions: `paper/SCORE_DEFINITIONS.md`. Method details: `docs/METHODS.md`.

---

## 2. Main results

**Held-out vs EVAE in the three tests.** The same pattern in all three tests shows that the EVAE is not fitted to one
part of the wall.

| Parameter | Gap-filling: held-out | EVAE | New-bench: held-out | EVAE | New-stretch: held-out | EVAE |
|---|---|---|---|---|---|---|
| Median trace length (m) | 5.8 | 5.5 | 5.7 | 5.5 | 5.7 | 5.1 |
| 90th percentile length (m) | 13.9 | 11.8 | 12.4 | 12.1 | 12.4 | 11.4 |
| Intersections per 100 m² | 0.50 | 0.75 | 0.41 | 0.75 | 0.41 | 0.65 |
| Connections per trace | 0.73 | 0.90 | 0.68 | 1.00 | 0.68 | 0.87 |
| Spacing, nearest trace (m) | 3.1 | 4.1 | 3.0 | 4.1 | 3.0 | 4.0 |

* **Where the EVAE is closest to held-out:**
  * trace length and connectivity, in all three tests;
  * ADFNE and KDE make traces 10-20 % too short and give 1.5-3 times too many intersections.
* **Trace directions are a tie.** All three generators are within about 1° of the held-out cluster directions.
* **Where the EVAE is worse:**
  * its traces are spaced a little too far apart;
  * it makes slightly fewer traces;
  * it has about 4 points less of cluster 2.
* **Paired tests over the held-out panels.** 38 scores x 3 tests = 114 comparisons each; Holm over the two baselines;
  undefined scores left out (see "n.d." below):

| EVAE against | Better | No difference | Worse |
|---|---|---|---|
| ADFNE | 24 | 84 | 6 |
| KDE | 21 | 88 | 5 |

* **Clear winner in at least 2 of the 3 tests:**
  * The EVAE wins 7 scores: length distribution, median length, long traces, P21, intersections, connections per
    trace and node types.
  * ADFNE and KDE win none.

**Ablation** (`docs/ABLATION.md`):

* **The geology-informed terms are what matter.** Full EVAE vs EVAE without these terms: 25 better, 87 no difference,
  2 worse. Without them, cluster 1 falls to 18-23 % of traces (held-out 34-36 %).
* **Dual vs single latent makes no consistent difference** once the terms are on: 2 / 106 / 6.

**Undefined scores (n.d.).** Some scores cannot be computed for some realisations: for example, a cluster score when a
realisation has fewer than 2 traces of that cluster.

* These values are "n.d." and are left out of the medians, tests and intervals. This is the rule used in the paper.
* The first version of the study counted them as the worst possible value instead. With that rule the counts are:
  * EVAE vs ADFNE 32 / 70 / 12; EVAE vs KDE 26 / 75 / 13;
  * clear winners: EVAE 8 scores, KDE 2;
  * ablation 35 / 75 / 4.

  These are kept as a sensitivity check (`--penalty`, files ending in `_penalty`).

---

## 3. What is in the repository

| Folder | Contents |
|---|---|
| `data/` | the 50 mapped panels (`box_library/`, trace coordinates only, no photographs); the folds of the three tests (`splits/`); the trace-direction clusters of every fold; the fitted ADFNE and KDE parameters |
| `models/evae/` | the 45 trained EVAE models (15 folds x 3 run seeds), each with its training record |
| `models/ablation/` | the 135 ablation models (single latent with and without the geology-informed terms; dual latent without them) |
| `networks/` | every realisation (17,280 files): `<test>/<generator>/f<fold>_<panel>_s<run seed>_d<draw>.csv`, one trace per row (x1, y1, x2, y2; 1 unit = 20 m) |
| `seeds/` | all seeds: the run seeds, the seed rule, the seed of every realisation, and the realisations shown in the figures |
| `src/` | the code: EVAE model and training, generators, trace-direction clusters, topology, figure style |
| `scripts/` | one script per step (Section 5) |
| `figures/`, `tables/` | quick-look figures (16 cm) and all result tables; `tables/final_tables.xlsx` has every comparison number in one Excel file |
| `paper/` | the figures and tables as used in the paper (14.65 cm figures), the Results and Discussion checks, and the score definitions; see `paper/README.md` |
| `docs/` | methods, results, ablation, data dictionary and reproducibility notes |

**Names in files and code.** Some older names are kept inside file and folder names because they are part of the
seeds. They mean:

| Name in files and code | Meaning |
|---|---|
| box | panel |
| network | realisation |
| S1, S2, S3 | gap-filling, new-bench, new-stretch test |
| guide / noguide | with / without the geology-informed terms |
| orientation cluster | trace-direction cluster |
| geobg | the EVAE (in seed keys) |
| main | ADFNE and KDE (in seed keys) |

---

## 4. Quick start

You need Python 3.10 or newer, and the Times New Roman font for the figures.

```bash
pip install -r requirements.txt
python scripts/verify_release.py              # checksums, splits, clusters, seeds: regenerates the example realisations
python scripts/make_figures.py --check        # quick-look figures and parameter tables, compared with tables/reference/
python scripts/statistical_tests.py --check   # EVAE vs ADFNE and KDE, 38 scores x 3 tests
python scripts/export_excel.py                # tables/final_tables.xlsx
python scripts/ablation_table.py --check      # the ablation table and tests
python paper/code/run_all.py                  # everything in paper/ (about 1 minute)
```

`scripts/reproduce_all.sh` (Linux, Mac) or `scripts\reproduce_all.bat` (Windows) runs the first five steps. No GPU is
needed.

---

## 5. Going further

| Step | Command | Needs |
|---|---|---|
| Learn the trace-direction clusters again | `python scripts/fit_orientation_clusters.py` | Python |
| Retrain one EVAE | `python scripts/train_evae.py <S1/S2/S3> <fold> <run seed>` | PyTorch, about 2-3 minutes on a CPU |
| Regenerate realisations from their seeds | `python scripts/generate_networks.py evae S1 2` and `... baselines S1 2` | PyTorch; GNU Octave and ADFNE 1.5 for ADFNE (`--no-adfne` skips it) |
| Retrain or regenerate the ablation | `python scripts/ablation_run_all.py`, `python scripts/ablation_generate.py all` | PyTorch |
| Check all realisations | `python scripts/verify_release.py --full` | about 10 minutes (plus 1 hour for ADFNE) |

* **Where output goes.** Retrained models and regenerated realisations go to `work/`, never over the stored files.
* **ADFNE 1.5** is third-party software and is not included; `src/baselines/README.md` says how to install it.
* **Checked on 1 October 2026** (`docs/REPRODUCIBILITY.md`):
  * every table recomputes identically;
  * every example realisation regenerates bit for bit, for all three generators;
  * a retrained EVAE gives a bit-identical model.

---

## 6. Limitations

* **One wall.** All data come from one wall of one mine. The panels touch each other, so they are not independent
  samples.
* **Reused test panels.** The held-out panels were also used in earlier rounds of the study.
* **Traces only.** Only 2D traces are compared; no 3D fracture planes are inferred.

---

## 7. Licence

* **Code** (`src/`, `scripts/`, `paper/code/`): MIT (`LICENSE`).
* **Data, models, realisations, tables and figures:** CC BY 4.0 (`LICENSE-DATA`).
* **Not included:** the bench-face photographs, which belong to the mine operator, and ADFNE 1.5.
