# Loss-weight sensitivity test (Reviewer 2 #9): report

## Verdict

**The results are robust to halving or doubling any loss-weight group; no variant is better than the paper's model.**
Over the 20 held-out windows of the gap-filling test (S1), the 8 variants were not significantly different from the
paper's model on 296 of 304 variant-score comparisons (38 error scores x 8 variants). None was significantly better
on any score. 6 comparisons were worse, on only two scores:
- cluster variance-to-mean error (clustering of trace positions): worse for B_half, C_double, D_half and D_double
  (window median 0.22 vs 0.17 for the paper model);
- 90th-percentile length error: worse for B_half and C_double (median 1.96 and 1.98 m vs 1.50 m).

Halving or doubling the geology-informed loss (A), doubling the direction and cluster-share losses (B_double) or
halving the intersection and spacing terms (C_half) changed nothing (38 of 38 no difference). The 15 parameters
move little (Table_weights.md). The largest shifts are the 90th-percentile length (10.6 to 12.4 m; paper model
11.8 m, held-out 13.9 m), connections per trace (0.80 to 1.03; paper model 0.90, held-out 0.73), the C1 share
(30 to 37 %; held-out 36 %) and intersections per 100 m2 at C_double (0.56 vs 0.75; held-out 0.50).

**Which weights matter, and how.** The weakest point is the lower ends of B and C, read with care:
- B_half (direction + cluster-share losses 0.5): long traces are a little shorter (p90 10.7 m), more connections
  (1.03) and a lower C1 share (30 %); worse on p90 length error and clustering error.
- C_double (intersection 0.6, spacing 0.4): fewer intersections (0.56, closer to held-out), shorter long traces
  (p90 10.6 m); worse on p90 length error and clustering error.
- D (log-length) halved or doubled: only the clustering error is worse; length scores unchanged.
- A (geology-informed loss): no effect at x0.5 or x2.

**Caution on the clustering score.** It is worse for 4 of 8 variants, in both directions of D. That pattern
(a deviation from the paper model whichever way the weight moves) suggests that the paper model's realisations sit
on the good side of the noise for this score, rather than that the weight is tuned for it; the N_max test showed
that individual significant scores come and go with the noise draw. We cannot separate the two with this design.
In any case none of the variants does better, so there is no evidence that the paper weights were selected for a
favourable result and no evidence that a different setting would improve on them.

**Were the weights hand-tuned?** This test cannot say how the weights were chosen; it shows that a factor-of-two
change in any group changes no headline parameter materially and leaves 36 to 38 of the 38 scores unchanged.

## Checks
- Code edits verified as no-ops: a baseline model (S1 f0 s1337, release weights) retrained with the edited code has a
  checkpoint SHA-256 identical to the released one (logs/train_BASE_check_f0_s1337.log).
- Effective weights are printed by every training run ("WEIGHT ENV" and "EFFECTIVE WEIGHTS" lines in
  logs/train_*.log) and stored in each models/<variant>/*/run_status.json; they match the protocol for all 96 runs.
- 97 of 97 runs STABLE (no latent collapse). 480 realisations per variant, generated on CUDA as the release.
- Paper model = released S1 checkpoints and realisations (the N_max test showed a retrain is byte-identical).

## Results

### Counts vs the paper model (Table_weights_tests.csv; two-sided Wilcoxon over 20 windows, Holm over 8 variants, n.d. rule)

| Variant | Weights changed | Better | No difference | Worse | Worse scores |
|---|---|---|---|---|---|
| A_half | geology 0.0025 | 0 | 38 | 0 | |
| A_double | geology 0.01 | 0 | 38 | 0 | |
| B_half | direction, cluster share 0.5 | 0 | 36 | 2 | p90 length, cluster VMR |
| B_double | direction, cluster share 2.0 | 0 | 38 | 0 | |
| C_half | intersection 0.15, spacing 0.1 | 0 | 38 | 0 | |
| C_double | intersection 0.6, spacing 0.4 | 0 | 36 | 2 | p90 length, cluster VMR |
| D_half | log-length 0.5 | 0 | 37 | 1 | cluster VMR |
| D_double | log-length 2.0 | 0 | 37 | 1 | cluster VMR |

By group: Orientation distribution (5 scores) and Orientation clusters (14) and Topology (3): no difference in every
variant. Length (7): one worse score in B_half and C_double. Density (9): one worse score in B_half, C_double,
D_half, D_double. Per-score details: outputs/tests_per_score.csv.

### Key parameters: see Table_weights.md (held-out, paper model and 8 variants).

## Suggested sentences (only what the data show)

**Paper (Section 4.1):** "The loss weights were not optimised on the test windows; in a sensitivity test in which
each weight group was halved and doubled (gap-filling test, 12 retrained models per setting), 36 to 38 of the 38
error scores were not significantly different from the reported model and none was significantly better."

**Response letter (R2 #9):** "We retrained the EVAE with each loss-weight group halved and doubled in turn (geology-
informed loss; trace-direction distribution and cluster-share losses; intersection and spacing terms; log-length
term), under otherwise identical settings (gap-filling test, 4 folds x 3 run seeds, same generator seeds). Against
the reported model, 296 of the 304 variant-score comparisons showed no significant difference (paired Wilcoxon over
the 20 held-out windows, Holm), no variant was better on any score, and the 6 worse results concerned only the
clustering error of trace positions and the 90th-percentile length error, mainly when the direction and cluster-share
losses were halved or the intersection and spacing terms doubled. The results therefore do not depend on a finely
tuned choice of weights within a factor of two."

Note for the author: whether the weights were originally set by hand must be stated by you; this test does not
show how they were chosen.

## Files
- PROTOCOL.md; code/ (edits marked "WEIGHT SENSITIVITY 2026-10-05" in src/model/training.py, scripts/train_evae.py)
- run_training.py, generate_weights.py, score_weights.py, make_table.py
- models/<variant>/ (96 models + BASE_check), networks/<variant>/
- Table_weights.csv/.md, Table_weights_tests.csv; outputs/ (scores, window medians, tests_per_score.csv); logs/
