# Combined parameter table (held-out | natural-variability reference | EVAE | ADFNE | KDE)

Values: median over the held-out panels of the test (per panel, a generator value is the median of its 24 realisations; the reference value is the median of the 8 INTACT neighbouring panels). Rows taken from the release (trace direction, length, intensity, spacing, intersections, connections) are computed exactly as `paper/tables/Table_D_parameters.csv` (replicated value for value). **Bold** = the generator value closest to the held-out value (ties bolded). Significance (EVAE vs ADFNE / vs KDE): + EVAE closer, = no significant difference, − EVAE further (paired Wilcoxon over panels, Holm over the two baselines, alpha 0.05; release rows from the release error score of that parameter, `recount_EVAE_vs_baselines.csv`, n.d. rule; new rows from `engineering_tests.csv`). The spacing row uses the spacing-distribution score; the crossing-share row uses the node-type score.

| Group | Parameter | Unit | gap-filling: Held-out | gap-filling: Reference | gap-filling: EVAE | gap-filling: ADFNE | gap-filling: KDE | gap-filling: EVAE vs ADFNE/KDE | new-bench: Held-out | new-bench: Reference | new-bench: EVAE | new-bench: ADFNE | new-bench: KDE | new-bench: EVAE vs ADFNE/KDE | new-stretch: Held-out | new-stretch: Reference | new-stretch: EVAE | new-stretch: ADFNE | new-stretch: KDE | new-stretch: EVAE vs ADFNE/KDE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace direction | Cluster C1 (~125°): share | % | 36 | 36 | 34 | **36** | 34 | =/= | 34 | 36 | **34** | 36 | 35 | =/= | 34 | 36 | 36 | 36 | **34** | =/= |
| Trace direction | Cluster C2 (~56°): share | % | 32 | 30 | 28 | **32** | 29 | −/= | 31 | 30 | 28 | 33 | **31** | =/= | 32 | 29 | 28 | **33** | **31** | =/= |
| Trace direction | Cluster C3 (~27°): share | % | 19 | 19 | **19** | 17 | 21 | =/= | 19 | 20 | **20** | 17 | **20** | =/= | 18 | 20 | **18** | 17 | 20 | =/+ |
| Trace direction | Cluster C4 (~89°): share | % | 10 | 11 | 13 | **11** | **11** | =/= | 10 | 10 | **10** | 8 | **10** | =/= | 10 | 11 | 13 | **10** | 11 | =/= |
| Trace direction | Cluster C1: direction | ° | 125 | 125 | 126 | **125** | **125** | =/= | 125 | 124 | **125** | 124 | **125** | =/= | 124 | 124 | **124** | **124** | **124** | =/= |
| Trace direction | Cluster C2: direction | ° | 56 | 57 | **56** | **56** | **56** | =/= | 57 | 57 | 56 | **57** | **57** | =/= | 56 | 56 | **56** | **56** | 57 | =/= |
| Trace direction | Cluster C1: spread | ° | 10.1 | 10.3 | 11.6 | **10.8** | **10.8** | −/− | 11.0 | 10.9 | 12.0 | **11.1** | 10.8 | =/= | 10.9 | 11.2 | 12.2 | 11.4 | **11.0** | =/= |
| Trace direction | Cluster C2: spread | ° | 9.3 | 9.3 | 10.0 | 9.8 | **9.7** | =/= | 9.8 | 9.8 | 10.4 | 10.5 | **9.7** | −/− | 10.3 | 9.4 | 10.6 | **10.1** | 9.6 | −/= |
| Length | Median trace length | m | 5.8 | 6.0 | **5.5** | 4.6 | 5.2 | +/+ | 5.7 | 6.0 | **5.5** | 4.5 | 5.2 | +/+ | 5.7 | 5.8 | 5.1 | 4.6 | **5.2** | +/= |
| Length | 90th-percentile trace length | m | 13.9 | 12.9 | **11.8** | 11.2 | 10.2 | +/+ | 12.4 | 12.8 | **12.1** | 11.1 | 10.4 | +/+ | 12.4 | 12.4 | **11.4** | 11.3 | 10.3 | =/+ |
| Intensity and spacing | Trace density (P20) | per 100 m² | 3.75 | 3.50 | 3.50 | **3.75** | **3.75** | =/= | 3.93 | 3.55 | 3.50 | **3.75** | **3.75** | =/= | 3.93 | 3.74 | **3.50** | **3.50** | **3.50** | =/= |
| Intensity and spacing | Trace intensity (P21) | m/m² | 0.269 | 0.263 | 0.214 | 0.210 | **0.215** | +/+ | 0.265 | 0.258 | **0.223** | 0.207 | 0.217 | +/+ | 0.265 | 0.252 | **0.206** | 0.202 | 0.204 | =/= |
| Intensity and spacing | Spacing to the nearest trace | m | 3.1 | 3.0 | 4.1 | **2.5** | 2.4 | =/= | 3.0 | 3.2 | 4.1 | **2.5** | 2.4 | =/= | 3.0 | 3.1 | 4.0 | **2.6** | 2.4 | =/= |
| Connectivity and termination | Intersections | per 100 m² | 0.50 | 0.38 | **0.75** | 1.19 | 1.50 | +/+ | 0.41 | 0.38 | **0.75** | 1.25 | 1.50 | +/+ | 0.41 | 0.38 | **0.65** | 1.12 | 1.25 | +/+ |
| Connectivity and termination | Connections per trace | - | 0.73 | 0.68 | **0.90** | 1.32 | 1.43 | +/+ | 0.68 | 0.58 | **1.00** | 1.29 | 1.46 | +/+ | 0.68 | 0.57 | **0.87** | 1.27 | 1.36 | +/+ |
| Connectivity and termination | T-end share (ends stopping on another trace) | - | 0.09 | 0.10 | **0.09** | 0.12 | 0.13 | =/= | 0.09 | 0.08 | **0.09** | 0.12 | 0.12 | =/= | 0.09 | 0.08 | **0.08** | 0.11 | 0.13 | =/= |
| Connectivity and termination | Crossing share of nodes | - | 0.08 | 0.07 | **0.11** | 0.17 | 0.19 | +/+ | 0.07 | 0.07 | **0.14** | 0.17 | 0.19 | +/+ | 0.07 | 0.07 | **0.11** | 0.17 | 0.17 | +/+ |
| Connectivity and termination | Percolation parameter p (threshold about 5.6) | - | 2.75 | 2.56 | **1.88** | 1.68 | 1.63 | +/+ | 2.35 | 2.48 | **2.05** | 1.63 | 1.66 | +/+ | 2.35 | 2.48 | **1.82** | 1.58 | 1.55 | +/+ |
| Connectivity and termination | Panels with a spanning cluster | share | 0.45 | 0.33 | 0.03 | **0.11** | 0.10 | =/= | 0.24 | 0.32 | 0.05 | **0.11** | 0.09 | +/+ | 0.24 | 0.29 | 0.09 | **0.13** | 0.10 | =/= |
| Connectivity and termination | Largest connected cluster | share of length | 0.28 | 0.26 | **0.39** | 0.42 | 0.41 | +/+ | 0.28 | 0.27 | **0.41** | 0.42 | 0.42 | =/= | 0.28 | 0.25 | **0.40** | 0.43 | **0.40** | +/= |
| Engineering inputs | Equivalent modulus along the bench, E/E0 | - | 0.26 | 0.27 | **0.36** | 0.38 | 0.41 | +/+ | 0.31 | 0.28 | **0.35** | 0.39 | 0.39 | +/+ | 0.31 | 0.29 | **0.35** | 0.40 | 0.41 | +/+ |
| Engineering inputs | Equivalent modulus down the face, E/E0 | - | 0.41 | 0.41 | **0.47** | 0.49 | 0.51 | =/= | 0.41 | 0.41 | **0.44** | 0.50 | 0.50 | +/+ | 0.41 | 0.41 | **0.49** | 0.52 | 0.52 | +/+ |
| Engineering inputs | Deformability anisotropy index | - | 0.51 | 0.48 | **0.41** | 0.37 | 0.34 | =/+ | 0.50 | 0.51 | **0.39** | 0.36 | 0.35 | =/= | 0.50 | 0.50 | **0.50** | 0.40 | 0.37 | +/+ |
| Engineering inputs | Softest loading direction (from the bench axis) | ° | 3 | 2 | 13 | -3 | **-2** |  | -3 | -3 | 12 | **-3** | **-3** |  | -3 | -1 | 11 | -8 | **-7** |  |
| Engineering inputs | Mean persistence, C1 | - | 0.059 | 0.055 | 0.038 | 0.036 | **0.039** | +/= | 0.043 | 0.047 | **0.045** | 0.039 | 0.040 | =/= | 0.042 | 0.056 | **0.043** | 0.033 | 0.036 | =/= |
| Engineering inputs | Mean persistence, C2 | - | 0.037 | 0.033 | 0.022 | **0.031** | **0.031** | =/= | 0.033 | 0.030 | 0.028 | 0.030 | **0.031** | =/= | 0.031 | 0.031 | 0.021 | **0.031** | 0.030 | =/− |
| Engineering inputs | Maximum persistence, C1 | - | 0.43 | 0.39 | 0.31 | 0.29 | **0.32** | =/= | 0.32 | 0.37 | 0.29 | 0.31 | **0.32** | +/= | 0.30 | 0.35 | 0.33 | 0.28 | **0.30** | =/= |
| Engineering inputs | Maximum persistence, C2 | - | 0.28 | 0.28 | 0.24 | 0.26 | **0.29** | =/= | 0.30 | 0.28 | 0.25 | 0.26 | **0.29** | =/= | 0.33 | 0.27 | 0.21 | 0.27 | **0.29** | =/= |

## Pooled over the 120 panel cases (compact version for the main text)

| Group | Parameter | Unit | Held-out | Reference | EVAE | ADFNE | KDE | EVAE vs ADFNE/KDE: gap-filling, new-bench, new-stretch |
|---|---|---|---|---|---|---|---|---|
| Trace direction | Cluster C1 (~125°): share | % | 35 | 36 | **35** | 36 | 34 | =/=; =/=; =/= |
| Trace direction | Cluster C2 (~56°): share | % | 32 | 30 | 28 | **33** | **31** | −/=; =/=; =/= |
| Trace direction | Cluster C3 (~27°): share | % | 18 | 20 | **19** | **17** | 20 | =/=; =/=; =/+ |
| Trace direction | Cluster C4 (~89°): share | % | 10 | 11 | 12 | **9** | **11** | =/=; =/=; =/= |
| Trace direction | Cluster C1: direction | ° | 124 | 124 | 125 | **124** | 125 | =/=; =/=; =/= |
| Trace direction | Cluster C2: direction | ° | 56 | 57 | **56** | **56** | 57 | =/=; =/=; =/= |
| Trace direction | Cluster C1: spread | ° | 10.8 | 10.9 | 12.0 | 11.2 | **10.9** | −/−; =/=; =/= |
| Trace direction | Cluster C2: spread | ° | 9.9 | 9.6 | 10.4 | 10.2 | **9.7** | =/=; −/−; −/= |
| Length | Median trace length | m | 5.7 | 5.9 | **5.4** | 4.6 | 5.2 | +/+; +/+; +/= |
| Length | 90th-percentile trace length | m | 12.4 | 12.7 | **11.8** | 11.2 | 10.3 | +/+; +/+; =/+ |
| Intensity and spacing | Trace density (P20) | per 100 m² | 3.93 | 3.56 | 3.50 | **3.75** | **3.75** | =/=; =/=; =/= |
| Intensity and spacing | Trace intensity (P21) | m/m² | 0.265 | 0.257 | **0.216** | 0.205 | 0.214 | +/+; +/+; =/= |
| Intensity and spacing | Spacing to the nearest trace | m | 3.0 | 3.1 | 4.1 | **2.5** | 2.4 | =/=; =/=; =/= |
| Connectivity and termination | Intersections | per 100 m² | 0.50 | 0.38 | **0.75** | 1.14 | 1.38 | +/+; +/+; +/+ |
| Connectivity and termination | Connections per trace | - | 0.73 | 0.61 | **0.94** | 1.29 | 1.43 | +/+; +/+; +/+ |
| Connectivity and termination | T-end share (ends stopping on another trace) | - | 0.09 | 0.08 | **0.09** | 0.12 | 0.12 | =/=; =/=; =/= |
| Connectivity and termination | Crossing share of nodes | - | 0.07 | 0.07 | **0.12** | 0.17 | 0.19 | +/+; +/+; +/+ |
| Connectivity and termination | Percolation parameter p (threshold about 5.6) | - | 2.47 | 2.52 | **1.96** | 1.63 | 1.63 | +/+; +/+; +/+ |
| Connectivity and termination | Panels with a spanning cluster | share | 0.28 | 0.31 | 0.06 | **0.12** | 0.10 | =/=; +/+; =/= |
| Connectivity and termination | Largest connected cluster | share of length | 0.28 | 0.26 | **0.40** | 0.43 | 0.41 | +/+; =/=; +/= |
| Engineering inputs | Equivalent modulus along the bench, E/E0 | - | 0.29 | 0.28 | **0.35** | 0.39 | 0.40 | +/+; +/+; +/+ |
| Engineering inputs | Equivalent modulus down the face, E/E0 | - | 0.41 | 0.41 | **0.46** | 0.51 | 0.51 | =/=; +/+; +/+ |
| Engineering inputs | Deformability anisotropy index | - | 0.50 | 0.50 | **0.45** | 0.38 | 0.36 | =/+; =/=; +/+ |
| Engineering inputs | Softest loading direction (from the bench axis) | ° | -1 | -1 | 12 | -5 | **-4** |  |
| Engineering inputs | Mean persistence, C1 | - | 0.044 | 0.051 | **0.044** | 0.037 | 0.039 | +/=; =/=; =/= |
| Engineering inputs | Mean persistence, C2 | - | 0.036 | 0.031 | 0.024 | **0.031** | **0.031** | =/=; =/=; =/− |
| Engineering inputs | Maximum persistence, C1 | - | 0.35 | 0.36 | 0.31 | 0.30 | **0.32** | =/=; +/=; =/= |
| Engineering inputs | Maximum persistence, C2 | - | 0.31 | 0.28 | 0.24 | 0.26 | **0.29** | =/=; =/=; =/= |
