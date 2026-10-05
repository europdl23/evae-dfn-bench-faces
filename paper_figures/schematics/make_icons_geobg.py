# -*- coding: utf-8 -*-
"""Icons of the methodology schematics that change with the geobg EVAE (DECISIONS_V2, 1 Oct 2026). Run AFTER
make_icons.py (which still draws the Step 2 sketches, the hold-out mini grids and every Fig. 3 icon; Fig. 3 is unchanged).
This script overwrites only (2 Oct 2026, author decision: no photographs; the Step 1 thumbnail on the bench photographs,
f1_panelgrid.png, is no longer drawn: Fig. 1 uses the drawn thumbnail of make_icons_nophoto.py; no image is read here):
  f1_neighbours.png  Fig. 1 Step 3: new example panel A (W03_C2, gap-filling test, fold index 2) and its 8 neighbouring
                     panels (held-out fractures removed), centre = EVAE realisation run seed 1337, draw 0
  f1_compare.png     Fig. 1 Step 4: panel A held-out, EVAE, ADFNE, KDE (run seed 1337, draw 0) in the method colours of
                     DECISIONS_V2 Section 5 (held-out black, EVAE #009E73, ADFNE #E69F00, KDE #56B4E9)
  f4_dirloss.png     Fig. 4 orientation-distribution loss icon, panel A (same realisation)
  f1_holdout.png     Fig. 1 Step 4 mini grids: the gap-filling fold that holds the new panel A (fold index 2), the new-bench
                     fold W03 and the new-stretch fold of columns C3-C4 (folds from the release data/splits)
and writes the new
  f4_clusters.png    Fig. 4 cluster-share loss icon: shares of C1-C4 and unclustered (U), mapped (white, black edge)
                     against generated (green), panel A, fold cluster model S1 fold index 2
  f1_rose.png,       Fig. 1 Step 4 thumbnails (FIXLIST_V2 G-06), as the gap-filling column of Fig. 7: trace-direction
  f1_lengths.png     rose and length histogram, held-out black outline, EVAE green fill, no tick labels
Data are read from the release (geobg_common, read-only). Sizes in cm as placed on the slide."""
import sys, json, math, glob, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem_paths as _SP                               # repository paths (schematics/schem_paths.py)   # puts paper_figures/ (geobg_common, figdata) on the path
sys.dont_write_bytecode = True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from scipy.stats import vonmises
import geobg_common as GB
import figdata as D

C = D.C
OUT = str(_SP.ICON_OUT)
plt.rcParams.update({'font.family': 'Times New Roman', 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6})
CMI = 1 / 2.54
NAVY = '#042433'
MCOL = {'Held-out': '#000000', 'EVAE': GB.METHOD_COL['EVAE'], 'ADFNE': GB.METHOD_COL['ADFNE'], 'KDE': GB.METHOD_COL['KDE']}
DPI = 1200

eA = GB.example('A'); S_, FI, BOX = eA['scheme'], eA['fold'], eA['panel']
assert (S_, BOX, eA['realisation']['run_seed'], eA['realisation']['draw']) == ('S1', 'W03_C2', 1337, 0)
SP = GB.split(S_, FI)
NETS = {'Held-out': SP['panels'][BOX]['lines'], **{m: GB.net(S_, m, FI, BOX, 1337, 0) for m in ('EVAE', 'ADFNE', 'KDE')}}
YM = GB.LIB[BOX]['y_max']
CMOD = GB.cluster_model(S_, FI)
print('panel A', BOX, 'fold index', FI, {k: len(v) for k, v in NETS.items()})


def canvas(w_cm, h_cm):
    fig = plt.figure(figsize=(w_cm * CMI, h_cm * CMI))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_cm); ax.set_ylim(h_cm, 0); ax.set_aspect('equal'); ax.axis('off')
    return fig, ax


def save(fig, name, transparent=True):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=DPI, transparent=transparent)
    plt.close(fig)
    print('wrote', p)


# ============================================================== Fig. 1, Step 1: traces by cluster (values file only; the
# thumbnail itself is drawn without photographs by make_icons_nophoto.py)
ROOT = C.BASE; ORDER = C.ORDER; PX = 0.02
rows = {}
for f in sorted(glob.glob(str(ROOT / 'to_map_metadata' / 'W0?_*.json'))):
    m = json.load(open(f)); tag = m['image'][:3]
    if tag in ORDER:
        rows[tag] = dict(meta=m, H=m['height_px'] * PX, rl_top=float(m['RL_top']), dip=math.radians(m['face_dip_deg']), name=m['image'][:-4])
GAP = 3.0
ytop, yy = {}, 0.0
for t in ORDER:
    ytop[t] = yy; yy += rows[t]['H'] + GAP
T = json.load(open(C.TRACES))['traces']
CM_ALL, _ = GB.fit_all_panels()
man = list(csv.DictReader(open(C.LIB / 'box_manifest.csv')))
segs = []
for tr in T:
    r = rows[tr['image'][:3]]; s = math.sin(r['dip'])
    u1, y1, u2, y2 = tr['u1_m'], (r['rl_top'] - tr['RL1']) / s, tr['u2_m'], (r['rl_top'] - tr['RL2']) / s
    th = math.atan2(y2 - y1, u2 - u1) % math.pi
    k = int(GB.clusters(np.array([[0.0, 0.0, math.cos(th), math.sin(th)]]), CM_ALL)[0])
    segs.append((k, u1, ytop[tr['image'][:3]] + y1, u2, ytop[tr['image'][:3]] + y2))
print('thumbnail: traces per cluster', np.bincount([q[0] for q in segs], minlength=5).tolist())

# ============================================================== Fig. 1, Step 3: held-out panel A from its 8 neighbouring panels
P = SP['panels']; b = P[BOX]
nbrs = GB.neighbours(SP, BOX)
G = 2.30; cell = G / 3.0; pad = 0.05
fig, ax = canvas(G, G)
for k in nbrs:
    q = P[k]; i, j = q['ri'] - b['ri'] + 1, q['col'] - b['col'] + 1
    x0, y0 = j * cell + pad / 2, i * cell + pad / 2; s_ = cell - pad
    ax.add_patch(Rectangle((x0, y0), s_, s_, fc='white', ec='#7F7F7F', lw=0.5, zorder=1))
    for (a1, b1, a2, b2) in np.asarray(q['lines']).reshape(-1, 4):
        ax.plot([x0 + a1 * s_, x0 + a2 * s_], [y0 + b1 * s_, y0 + b2 * s_], color='#8C8C8C', lw=0.35, zorder=2)
x0 = y0 = cell + pad / 2; s_ = cell - pad
for off in (0.10, 0.05):
    ax.add_patch(Rectangle((x0 + off, y0 - off), s_, s_, fc='white', ec=NAVY, lw=0.45, zorder=3))
ax.add_patch(Rectangle((x0, y0), s_, s_, fc='white', ec=NAVY, lw=0.8, zorder=4))
for (a1, b1, a2, b2) in np.asarray(NETS['EVAE']).reshape(-1, 4):
    ax.plot([x0 + a1 * s_, x0 + a2 * s_], [y0 + b1 * s_, y0 + b2 * s_], color=MCOL['EVAE'], lw=0.55, zorder=5)
cx = cy = G / 2
for k in nbrs:
    q = P[k]; i, j = q['ri'] - b['ri'] + 1, q['col'] - b['col'] + 1
    sx, sy = (j + 0.5) * cell, (i + 0.5) * cell
    dx, dy = cx - sx, cy - sy
    t_edge = 1 - (0.5 * cell) / max(abs(dx), abs(dy))
    ex, ey = sx + dx * (t_edge - 0.02), sy + dy * (t_edge - 0.02)
    ax.add_patch(FancyArrowPatch((sx + dx * 0.18, sy + dy * 0.18), (ex, ey), arrowstyle='-|>', mutation_scale=4.2, color=NAVY, lw=0.7, zorder=6,
                                 shrinkA=0, shrinkB=0))
save(fig, 'f1_neighbours.png')
print('neighbours of', BOX, nbrs)

# ============================================================== Fig. 1, Step 4: comparison icon (panel A, one realisation each)
CW, CH = 2.30, 2.62
fig, ax = canvas(CW, CH)
s_ = 0.95
for idx, meth in enumerate(['Held-out', 'EVAE', 'ADFNE', 'KDE']):
    X0 = 0.12 + (idx % 2) * (s_ + 0.16); Y0 = 0.33 + (idx // 2) * (s_ + 0.34)
    ax.add_patch(Rectangle((X0, Y0), s_, s_, fc='white', ec='black', lw=0.5))
    for (a1, b1, a2, b2) in np.asarray(NETS[meth]).reshape(-1, 4):
        ax.plot([X0 + a1 * s_, X0 + a2 * s_], [Y0 + b1 * s_, Y0 + b2 * s_], color=MCOL[meth], lw=0.6)
    ax.text(X0 + s_ / 2, Y0 - 0.04, meth, fontsize=8.6, ha='center', va='bottom', color='black')
save(fig, 'f1_compare.png')

# ============================================================== Fig. 1, Step 4: hold-out tests (mini panel grids)
man_u = {m['box']: m for m in man if m['usable'] == 'True'}
gap = GB.split('S1', FI)['test']
bench = [GB.split('S2', k)['test'] for k in range(7) if all(x.startswith('W03') for x in GB.split('S2', k)['test'])][0]
stretch = [GB.split('S3', k)['test'] for k in range(4) if 'W00_C3' in GB.split('S3', k)['test']][0]
print('gap-filling fold', gap); print('new-bench fold', bench); print('new-stretch fold', stretch)
BLUE = '#4E95D9'
HW, HH = 4.60, 1.42
fig, ax = canvas(HW, HH)
gw = 1.15; c_ = gw / 8.0; gh = 7 * c_
for gi, (name, held) in enumerate([('Hold-out', gap), ('Whole bench', bench), ('40 m stretch', stretch)]):
    X0 = (0.71, 2.28, 3.85)[gi] - gw / 2; Y0 = 0.03
    for bx, m in man_u.items():
        r_, c1 = int(m['row_index']), int(m['col']) - 1
        ax.add_patch(Rectangle((X0 + c1 * c_, Y0 + r_ * c_), c_, c_, fc=BLUE if bx in held else 'white', ec='#595959', lw=0.3))
    ax.text(X0 + gw / 2, Y0 + gh + 0.06, name, fontsize=8.6, ha='center', va='top')
save(fig, 'f1_holdout_round2_three_tests.png')   # round 3: f1_holdout.png is drawn by make_icons_round3.py

# ============================================================== Fig. 4: orientation-distribution loss icon (panel A)
thd = np.linspace(0, 180, 721); tr_ = np.radians(thd)


def smooth(th, kappa=20.0):
    g = np.zeros_like(thd)
    for t in th:
        g += vonmises.pdf(2 * tr_, kappa, loc=2 * t)
    return g / (g.sum() * (thd[1] - thd[0]))


th_m = GB.geom(NETS['Held-out'])[2]; th_g = GB.geom(NETS['EVAE'])[2]
DW, DH = 4.80, 2.80
fig = plt.figure(figsize=(DW * CMI, DH * CMI)); ax = fig.add_axes([0.10, 0.27, 0.78, 0.68])
gm, gg = smooth(th_m), smooth(th_g)
ax.plot(thd, gm, color='black', lw=1.6)
ax.plot(thd, gg, color=MCOL['EVAE'], lw=1.6)
ax.set_xlim(0, 180); ax.set_ylim(0, max(gm.max(), gg.max()) * 1.08)
ax.set_xticks([0, 90, 180]); ax.set_xticklabels(['0°', '90°', '180°'], fontsize=18)
ax.set_yticks([]); ax.tick_params(length=3, width=0.9, pad=1)
ax.patch.set_alpha(0)
for sname in ('top', 'right', 'left'):
    ax.spines[sname].set_visible(False)
ax.spines['bottom'].set_linewidth(1.0)
save(fig, 'f4_dirloss.png', transparent=True)

# ============================================================== Fig. 4: cluster-share loss icon (panel A, fold cluster model)
sh_m = np.bincount(GB.clusters(NETS['Held-out'], CMOD), minlength=5) / len(NETS['Held-out'])
sh_g = np.bincount(GB.clusters(NETS['EVAE'], CMOD), minlength=5) / len(NETS['EVAE'])
print('cluster shares held-out', np.round(sh_m, 3).tolist(), 'EVAE', np.round(sh_g, 3).tolist())
QW = 6.80                                                    # the cluster icon is wider (five 18 pt category labels)
fig = plt.figure(figsize=(QW * CMI, DH * CMI)); ax = fig.add_axes([0.04, 0.27, 0.92, 0.68])
x = np.arange(5); bw = 0.36
ax.bar(x - bw / 2 - 0.02, sh_m, bw, color='white', edgecolor='black', lw=1.2)
ax.bar(x + bw / 2 + 0.02, sh_g, bw, color=MCOL['EVAE'], edgecolor=MCOL['EVAE'], lw=0.8)
ax.set_xlim(-0.6, 4.6); ax.set_ylim(0, max(sh_m.max(), sh_g.max()) * 1.10)
ax.set_xticks(x); ax.set_xticklabels(['C1', 'C2', 'C3', 'C4', 'U'], fontsize=18)
ax.set_yticks([]); ax.tick_params(length=0, pad=2)
ax.patch.set_alpha(0)
for sname in ('top', 'right', 'left'):
    ax.spines[sname].set_visible(False)
ax.spines['bottom'].set_linewidth(1.0)
save(fig, 'f4_clusters.png', transparent=True)
# ============================================================== Fig. 1, Step 4: direction rose and length histogram (FIXLIST_V2 G-06)
# As the gap-filling column of Fig. 7 (release Fig_R2_geometry): all held-out panels of the gap-filling test against the
# EVAE (24 realisations per panel, each weighted 1/24); held-out black outline, EVAE green fill; no tick labels.
SEEDS, NDRAW = (1337, 20260903, 7), 8
th_h, ln_h, th_e, ln_e, w_e = [], [], [], [], []
for fi in range(4):
    sp_ = GB.split('S1', fi)
    for bx in sp_['test']:
        _, l_, t_ = GB.geom(sp_['panels'][bx]['lines']); th_h += list(t_); ln_h += list(l_ * GB.M)
        for sd in SEEDS:
            for d_ in range(NDRAW):
                L_ = GB.net('S1', 'EVAE', fi, bx, sd, d_)
                if len(L_):
                    _, l_, t_ = GB.geom(L_); th_e += list(t_); ln_e += list(l_ * GB.M); w_e += [1.0 / (len(SEEDS) * NDRAW)] * len(L_)
th_h, ln_h, th_e, ln_e, w_e = map(np.asarray, (th_h, ln_h, th_e, ln_e, w_e))
rb = np.radians(np.arange(0, 361, 10)); rc = rb[:-1] + np.radians(5)


def rose_share(th, w):
    h, _ = np.histogram(np.r_[th, th + np.pi], bins=rb, weights=np.r_[w, w]); return h / h.sum()


r_e, r_h = rose_share(th_e, w_e), rose_share(th_h, np.ones_like(th_h))
RW, RH = 1.50, 1.49
fig = plt.figure(figsize=(RW * CMI, RH * CMI)); ax = fig.add_axes([0.04, 0.04, 0.92, 0.92], projection='polar')
ax.bar(rc, r_e, width=np.radians(10), color=MCOL['EVAE'], alpha=0.75, edgecolor='white', linewidth=0.15)
ax.plot(np.r_[rc, rc[0]], np.r_[r_h, r_h[0]], color='black', lw=0.6)
ax.set_theta_zero_location('E'); ax.set_theta_direction(-1); ax.set_ylim(0, max(r_e.max(), r_h.max()) * 1.05)
ax.set_xticks(np.radians(np.arange(0, 360, 90))); ax.set_xticklabels([]); ax.set_yticks([]); ax.grid(lw=0.2, color='0.6')
ax.spines['polar'].set_linewidth(0.4)
save(fig, 'f1_rose.png')
lb_ = np.arange(0, 31, 1.0)
h_e = np.histogram(ln_e, bins=lb_, weights=w_e, density=True)[0]; h_h = np.histogram(ln_h, bins=lb_, density=True)[0]
LW_, LH_ = 1.62, 1.36
fig = plt.figure(figsize=(LW_ * CMI, LH_ * CMI)); ax = fig.add_axes([0.06, 0.06, 0.90, 0.90])
ax.bar(lb_[:-1] + 0.5, h_e, width=0.9, color=MCOL['EVAE'], alpha=0.75)
ax.step(lb_, np.r_[h_h, h_h[-1]], where='post', color='black', lw=0.6)
ax.set_xlim(0, 30); ax.set_ylim(0, max(h_e.max(), h_h.max()) * 1.08); ax.set_xticks([]); ax.set_yticks([])
for sname in ('top', 'right'):
    ax.spines[sname].set_visible(False)
for sname in ('bottom', 'left'):
    ax.spines[sname].set_linewidth(0.5)
ax.patch.set_alpha(0)
save(fig, 'f1_lengths.png')
print('Step 4 thumbnails: gap-filling test, %d held-out traces, %.0f EVAE traces per realisation set' % (len(th_h), w_e.sum()))

json.dump(dict(panel=BOX, scheme=S_, fold_index=FI, run_seed=1337, draw=0, neighbours=nbrs,
               step4_thumbnails=dict(test='gap-filling', heldout_traces=int(len(th_h)), evae_traces_weighted=float(w_e.sum()),
                                     rose_bins_deg=10, length_bins_m=1, evae_rose_share=r_e.tolist(), heldout_rose_share=r_h.tolist()),
               counts={k: int(len(v)) for k, v in NETS.items()}, cluster_shares_heldout=sh_m.tolist(), cluster_shares_evae=sh_g.tolist(),
               cluster_order='C1..C4, unclustered', thumbnail_traces_per_cluster=np.bincount([q[0] for q in segs], minlength=5).tolist()),
          open(os.path.join(OUT, 'icons_geobg_values.json'), 'w'), indent=1)
print('done')
