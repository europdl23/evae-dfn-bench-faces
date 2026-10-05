# Loss-weight sensitivity test: protocol

Written 2026-10-05, before any model was trained or scored. Purpose: answer Reviewer 2 #9 of IJRMMS-D-26-00250
("were the loss weights hand-tuned; are the results robust to them?"). Results are reported as they come out.

## Source
- Release (read only): the repository root (release of 1 Oct 2026).
- code\ = the code of the finished N_max test (nmax_sensitivity_2026-10-05\code, itself the release with the slot
  capacity read from EVAE_NMAX, default 120; that code retrained the 12 released S1 checkpoints byte-identically).
- Changes, marked "WEIGHT SENSITIVITY 2026-10-05":
  - src\model\training.py: the literal 0.005 on the geology-informed (physics) loss, w_int = 0.3 and w_sp = 0.2 are
    read from EVW_PHYS, EVW_INT, EVW_SP (defaults = release values). Effective weights are printed at the start of
    training ("EFFECTIVE WEIGHTS: ...") and stored in run_status.json.
  - scripts\train_evae.py: optional overrides WS_EVGEO_W, WS_EVBG_W, WS_EVFIX_WQ, WS_EVW_PHYS, WS_EVW_INT, WS_EVW_SP,
    applied after study.py is imported (study.py forces EVFIX_WQ = 1.0 on import).
- Unchanged in every variant: N_max 120, LAMBDA_FREE 0.22, EVFIX_WLEN 0.005 (length-ceiling penalty), KL schedule,
  1.25 factors inside the physics loss, optimiser, schedule, 100 epochs max, patience 20, CPU 4 threads,
  deterministic algorithms, run-seed seeding.
- Check: one baseline model (all defaults) is retrained with this code and its checkpoint SHA-256 compared with the
  released one, to show the edits are no-ops at the release values.

## Weight mapping (term in the paper -> code)
| Group | Term | Code | Release |
|---|---|---|---|
| A | geology-informed loss | w_phys (EVW_PHYS) x physics_loss | 0.005 |
| B | trace-direction distribution loss + cluster-share loss | EVGEO_W, EVBG_W | 1.0, 1.0 |
| C | intersection term + spacing term | w_int (EVW_INT), w_sp (EVW_SP) | 0.3, 0.2 |
| D | log-length term (sorted log-length W1) | EVFIX_WQ | 1.0 |

## Variants (one group halved or doubled, everything else unchanged)
1 A_half 0.0025; 2 A_double 0.01; 3 B_half 0.5/0.5; 4 B_double 2.0/2.0; 5 C_half 0.15/0.1; 6 C_double 0.6/0.4;
7 D_half 0.5; 8 D_double 2.0.

## Fixed design
- Gap-filling test (S1), 4 folds x 3 run seeds (1337, 20260903, 7) = 12 models per variant, 96 new models.
- Baseline ("paper model") = released S1 EVAE checkpoints and their released realisations
  (release networks\S1\EVAE), shown in the N_max test to equal a retrain with this code.
- Generation as the release (scripts\generate_networks.py evae via study.generate, CUDA as the release): posterior
  of the 8 neighbouring windows, 8 draws x 3 run seeds = 24 realisations per held-out window, same generator seeds
  for every variant.
- Models trained in parallel (6 at a time), jobs interleaved across variants.

## Scoring
- Release scorer (scripts\statistical_tests.py score(), n.d. rule) against the held-out window, fold cluster model.
- 38 error scores: window value = median over its 24 realisations. Paired two-sided Wilcoxon (zsplit, as release)
  over the 20 held-out windows, each variant vs the paper model; Holm over the 8 variants per score; alpha 0.05.
  Counts better / not significantly different / worse per variant, per score group and in total; list of scores
  that change.
- 15 network parameters (make_figures.props / table_value, as the paper's Table D) for held-out, paper model and
  each variant.

## Outputs
Table_weights.csv/.md, Table_weights_tests.csv, outputs\tests_per_score.csv, REPORT.md, scripts, logs.
