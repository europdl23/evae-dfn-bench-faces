# Protocol: engineering demonstration (equivalent deformability, connectivity and persistence)

Written 1 October 2026, BEFORE any generator (EVAE, ADFNE, KDE) value of these measures was computed. The only computation made before this protocol is Step 1a, the percolation parameter of the 50 mapped panels (no generator involved): median p = 2.35, maximum 4.53, no panel at or above the 2D threshold of about 5.6 (`tables/step1a_percolation_mapped_panels.csv`).

Purpose: answer Reviewer 2, Comments #4 and #12(c), with one engineering demonstration that the 2D trace data support. Question: *if an engineer fed each generated network into standard upscaling relations, would they get the same engineering input as from the mapped panel?* This is a comparison between generators on identical inputs, not a statement of rock-mass properties of the site.

Data: the geobg release, read only (`SECTION1_EVAE_ADFNE_KDE_RELEASE_2026-10-01`): held-out panels from the box library and the fold splits; 24 saved realisations per held-out panel for EVAE, ADFNE and KDE (`networks/S*/<method>`); the trace-direction cluster model of each fold. No retraining, no regeneration.

## 1. Measures (per network; panel width W = 20 m, height H = 20 y_max m, area A = W H; traces in metres; x along the bench, y down the face)

**Deformability: 2D crack-density tensor (Kachanov 1992; Oda 1984 for the fabric form)**
- alpha = (1/A) sum_k a_k^2 n_k n_k^T, with a_k = l_k / 2 the half-length and n_k the unit normal of trace k in the face plane.
- D1 **E_along / E0** = 1 / (1 + 2 pi alpha_xx): equivalent in-plane Young's modulus along the bench relative to intact rock (open, non-interacting cracks; plane stress).
- D2 **E_down / E0** = 1 / (1 + 2 pi alpha_yy): the same, down the face.
- D3 **Anisotropy index** = (lambda_1 - lambda_2) / (lambda_1 + lambda_2) of alpha (0 isotropic, 1 all traces parallel); undefined for an empty network.
- Descriptive only (in the table, not tested): softest loading direction (eigenvector of lambda_1, axial angle in the face).

**Connectivity**
- C1 **Percolation parameter** p = (1/A) sum_k l_k^2 (Bour and Davy 1997), against the 2D threshold of about 5.6 (Robinson 1984). Error: relative, |p_g - p_h| / p_h.
- C2 **Spanning cluster**: 1 if any connected cluster touches both opposite sides of the panel (left and right, or top and bottom; a trace end within 0.1 m of a side counts as touching). Two traces are connected if they cross or an end lies within 0.3 m of the other (the tolerances of the release topology code). Panel value of a generator = share of its 24 realisations that span. Error = |share - held-out value| (mean over realisations, since the score is binary).
- C3 **Largest-cluster share**: total trace length of the largest connected cluster / total trace length (0-1); undefined for an empty network.

**Persistence and rock bridges (Jennings 1970; Einstein et al. 1983), for clusters C1 (~125 deg) and C2 (~56 deg)**
- Lines parallel to the cluster's centre direction in that fold (the same lines for every method), perpendicular spacing 0.5 m, covering the panel; only line segments of at least 10 m inside the panel are used.
- For each line: covered length = length of the union of the projections onto the line of the parts of the cluster's traces that lie within 0.25 m (perpendicular) of the line; persistence k = covered length / line length.
- P1, P2 **Mean persistence** of C1 and of C2 (mean k over the lines).
- P3, P4 **Maximum persistence** of C1 and of C2 (k of the most persistent line: the weakest potential plane of that cluster in the panel); the rock-bridge fraction along it is 1 - k_max.
- Trace membership by the fold's cluster model (as everywhere in the paper).

**Topology rows for the combined parameter table** (already defined in the release, `topology.py`): T-end share N_Y / (N_I + N_Y) and crossing share N_X / (N_I + N_Y + N_X).

## 2. Values and references
- Panel value: held-out = its own value; generator = median over its 24 realisations where defined (spanning: share of realisations).
- Natural-variability reference: the 8 neighbouring panels of each held-out panel, INTACT (all mapped traces), panel value = median over the 8 (spanning: share). Reason: the release reference removes every held-out fracture from the neighbours, which biases intensity and connectivity low, exactly the quantities measured here. Caveat to state: intact neighbours share a few fractures that cross into the held-out panel, so this reference is slightly optimistic. The fracture-removed version is computed as a sensitivity check.
- Test value: median over the held-out panels of a test (20, 50 and 50 panels); pooled values over the 120 panel cases for the figure.

## 3. Tests (identical to the release rules)
- Score of a realisation = absolute error of the measure against its held-out panel (relative for p). Panel score = median over the 24 realisations where defined (n.d. rule); spanning: mean. As in the release (`statistical_tests.score`), an empty realisation is undefined (n.d.) for every score and is left out of the panel score; a panel with no defined realisation is n.d. for that score and is left out of the test.
- EVAE vs ADFNE and vs KDE: paired two-sided Wilcoxon over held-out panels (zero_method = zsplit), Holm over the 2 baselines, alpha 0.05; better / worse by the sign of the median paired difference (release `statistical_tests.paired`).
- "Overall better": lowest median and clear one-sided win over both others (Holm) in at least 2 of the 3 tests (release `three_way`).
- EVAE vs natural-variability reference: paired two-sided Wilcoxon, alpha 0.05 (release `checks.compare`).
- Bootstrap 95% CI of the median paired difference EVAE - baseline (2,000 resamples of panels, seed 20261001). Benjamini-Hochberg over all EVAE-vs-baseline comparisons of these 10 tested measures (10 x 3 tests x 2 baselines = 60) as a sensitivity check.
- Tested measures (10): D1, D2, D3, C1, C2, C3, P1, P2, P3, P4. Counts reported as better / no difference / worse.

## 4. Reporting
- All 10 measures, all three tests, gap-filling first, whatever the outcome; no measure dropped or added after seeing results. The outcome is genuinely uncertain (the EVAE has slightly fewer traces, so it may underestimate crack density and persistence).
- Report the Spearman correlation of p and of the crack density with P21 over panels, to show what is and is not a restatement of P21.
- Equivalent permeability is NOT computed: the mapped networks lie below the percolation threshold (Step 1a), and with a constant aperture its magnitude would restate P21.

## 5. Outputs
- `tables/engineering_panel_values.csv`, `engineering_panel_scores.csv`, `engineering_tests.csv`, `engineering_counts.csv`, `engineering_bootstrap.csv`, `engineering_reference.csv`.
- `tables/Table_parameters_combined.csv/.xlsx/.md`: one parameter table for Results, held-out | reference | EVAE | ADFNE | KDE, the 15 release parameters plus the topology rows plus the engineering rows, closest value to held-out marked.
- `figures/Fig_E1_engineering` (14.65 cm, Times New Roman, release layout check): box plots of the per-panel values pooled over the 120 panel cases.
- `REPORT_ENGINEERING.md` and `HANDOFF_FOR_MANUSCRIPT_AGENT.md`.

## 6. Limitations to state with the result
Geometry-only, face-parallel 2D proxies for the inputs of equivalent-continuum and persistence-based strength models, not rock-mass properties; traces treated as open, non-interacting cracks (an upper bound on softening, beyond the strict validity of the non-interacting estimate at the crack densities here, used only to compare generators); aperture, stiffness and strength unknown and equal for all generators, so only relative values are compared; a 20 m panel is below a representative elementary volume; persistence is measured along the face, not over failure planes, whose dip is unknown; the networks lie below the 2D percolation threshold, so no equivalent permeability; block theory, DEM/SRM and 3D upscaling are not attempted (they need fracture planes and termination types).
