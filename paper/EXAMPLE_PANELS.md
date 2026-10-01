# Example panels (one rule for Results and Discussion)

**Rule (fixed before drawing).** For each test, every held-out panel gets four EVAE errors, each the median over its 24 realisations:

* trace-direction W1;
* trace-length W1;
* trace-count error;
* trace-direction-cluster share error.

Each error is standardised within the test.

* **Typical panel:** the panel whose standardised errors are closest to the test medians. Tests are taken in the order gap-filling, new-bench, new-stretch; a panel already chosen is skipped.
* **Hard panel:** one gap-filling panel, at the 90th percentile of the mean standardised error.
* **Realisation shown:** run seed 1337, draw 0 for every method (EVAE, ADFNE, KDE). It is the first realisation, not selected.

| Label | Role | Test | Panel | Fold | Direction W1 (°) | Length W1 (m) | Count error | Cluster-share error | Generator seeds (EVAE / ADFNE / KDE) |
|---|---|---|---|---|---|---|---|---|---|
| A | typical | gap-filling | W03_C2 | 2 | 11.93 | 1.11 | 0.22 | 0.254 | 2058722514 / 1858885179 / 2362463540 |
| B | typical | new-bench | W06_C5 | 6 | 12.70 | 1.51 | 0.14 | 0.275 | 4257113559 / 2790931267 / 1145452620 |
| C | typical | new-stretch | W04_C4 | 1 | 14.76 | 1.67 | 0.30 | 0.285 | 1762277702 / 3199592902 / 1554639561 |
| D | hard | gap-filling | W02_C2 | 0 | 11.24 | 4.15 | 0.40 | 0.306 | 331215491 / 130300010 / 3856153445 |

Test medians of the four errors (for comparison):

* Gap-filling test: direction W1 12.86°, length W1 1.43 m, count error 0.22, cluster-share error 0.271.
* New-bench test: direction W1 13.36°, length W1 1.54 m, count error 0.24, cluster-share error 0.269.
* New-stretch test: direction W1 14.80°, length W1 1.53 m, count error 0.22, cluster-share error 0.285.

Code: `paper/code/select_examples.py`; values from `tables/stats_box_medians.csv` of the release.
