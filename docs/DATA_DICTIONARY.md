# Data dictionary

Older names used in files: box = panel, network = realisation, S1 / S2 / S3 = gap-filling / new-bench / new-stretch test, guide = geology-informed terms, orientation cluster = trace-direction cluster.

Lengths in m unless stated. **Box units:** every box is divided by its longest side, so 1 unit = 20 m. Directions (theta)
are measured in the face image from the along-bench axis, with y pointing down the face. They are axial: theta and
theta + 180 deg are the same direction.

## data/box_library/box_manifest.csv

| Column | Meaning |
|---|---|
| box | box name, `W<row>_C<column>` |
| row, row_index | bench face W00..W06 (0 = top face) |
| col | column 1..8 along the wall |
| usable | False for the 6 boxes at an inner berm (not used) |
| u_left | left edge of the box along the wall (m, local wall frame) |
| y_top | top edge of the box down the face (m, from the top of the face image) |
| width_m, height_m | box size (m) |
| centre_u, centre_stack | box centre along the wall and down the stacked faces (m); used to find the 8 nearest boxes |
| n_traces | number of trace pieces in the box |

## data/box_library/boxes/<box>.json (LabelMe 6.3.1)

| Field | Meaning |
|---|---|
| imageWidth, imageHeight | box size in pixels (2 cm per pixel); the photograph itself is not included (`imageData` is null) |
| shapes[].points | the two ends of a trace piece, pixels, origin top left, y down the face |
| shapes[].description | the fracture ID. The same ID in several boxes is one fracture cut at box edges |
| shapes[].full_length_m | length of the whole fracture trace on the face, before cutting at box edges |
| section1 | box position: u_left_m, u_right_m, y_top_m, y_bottom_m, pixel_size_m, centre_stack_m |

## data/splits/<scheme>_f<fold>.json

| Field | Meaning |
|---|---|
| test | the held-out test boxes of the fold |
| validation | boxes used only for early stopping of the EVAE |
| fitting | boxes used to train the EVAE and to fit ADFNE, KDE and the orientation clusters |
| held_out_fractures_removed_from_training | IDs of fractures in a test box; their pieces are removed from all non-test boxes |

## data/orientation_clusters/<scheme>_f<fold>.json

| Field | Meaning |
|---|---|
| K | number of clusters (chosen by BIC over 1..4) |
| centres_deg | cluster directions on the face (deg), in the fixed order ~125, ~56, ~27, ~89 |
| mu2, kappa2 | von Mises centre (radians of 2-theta) and concentration on 2-theta, per cluster |
| w_sets | cluster weights |
| w_bg | weight of the uniform component (unclustered traces) |
| bic | BIC for each K tried |
| n | number of fitting traces |
| kappa_min | minimum concentration of a cluster (8 = about +-20 deg) |

## data/baseline_fits/<scheme>_f<fold>.json (ADFNE and KDE fitted distributions)

| Field | Meaning |
|---|---|
| orientation_fit | the standard 2-set axial von Mises fit: centres_deg, mu2, kappa2, weights, em_seed |
| mean_ymax | mean height of the fitting boxes (box units) |
| sets[].centre_deg, kappa_dir | direction centre and directional concentration of the set |
| sets[].length_fit_low_mu_high | truncated-exponential length fit, box units: lower bound, mean, upper bound |
| sets[].mean_count | mean number of traces of the set per fitting box |
| sets[].n_fitting_traces | traces of the set in the fitting boxes |

KDE also resamples the set's fitting trace lengths, directions and centres; these come from the boxes and are recomputed
by `generators.fit_baseline_stats`.

## models/evae/<scheme>_f<fold>_s<seed>/

| File | Meaning |
|---|---|
| checkpoint.pt | trained EVAE (PyTorch state, loaded by `generators.load_evae`) |
| run_status.json | settings and outcome: epochs, best validation loss, KL per latent, guidance weights, checkpoint sha256 |
| train_history.csv | training and validation loss per epoch |

## networks/<scheme>/<method or ablation arm>/f<fold>_<box>_s<run seed>_d<draw>.csv

Methods: EVAE, ADFNE, KDE. Ablation arms: single_noguide, single_guide, dual_noguide (the dual latent with guide is EVAE).

One generated network. Each row is one trace: `x1, y1, x2, y2` in box units (multiply by 20 for metres), no header,
already clipped to the box. An empty file is a network with no traces.

## seeds/

| File | Meaning |
|---|---|
| seeds.json | run seeds, draws, the generator-seed rule and the other fixed seeds |
| network_seeds.csv | one row per network: scheme, fold, box, method, run_seed, draw, generator_seed, seed_key, file |
| ablation_network_seeds.csv | the generator seed of every ablation network (all arms use the EVAE's seeds) |
| figure_networks.json | the networks shown in Figure 1 (run seed 1337, draw 0 for every method) and how the boxes were chosen |

## tables/

| File | Meaning |
|---|---|
| ablation_tables.xlsx | the ablation in one Excel file: table (held-out and the four arms per scheme), test counts, tests per score, which component matters, per test box, full precision, notes |
| ablation_table.csv, ablation_properties.csv, ablation_tests_*.csv | the same as CSV |
| final_tables.xlsx | every table number in one Excel file: held-out vs EVAE, all methods, tests, tests per score, verdict, per test box, full precision, notes |
| final_properties.csv | per test box and method: held-out value, or the median over 24 networks (n, P20 per 100 m2, P21, P22 per 100 m2, len_med, len_p90, nn_med, CL, pI, pY, pX, unclustered and OC1..OC4 shares) |
| final_table_all.csv, final_table_heldout_vs_EVAE.csv, final_tables.md | Tables 1 and 2 |
| stats_network_scores.csv | the 38 error scores of every network against its held-out box; n.d. = not defined (empty network, or fewer than 2 members of a cluster the held-out box has) |
| stats_box_medians.csv | box values (median over 24 networks) |
| stats_decisions.csv | EVAE against ADFNE and KDE per score and scheme: median difference, Holm p, result |
| stats_counts.csv | better / no difference / worse counts per group |
| stats_verdict.csv | three-way winner per scheme and overall verdict |
| *_penalty.csv | the same tables under the first-version rule (an undefined score counts as the worst value, 1e9); sensitivity check only |
| reference/ | the same tables as produced in the study, for `--check` (older names: "Real" = held-out, "Sets and background" = orientation clusters) |
