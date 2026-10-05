# -*- coding: utf-8 -*-
"""Step 1 icons of Fig. 1 (final review D7 and the authors' answer 7, 2 Oct 2026): Step 1 without photographs. Since the
author decision of 2 Oct 2026 (the mine operator does not permit photographs) these are THE Step 1 icons of Fig. 1; the
photograph icons are no longer used. No image file is opened (face widths from the metadata). Writes:
  f1_pit_drawn.png          'Open-pit mine': a drawn bench profile of an open pit (stepped walls with benches and berms),
                            with a UAV and dashed sight lines to one wall (the traces were mapped on a photogrammetric model)
  f1_traces_drawn.png       'Fracture labelling': traces only (no orthophoto), a crop of the mapped traces of bench faces
                            W02 to W04 (66 m along the wall), drawn in dark red with end points on light-grey bench faces (berms white)
  f1_panelgrid_nophoto.png  window-grid thumbnail as f1_panelgrid.png but without the orthomosaic: bench faces light grey,
                            traces coloured by trace-direction cluster (same all-window cluster model), window outlines
Data are read only (release library and traces_all.json via figdata / geobg_common). Sizes in cm as placed on the slide.
Run after make_icons.py and make_icons_geobg.py (independent of both)."""
import sys, json, math, glob, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem_paths as _SP                               # repository paths (schematics/schem_paths.py)   # puts paper_figures/ (geobg_common, figdata) on the path
sys.dont_write_bytecode = True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from PIL import Image
import geobg_common as GB
import figdata as D

C = D.C
OUT = str(_SP.ICON_OUT)
plt.rcParams.update({'font.family': 'Times New Roman', 'axes.linewidth': 0.6})
CMI = 1 / 2.54
NAVY = '#042433'
FACE = '#E4E4E4'
DPI = 1200


def save(fig, name, transparent=False):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=DPI, transparent=transparent)
    plt.close(fig)
    print('wrote', p)


# ============================================================== geometry of the stacked bench faces (as make_icons_geobg.py)
ROOT = C.BASE; ORDER = C.ORDER; PX = 0.02; R = 0.20
rows = {}
for f in sorted(glob.glob(str(ROOT / 'to_map_metadata' / 'W0?_*.json'))):
    m = json.load(open(f)); tag = m['image'][:3]
    if tag in ORDER:
        rows[tag] = dict(meta=m, H=m['height_px'] * PX, rl_top=float(m['RL_top']), dip=math.radians(m['face_dip_deg']), name=m['image'][:-4])
U0, U1 = -135.0, 29.0; GAP = 3.0
ytop, yy = {}, 0.0
for t in ORDER:
    ytop[t] = yy; yy += rows[t]['H'] + GAP
TOT = yy - GAP
NU = int(round((U1 - U0) / R))
u_cols = np.arange(NU) * R + U0 + R / 2
mask = np.zeros((int(round(TOT / R)), NU), bool)          # True where a bench face was mapped (metadata only)
for t, r in rows.items():
    wpx = int(r['meta']['width_px'])                                           # face width in pixels (metadata)
    h = int(round(r['H'] / R))
    if 'stitched_from' in r['meta']:
        col = (u_cols - r['meta']['u_along_wall_left_m']) / PX - 0.5
    else:
        g = np.load(ROOT / 'to_map_metadata' / (r['name'] + '_geometry.npz'))
        uu = np.asarray(g['u_along_wall_every_50px'], float); cc = np.arange(len(uu)) * 50.0; o_ = np.argsort(uu)
        col = np.interp(u_cols, uu[o_], cc[o_], left=np.nan, right=np.nan)
    ok = np.isfinite(col) & (col >= 0) & (col <= wpx - 1)
    y0 = int(round(ytop[t] / R)); mask[y0:y0 + h, ok] = True
face_rgb = np.full(mask.shape + (3,), 255, np.uint8)
face_rgb[mask] = (228, 228, 228)

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

# ============================================================== window-grid thumbnail without the orthomosaic
thumb_h = 1.98; thumb_w = thumb_h * (U1 - U0) / TOT
fig = plt.figure(figsize=(thumb_w * CMI, thumb_h * CMI)); ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(face_rgb, extent=(U0, U1, TOT, 0), interpolation='nearest')
for k, u1, a, u2, b in sorted(segs, key=lambda q: q[0] == 4, reverse=True):
    ax.plot([u1, u2], [a, b], color=GB.CLU_COL[k], lw=0.30, solid_capstyle='round')
for m in man:
    y = ytop[m['row']] + float(m['y_top'])
    if m['usable'] == 'True':
        ax.add_patch(Rectangle((float(m['u_left']), y), 20, float(m['height_m']), fill=False, ec=NAVY, lw=0.55))
    else:
        ax.add_patch(Rectangle((float(m['u_left']), y), 20, float(m['height_m']), fc='0.45', alpha=0.6, ec=NAVY, lw=0.55))
ax.add_patch(Rectangle((U0, 0), U1 - U0, TOT, fill=False, ec='black', lw=0.9))
ax.set_xlim(U0, U1); ax.set_ylim(TOT, 0); ax.axis('off')
save(fig, 'f1_panelgrid_nophoto.png')
print('thumbnail: traces per cluster', np.bincount([q[0] for q in segs], minlength=5).tolist(), 'of', len(segs))

# ============================================================== traces-only crop ('Fracture labelling')
IW, IH = 2.39, 1.97                                      # placed size (cm) of the photograph it replaces
CU0 = -112.0; CW = 66.0; CH = CW * IH / IW                 # crop along the wall (m) and down the stacked faces
CY0 = ytop['W02'] - 1.0
fig = plt.figure(figsize=(IW * CMI, IH * CMI)); ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(face_rgb, extent=(U0, U1, TOT, 0), interpolation='nearest')
n_in = 0
for k, u1, a, u2, b in segs:
    if max(u1, u2) < CU0 or min(u1, u2) > CU0 + CW or max(a, b) < CY0 or min(a, b) > CY0 + CH:
        continue
    n_in += 1
    ax.plot([u1, u2], [a, b], color='#B00000', lw=0.45, solid_capstyle='round', zorder=3)
    ax.plot([u1, u2], [a, b], ls='none', marker='o', ms=0.55, mfc='#B00000', mec='#B00000', zorder=4)
ax.add_patch(Rectangle((CU0, CY0), CW, CH, fill=False, ec='black', lw=1.0, zorder=5))
ax.set_xlim(CU0, CU0 + CW); ax.set_ylim(CY0 + CH, CY0); ax.axis('off')
save(fig, 'f1_traces_drawn.png')
print('traces-only crop: u %.0f to %.0f m, %d traces (bench faces W02 to W04)' % (CU0, CU0 + CW, n_in))

# ============================================================== drawn open-pit bench profile ('Open-pit mine')
PW, PH = 2.39, 1.95
fig, ax = plt.subplots(figsize=(PW * CMI, PH * CMI)); fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, PW); ax.set_ylim(0, PH); ax.set_aspect('equal'); ax.axis('off')
nb, bh, bw, fw = 5, 0.215, 0.115, 0.075               # benches, bench height, berm width, face run (cm)
top, xl = 1.42, 0.0
pts = [(xl, 0.0), (xl, top)]
x, y = xl, top
for i in range(nb):                                      # left wall: berm, face, berm, face ...
    x += bw; pts.append((x, y)); x += fw; y -= bh; pts.append((x, y))
xb0 = x; floor = y
xr = PW
x2 = xr; y2 = top; right = [(xr, top)]
for i in range(nb):
    x2 -= bw; right.append((x2, y2)); x2 -= fw; y2 -= bh; right.append((x2, y2))
pts += right[::-1] + [(xr, top), (xr, 0.0)]
ax.add_patch(Polygon(pts, closed=True, fc='#C9C9C9', ec='black', lw=0.6, joinstyle='miter', zorder=2))
# the mapped wall: the faces of the left wall drawn darker
x, y = xl, top
for i in range(nb):
    x += bw
    ax.plot([x, x + fw], [y, y - bh], color='#4D4D4D', lw=1.3, solid_capstyle='butt', zorder=3)
    x += fw; y -= bh
# UAV over the pit, dashed sight lines to the left wall
ux, uy = 1.45, 1.72
for dx in (-0.11, 0.11):
    ax.add_patch(Circle((ux + dx, uy + 0.035), 0.055, fc='white', ec='black', lw=0.45, zorder=6))
ax.add_patch(Rectangle((ux - 0.075, uy - 0.03), 0.15, 0.065, fc='#333333', ec='black', lw=0.4, zorder=7))
ax.plot([ux - 0.11, ux + 0.11], [uy + 0.035, uy + 0.035], color='black', lw=0.45, zorder=6)
for tx, ty in ((xl + bw + 0.5 * fw, top - 0.5 * bh), (xl + 3 * bw + 2.5 * fw, top - 2.5 * bh)):
    ax.plot([ux - 0.05, tx + 0.02], [uy - 0.04, ty], color='#555555', lw=0.45, ls=(0, (2.5, 1.5)), zorder=5)
ax.add_patch(Rectangle((0.004, 0.004), PW - 0.008, PH - 0.008, fill=False, ec='black', lw=1.0, zorder=8))   # frame, as the other icons
save(fig, 'f1_pit_drawn.png')
