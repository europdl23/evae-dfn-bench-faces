# Engineering inputs derived from the trace maps

This folder holds the code, the tables and the protocol behind the engineering inputs of the paper: Section 2.5.5 (definitions), Section 3.5 (results), Fig. 9, the engineering block of Table 3, and the engineering rows of Tables S4 and S5. They answer the question: if an engineer fed each realisation into standard upscaling relations, would they get the same input as from the mapped window?

Nothing here retrains or regenerates anything. The code reads the mapped windows (`data/box_library`), the fold splits and cluster models (`data/`) and the stored realisations (`networks/`) of this repository.

## Which reference the paper uses

The natural-variability reference is the eight neighbouring windows of each held-out window.

* **Primary reference (used everywhere in the paper):** the neighbouring windows **with the held-out fractures removed**. In the tables this is the method or column `Reference (fracture-removed)`. It is the same reference as the release's `paper/tables/Table_R1.csv`.
* **Sensitivity only:** the **intact** neighbouring windows (all mapped traces kept), labelled `Reference` in the tables. The pooled values in Section 3 of `REPORT_ENGINEERING.md` and its "against the intact neighbouring panels" counts use this intact reference. They are a sensitivity check (Table S5), not the paper's values.

`REPORT_ENGINEERING.md` and `PROTOCOL_ENGINEERING.md` are kept as written on 1 October 2026. The protocol was fixed before any generator value was computed. They use the older word "panel" for a sampling window.

## The engineering inputs

Six inputs are tested in the main text (Table 3 and Section 3.5):

* equivalent modulus E/E0 along the bench;
* E/E0 down the face;
* deformability anisotropy;
* largest-cluster share;
* maximum persistence k_max of trace-direction cluster C1;
* k_max of cluster C2.

Three more are reported but not counted:

* the percolation parameter p;
* mean persistence;
* the spanning cluster.

The paper gives the reason once, in Section 2.5.5:

* p and the two moduli restate one quantity (p = 4 tr(alpha));
* the spanning score rewards a generator that rarely spans;
* mean persistence restates the cluster's P21.

The protocol tests all ten. `engineering_tests.csv` and `engineering_counts.csv` hold all ten, and the paper's six-input counts are the rows of those six inputs.

T-end share and crossing share appear in Table 3 too. They are not new inputs: they are the values behind two existing error scores of the release (T-end share error and node types).

## Files

| File | What |
|---|---|
| `PROTOCOL_ENGINEERING.md` | measures, references and tests, fixed before computing |
| `REPORT_ENGINEERING.md` | results in plain words (intact-reference pooled values: sensitivity, see above) |
| `code/eng_metrics.py`, `code/eng_common.py` | the measures; repository paths (`eng_common.py` is the only file changed for the repository: paths only) |
| `code/test_eng_metrics.py` | unit checks of the measures |
| `code/step1a_percolation_check.py` | p of the 50 mapped windows (no window reaches the 2D threshold of about 5.6) |
| `code/run_engineering.py` | values and scores of every realisation, held-out window and reference window |
| `code/analyse_engineering.py` | window values, tests, verdict, bootstrap, reference comparisons, Spearman with P21, combined parameter table |
| `code/fig_engineering.py` | the protocol's quick-look figure (box plots); the paper's Fig. 9 is drawn by `paper_figures/fig_engineering.py` |
| `code/compare_with_stored.py` | compares a rerun with the stored tables |
| `tables/engineering_network_values.csv`, `engineering_network_scores.csv`, `engineering_network_props.csv` | one row per realisation (and per held-out and reference window) |
| `tables/engineering_panel_values.csv`, `engineering_panel_scores.csv` | one row per window case and method |
| `tables/engineering_tests.csv`, `engineering_counts.csv`, `engineering_verdict.csv`, `engineering_bootstrap.csv` | EVAE against ADFNE and KDE (paired Wilcoxon, Holm over the two baselines) |
| `tables/engineering_reference.csv` | EVAE against both references |
| `tables/engineering_spearman_P21.csv` | correlation of each input with P21 over the 120 window cases |
| `tables/Table_parameters_combined*.csv/.md/.xlsx` | the combined parameter table, by test and pooled; the column `Reference (fracture-removed)` is the paper's reference |
| `tables/engineering_pooled_traces.csv` | all traces pooled, for the length rows of the combined table |
| `tables/step1a_percolation_mapped_panels.csv` | p of the mapped windows |

No table was left out: all are under 20 MB.

## Rerun (about 30 seconds, no GPU)

```bash
cd engineering/code
python test_eng_metrics.py
python step1a_percolation_check.py
python run_engineering.py
python analyse_engineering.py
python fig_engineering.py
python compare_with_stored.py      # expected: 15 tables compared, 0 different
```

A rerun writes to `work/engineering/` (ignored by git), never over `engineering/tables/`. This sequence was checked on 2 October 2026 in a copy of the repository: all 15 tables were reproduced identically.

## Limitations (as in the paper)

* These are geometry-only, face-parallel 2D proxies for the inputs of equivalent-continuum and persistence-based models, not rock-mass properties.
* Traces are treated as open, non-interacting cracks. This is a first-order proxy, used only to compare generators.
* No strength was assigned. Joint and rock-bridge shear properties are not available for this wall, and a trace map does not provide them.
* No permeability was computed. Aperture would need field measurement or hydraulic tests, and the mapped windows lie below the 2D percolation threshold.
