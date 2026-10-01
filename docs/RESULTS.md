# Results: EVAE against ADFNE and KDE on the held-out boxes

* **EVAE** = learned. **ADFNE** and **KDE** = fitted distributions; they learn nothing.
* All three use the same fitting boxes of each fold.
* Everything below is measured on held-out test boxes, in each of the three tests:
  * **S1, fill a gap:** 20 box cases;
  * **S2, new bench level:** 50 box cases;
  * **S3, new part of the wall:** 50 box cases.

The tables are written by `scripts/make_figures.py` (`tables/final_tables.md`); every table number is also in `tables/final_tables.xlsx`. The tests are written by
`scripts/statistical_tests.py` (`tables/stats_*.csv`).

## Figures

| File | Shows |
|---|---|
| `figures/Figure_1_plain_comparison` | held-out traces, then EVAE, ADFNE, KDE, one test box per scheme; run seed 1337, draw 0 for every method |
| `figures/Figure_2_rose_0_360` | orientation roses over 0-360 deg; black outline = held-out on every panel |
| `figures/Figure_3_length_histograms` | length histograms; black outline = held-out; median written |
| `figures/Figure_4_boxplots` | per-box values; dashed line = held-out median; each median and its % difference written |

## Table 1: held-out vs EVAE, for all three held-out schemes

| Parameter | S1 held-out | S1 EVAE | S2 held-out | S2 EVAE | S3 held-out | S3 EVAE |
|---|---|---|---|---|---|---|
| Traces per 100 m2 | 3.75 | 3.50 | 3.93 | 3.50 | 3.93 | 3.50 |
| Median trace length (m) | 5.8 | 5.5 | 5.7 | 5.5 | 5.7 | 5.1 |
| Long traces: 90th percentile length (m) | 13.9 | 11.8 | 12.4 | 12.1 | 12.4 | 11.4 |
| Trace intensity P21 (m/m2) | 0.269 | 0.214 | 0.265 | 0.223 | 0.265 | 0.206 |
| Intersections per 100 m2 | 0.50 | 0.75 | 0.41 | 0.75 | 0.41 | 0.65 |
| Connections per trace | 0.73 | 0.90 | 0.68 | 1.00 | 0.68 | 0.87 |
| Spacing: nearest trace (m) | 3.1 | 4.1 | 3.0 | 4.1 | 3.0 | 4.0 |
| Orientation cluster 1 (~125 deg): share (%) | 36 | 34 | 34 | 34 | 34 | 36 |
| Orientation cluster 2 (~56 deg): share (%) | 32 | 28 | 31 | 28 | 32 | 28 |
| Orientation cluster 3 (~27 deg): share (%) | 19 | 19 | 19 | 20 | 18 | 18 |
| Orientation cluster 4 (~89 deg): share (%) | 10 | 13 | 10 | 10 | 10 | 13 |
| Orientation cluster 1: direction (deg) | 125 | 126 | 125 | 125 | 124 | 124 |
| Orientation cluster 2: direction (deg) | 56 | 56 | 57 | 56 | 56 | 56 |
| Orientation cluster 1: spread (deg) | 10.1 | 11.6 | 11.0 | 12.0 | 10.9 | 12.2 |
| Orientation cluster 2: spread (deg) | 9.3 | 10.0 | 9.8 | 10.4 | 10.3 | 10.6 |

## Table 2: all methods (each cell = S1 / S2 / S3)

| Parameter | Held-out | EVAE | ADFNE | KDE |
|---|---|---|---|---|
| Traces per 100 m2 | 3.75 / 3.93 / 3.93 | 3.50 / 3.50 / 3.50 | 3.75 / 3.75 / 3.50 | 3.75 / 3.75 / 3.50 |
| Median trace length (m) | 5.8 / 5.7 / 5.7 | 5.5 / 5.5 / 5.1 | 4.6 / 4.5 / 4.6 | 5.2 / 5.2 / 5.2 |
| Long traces: 90th percentile length (m) | 13.9 / 12.4 / 12.4 | 11.8 / 12.1 / 11.4 | 11.2 / 11.1 / 11.3 | 10.2 / 10.4 / 10.3 |
| Trace intensity P21 (m/m2) | 0.269 / 0.265 / 0.265 | 0.214 / 0.223 / 0.206 | 0.210 / 0.207 / 0.202 | 0.215 / 0.217 / 0.204 |
| Intersections per 100 m2 | 0.50 / 0.41 / 0.41 | 0.75 / 0.75 / 0.65 | 1.19 / 1.25 / 1.12 | 1.50 / 1.50 / 1.25 |
| Connections per trace | 0.73 / 0.68 / 0.68 | 0.90 / 1.00 / 0.87 | 1.32 / 1.29 / 1.27 | 1.43 / 1.46 / 1.36 |
| Spacing: nearest trace (m) | 3.1 / 3.0 / 3.0 | 4.1 / 4.1 / 4.0 | 2.5 / 2.5 / 2.6 | 2.4 / 2.4 / 2.4 |
| Orientation cluster 1 (~125 deg): share (%) | 36 / 34 / 34 | 34 / 34 / 36 | 36 / 36 / 36 | 34 / 35 / 34 |
| Orientation cluster 2 (~56 deg): share (%) | 32 / 31 / 32 | 28 / 28 / 28 | 32 / 33 / 33 | 29 / 31 / 31 |
| Orientation cluster 3 (~27 deg): share (%) | 19 / 19 / 18 | 19 / 20 / 18 | 17 / 17 / 17 | 21 / 20 / 20 |
| Orientation cluster 4 (~89 deg): share (%) | 10 / 10 / 10 | 13 / 10 / 13 | 11 / 8 / 10 | 11 / 10 / 11 |
| Orientation cluster 1: direction (deg) | 125 / 125 / 124 | 126 / 125 / 124 | 125 / 124 / 124 | 125 / 125 / 124 |
| Orientation cluster 2: direction (deg) | 56 / 57 / 56 | 56 / 56 / 56 | 56 / 57 / 56 | 56 / 57 / 57 |
| Orientation cluster 1: spread (deg) | 10.1 / 11.0 / 10.9 | 11.6 / 12.0 / 12.2 | 10.8 / 11.1 / 11.4 | 10.8 / 10.8 / 11.0 |
| Orientation cluster 2: spread (deg) | 9.3 / 9.8 / 10.3 | 10.0 / 10.4 / 10.6 | 9.8 / 10.5 / 10.1 | 9.7 / 9.7 / 9.6 |

## Statistical tests

Paired Wilcoxon over held-out panels, Holm over the 2 baselines (better / no difference / worse = EVAE closer / no
significant difference / EVAE further). Undefined scores (n.d.) are left out, as in the paper:

| EVAE against | Trace-direction distribution | Trace-direction clusters | Length | Density and spacing | Topology | All (114) |
|---|---|---|---|---|---|---|
| ADFNE | 2 / 12 / 1 | 1 / 36 / 5 | 9 / 12 / 0 | 6 / 21 / 0 | 6 / 3 / 0 | **24 / 84 / 6** |
| KDE | 0 / 14 / 1 | 1 / 39 / 2 | 8 / 11 / 2 | 6 / 21 / 0 | 6 / 3 / 0 | **21 / 88 / 5** |

**Three-way verdict** (clear winner in at least 2 of the 3 tests):

* **EVAE wins 7 scores:**
  * length distribution, median length and long traces;
  * P21;
  * intersections, connections per trace and node types.
* **ADFNE and KDE win none.**
* **No clear winner on 31.**

**Sensitivity (first version of the study).** Undefined scores were counted as the worst value instead of being left
out (`python scripts/statistical_tests.py --penalty`):

* EVAE vs ADFNE 32 / 70 / 12; EVAE vs KDE 26 / 75 / 13.
* EVAE 8 clear wins, KDE 2.

The penalty mostly adds cluster comparisons that the baselines lose, because they often produce no traces of the
minor clusters.

## Where the EVAE is better

* **Trace length.**
  * The EVAE is closest to held-out in all three schemes for long traces (90th percentile), and in S1 and S2 for the
    median length.
  * ADFNE makes traces about 20 % too short; KDE about 10 %.
* **Connectivity.**
  * The EVAE is closest in every scheme for intersections and for connections per trace.
  * ADFNE and KDE have 1.5-3 times too many intersections.
* **Trace intensity (P21).** The EVAE is closest in S2 and S3. All three methods are 15-20 % low.
* **The same in every scheme.** The EVAE gives the same picture for a gap, a new bench and a new part of the wall, so it
  is not fitted to one area.

## Where it is not better

* **Orientation is a tie.** All three methods are within about 1 deg of the held-out cluster directions.
  * The EVAE's clusters are about 1-1.5 deg wider.
  * The EVAE has about 4 points less of cluster 2.
* **Trace count.** The EVAE makes slightly fewer traces (3.5 vs 3.9 per 100 m2).
* **Spacing.**
  * EVAE traces are a little too far apart (4.1 vs 3.0 m).
  * ADFNE and KDE traces are too close (2.4-2.6 m).
