# N_max (slot capacity) sensitivity test: protocol

Written 2026-10-05, before any model was trained or scored. Purpose: answer Reviewer 2 #6 of IJRMMS-D-26-00250
("why N_max = 120, why not 500"). Results are reported as they come out.

## Source
- Release (read only): the repository root (release of 1 Oct 2026)
- Copied to code\ here (src, scripts, data, seeds, paper\code, models\evae\S1_* for the reproduction check).
- Only change: the slot capacity is read from the environment variable EVAE_NMAX (default 120 = release).
  - src\model\utils.py: CONFIG data.NMAX and model.max_lines = EVAE_NMAX. This sets the input padding and validity
    mask of the dataset (EnhancedDataset: slot arrays P[Nmax,4], mask M[Nmax]).
  - src\model\training.py: DualLatentVAE_Updated(max_lines=None) -> NMAX. This sets encoder input sizes (2*Nmax),
    spatial decoder (2*Nmax), length decoder (Nmax), the three angle heads (3*Nmax), existence head (Nmax).
    The Hungarian matching uses all Nmax predicted slots against the valid targets, so it follows automatically;
    posterior encoding and generation (study.py) pad to model.max_lines and read model.max_lines.
  - scripts\train_evae.py: --nmax argument, asserts on every layer size, dataset Nmax and max window count <= Nmax.
  - The checkpoint loader (generators.load_evae) builds the model with the default, i.e. EVAE_NMAX; the generation
    script sets EVAE_NMAX and asserts model.max_lines.
- Densest window in the library: 26 traces (W00_C1). N_max = 50 exceeds it, so no window is truncated in any variant.

## Variants
N_max = 50, 120, 200. 120 is the paper's model and is retrained with the same copied code, so all three are
like-for-like. Its checkpoints are compared with the released ones (SHA-256) and its scores with the release
scores. If the retrained 120 checkpoints are identical to the released ones, the release checkpoints are
equivalent to the 120 arm.

## Fixed design (identical for every variant)
- Gap-filling test (S1), 4 folds x 3 run seeds (1337, 20260903, 7) = 12 models per variant, 36 in all.
- Training exactly as scripts\train_evae.py: same losses and weights (EVGEO_W = EVBG_W = 1.0, LAMBDA_FREE 0.22,
  EVFIX_WQ 1.0, EVFIX_WLEN 0.005), schedule, 100 epochs max, early stopping patience 20, run-seed seeding,
  CPU 4 threads, deterministic algorithms.
- Generation exactly as scripts\generate_networks.py evae: posterior of the 8 neighbouring windows, one window per
  draw, 8 draws x 3 run seeds = 24 realisations per held-out window, same generator seeds
  (crc32 "EVAE|S1|geobg|fold|box|run_seed|draw") for every variant.
- Models are trained in parallel (5 at a time, jobs interleaved across variants so load is the same for all).

## Scoring
- Release scorer (scripts\statistical_tests.py score(), n.d. rule: undefined values left out of the window medians
  and the tests) against the held-out window, fold cluster model.
- 38 error scores: window value = median over its 24 realisations. Paired two-sided Wilcoxon (zero_method zsplit,
  as release) over the 20 held-out windows: N_max 50 vs 120 and 200 vs 120, Holm over the two comparisons,
  alpha 0.05. Counts better / no significant difference / worse per score group and in total.
- 15 network parameters (scripts\make_figures.py props() and table_value(): per-window medians over the 24
  realisations then median over windows; pooled-trace values for median length, 90th percentile, cluster shares,
  directions and spreads), held-out vs N_max 50 / 120 / 200.
- Also: training time per model, epochs, number of parameters, mean number of active slots
  (existence probability >= 0.5 before clipping) and mean traces per realisation after clipping.

## Outputs
Table_Nmax.csv/.md, Table_Nmax_tests.csv, REPORT.md, scripts and logs in this folder.

## Amendment (2026-10-05, after training; the CPU pass had already been scored once)
A first generation pass on the CPU did not reproduce the released S1 EVAE realisations (0 of 480 identical) although
the retrained N_max 120 checkpoints are SHA-256 identical to the released ones (12 of 12). Cause: the released
realisations were generated on the GPU (generators.load_evae selects CUDA when available), and torch.randn on CUDA
draws different noise than on the CPU for the same seed. A test realisation regenerated on CUDA from the released
checkpoint is identical to the released file. All three variants are therefore regenerated on CUDA, as in the
release; the CPU pass is kept in networks_cpu_superseded\ and outputs\cpu_superseded\ only as a record (it is a
second, independent set of noise draws; its counts are reported in REPORT.md as a robustness check, not hidden). Training stays on the CPU as in the release.
