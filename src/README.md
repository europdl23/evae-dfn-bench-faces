# Source code

| File | What it does | Origin |
|---|---|---|
| `repo_paths.py` | every path, relative to the repository root (marker file `.repo-root`) | new |
| `model/training.py` | the dual-latent EVAE, its losses and the training loop, plus the two guidance terms `generated_direction_w1` (`EVGEO_W`) and `generated_class_share_l1` (`EVBG_W`) | Paper 1 release + the two terms; with both weights 0 it is the release code |
| `model/utils.py`, `model/utils_additions.py` | helpers of the training code | Paper 1 release, unchanged |
| `evaluation/common.py` | geometry, clipping, crossings, nearest-neighbour distances, W1 distances, the 2-set orientation fit, `gen_seed` | Paper 1 release, unchanged |
| `evaluation/generators.py` | EVAE loader, ADFNE and KDE generators, `fit_baseline_stats`, `quota` | Paper 1 release, unchanged |
| `model_ablation/training.py` | the EVAE code plus the two ablation switches: single latent (`EVFIX_SINGLE_LATENT`, Paper 1 `SingleLatentVAE`) and the geology-term weight (`EVFIX_WGEO`); at the EVAE's settings it is the EVAE code | new, for the ablation |
| `study/ablation.py` | ablation arms, model and network paths, single-latent loader and generator | new |
| `study/study.py` | box library, the three held-out schemes, fold split, context boxes, fold data, EVAE posterior generation, batched ADFNE, network files, seeds | study code, paths made relative |
| `study/setbg.py` | learned orientation clusters: axial von Mises mixture + uniform component, EM, K by BIC | study code, unchanged |
| `study/topology.py` | node types I / Y / X and connections per trace | study code, unchanged |
| `study/figstyle.py` | figure style (Times New Roman: 12 pt normal text, 10 pt tick labels, values and legends, 8 pt notes; figures at print size, 16 cm wide) and the layout check every figure must pass (fonts, sizes, no overlapping text, nothing outside, no text on data or other panels) | study code, extended |
| `baselines/adfne_octave/` | launchers and the Octave shim for ADFNE 1.5 (ADFNE itself is not included) | Paper 1 release |

The scripts in `../scripts/` are the entry points; nothing here needs to be run directly.
