# -*- coding: utf-8 -*-
"""Fig. 3 input thumbnails f3_panel_1..3.png and the output icon f3_out_direction.png only (final-paper review F6, 1 Oct 2026).

make_icons.py coloured the traces of the three input windows (W04_C2, W04_C3, W04_C4) with an old two-component rule in
blue and orange, and the colours came out reversed against the trace-direction cluster convention of Figs. 2, 6 and 7
(C1 blue '/', C2 orange '\\'). The EVAE input carries no cluster labels, so the traces are now drawn in the mapped-trace
colour of Fig. 4 (#333333). Same windows, size (3.0 cm), frame and line width as make_icons.py; nothing else is redrawn
(make_icons.py would also overwrite the geobg icons of make_icons_geobg.py). make_icons.py draws the same now."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem_paths as _SP                               # repository paths (schematics/schem_paths.py)
sys.path.insert(0, str(_SP.manuscript_code()))   # fig_common (not released)
sys.dont_write_bytecode = True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import fig_common as F

OUT = str(_SP.ICON_OUT)
CMI = 1 / 2.54
DPI = 1200
MAPPED = '#333333'      # mapped traces, as in Fig. 4 (FIXLIST_V2 G-06)
PS = 3.0


def canvas(w_cm, h_cm):
    fig = plt.figure(figsize=(w_cm * CMI, h_cm * CMI))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_cm); ax.set_ylim(h_cm, 0); ax.set_aspect('equal'); ax.axis('off')
    return fig, ax


for k_, bx in enumerate(['W04_C2', 'W04_C3', 'W04_C4']):
    fig, ax = canvas(PS, PS)
    ax.add_patch(Rectangle((0.02, 0.02), PS - 0.04, PS - 0.04, fc='white', ec='black', lw=0.8))
    Lb = np.asarray(F.LIB[bx]['lines']).reshape(-1, 4)
    for (a1, b1, a2, b2) in Lb:
        ax.plot([a1 * PS, a2 * PS], [b1 * PS, b2 * PS], color=MAPPED, lw=0.9)
    p = os.path.join(OUT, 'f3_panel_%d.png' % (k_ + 1))
    fig.savefig(p, dpi=DPI, transparent=False)
    plt.close(fig)
    print('wrote', p, len(Lb), 'traces')


# ---- f3_out_direction.png: same mixture as make_icons.py, component colours in the cluster convention (review F6):
# the component at about 125 deg is C1 (blue #0072B2), the one at about 50 deg is C2 (orange #D55E00)
import math
from scipy.stats import vonmises
OW, OH = 3.90, 2.50
fig = plt.figure(figsize=(OW * CMI, OH * CMI)); ax = fig.add_axes([0.13, 0.30, 0.70, 0.64])
thd = np.linspace(0, 180, 721); tr_ = np.radians(thd)
comp = [(0.55, 50.0, 6.0, '#D55E00'), (0.35, 125.0, 12.0, '#0072B2'), (0.10, 90.0, 1.5, '#7F7F7F')]
tot = np.zeros_like(thd)
for w_, mu, ka, col in comp:
    pdf = w_ * vonmises.pdf(2 * tr_, ka, loc=2 * math.radians(mu))
    tot += pdf
    ax.fill_between(thd, 0, pdf, color=col, alpha=0.30, lw=0)
    ax.plot(thd, pdf, color=col, lw=1.0, ls='--')
ax.plot(thd, tot, color='black', lw=1.4)
ax.set_xlim(0, 180); ax.set_ylim(0, tot.max() * 1.08)
ax.set_xticks([0, 90, 180]); ax.set_xticklabels(['0°', '90°', '180°'], fontsize=17, fontfamily='Times New Roman')
ax.set_yticks([]); ax.tick_params(length=3, width=0.8, pad=1)
for sname in ('top', 'right', 'left'):
    ax.spines[sname].set_visible(False)
ax.spines['bottom'].set_linewidth(0.9)
fig.patches.append(Rectangle((0.004, 0.006), 0.992, 0.988, transform=fig.transFigure, fill=False, ec='black', lw=0.8))
p = os.path.join(OUT, 'f3_out_direction.png')
fig.savefig(p, dpi=DPI, transparent=False)
plt.close(fig)
print('wrote', p)
