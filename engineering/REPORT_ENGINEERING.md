# Engineering demonstration: results (1 October 2026)

Answers Reviewer 2, Comments #4 and #12(c): do the generated networks give the same **engineering inputs** as the mapped rock? Method and tests were fixed in `PROTOCOL_ENGINEERING.md` before any generator value was computed. EVAE = the paper's EVAE (geobg release). All numbers below come from `tables/`; nothing was typed by hand.

## 1. Answer in four lines

- **Deformability and connectivity:** the EVAE gives equivalent inputs closer to the mapped panels than ADFNE and KDE. It wins the "overall better" verdict on 3 of the 10 measures (modulus along the bench, modulus down the face, percolation parameter); no baseline wins any.
- **Persistence and rock bridges:** no generator is consistently closer. All three under-estimate the maximum persistence, so the rock bridges come out too large.
- **All three generators err the same way:** a slightly stiffer, less persistent rock mass than mapped. The EVAE errs least on deformability and connectivity.
- **Weakness to report:** a cluster that spans the whole panel occurs in 28% of the mapped panels but in only 6% of EVAE realisations (10-12% for the baselines). The cause is the 20 m decoder limit: in the rock, one long trace often crosses the whole panel.

## 2. Step 1a (before the protocol): mapped panels only
- Percolation parameter p = Σl²/A of the 50 mapped panels: median 2.35, maximum 4.53.
- No panel reaches the 2D threshold of about 5.6.
- Therefore equivalent permeability was not computed (`tables/step1a_percolation_mapped_panels.csv`).

## 3. Values (pooled over the 120 held-out panel cases; per panel, generator = median of 24 realisations, reference = median of the 8 intact neighbouring panels)

| Measure | Held-out | Reference | EVAE | ADFNE | KDE |
|---|---|---|---|---|---|
| Percolation parameter p (threshold about 5.6) | 2.47 | 2.52 | **1.96** | 1.63 | 1.63 |
| Equivalent modulus along the bench, E/E0 | 0.29 | 0.28 | **0.35** | 0.39 | 0.40 |
| Equivalent modulus down the face, E/E0 | 0.41 | 0.41 | **0.46** | 0.51 | 0.51 |
| Deformability anisotropy index | 0.50 | 0.50 | **0.45** | 0.38 | 0.36 |
| Softest loading direction, from the bench axis (descriptive) | -1° | -1° | 12° | -5° | **-4°** |
| Panels with a spanning cluster (share) | 0.28 | 0.31 | 0.06 | **0.12** | 0.10 |
| Largest connected cluster (share of trace length) | 0.28 | 0.26 | **0.40** | 0.43 | 0.41 |
| Mean persistence, C1 | 0.044 | 0.051 | **0.044** | 0.037 | 0.039 |
| Mean persistence, C2 | 0.036 | 0.031 | 0.024 | **0.031** | **0.031** |
| Maximum persistence, C1 | 0.35 | 0.36 | 0.31 | 0.30 | **0.32** |
| Maximum persistence, C2 | 0.31 | 0.28 | 0.24 | 0.26 | **0.29** |
| T-end share (ends stopping on another trace) | 0.09 | 0.08 | **0.09** | 0.12 | 0.12 |
| Crossing share of nodes | 0.07 | 0.07 | **0.12** | 0.17 | 0.19 |

Bold = the generator closest to the held-out value. Per-test values (gap-filling first) are in `tables/Table_parameters_combined.md` / `.csv`.

## 4. Tests (paired Wilcoxon over held-out panels, Holm over the two baselines, alpha 0.05; release rules)

| EVAE against | Deformability (9) | Connectivity (9) | Persistence (12) | All (30) | BH over 60 | Bootstrap CI |
|---|---|---|---|---|---|---|
| ADFNE: better / no difference / worse | 6 / 3 / 0 | 6 / 3 / 0 | 2 / 10 / 0 | **14 / 16 / 0** | 13 / 17 / 0 | 13 / 17 / 0 |
| KDE: better / no difference / worse | 7 / 2 / 0 | 5 / 4 / 0 | 0 / 11 / 1 | **12 / 17 / 1** | 10 / 19 / 1 | 11 / 19 / 0 |

- **Modulus along the bench:** better than both baselines in all three tests.
- **Percolation parameter:** better than both in all three tests.
- **Modulus down the face:** better than both in the new-bench and new-stretch tests; no difference in the gap-filling test.
- **The one "worse":** mean persistence of C2 in the new-stretch test, against KDE.
- **Against the intact neighbouring panels** (the natural variability of the rock): 4 better / 24 no difference / 2 worse. The two worse are the modulus along the bench (gap-filling) and the largest-cluster share (new-bench). With fracture-removed neighbours: 5 / 23 / 2.
- **Spanning score:** the EVAE is better in the new-bench test even though it spans least. Most panels (72%) do not span, and the score rewards not spanning there.
- **Not restatements of P21:** Spearman correlation with P21 over the 120 held-out panels is 0.72 for p, −0.65 for E/E0 along the bench, −0.47 down the face, −0.28 for anisotropy, 0.47 and 0.25 for maximum persistence of C1 and C2, 0.16 for spanning and 0.03 for the largest-cluster share (`tables/engineering_spearman_P21.csv`).

## 5. Engineering reading
- **Equivalent deformability:** passed through the crack-tensor relation, the mapped panels soften the rock to about 0.29 E0 along the bench and 0.41 E0 down the face. The EVAE gives 0.35 and 0.46 (+21% and +13%); ADFNE and KDE give 0.39-0.40 and 0.51 (+36-39% and +23%).
  - All generators describe a stiffer rock mass than mapped, because their traces are fewer or shorter. The EVAE is closest, because its trace lengths are closest.
  - The absolute values come from the non-interacting open-crack estimate (an upper bound on softening). Only the comparison between generators is meaningful.
- **Connectivity:** every network is below the 2D percolation threshold, so the fractures form isolated clusters, not a connected network.
  - All generators under-estimate p: the EVAE by 21%, the baselines by 34%.
  - None reproduces the spanning traces of the rock.
- **Persistence and rock bridges (Jennings):** the most persistent line of C1 is 35% fracture in the mapped panels and 30-32% in all generators.
  - The rock-bridge fraction is therefore slightly over-estimated by all three, which would make a step-path strength slightly unconservative.
  - No generator is consistently better.

## 6. Limitations (to state with the result)
- **Proxies, not properties.** These are geometry-only, face-parallel 2D proxies for the inputs of equivalent-continuum and persistence-based strength models, not rock-mass properties.
- **Open-crack assumption.** Traces are treated as open, non-interacting cracks: an upper bound on softening, used here only to compare generators.
- **Relative comparison only.** Aperture, stiffness and strength are unknown and equal for all generators, so only relative values are compared.
- **Scale.** A 20 m panel is below a representative elementary volume.
- **Persistence along the face.** It is measured along the face, not over failure planes, whose dip is unknown.
- **No permeability.** The networks lie below the 2D percolation threshold.
- **Reused test panels.** The test panels were used in earlier rounds of the study.

## 7. Files
- `PROTOCOL_ENGINEERING.md`: written before computing.
- `code/`:
  - `eng_common.py`, `eng_metrics.py`: the measures.
  - `test_eng_metrics.py`: unit checks, all passed.
  - `step1a_percolation_check.py`.
  - `run_engineering.py`: about 10 s on 12 processes.
  - `analyse_engineering.py`: tests and tables. It also checks that the release's 15 parameters are reproduced value for value; all 180 match.
  - `fig_engineering.py`.
- `tables/`:
  - per network, per panel, tests, verdict, counts, bootstrap, reference, Spearman;
  - `Table_parameters_combined.*`: by test, pooled, and xlsx with both sheets.
- `figures/Fig_E1_engineering.png/.pdf`: 14.65 cm, passed the release layout check.
- Rerun: `cd code; python step1a_percolation_check.py; python run_engineering.py; python analyse_engineering.py; python fig_engineering.py`.
