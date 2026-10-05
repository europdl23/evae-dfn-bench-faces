# -*- coding: utf-8 -*-
"""Helper images for the methodology schematics (Figs. 1, 3, 4). Every image is drawn at its placed size on the slide
(cm), so font sizes here are slide point sizes. FIXLIST G-4: every label prints at 8 pt or more at 14.65 cm (Fig. 1 prints at
0.933 of slide size: 9 pt; Fig. 3 at 0.473: 17 pt; Fig. 4 at about 0.45: 18 pt). Real data: case A (held-out panel W04_C3, gap-filling test, training seed
20260903, realisation 3; facts/EXAMPLE_BOXES.json), its 8 neighbouring panels and the 50-panel grid.
2 Oct 2026 (author decision: the mine operator does not permit photographs): the Step 1 thumbnail on the bench
photographs (f1_panelgrid.png) is no longer drawn; Fig. 1 uses the drawn thumbnail of make_icons_nophoto.py. No image is read."""
import sys, json, math, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem_paths as _SP                               # repository paths (schematics/schem_paths.py)
sys.path.insert(0, str(_SP.manuscript_code()))   # fig_common (not released)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Arc
from scipy.stats import vonmises
import fig_common as F

C = F.C
OUT = str(_SP.ICON_OUT)
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.family': 'Times New Roman', 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6})
CMI = 1 / 2.54
NAVY, LBLUE, TEAL, BLUE = '#042433', '#C1E5F5', '#156082', '#4E95D9'
SET = ['#0072B2', '#D55E00']
MCOL = {'Mapped': '#000000', 'EVAE': '#009E73', 'ADFNE': '#CC79A7', 'KDE': '#666666'}
DPI = 1200


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


cs = F.case('A')
LIB = F.LIB
sp = C.split(cs['scheme'], cs['fold'], LIB)
rule = cs['rule']

# ============================================================== Fig. 1, Step 2 sketches (same style, redrawn crisp)
W2, H2 = 2.40, 1.98


def frame(ax, w, h, lw=0.9):
    ax.add_patch(Rectangle((0.03, 0.03), w - 0.06, h - 0.06, fill=True, fc='white', ec='black', lw=lw, zorder=0))


def endpoint(ax, x, y, r=0.13):
    ax.add_patch(Circle((x, y), r, fc=LBLUE, ec=NAVY, lw=0.7, zorder=5))


# (a) centre of line
fig, ax = canvas(W2, H2); frame(ax, W2, H2)
p1, p2 = (0.62, 1.62), (1.62, 0.34)
ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', lw=0.9, zorder=2)
endpoint(ax, *p1); endpoint(ax, *p2)
mc = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
ax.add_patch(Circle(mc, 0.15, fc='#FF0000', ec=NAVY, lw=0.7, zorder=6))
ax.text(mc[0] + 0.22, mc[1] + 0.22, '(x, y)', fontsize=9, va='top', ha='left')
save(fig, 'f1_centre.png', transparent=False)

# (b) length of line
fig, ax = canvas(W2, H2); frame(ax, W2, H2)
p1, p2 = (0.95, 1.62), (1.80, 0.34)
ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', lw=0.9, zorder=2)
endpoint(ax, *p1); endpoint(ax, *p2)
d = np.array(p2) - np.array(p1); n = np.array([-d[1], d[0]]) / np.hypot(*d)
o = -0.30 * n
ax.add_patch(FancyArrowPatch((p1[0] + o[0], p1[1] + o[1]), (p2[0] + o[0], p2[1] + o[1]), arrowstyle='<|-|>', mutation_scale=5,
                             color=TEAL, lw=0.8, shrinkA=2, shrinkB=2))
ax.text(0.78, 0.86, 'l', fontsize=9, style='italic', ha='center', va='center')
save(fig, 'f1_length.png', transparent=False)

# (c) angle of line: measured clockwise from the along-wall axis x, y pointing down the face; axial 0-180 deg
fig, ax = canvas(W2, H2); frame(ax, W2, H2)
ox, oy = 0.22, 0.26                                           # axis indicator, top-left
ax.add_patch(FancyArrowPatch((ox, oy), (ox + 0.45, oy), arrowstyle='-|>', mutation_scale=4.5, color='black', lw=0.6, shrinkA=0, shrinkB=0))
ax.add_patch(FancyArrowPatch((ox, oy), (ox, oy + 0.45), arrowstyle='-|>', mutation_scale=4.5, color='black', lw=0.6, shrinkA=0, shrinkB=0))
ax.text(ox + 0.50, oy, 'x', fontsize=9, style='italic', va='center', ha='left')
ax.text(ox, oy + 0.52, 'y', fontsize=9, style='italic', va='top', ha='center')
th = math.radians(50.0)
A_ = (1.08, 0.55); Lr = 1.22
B_ = (A_[0] + Lr * math.cos(th), A_[1] + Lr * math.sin(th))         # y down: positive angle goes down the face
ax.plot([A_[0], A_[0] + 1.00], [A_[1], A_[1]], color='black', lw=1.2, zorder=2)      # reference (along-wall) line
ax.plot([A_[0], B_[0]], [A_[1], B_[1]], color='black', lw=0.9, zorder=2)
# arc clockwise on screen from +x down to the line (y axis inverted, so theta1=0..50 in data coords draws downward)
ax.add_patch(Arc(A_, 0.80, 0.80, angle=0, theta1=0, theta2=50, color='black', lw=0.7))
ax.text(A_[0] + 0.55 * math.cos(th / 2), A_[1] + 0.55 * math.sin(th / 2), 'θ', fontsize=9, ha='left', va='center')
endpoint(ax, *A_); endpoint(ax, *B_)
ax.text(0.14, H2 - 0.10, '0°–180°', fontsize=9, ha='left', va='bottom')
save(fig, 'f1_angle.png', transparent=False)

# ============================================================== Fig. 1, Step 1: window grid (no thumbnail here, see make_icons_nophoto.py)
import csv
T = json.load(open(C.TRACES))['traces']
man = list(csv.DictReader(open(C.LIB / 'box_manifest.csv')))
n_usable = sum(1 for m in man if m['usable'] == 'True')
print('usable panels', n_usable, 'traces', len(T))

# ============================================================== Fig. 1, Step 3: held-out panel from its 8 neighbouring panels
P = sp['panels']; b = P[cs['box']]
nbrs = C.context(sp, cs['box'])
G = 2.30; cell = G / 3.0; pad = 0.05
fig, ax = canvas(G, G)
for k in nbrs:
    q = P[k]; i, j = q['ri'] - b['ri'] + 1, q['col'] - b['col'] + 1
    x0, y0 = j * cell + pad / 2, i * cell + pad / 2; s_ = cell - pad
    ax.add_patch(Rectangle((x0, y0), s_, s_, fc='white', ec='#7F7F7F', lw=0.5, zorder=1))
    for (a1, b1, a2, b2) in np.asarray(q['lines']).reshape(-1, 4):
        ax.plot([x0 + a1 * s_, x0 + a2 * s_], [y0 + b1 * s_, y0 + b2 * s_], color='#8C8C8C', lw=0.35, zorder=2)
# centre = held-out panel, filled with one EVAE realisation
x0 = y0 = cell + pad / 2; s_ = cell - pad
# two offset frames behind: several realisations
for off in (0.10, 0.05):
    ax.add_patch(Rectangle((x0 + off, y0 - off), s_, s_, fc='white', ec=NAVY, lw=0.45, zorder=3))
ax.add_patch(Rectangle((x0, y0), s_, s_, fc='white', ec=NAVY, lw=0.8, zorder=4))
for (a1, b1, a2, b2) in np.asarray(F.lines(cs, 'EVAE')).reshape(-1, 4):
    ax.plot([x0 + a1 * s_, x0 + a2 * s_], [y0 + b1 * s_, y0 + b2 * s_], color=MCOL['EVAE'], lw=0.55, zorder=5)
cx = cy = G / 2
for k in nbrs:
    q = P[k]; i, j = q['ri'] - b['ri'] + 1, q['col'] - b['col'] + 1
    sx, sy = (j + 0.5) * cell, (i + 0.5) * cell
    dx, dy = cx - sx, cy - sy; L_ = math.hypot(dx, dy)
    ex, ey = sx + dx * (1 - 0.43 * cell / L_ * (1.0 if (dx and dy) else 1.0) / (max(abs(dx), abs(dy)) / L_)), 0
    # stop at the centre cell edge
    t_edge = 1 - (0.5 * cell) / max(abs(dx), abs(dy))
    ex, ey = sx + dx * (t_edge - 0.02), sy + dy * (t_edge - 0.02)
    ax.add_patch(FancyArrowPatch((sx + dx * 0.18, sy + dy * 0.18), (ex, ey), arrowstyle='-|>', mutation_scale=4.2, color=NAVY, lw=0.7, zorder=6,
                                 shrinkA=0, shrinkB=0))
save(fig, 'f1_neighbours.png')
print('neighbours of', cs['box'], nbrs)

# ============================================================== Fig. 1, Step 4: hold-out tests (mini panel grids)
usable = {m['box']: m for m in man if m['usable'] == 'True'}
f1 = [sorted(f) for f in C.folds('S1', LIB)]; f2 = [sorted(f) for f in C.folds('S2', LIB)]; f3 = [sorted(f) for f in C.folds('S3', LIB)]
gap = next(f for f in f1 if cs['box'] in f)
bench = next(f for f in f2 if all(x.startswith('W03') for x in f))
stretch = next(f for f in f3 if 'W00_C3' in f)
print('gap-filling fold', gap); print('new-bench fold', bench); print('new-stretch fold', stretch)
HW, HH = 4.60, 1.42                     # wider (G-4) so the three 8.6 pt names (8.0 pt printed) fit on one line each
fig, ax = canvas(HW, HH)
gw = 1.15; c_ = gw / 8.0; gh = 7 * c_
for gi, (name, held) in enumerate([('Hold-out', gap), ('Whole bench', bench), ('40 m stretch', stretch)]):
    X0 = (0.71, 2.28, 3.85)[gi] - gw / 2; Y0 = 0.03
    for bx, m in usable.items():
        r_, c1 = int(m['row_index']), int(m['col']) - 1
        fc = BLUE if bx in held else 'white'
        ax.add_patch(Rectangle((X0 + c1 * c_, Y0 + r_ * c_), c_, c_, fc=fc, ec='#595959', lw=0.3))
    ax.text(X0 + gw / 2, Y0 + gh + 0.06, name, fontsize=8.6, ha='center', va='top')
save(fig, 'f1_holdout_round2_three_tests.png')   # round 3: f1_holdout.png is drawn by make_icons_round3.py

# ============================================================== Fig. 1, Step 4: comparison icon (case A, one realisation each)
CW = 2.30; CH = 2.62
fig, ax = canvas(CW, CH)
s_ = 0.95
for idx, meth in enumerate(['Mapped', 'EVAE', 'ADFNE', 'KDE']):
    X0 = 0.12 + (idx % 2) * (s_ + 0.16); Y0 = 0.33 + (idx // 2) * (s_ + 0.34)
    ax.add_patch(Rectangle((X0, Y0), s_, s_, fc='white', ec='black', lw=0.5))
    for (a1, b1, a2, b2) in np.asarray(F.lines(cs, meth)).reshape(-1, 4):
        ax.plot([X0 + a1 * s_, X0 + a2 * s_], [Y0 + b1 * s_, Y0 + b2 * s_], color=MCOL[meth], lw=0.5)
    ax.text(X0 + s_ / 2, Y0 - 0.04, meth, fontsize=8.6, ha='center', va='bottom', color='black')
save(fig, 'f1_compare.png')

# ============================================================== Fig. 3 inputs: three 20 m panels (mapped traces, set colours)
PS = 3.0
for k_, bx in enumerate(['W04_C2', 'W04_C3', 'W04_C4']):
    fig, ax = canvas(PS, PS)
    ax.add_patch(Rectangle((0.02, 0.02), PS - 0.04, PS - 0.04, fc='white', ec='black', lw=0.8))
    Lb = np.asarray(LIB[bx]['lines']).reshape(-1, 4)
    # final-paper review F6: traces in the mapped-trace colour (the two-component colours were reversed against the
    # C1/C2 cluster convention of Figs. 2, 6, 7); same as make_icons_fig3_inputs.py, which redraws only these three icons
    for (a1, b1, a2, b2) in Lb:
        ax.plot([a1 * PS, a2 * PS], [b1 * PS, b2 * PS], color='#333333', lw=0.9)
    save(fig, 'f3_panel_%d.png' % (k_ + 1), transparent=False)

# ============================================================== Fig. 3 outputs
OW, OH = 3.90, 2.50
Lev = np.asarray(F.lines(cs, 'EVAE')).reshape(-1, 4)
sel = Lev[np.argsort(-np.hypot(Lev[:, 2] - Lev[:, 0], Lev[:, 3] - Lev[:, 1]))[:6]]


def to_icon(L_, w, h, m=0.12):
    return [(m + a1 * (w - 2 * m), m + b1 * (h - 2 * m), m + a2 * (w - 2 * m), m + b2 * (h - 2 * m)) for a1, b1, a2, b2 in L_]


# centres
fig, ax = canvas(OW, OH)
ax.add_patch(Rectangle((0.02, 0.02), OW - 0.04, OH - 0.04, fc='white', ec='black', lw=0.8))
for a1, b1, a2, b2 in to_icon(sel, OW, OH):
    ax.plot([a1, a2], [b1, b2], color='black', lw=1.1, zorder=2)
    ax.add_patch(Circle(((a1 + a2) / 2, (b1 + b2) / 2), 0.12, fc='#FF0000', ec='black', lw=0.7, zorder=3))
save(fig, 'f3_out_centres.png', transparent=False)
# length
fig, ax = canvas(OW, OH)
ax.add_patch(Rectangle((0.02, 0.02), OW - 0.04, OH - 0.04, fc='white', ec='black', lw=0.8))
Ls = to_icon(sel, OW, OH)
for a1, b1, a2, b2 in Ls:
    ax.plot([a1, a2], [b1, b2], color='black', lw=1.1)
a1, b1, a2, b2 = Ls[0]; d = np.array([a2 - a1, b2 - b1]); n = np.array([-d[1], d[0]]) / np.hypot(*d)
o = 0.22 * n
ax.add_patch(FancyArrowPatch((a1 + o[0], b1 + o[1]), (a2 + o[0], b2 + o[1]), arrowstyle='<|-|>', mutation_scale=9, color=TEAL, lw=1.1,
                             shrinkA=0, shrinkB=0))
ax.text((a1 + a2) / 2 + 2.3 * o[0], (b1 + b2) / 2 + 2.3 * o[1], 'l', fontsize=17, style='italic', ha='center', va='center')
save(fig, 'f3_out_length.png', transparent=False)
# direction mixture: one slot's axial von Mises mixture, three components (weight, mean, concentration)
fig = plt.figure(figsize=(OW * CMI, OH * CMI)); ax = fig.add_axes([0.13, 0.30, 0.70, 0.64])
thd = np.linspace(0, 180, 721); tr_ = np.radians(thd)
comp = [(0.55, 50.0, 6.0, SET[1]), (0.35, 125.0, 12.0, SET[0]), (0.10, 90.0, 1.5, '#7F7F7F')]   # review F6: C1 blue at about 125 deg
tot = np.zeros_like(thd)
for w_, mu, ka, col in comp:
    pdf = w_ * vonmises.pdf(2 * tr_, ka, loc=2 * math.radians(mu))
    tot += pdf
    ax.fill_between(thd, 0, pdf, color=col, alpha=0.30, lw=0)
    ax.plot(thd, pdf, color=col, lw=1.0, ls='--')
ax.plot(thd, tot, color='black', lw=1.4)
ax.set_xlim(0, 180); ax.set_ylim(0, tot.max() * 1.08)
ax.set_xticks([0, 90, 180]); ax.set_xticklabels(['0°', '90°', '180°'], fontsize=17)
ax.set_yticks([]); ax.tick_params(length=3, width=0.8, pad=1)
for sname in ('top', 'right', 'left'):
    ax.spines[sname].set_visible(False)
ax.spines['bottom'].set_linewidth(0.9)
fig.patches.append(Rectangle((0.004, 0.006), 0.992, 0.988, transform=fig.transFigure, fill=False, ec='black', lw=0.8))
save(fig, 'f3_out_direction.png', transparent=False)
# existence: kept slots (existence >= 0.5) as black traces, empty slots grey dashed, as in Fig. 4 (G-4)
fig, ax = canvas(OW, OH)
ax.add_patch(Rectangle((0.02, 0.02), OW - 0.04, OH - 0.04, fc='white', ec='black', lw=0.8))
rng = np.random.default_rng(7)
for i, (a1, b1, a2, b2) in enumerate(to_icon(Lev[:7], OW, OH)):
    ax.plot([a1, a2], [b1, b2], color='black', lw=1.3)
for _ in range(4):
    c0 = rng.uniform([0.4, 0.4], [OW - 0.4, OH - 0.4]); ang = rng.uniform(0, math.pi); l_ = rng.uniform(0.5, 1.1)
    ax.plot([c0[0] - l_ / 2 * math.cos(ang), c0[0] + l_ / 2 * math.cos(ang)], [c0[1] - l_ / 2 * math.sin(ang), c0[1] + l_ / 2 * math.sin(ang)],
            color='#7F7F7F', lw=1.1, ls=(0, (2.5, 2)))
save(fig, 'f3_out_exist.png', transparent=False)

# ============================================================== Fig. 4: orientation-distribution loss icon (case A)
Lm = np.asarray(cs['real']['lines']).reshape(-1, 4)
th_m = C.common.geom(Lm)[2]; th_g = C.common.geom(Lev)[2]


def smooth(th, kappa=20.0):
    g = np.zeros_like(thd)
    for t in th:
        g += vonmises.pdf(2 * tr_, kappa, loc=2 * t)
    return g / (g.sum() * (thd[1] - thd[0]))


DW, DH = 4.80, 2.80
fig = plt.figure(figsize=(DW * CMI, DH * CMI)); ax = fig.add_axes([0.10, 0.27, 0.78, 0.68])
gm, gg = smooth(th_m), smooth(th_g)
ax.fill_between(thd, gm, gg, color='#FFFFFF', alpha=0.75, lw=0)
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

# Fig. 4 model predictions: existence panel in the style of the other prediction panels (grey #D1D1D1, black traces)
EW, EH = 6.62, 2.60
fig, ax = canvas(EW, EH)
ax.add_patch(Rectangle((0.02, 0.02), EW - 0.04, EH - 0.04, fc='#D1D1D1', ec='black', lw=1.0))
kept = to_icon(Lev[:7], EW, EH, m=0.25)
for a1, b1, a2, b2 in kept:
    ax.plot([a1, a2], [b1, b2], color='black', lw=1.3)
rng = np.random.default_rng(11)
for _ in range(5):
    c0 = rng.uniform([0.6, 0.4], [EW - 0.6, EH - 0.4]); ang = rng.uniform(0, math.pi); l_ = rng.uniform(0.6, 1.3)
    ax.plot([c0[0] - l_ / 2 * math.cos(ang), c0[0] + l_ / 2 * math.cos(ang)], [c0[1] - l_ / 2 * math.sin(ang), c0[1] + l_ / 2 * math.sin(ang)],
            color='#7F7F7F', lw=1.1, ls=(0, (2.5, 2)))
save(fig, 'f4_exist.png', transparent=False)
print('done')
