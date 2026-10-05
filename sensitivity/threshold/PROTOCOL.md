# Existence-threshold sensitivity test: protocol

Written 2026-10-05, before any realisation was generated or scored. Purpose: answer Reviewer 2 #9 of IJRMMS-D-26-00250
(inference settings of the EVAE). Results are reported as they come out.

## Source
- Release (read only): the repository root (release of 1 Oct 2026).
- code\ and work\ copied from nmax_sensitivity_2026-10-05 (itself a copy of the release code; its only change, EVAE_NMAX,
  defaults to 120 = release and is left at 120 here).
- Only change in this test: src\study\study.py generate(), the existence threshold `sigmoid(exist) >= 0.5` reads the
  environment variable EVAE_THR (default 0.5 = release). The fallback rule is unchanged: if fewer than 2 slots pass,
  the 10 slots with the highest existence logits are kept.
- No retraining. The released S1 EVAE checkpoints (models\evae\S1_f{0..3}_s{1337,20260903,7}, 12 models) are loaded
  directly from the release.

## Variants
Threshold 0.4, 0.5 (paper), 0.6. Generation as scripts\generate_networks.py evae on CUDA (as the release; see
nmax_sensitivity PROTOCOL amendment): posterior of the 8 surrounding windows, 8 draws x 3 run seeds = 24 realisations
per held-out window, same noise seeds for every threshold (so the same latent draws; only the kept slots differ).
Check: threshold 0.5 must reproduce the released S1 EVAE realisation files byte for byte (480 files).
Also recorded: number of slots passing the threshold, whether the fallback fired, traces per realisation after clipping.

## Scoring
- Release scorer (scripts\statistical_tests.py score(), n.d. rule) against the held-out window, fold cluster model.
- 38 error scores, window value = median over 24 realisations; paired two-sided Wilcoxon (zsplit, as release) over the
  20 held-out windows: 0.4 vs 0.5 and 0.6 vs 0.5, Holm over the two comparisons, alpha 0.05; counts better / no
  significant difference / worse.
- 15 network parameters (make_figures.py props()/table_value()), held-out vs 0.4 / 0.5 / 0.6, plus mean traces per
  realisation.

## Outputs
Table_threshold.md/.csv, Table_threshold_tests.csv, REPORT.md, scripts and logs here.
