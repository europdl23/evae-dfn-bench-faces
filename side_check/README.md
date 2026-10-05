# BIC re-fit and labelled side check

This folder holds two analyses added in the October 2026 revision of the paper. Both use only the repository's data, models and realisations; nothing was retrained. The numbers below are read from `tables/` by the package build.

## 1. Why ADFNE and KDE get two trace-direction components (`kfit_unconstrained`)

ADFNE and KDE are given the standard fit of a conventional DFN: two trace-direction components, from a two-component axial von Mises mixture (`data/baseline_fits/`). The EVAE's cluster-share loss and the scoring use four trace-direction clusters, from a separate mixture fit in which every cluster must be tight (concentration of at least 8 on 2θ, about ±20°), plus a uniform component for unclustered traces (`data/orientation_clusters/`).

`code/kfit_unconstrained.py` re-fits the trace directions of the training windows of each of the 15 folds with the release code, choosing the number of components K from 1 to 6 by BIC:

| Fit | Folds where BIC picks K = 2 |
|---|---|
| plain axial von Mises mixture (the baselines' own fit, release `fit_set_rule`) | 14 of 15 |
| the same with a uniform component, without the tightness rule (release `setbg.fit`, minimum concentration removed) | 15 of 15 |
| sensitivity: independent EM of the review check (10 restarts, 400 iterations) | 13 of 15 |
| the constrained model of the paper (tightness rule, uniform component) | K = 4 in 15 of 15 |

* In 15 of 15 folds the plain K = 2 fit has a lower BIC than the constrained four-cluster fit.
* With the uniform component and no tightness rule, this holds in 15 of 15 folds.
* The K = 2 fit equals the stored baseline fit in 15 of 15 folds.

Without the tightness rule, the trace directions are best described by two wide components. The four clusters come from the tight-cluster definition, which the measured fracture planes of the wall support (paper, Text S3).

Files: `tables/kfit_unconstrained.csv` (one row per fold), `tables/kfit_unconstrained_log.txt`.

## 2. Labelled side check: ADFNE and KDE given the four learned clusters (`sidecheck_baselines_with_clusters`)

**This is a side check, not the main comparison.** In the paper, ADFNE and KDE are always fitted in their standard form.

Here each baseline was instead given the fold's four learned clusters and the unclustered component, each with its own fitted lengths and counts. Its realisations were then scored against the held-out windows with the same 38 error scores, n.d. rule and paired tests (Wilcoxon over held-out windows, Holm over the two baselines, α = 0.05) as the main comparison:

| EVAE against | Better | Not significantly different | Worse |
|---|---|---|---|
| ADFNE given the clusters | 20 | 77 | 17 |
| KDE given the clusters | 17 | 80 | 17 |

38 scores × 3 tests = 114 comparisons each. Better or worse means a lower or higher EVAE error.

By score group (EVAE against ADFNE / against KDE, better / not significantly different / worse):

* Trace-direction distribution: 0 / 9 / 6 against ADFNE; 0 / 13 / 2 against KDE
* Trace-direction clusters: 0 / 33 / 9 against ADFNE; 0 / 30 / 12 against KDE
* Trace length: 9 / 12 / 0 against ADFNE; 8 / 12 / 1 against KDE
* Density and spacing: 5 / 20 / 2 against ADFNE; 3 / 22 / 2 against KDE
* Topology: 6 / 3 / 0 against ADFNE; 6 / 3 / 0 against KDE

"Overall better" (a clear winner in at least 2 of the 3 tests): EVAE 5 scores, ADFNE given the clusters 0, KDE given the clusters 1, no method 32.

Given the clusters, the baselines match the cluster scores better. The EVAE keeps its advantage on trace length and topology.

### Files

| File | What |
|---|---|
| `networks/<test>/bgbase/<ADFNE or KDE>/f<fold>_<window>_s<run seed>_d<realisation>.csv` | the 2 × 2,880 realisations scored. Same format as `networks/` (x1, y1, x2, y2 in window units, 1 unit = 20 m), same window cases, run seeds and realisation indices. `bgbase` is the study's name for this variant. |
| `tables/sidecheck_baselines_with_clusters_scores.csv` | the 38 error scores of every realisation (n.d. = not defined) |
| `tables/sidecheck_baselines_with_clusters_panel_medians.csv` | window values (median over the 24 realisations), EVAE and both baselines |
| `tables/sidecheck_baselines_with_clusters_tests.csv`, `_counts.csv`, `_verdict.csv` | tests per score and test, counts by group, three-way verdict |
| `tables/sidecheck_baselines_with_clusters_summary.json`, `_log.txt` | summary and the full log, including the provenance and self-tests below |

### Checks made when the side check was run

The authors' script `code/sidecheck_baselines_with_clusters.py` checked, in the study folder:

* the realisations cover exactly the paper's window cases, seeds and realisation indices;
* the study's cluster models and window library are byte-identical to `data/`;
* one KDE realisation per fold regenerates bit for bit from its recorded seed;
* the EVAE realisations equal `networks/`.

The scoring and test functions are copied verbatim from the release. As a self-test, they reproduce the paper's main comparison row by row.

The old counts of an earlier version of this check used the first-version undefined-score rule and a different scorer. They are not used anywhere.

### Rerun from the repository

```bash
cd side_check/code
python rescore_from_repository.py     # about 10 s: rescores every realisation, recomputes tests, counts and verdict, compares with tables/
python kfit_unconstrained.py          # about 2 min: the BIC re-fit; writes work/side_check/
```

Both were checked on 2 October 2026 in a copy of the repository:

* every score, test, count and verdict was reproduced;
* the re-fit table and log were identical.

`sidecheck_baselines_with_clusters.py` itself also needs the study folder for its provenance checks; set `EVAE_CV_STUDY` to it. Reruns write to `work/side_check/`, never over `tables/`.
