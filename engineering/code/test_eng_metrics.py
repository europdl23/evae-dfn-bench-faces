# -*- coding: utf-8 -*-
"""Unit checks of eng_metrics on hand-made networks with known answers (metres; panel 20 m x 20 m)."""
import math
import numpy as np
import eng_metrics as M

W = H = 20.0
# 1) one horizontal trace across the panel at y = 10
L = np.array([[0, 10, 20, 10]], float)
d = M.deformability(L, W, H)
assert abs(d['E_along'] - 1.0) < 1e-12, d
assert abs(d['E_down'] - 1 / (1 + 2 * math.pi * 0.25)) < 1e-12, d          # alpha_yy = 10^2 / 400
assert abs(d['aniso'] - 1.0) < 1e-12 and abs(d['soft_dir_deg'] - 90) < 1e-9, d
assert abs(M.percolation_p(L, W * H) - 1.0) < 1e-12
c = M.connectivity(L, W, H); assert c['span'] == 1.0 and c['largest_share'] == 1.0, c
# 2) persistence: horizontal trace x 5..15 at y = 10, horizontal lines every 0.5 m (offsets 0.25 .. 19.75)
L2 = np.array([[5, 10, 15, 10]], float)
r = M.persistence(L2, 0.0, W, H)
assert r['n_lines'] == 40 and abs(r['k_max'] - 0.5) < 1e-12 and abs(r['k_mean'] - 2 * 0.5 / 40) < 1e-12, r
#    two collinear traces with a 4 m rock bridge: k = (6 + 6) / 20 on the best line
L3 = np.array([[0, 10.1, 6, 10.1], [10, 10.1, 16, 10.1]], float)
r = M.persistence(L3, 0.0, W, H); assert abs(r['k_max'] - 0.6) < 1e-12, r
#    overlapping projections are counted once
L4 = np.array([[0, 10.1, 8, 10.1], [6, 10.2, 12, 10.2]], float)
r = M.persistence(L4, 0.0, W, H); assert abs(r['k_max'] - 0.6) < 1e-12, r
#    inclined lines (45 deg): only lines >= 10 m are used, all inside the panel
lines, u, v = M.lines_in_panel(math.radians(45), W, H)
assert all(t1 - t0 >= 10 for _, t0, t1 in lines) and len(lines) > 0
# 3) isotropic random cracks: E_along ~ E_down ~ 1 / (1 + pi rho)
rng = np.random.default_rng(1); n = 20000; th = rng.uniform(0, math.pi, n); c0 = rng.uniform(5, 15, (n, 2)); a = 0.05
Lr = np.column_stack((c0 - a * np.c_[np.cos(th), np.sin(th)], c0 + a * np.c_[np.cos(th), np.sin(th)]))
d = M.deformability(Lr, W, H); rho = n * a * a / (W * H)
assert abs(d['E_along'] - 1 / (1 + math.pi * rho)) < 0.005 and abs(d['E_down'] - 1 / (1 + math.pi * rho)) < 0.005 and d['aniso'] < 0.03, (d, rho)
# 4) spanning top-bottom through a crossing, not left-right; an isolated short trace stays its own cluster
L5 = np.array([[10, 0, 10, 12], [5, 11, 15, 11], [12, 11.2, 12, 20], [1, 1, 2, 2]], float)
lab = M.clusters(L5); assert lab[0] == lab[1] == lab[2] and lab[3] != lab[0], lab     # [2] touches [1] within 0.3 m
c = M.connectivity(L5, W, H); assert c['span'] == 1.0, c
L6 = np.array([[10, 0.5, 10, 12], [5, 11, 15, 11]], float)                                     # 0.5 m short of the top
assert M.connectivity(L6, W, H)['span'] == 0.0
print('all unit checks passed')
