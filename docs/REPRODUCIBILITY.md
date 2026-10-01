# Reproducibility

## Order of the steps

1. **Orientation clusters** of every fold, from its fitting boxes:
   `python scripts/fit_orientation_clusters.py` (add `--write` to overwrite `data/orientation_clusters/`).
2. **Train the EVAEs:** `python scripts/train_evae.py <scheme> <fold> <run seed>`.
   * 45 runs: S1 folds 0-3, S2 folds 0-6, S3 folds 0-3, each with run seeds 1337, 20260903 and 7.
   * Output goes to `work/models_retrained/`.
3. **Generate the networks:**
   * `python scripts/generate_networks.py evae <scheme> <fold> --models <models folder>`;
   * `python scripts/generate_networks.py baselines <scheme> <fold>`.
   * Output goes to `work/networks_regenerated/`.
   * ADFNE needs GNU Octave and ADFNE 1.5 (`src/baselines/README.md`); `--no-adfne` makes only KDE.
4. **Figures and tables:** `python scripts/make_figures.py`.
5. **Statistical tests:** `python scripts/statistical_tests.py`.
6. **Excel file of all tables:** `python scripts/export_excel.py` writes `tables/final_tables.xlsx` (same bytes on every run).
7. **Ablation:** `python scripts/ablation_table.py` (table, tests, Excel).
8. **Paper figures, tables and checks:** `python paper/code/run_all.py` (about 1 minute; Figure R1 is drawn without the photographs unless `S1_PHOTO_DIR` points to them).

Steps 4 and 5 read `networks/`. To use regenerated networks, set `S1_NETWORKS_DIR` to their folder.

## Checked on 1 October 2026

Windows 11, Python 3.10.11, numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, torch 2.6.0 (CPU), matplotlib 3.10.6, Octave 11.3.0.

| Check | Result |
|---|---|
| Tables behind Figures 2-4 recomputed from `networks/` | identical to `tables/reference/` |
| Statistical counts and verdicts recomputed | identical; n.d. rule: 24 / 84 / 6 vs ADFNE, 21 / 88 / 5 vs KDE, EVAE 7 verdict wins; first-version penalty rule (`--penalty`): 32 / 70 / 12, 26 / 75 / 13, EVAE 8 and KDE 2 |
| Orientation clusters refitted (15 folds) | identical (maximum difference 0) |
| Fold splits recomputed (15 folds) | identical to `data/splits/` |
| Figure 1 networks regenerated from their seeds | EVAE, ADFNE and KDE: all 9 bit-identical |
| All EVAE and KDE networks of fold S1-2 regenerated | 288 of 288 bit-identical |
| EVAE S1 fold 2, run seed 1337 retrained from scratch | checkpoint bit-identical (same sha256, same 87 epochs) |

## What can make a rerun differ

* **Training.** It is deterministic on the CPU with 4 threads and the library versions above. Another PyTorch version,
  thread count or a GPU can change the last digits of the weights, and therefore the networks; the conclusions should
  not change.
* **ADFNE.** It depends on Octave's random-number generator. The networks above were made with Octave 11.3.0.
* **Fixed seeds.** All seeds are fixed (`seeds/seeds.json`). Nothing is drawn from the clock.

## One correction made while packaging

In `tables/reference/final_properties.csv`, the per-box cluster-share columns OC1 and OC2 of fold S2-4 were swapped in
the study copy. That table was written before the clusters of that fold were stored in the fixed direction order. The
values were right; only the two column labels were exchanged. No figure, table value or test used these two columns.
The reference copy here is the corrected one.
