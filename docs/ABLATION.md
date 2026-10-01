# Ablation: single vs dual latent, without vs with the geology guide

## Design (2 x 2)

| Arm | Latent | Geology guide | Models |
|---|---|---|---|
| Single-latent EVAE without geology-informed terms | single | off | `models/ablation/single_noguide/` (45) |
| Single-latent EVAE | single | on | `models/ablation/single_guide/` (45, trained 1 Oct 2026) |
| EVAE without geology-informed terms | dual | off | `models/ablation/dual_noguide/` (45) |
| Full EVAE (dual latent, with the terms) | dual | on | `models/evae/` (45) |

* **Geology guide.** Three terms, all switched off together for "no guide":
  * the released geology-informed term (weight 0.005);
  * the generated-direction term (`EVGEO_W` 1.0);
  * the orientation-cluster share term (`EVBG_W` 1.0).
* **Single latent.** The Paper 1 `SingleLatentVAE`: one joint encoder giving one 56-d code, which every decoder head reads. The dual latent keeps a 24-d spatial code and a 32-d geometry code apart.
* **Everything else is identical:** data, folds, fitting and validation boxes, training settings, run seeds and the generator.
* **Code.** `src/model_ablation/training.py` is the EVAE code plus the single-latent switch (`EVFIX_SINGLE_LATENT`) and the geology-weight knob (`EVFIX_WGEO`). At the EVAE's settings it is the EVAE code.

## Seeds

* **Run seeds and draws.** Every arm is trained with run seeds 1337, 20260903 and 7, and generates 8 draws per seed, as the EVAE.
* **Generator seeds.** Every arm uses the EVAE's own generator seeds, `crc32("EVAE|scheme|geobg|fold|box|run seed|draw")`, so the four columns share the same seeds draw for draw (`seeds/ablation_network_seeds.csv`).

## Checks (1 Oct 2026)

| Check | Result |
|---|---|
| Ablation code at the EVAE's settings retrains the EVAE (S1 fold 2, seed 1337) | checkpoint identical |
| Ablation code retrains the single-latent no-guide model (S1 fold 0, seed 1337) | checkpoint identical to the study's |
| Ablation code retrains the dual-latent no-guide model (S1 fold 0, seed 1337) | checkpoint identical to the study's |
| Ablation generator on the EVAE models, fold S1-2 | 144 of 144 networks identical to `networks/S1/EVAE` |
| All 45 new models (single latent, with guide) | all stable, no latent collapse; the top-10 fallback never fired |

The two no-guide arms were trained in the study. They do not depend on the guide version, which the checks confirm. All three arms were regenerated here with the EVAE's seeds.

## Result

Table: `figures/Table_ablation.png` / `.pdf`; numbers in `tables/ablation_tables.xlsx`; paper version `paper/tables/Table_ablation_paper.xlsx` and `paper/figures/Fig_9_ablation_counts`.

Tests:
* paired two-sided Wilcoxon over held-out panels;
* Holm over the 4 comparisons;
* undefined scores (n.d.) left out.

Counts are better / no difference / worse out of 114 (38 scores x 3 tests). The last column is the first version, which counted undefined scores as the worst value.

| Comparison | Better | No difference | Worse | First version |
|---|---|---|---|---|
| Full EVAE vs EVAE without geology-informed terms | 25 | 87 | 2 | 35 / 75 / 4 |
| Geology-informed terms, in the single latent | 14 | 95 | 5 | 35 / 69 / 10 |
| Full EVAE vs single-latent EVAE (both with terms) | 2 | 106 | 6 | 5 / 102 / 7 |
| Dual vs single latent, both without terms | 5 | 93 | 16 | 10 / 81 / 23 |

* **The geology-informed terms are what matter.**
  * **Trace directions.** Without the terms, trace-direction cluster 1 (~125°) is badly under-produced: 18-20 % of traces (dual) or 22-23 % (single), against 34-36 % held-out. With the terms it is 34-36 % in every test.
  * **Never worse on directions.** In the dual latent the terms never make the trace directions worse: 18 better and 0 worse of 57 direction and cluster comparisons.
  * **Long traces.** The terms also lengthen the long traces. The 90th percentile rises from 10.4-11.1 m to 11.4-12.1 m (held-out 12.4-13.9 m).
* **Dual vs single latent makes no consistent difference once the terms are on.** No score differs in the same direction in at least 2 of the 3 tests.
  * **Where the dual latent is closer:** long traces (all 3 tests), cluster spreads and intersections (new-bench and new-stretch tests).
  * **Where the single latent is closer:** P21 (all 3 tests) and the median length (gap-filling and new-stretch tests).
* **Without the terms, the dual latent is worse than the single latent** on cluster 1 (share and count) and on the length distribution.

**Reading for the paper.** The accuracy comes from the geology-informed terms. The dual latent does not improve accuracy over a single latent when the terms are on; present it as a design choice, not as a source of accuracy.
