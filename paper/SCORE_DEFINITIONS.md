# Definitions: the 15 parameters and the 38 error scores (for Methods Table 2)

## Common terms

* **Panel.** 20 m wide and the full face height (15.4, 17.6 or 20 m). Traces are clipped at the panel edges.
* **Trace direction θ.** Measured on the face from the along-bench axis. It is axial, so θ and θ + 180° are the same direction.
* **Axial mean direction.** ½ · arg(mean of e^{2iθ}).
* **Axial spread.** ½ · √(−2 ln R) in degrees, where R = |mean of e^{2iθ}|.
* **Trace-direction cluster (C1-C4).** Each trace is assigned to the most likely component of its fold's learned mixture: 4 axial von Mises clusters at about 125, 56, 27 and 89°, plus a uniform component. Traces assigned to the uniform component are **unclustered**.
* **Nodes** (Sanderson and Nixon 2015).
  * **I** = a free trace end.
  * **Y** = a trace end within 0.3 m of another trace.
  * **X** = a crossing of two traces.
  * Ends within 0.1 m of the panel edge are censored, because the trace leaves the panel.

## The 15 parameters (Tables R1, D and ablation)

Per held-out panel:
* the held-out value is that of the mapped panel;
* a method's value is the median over its 24 realisations;
* the test value is the median over the test's panels.

Rows marked "pooled" are computed instead over all traces of the test, with each realisation weighted 1/24.

| Parameter | Definition | Unit |
|---|---|---|
| Trace count (P20) | number of traces / panel area × 100 | traces per 100 m² |
| Median trace length | median trace length in the panel (pooled) | m |
| Long traces: 90th percentile length | 90th percentile of trace length (pooled) | m |
| Trace intensity (P21) | total trace length / panel area | m/m² |
| Intersections | number of crossings (X nodes) / panel area × 100 | per 100 m² |
| Connections per trace | C_L = 2 (N_Y + N_X) / N_L, with N_L = (N_I + N_Y) / 2 the number of traces counted from their uncensored ends | - |
| Spacing: nearest trace | median distance from each trace centre to the nearest other trace centre | m |
| Cluster 1-4 share | share of traces in the cluster (pooled) | % |
| Cluster 1, 2 direction | axial mean direction of the cluster's traces (pooled) | ° |
| Cluster 1, 2 spread | axial spread of the cluster's traces (pooled) | ° |

## The 38 error scores (Tables S, checks, Figure 9)

Each score is the error of one realisation against its held-out panel; smaller means closer.

* **Panel value.** The median over the realisations where the score is defined.
* **n.d. (not defined).** When the score is undefined in every realisation, the panel value is n.d. A score is n.d. when:
  * the realisation is empty; or
  * the realisation has fewer than 2 members of a cluster that the held-out panel has (for the cluster W1, direction, spread and length scores); or
  * the held-out panel lacks what the score needs: no crossings (intersection error), fewer than 2 members of the cluster, or fewer than 2 traces (spacing).
* **Use of n.d. values.** They are excluded from medians, tests and confidence intervals.

**W1** is the Wasserstein-1 (earth mover's) distance between the two empirical distributions.
* For directions it is circular, computed on 2θ with the cut point minimised, and reported in degrees of θ.

| Group | Score | Definition | Unit |
|---|---|---|---|
| Trace-direction distribution | Trace-direction distribution (W1) | circular W1 between all realisation and all held-out trace directions | ° |
| Trace-direction distribution | Cluster j orientation (W1), j = 1-4 | circular W1 between the directions of the members of cluster j | ° |
| Trace-direction clusters | Cluster j direction error | axial angle between the cluster's mean directions | ° |
| Trace-direction clusters | Cluster j spread error | absolute difference of the cluster's axial spreads | ° |
| Trace-direction clusters | Cluster j share error | absolute difference of the cluster's share of traces | fraction |
| Trace-direction clusters | Unclustered share error | absolute difference of the unclustered share | fraction |
| Trace-direction clusters | Cluster shares (total variation) | ½ Σ \|share difference\| over C1-C4 and unclustered | fraction (0-1) |
| Trace length | Length distribution (W1) | W1 between all trace lengths | m |
| Trace length | Median length error | absolute difference of the median trace lengths | m |
| Trace length | 90th percentile length error | absolute difference of the 90th percentile lengths | m |
| Trace length | Cluster j length (W1) | W1 between the lengths of the members of cluster j | m |
| Density and spacing | Trace count P20 (relative error) | \|N_realisation − N_held-out\| / N_held-out (same panel area) | - |
| Density and spacing | Trace intensity P21 (relative error) | \|ΣL_realisation − ΣL_held-out\| / ΣL_held-out | - |
| Density and spacing | Intersections (relative error) | \|X_realisation − X_held-out\| / X_held-out, X = number of crossings | - |
| Density and spacing | Spacing distribution (W1) | W1 between the nearest-trace-centre distances | m |
| Density and spacing | Clustering (variance-to-mean ratio error) | absolute difference of the variance-to-mean ratio of trace-centre counts in a grid of about 5 m cells (4 across the panel) | - |
| Density and spacing | Cluster j count (relative error) | \|n_j realisation − n_j held-out\| / n_j held-out | - |
| Topology | T-ends share error | absolute difference of the termination share, N_Y / (N_I + N_Y): the share of uncensored trace ends that stop on another trace | fraction |
| Topology | Connections per trace error | absolute difference of C_L = 2 (N_Y + N_X) / N_L | - |
| Topology | Node types I / Y / X (total variation) | ½ (\|ΔP_I\| + \|ΔP_Y\| + \|ΔP_X\|), with P_I, P_Y, P_X the proportions of I, Y and X nodes among all nodes | fraction (0-1) |

## Counts by group

| Group | Scores |
|---|---|
| Trace-direction distribution | 5 |
| Trace-direction clusters | 14 |
| Trace length | 7 |
| Density and spacing | 9 |
| Topology | 3 |
| **Total** | **38** |

Across the 3 tests this gives 114 score-by-test comparisons per pair of methods.
