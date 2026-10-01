# Methods

Older names in this file: box = panel, network = realisation, scheme S1 / S2 / S3 = gap-filling / new-bench / new-stretch test, guide = geology-informed terms, orientation cluster = trace-direction cluster.

## 1. Boxes and held-out schemes

* **Boxes.** The 50 usable boxes of the Section 1 west wall (`data/box_library/`): 20 m wide and the full face height.
  Every box is normalised by its longest side, so 1 unit = 20 m and the aspect ratio is kept.
* **Schemes.** `src/study/study.py`, `folds` and `split`:
  * **S1, fill a gap.** Boxes whose 8 neighbours all exist, in 4 folds by row and column parity (20 test-box cases).
  * **S2, new bench level.** One fold per bench row, W00 to W06 (7 folds, 50 cases).
  * **S3, new part of the wall.** Column pairs (1-2, 3-4, 5-6, 7-8) (4 folds, 50 cases).
* **Fold split.** Test boxes = the fold. Validation boxes = every 10th non-test box, starting at the fold index. Fitting
  boxes = the rest.
* **No shared fractures.** Every fracture that appears in a test box is removed from all fitting and validation boxes,
  so a fracture cut by a box edge cannot leak into training.
* **Stored splits.** The splits are in `data/splits/`; the code recomputes them and checks they are equal.

## 2. Orientation clusters (learned, `src/study/setbg.py`)

* **Model.** A mixture of K axial von Mises components on 2-theta plus one uniform component, fitted by EM:
  * 10 random restarts, seed 20261001;
  * K in 1..4 by BIC.
* **Cluster definition.** A cluster is a tight group: concentration at least 8 on 2-theta, which puts about 94 % of a
  cluster within +-20 deg of its centre.
* **Unclustered traces.** Traces most likely under the uniform component are "unclustered".
* **Fitting data.** The clusters are fitted to the traces of the fitting boxes of each fold.
* **Naming.** Clusters are listed in a fixed direction order, matched to 125, 56, 27 and 89 deg, so that "cluster 1"
  means the same direction in every fold.
* **Result.** Every fold gives K = 4, with 14-23 % of traces unclustered.
* **Check against 3D.** The 4 face directions match the face traces of the 4 joint sets measured as planes on the same
  wall (117, 49, 20 and 83 deg).

## 3. EVAE (learned)

* **Model.** The dual-latent EVAE of the Paper 1 release (`src/model/training.py`):
  * spatial latent 24, geometry latent 32, up to 120 traces per window;
  * 3-component axial von Mises direction head;
  * KL free-bits floor 0.22, final L2 settings.
* **Added guidance.** Two terms are added to the training loss, weight 1.0 each:
  * `generated_direction_w1`: circular W1 between the direction distribution the model would generate for a window
    (each slot's von Mises mixture, slots weighted by existence probability) and the window's real directions;
  * `generated_class_share_l1`: L1 difference between the orientation-cluster shares (4 clusters + unclustered) of
    the generated and the real directions, under the fold's learned cluster model.
* **Training.** `scripts/train_evae.py`:
  * fitting boxes for training, validation boxes for early stopping;
  * up to 100 epochs, stop after 20 epochs without improvement;
  * CPU, 4 threads, deterministic algorithms;
  * one model per fold and run seed (1337, 20260903, 7), so 45 models.
* **Generation.** `src/study/study.py`, `generate`:
  * the latent is drawn around the encoder posterior of one of the 8 non-test boxes nearest to the test box (context
    box = draw mod 8);
  * decoded, then clipped to the test box;
  * 8 draws per model, so 24 networks per test box.

## 4. ADFNE and KDE (fitted distributions)

Fitted on the fitting boxes of each fold, never on a test box (`src/evaluation/generators.py`, `fit_baseline_stats`;
parameters in `data/baseline_fits/`):

* **Orientation.** The standard 2-set axial von Mises fit (EM, seed 20260907). Each trace goes to its most likely set.
* **Per set:**
  * centre and directional concentration;
  * a truncated-exponential length fit (low, mean, high);
  * the mean count per fitting box.
* **Count.** The trace count of a set is its mean count, scaled from the mean fitting-box height to the test-box height.
* **ADFNE 1.5** (GNU Octave):
  * draws direction, length and a uniform position per set;
  * traces are over-requested, filtered to centres inside the box, then subsampled to the count.
* **KDE:**
  * kernel-density positions;
  * lengths and directions resampled from the set's fitting traces.
* **Clipping.** Both are clipped to the box with the same routine as the EVAE.
* **No learned clusters.** The baselines are not given the learned orientation clusters.

## 5. Seeds

See `seeds/seeds.json` and README Section 5.

* Every network has its own generator seed, `crc32("METHOD|scheme|variant|fold|box|run seed|draw")`.
* All methods use the same run seeds and draws.

## 6. Properties and scores

**Per network** (`scripts/make_figures.py`, `props`; lengths in m, areas in m2):

| Property | Definition |
|---|---|
| Traces per 100 m2 (P20) | number of traces / box area x 100 |
| P21 | total trace length / box area |
| Intersections per 100 m2 (P22 here) | number of trace crossings (X nodes) / box area x 100 |
| Median length, 90th percentile length | of the traces in the box (clipped at the box edge) |
| Spacing | median distance from each trace centre to the nearest other trace centre |
| Connections per trace (CL) | 2 (Y + X) / ((I + Y) / 2), Sanderson and Nixon (2015) node types |
| Orientation-cluster share | share of traces in each learned cluster, and unclustered |
| Cluster direction, spread | axial mean and axial circular standard deviation of the cluster's traces |

**Node types** (`src/study/topology.py`):
* I = a free end; Y = an end within 0.3 m of another trace; X = a crossing.
* Ends within 0.1 m of the box edge are censored, because the trace leaves the box.

**Box value.** Median over the 24 networks of a method; for held-out, the mapped traces of the box. Tables and box plots
use box values; the per-scheme value is the median over the test boxes.

**Pooled distributions** (rose diagrams, length histograms, cluster shares, directions):
* all traces of all test boxes;
* each generated network is weighted 1/24, so every box counts the same for every method.

## 7. Statistical tests (`scripts/statistical_tests.py`)

* **Error scores.** Each network is scored against its held-out box. Smaller = closer to held-out. There are 38 error
  scores in 5 groups: orientation distribution, orientation clusters, length, density, topology.
* **Box value.** Median over the box's 24 networks where the score is defined.
* **Undefined scores (n.d.).** A score is undefined for an empty network, or for a cluster score when the network has fewer than 2 members of a cluster the held-out box has. Undefined values are left out of the box value; a box with no defined value is left out of that test. (The first version of the study counted them as the worst value: `--penalty`.)
* **EVAE against each baseline:**
  * paired two-sided Wilcoxon over the test boxes of a scheme (zero-split);
  * Holm over the 2 baselines, alpha 0.05;
  * outcome: better, no difference or worse.
* **Three-way verdict:**
  * the method with the lowest median error is the clear winner in a scheme if it beats both others (one-sided
    Wilcoxon, Holm);
  * a method wins a score if it is the clear winner in at least 2 of the 3 schemes.
