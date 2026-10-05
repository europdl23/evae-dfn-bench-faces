# N_max sensitivity test (Reviewer 2 #6): report

## Verdict

**N_max does not matter in the range tested (50 to 200).** Over the 20 held-out windows of the gap-filling test,
N_max 50 and N_max 200 are not significantly different from N_max 120 on 37 and 38 of the 38 error scores. The
only significant difference is a small one in favour of N_max 50: cluster C2 share error (median 0.093 vs 0.115).
The 15 network parameters change little: most move by no more than one rounding step. The largest shift is the
pooled 90th percentile length at N_max 50 (10.6 m vs 11.8 m; held-out 13.9 m), and the window-level score for it
is not significantly different.

**Is 120 justified?** Yes, as a safe upper limit, not as a tuned value. The densest window in the library has
26 traces, so 120 is 4.6 times that. The trained model switches on only about 14 slots per realisation (at most
18 to 22) whatever N_max is, so the slot limit never binds. Results do not depend on the choice. A smaller limit
(50) would do as well and train faster. A larger one (200) costs more parameters and time and gains nothing.
N_max = 500 was not tested. 200 already shows no change, so we expect none at 500, but that is an extrapolation.

## Reproduction of the paper's model
- The retrained N_max 120 checkpoints, made with the copied and modified code, are SHA-256 identical to the 12
  released S1 checkpoints (12 of 12). The release checkpoints could therefore have been used directly.
- Their 480 realisations (generated on CUDA, as the release was) are identical to the released S1 EVAE
  realisations (max coordinate difference 0.0).
- The N_max 120 column of Table_Nmax equals the EVAE gap-filling column of the paper's Table D.
- Parameter count at 120: 544,392, as in FACTS_GEOBG E1.

## Results

### Paired tests (Table_Nmax_tests.csv; 38 scores; two-sided Wilcoxon over 20 windows, Holm over the 2 comparisons, n.d. rule)

| Comparison | Better | No significant difference | Worse |
|---|---|---|---|
| N_max 50 vs N_max 120 | 1 | 37 | 0 |
| N_max 200 vs N_max 120 | 0 | 38 | 0 |

By group, every group is all "no difference" except Orientation clusters for 50 vs 120 (1 / 13 / 0; C2 share
error, p_holm = 0.004). Per-score details: outputs/tests_per_score.csv.

### Parameters (Table_Nmax.md)

| Parameter | Held-out | 50 | 120 | 200 |
|---|---|---|---|---|
| Median length (m) | 5.8 | 5.5 | 5.5 | 5.4 |
| 90th percentile length (m) | 13.9 | 10.6 | 11.8 | 12.0 |
| P20 (per 100 m2) | 3.75 | 3.50 | 3.50 | 3.31 |
| P21 (m/m2) | 0.269 | 0.209 | 0.214 | 0.208 |
| Intersections per 100 m2 | 0.50 | 0.75 | 0.75 | 0.75 |
| Connections per trace | 0.73 | 0.81 | 0.90 | 0.83 |
| Spacing (m) | 3.1 | 4.0 | 4.1 | 4.1 |
| C1 / C2 / C3 / C4 share (%) | 36 / 32 / 19 / 10 | 34 / 29 / 18 / 13 | 34 / 28 / 19 / 13 | 36 / 27 / 18 / 13 |

Directions and spreads of C1 and C2 differ by at most 1 degree and 0.4 degree across variants (Table_Nmax.csv).

### Cost and slot use (outputs/run_summary.csv; 12 models per variant, CPU 4 threads, 5 models trained at once, jobs interleaved across variants)

| N_max | Parameters | Training time per model, mean (range) | Epochs, mean | s per epoch | Active slots per realisation, mean (max) | Stable runs |
|---|---|---|---|---|---|---|
| 50 | 328,442 | 68 s (47-87) | 68.5 | 1.00 | 14.0 (22) | 12/12 |
| 120 | 544,392 | 96 s (72-117) | 84.5 | 1.14 | 13.9 (20) | 12/12 |
| 200 | 791,192 | 111 s (73-138) | 82.2 | 1.36 | 13.5 (18) | 12/12 |

Active slots = existence probability >= 0.5 before clipping; the top-10 fallback never triggered. Validation
losses are not comparable across N_max, because the existence loss is averaged over all slots.

### Robustness: a second set of noise draws
A first generation pass ran on the CPU, which draws different noise from the GPU for the same seeds (see the
PROTOCOL amendment). Scored the same way, it gave 50 vs 120: 2 / 35 / 1 and 200 vs 120: 0 / 36 / 2
(outputs/cpu_superseded/). The significant scores were not the same as in the main pass. Differences of this size
come and go with the noise draw, which agrees with the main result.

## Suggested sentences (state only what the data show)

**Paper:** "N_max = 120 is an upper limit on the number of trace slots, set well above the densest window
(26 traces); in a sensitivity test with N_max = 50 and 200 (gap-filling test, 12 retrained models each), 37 and 38
of the 38 error scores were not significantly different from N_max = 120, and the trained model used about 14 slots
per realisation in every case."

**Response letter:** "We retrained the EVAE with N_max = 50 and 200 under otherwise identical settings (gap-filling
test, 4 folds x 3 run seeds, same generator seeds). Against N_max = 120, 37 of 38 and 38 of 38 error scores showed
no significant difference (paired Wilcoxon over the 20 held-out windows, Holm), and the model switched on only about
14 slots per window whatever the limit. N_max = 120 is therefore a safe capacity above the densest window
(26 traces) rather than a tuned value. A larger value such as 500 would add parameters and training time; we did
not test 500 directly, but 200 already gave no change."

## Files
- PROTOCOL.md (design written before computing, plus the GPU amendment)
- code/ (copied release; changes marked "NMAX SENSITIVITY 2026-10-05" in src/model/utils.py, src/model/training.py,
  scripts/train_evae.py)
- run_training.py, generate_nmax.py, check_reproduction.py, score_nmax.py, summarise_runs.py
- models/N50, N120, N200 (36 models, run_status.json each); networks/N50, N120, N200, N120_release
- Table_Nmax.csv/.md, Table_Nmax_tests.csv; outputs/ (per-realisation scores, window medians, per-score tests,
  active slots, run summary); logs/
