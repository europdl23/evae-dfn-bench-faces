# -*- coding: utf-8 -*-
"""Simple Fig. 2 (5 Oct 2026; the old rev_fig2_wall.py is kept). No photograph.
(a) the mapped wall (seven bench faces on one along-wall axis), the window grid outlined, the six unused windows
    hatched, the 705 mapped traces coloured C1 / C2 / other by the trace-direction cluster model fitted to all windows
    (G.fit_all_panels, as rev_fig2_wall.py).
(b) the same grid with the window roles of the hold-out fold that holds out example window A (W03-2), release S1 fold
    index 2 (roles checked against the geobg release split, as rev_fig2_wall.py).
Data read only. Outputs out/figures/Figure_2_simple.png/.pdf and Figure_2_simple_values.json."""
import json, math, glob, csv
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
import figstyle as S
import figdata as D
import rev_common as RC
import geobg_common as G
import round3_common as R3
C = D.C

ROOT = C.BASE; ORDER = C.ORDER; PX = 0.02
rows = {}
for f in sorted(glob.glob(str(ROOT / 'to_map_metadata' / 'W0?_*.json'))):
    m = json.load(open(f)); tag = m['image'][:3]
    if tag in ORDER:
        rows[tag] = dict(meta=m, H=m['height_px'] * PX, rl_top=float(m['RL_top']), dip=math.radians(m['face_dip_deg']))
U0, U1 = -135.0, 29.0; GAP = 1.0
ytop, yy = {}, 0.0
for t in ORDER:
    ytop[t] = yy; yy += rows[t]['H'] + GAP
TOT = yy - GAP

T = json.load(open(C.TRACES))['traces']
boxes = C.load_library()
CM_ALL, _ = G.fit_all_panels()
cc = CM_ALL['centres_deg']
assert all(abs(c_ - r_) <= 1.0 for c_, r_ in zip(cc, G.REF)), (cc, G.REF)
seg = []
for tr in T:
    r = rows[tr['image'][:3]]; s = math.sin(r['dip'])
    u1, y1, u2, y2 = tr['u1_m'], (r['rl_top'] - tr['RL1']) / s, tr['u2_m'], (r['rl_top'] - tr['RL2']) / s
    th = math.atan2(y2 - y1, u2 - u1) % math.pi
    k = int(G.clusters(np.array([[0.0, 0.0, math.cos(th), math.sin(th)]]), CM_ALL)[0])
    seg.append((tr['image'][:3], u1, y1, u2, y2, k))
man = list(csv.DictReader(open(C.LIB / 'box_manifest.csv')))

eA = R3.EXAMPLES[0]; A = eA['box']; FI = eA['fold']
assert A == 'W03_C2'
sp = C.split('S1', FI, boxes); spG = G.split('S1', FI)
assert sorted(sp['val']) == sorted(spG['val']) and sorted(sp['test']) == sorted(spG['test'])
role = {}
for m in man:
    b = m['box']
    role[b] = 'unused' if m['usable'] != 'True' else 'held' if b in sp['test'] else 'val' if b in sp['val'] else 'train'
assert role[A] == 'held'

COL = {0: '#0072B2', 1: '#D55E00', 2: '#CC79A7', 3: '#F0E442', 'o': '#BBBBBB'}   # paper cluster colours (CLU_COL)
cat = lambda k: k if k in (0, 1, 2, 3) else 'o'
FILL = {'held': '#000000', 'val': '#8C8C8C', 'train': '#E3E3E3', 'unused': 'white'}

FW = 14.65
AW = 5.8; AH = AW * TOT / (U1 - U0)
AX0 = 1.15; BX0 = AX0 + AW + 1.0
TOP_A = TOP_B = 0.7
FH = TOP_A + AH + 1.0 + 1.55
fig = plt.figure(figsize=(FW * S.CM, FH * S.CM))


def frame(ax, xlabel, ylabel=True):
    ax.set_xlim(U0, U1); ax.set_ylim(TOT, 0); ax.set_aspect('equal')
    ax.set_xticks([-120, -80, -40, 0]); ax.set_yticks(np.arange(0, TOT + 0.1, 40))
    ax.tick_params(labelsize=8, length=2.5, pad=1.5)
    if xlabel:
        ax.set_xlabel('Position along the wall (m)', fontsize=10, labelpad=2)
    if ylabel:
        ax.set_ylabel('Depth down the stacked faces (m)', fontsize=10, labelpad=2)
    else:
        ax.set_yticklabels([])
    for t in ORDER:
        ax.text(U1 + 1.5, ytop[t] + rows[t]['H'] / 2, t, ha='left', va='center', fontsize=8)


def windows(ax, roles):
    for m in man:
        b = m['box']; x = float(m['u_left']); y = ytop[m['row']] + float(m['y_top']); h = float(m['height_m'])
        if roles:
            ax.add_patch(Rectangle((x, y), 20, h, fc=FILL[role[b]], ec='none', zorder=1))
        if role[b] == 'unused':
            ax.add_patch(Rectangle((x, y), 20, h, fill=False, ec='0.45', lw=0, hatch='////', zorder=1.5))
        ax.add_patch(Rectangle((x, y), 20, h, fill=False, ec='#222222', lw=0.6, zorder=3))
        if roles:
            ax.text(x + 10, y + h / 2, m['col'], ha='center', va='center', fontsize=8, zorder=4,
                    color='white' if role[b] in ('held', 'val') else 'black',
                    bbox=dict(fc='white', ec='none', pad=0.6) if role[b] == 'unused' else None)


# (a)
ax = RC.axes_cm(fig, AX0, TOP_A, AW, AH)
windows(ax, False)
for tag, u1, y1, u2, y2, k in sorted(seg, key=lambda q: cat(q[5]) != 'o'):
    ax.plot([u1, u2], [ytop[tag] + y1, ytop[tag] + y2], color=COL[cat(k)], lw=0.7 if cat(k) == 'o' else 0.9,
            solid_capstyle='round', zorder=2)
frame(ax, True)
fig.text(AX0 / FW, 1 - (TOP_A - 0.15) / FH, '(a) Mapped traces', ha='left', va='bottom', fontsize=12)
n = Counter(cat(q[5]) for q in seg)
Ha = [Line2D([], [], color=COL[0], lw=1.6, label='C1 (about %.0f°)' % G.REF[0]),
      Line2D([], [], color=COL[1], lw=1.6, label='C2 (about %.0f°)' % G.REF[1]),
      Line2D([], [], color=COL[2], lw=1.6, label='C3 (about %.0f°)' % G.REF[2]),
      Line2D([], [], color=COL[3], lw=1.6, label='C4 (about %.0f°)' % G.REF[3]),
      Line2D([], [], color=COL['o'], lw=1.6, label='Unclustered')]
LY = 1 - (TOP_A + AH + 1.05) / FH
fig.legend(handles=Ha, loc='upper left', bbox_to_anchor=(AX0 / FW, LY), frameon=False, fontsize=10, ncol=2,
           handlelength=1.4, labelspacing=0.3, columnspacing=0.8, borderaxespad=0, borderpad=0)

# (b)
axb = RC.axes_cm(fig, BX0, TOP_B, AW, AH)
windows(axb, True)
frame(axb, True, ylabel=False)
fig.text(BX0 / FW, 1 - (TOP_B - 0.15) / FH, '(b) Window roles', ha='left', va='bottom', fontsize=12)
mA = [m for m in man if m['box'] == A][0]
axb.add_patch(Rectangle((float(mA['u_left']), ytop[mA['row']] + float(mA['y_top'])), 20, float(mA['height_m']),
                        fill=False, ec='#D55E00', lw=1.8, zorder=5))
Hb = [Patch(fc=FILL['held'], ec='#222222', lw=0.6, label='Held-out'),
      Patch(fc=FILL['val'], ec='#222222', lw=0.6, label='Validation'),
      Patch(fc=FILL['train'], ec='#222222', lw=0.6, label='Training'),
      Patch(fc='white', ec='0.45', hatch='////', lw=0.6, label='Not used'),
      Patch(fc=FILL['held'], ec='#D55E00', lw=1.6, label='Window A')]
fig.legend(handles=Hb, loc='upper left', bbox_to_anchor=(BX0 / FW, LY), frameon=False, fontsize=10, ncol=2,
           handlelength=1.4, labelspacing=0.3, columnspacing=0.8, borderaxespad=0, borderpad=0)

probs = S.check_layout(fig, (8, 10, 12))
if probs:
    fig.savefig(RC.PREVIEW / 'Figure_2_simple_FAIL.png', dpi=150)
    raise SystemExit('\n'.join(probs))
for ext in ('png', 'pdf'):
    fig.savefig(RC.OUT / ('Figure_2_simple.' + ext), dpi=600 if ext == 'png' else None)
rc = Counter(role.values())
vals = dict(fold='hold-out test, release S1 fold index %d' % FI, window_A=RC.wid(A), traces=len(seg),
            traces_C1=n[0], traces_C2=n[1], traces_other=n['o'], role_counts=dict(rc),
            held_out=[RC.wid(b) for b in sorted(sp['test'])], validation=[RC.wid(b) for b in sorted(sp['val'])],
            cluster_centres_deg=list(map(float, cc)), size_cm=[FW, FH])
json.dump(vals, open(RC.OUT / 'Figure_2_simple_values.json', 'w'), indent=1)
print(json.dumps(vals))
