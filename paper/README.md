# Paper versions: Results and Discussion figures, tables and checks

Everything here is made from the rest of the repository by one command:

```bash
python paper/code/run_all.py     # from the repository root, about 1 minute
```

Terms follow the paper:
* held-out, neighbouring and training panel;
* realisation;
* gap-filling, new-bench and new-stretch test;
* geology-informed constraints (terms);
* trace-direction cluster (C1-C4, unclustered).

All figures:
* 14.65 cm wide, Times New Roman (12 pt; 10 pt for ticks and values);
* PNG at 600 dpi and PDF;
* passed the layout check: no overlapping text, nothing outside, no text on data, other panels or scatter points.

**Undefined scores are n.d.** A realisation can be empty, or have fewer than 2 members of a cluster that the held-out panel has.
* Such scores are excluded from panel medians, tests and confidence intervals.
* No placeholder values remain anywhere.
* Old vs new counts: `tables/changes_nd.csv`, and the sheet "Changes after n.d. rule" in `checks.xlsx`. The first-version check tables are in `tables/before_nd_rule/`.

## Results

| File | Shows |
|---|---|
| `EXAMPLE_PANELS.md`, `example_panels.json` | the example-panel rule and the 4 chosen panels, with their generator seeds |
| `figures/Fig_R1_examples_no_photo` | panel map, then the 4 example panels: held-out traces next to the EVAE realisation (run seed 1337, draw 0), coloured by trace-direction cluster. No version of this figure uses a photograph. |
| `figures/Fig_R2_geometry` | per test: rose over 0-360° and length histogram over 0-30 m (EVAE filled, held-out outline, 20 m decoder limit) |
| `figures/Fig_R4_panel_by_panel` | held-out vs EVAE per panel for P21, intersections, connections per trace and spacing; Spearman ρ per test |
| `tables/Table_R1.xlsx` (`.csv`) | 15 parameters; held-out, natural-variability reference and EVAE for each test |

## Discussion

| File | Shows |
|---|---|
| `figures/Fig_D1_comparison` | the 4 example panels: held-out, EVAE, ADFNE, KDE (run seed 1337, draw 0 for every method) |
| `figures/Fig_9_ablation_counts` | better / no difference / worse by group: (a) full EVAE vs EVAE without geology-informed terms; (b) full EVAE vs single-latent EVAE |
| `figures/Fig_11_boxplots` | 6 parameters, held-out / EVAE / ADFNE / KDE, per-panel values; held-out median dashed; medians and % difference under the boxes |
| `figures/Fig_11_alt_length_histograms` | trace-length histograms for held-out / EVAE / ADFNE / KDE (alternative to the box plots) |
| `tables/Table_D_parameters.xlsx` (`.csv`) | 15 parameters, held-out / EVAE / ADFNE / KDE, all 3 tests |
| `tables/Table_ablation_paper.xlsx` (`.csv`) | 15 parameters for the 4 ablation variants and held-out, gap-filling test first; plus the comparison counts |
| `tables/Table_S_scores.xlsx` (`.csv`) | supplementary: 38 scores × 3 tests, EVAE vs ADFNE and vs KDE: medians, Holm result, BH q, bootstrap CI |
| `SCORE_DEFINITIONS.md` | definition, group and unit of the 15 parameters and the 38 scores (for Methods Table 2) |
| `tables/checks.xlsx` | every check, as counts and per score |

## Checks (38 error scores, all three tests, n.d. rule)

| Check | Gap-filling | New-bench | New-stretch |
|---|---|---|---|
| EVAE vs natural-variability reference (better / no difference / worse) | 1 / 34 / 3 | 6 / 29 / 3 | 3 / 31 / 4 |
| Neighbouring vs random context (better / no difference / worse) | 5 / 33 / 0 | 6 / 31 / 1 | 8 / 30 / 0 |
| Source-panel distance, realisation vs held-out (m, medians; p) | 4.96 vs 5.09; p = 0.064 | 4.94 vs 5.00; p = 0.081 | 4.86 vs 5.13; p = 0.011 |
| Near-copies of the source neighbouring panel (realisation; held-out) | 0; 0 | 0; 0 | 0; 0 |
| Near-copy share with the nearest training panel (realisation vs held-out, medians; p) | 0.03 vs 0.06; p = 0.34 | 0 vs 0.05; p = 0.006 | 0 vs 0; p = 0.19 |
| Spearman ρ, P21 / intersections / connections / spacing | 0.67 / 0.46 / 0.20 / 0.34 | 0.11 / 0.10 / −0.15 / −0.02 | −0.12 / −0.19 / −0.16 / 0.11 |

**Source-panel distance** is the mean distance from each trace to the closest trace of the source neighbouring panel. The p-value is from a paired Wilcoxon test over panels. The realisations lie slightly closer to their source panel than the held-out panels do; the difference is significant only in the new-stretch test.

**EVAE vs ADFNE and KDE**
* **Holm over the 2 baselines,** better / no difference / worse of 114: vs ADFNE 24 / 84 / 6; vs KDE 21 / 88 / 5.
* **Three-way verdict:** EVAE 7, ADFNE 0, KDE 0, no method 31.
* **Per-seed verdict:** EVAE wins 6, 3 and 4 scores with run seeds 1337, 20260903 and 7; KDE wins 1, 0 and 1.
* **Benjamini-Hochberg** over 228 comparisons: vs ADFNE 19 / 92 / 3; vs KDE 16 / 95 / 3.
* **Gap-filling baselines refitted on the 8 neighbouring panels** (of 38): vs ADFNE 7 / 27 / 4; vs KDE 7 / 26 / 5.
* **Bootstrap 95% CIs** (better / includes 0 / worse): vs ADFNE 25 / 81 / 8; vs KDE 20 / 83 / 11.

**Ablation** (Holm over the 4 comparisons, of 114)
* Full EVAE vs EVAE without geology-informed terms: 25 / 87 / 2.
* Full EVAE vs single-latent EVAE: 2 / 106 / 6.

## Caveats

* **The n.d. rule removes the penalty that undefined scores used to carry.** Previously an empty realisation, or a missing cluster, scored as the worst value. This mainly lowers the counts of the cluster scores, for the baselines and for the variants without geology-informed terms.
* **The natural-variability reference is biased low on counts.** Every held-out fracture is removed from the neighbouring panels, so the reference has fewer traces and intersections than intact panels. For example, the gap-filling reference has 0.26 intersections per 100 m² against 0.50 held-out.
* **Panel-to-panel agreement is only clear in the gap-filling test.**
* **Reused test panels.** The test panels were used in earlier rounds of the study.
