# Existence-threshold sensitivity (Reviewer 2 #9), IJRMMS-D-26-00250

## Verdict
The results are insensitive to the existence threshold in the range 0.4 to 0.6. Compared with the paper's 0.5, threshold 0.4
differs significantly on none of the 38 error scores (0 better / 38 no significant difference / 0 worse). Threshold 0.6 differs
on 2 of 38 (0 better / 36 / 2 worse): orientation W1 distance (median 13.13 vs 12.86 deg, Holm p = 0.001) and P21 relative
error (0.259 vs 0.237, Holm p = 0.031), both small and both because a higher threshold keeps fewer traces. The threshold mainly
shifts the trace count: 15.0 / 13.9 / 12.8 traces per realisation at 0.4 / 0.5 / 0.6, against 14.6 traces per held-out window.
Network parameters move little (median length 5.4 / 5.5 / 5.6 m; P21 0.224 / 0.214 / 0.203 m/m2; cluster shares within 1
percentage point). Not a limitation; 0.5 is not tuned (0.4 is about as good and slightly closer in count and P21).

## Checks
- No retraining: released S1 checkpoints (4 folds x 3 run seeds) used directly; generation on CUDA as in the release.
- Threshold 0.5 reproduces the released S1 EVAE realisations byte for byte: 480 of 480.
- Fallback rule (top 10 logits if fewer than 2 slots pass) unchanged; it fired in 0 of 480 realisations at every threshold.
- Same noise seeds for every threshold, so each comparison uses the same latent draws; only the kept slots differ.

## Results
See Table_threshold.md/.csv (15 parameters + traces per realisation + counts), Table_threshold_tests.csv (counts per score
group), outputs\tests_per_score.csv (every score, raw and Holm p), outputs\slots_T0*.csv (slots per realisation).

## Suggested sentence for the paper
"Changing the existence threshold from 0.5 to 0.4 or 0.6, without retraining, changed the mean number of traces per realisation
from 13.9 to 15.0 and 12.8, respectively, and none (0.4) or 2 (0.6, orientation W1 distance and P21 error, both slightly worse) of the
38 error scores differed significantly from the 0.5 results (paired Wilcoxon over the 20 held-out windows, Holm-corrected)."

## Suggested sentence for the letter
"We tested the existence threshold directly: with the released gap-filling models and identical noise seeds, thresholds of 0.4 and
0.6 gave 0 and 2 (both slightly worse) significant differences out of 38 error scores relative to 0.5, mainly shifting the trace
count by about one trace per realisation; the threshold of 0.5 is therefore not a sensitive or tuned setting."

## Files
PROTOCOL.md, generate_thr.py, check_reproduction.py, score_thr.py, finish_table.py, logs\, networks\T04|T05|T06, outputs\.
Only code change vs release: study.py generate() threshold read from EVAE_THR (default 0.5).
