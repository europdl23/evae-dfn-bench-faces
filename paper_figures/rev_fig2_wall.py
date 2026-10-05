# -*- coding: utf-8 -*-
"""Fig. 2 of round 3 (PLAN_ROUND3 Section C and H4; replaces the old Figs. 2 and 5): the wall and the window roles of
one fold of the hold-out test, and the trace-direction clusters.
(a) seven bench faces on one along-wall axis (face extents in very light grey, no photograph), the 705 mapped traces
    coloured by trace-direction cluster, and the 56 window positions of the window grid with their roles in fold 3 of
    the hold-out test (release S1, fold index 2): held-out window A (W03-2), its 8 surrounding windows, the other
    held-out windows of the fold, the validation windows, the training windows and the 6 unused windows.
    Surrounding windows are training windows of the fold (they are mapped and used for training); a window that is
    both surrounding and validation is drawn as surrounding with the validation dots.
(b) rose of the trace directions of the 735 clipped traces (10° bins, both ends of the axis), bars stacked by
    trace-direction cluster C1 to C4 and unclustered traces (cluster model fitted to all 735 clipped traces, release
    setbg.fit, seed 20261001, as the old Fig. 2b; the folds use training windows only).
Moved to the Supplement (H4): the trace-length histogram and the complete fold map (Figure_S1, rev_figS1_folds.py).
Data read only (as rev_fig2_site.py): bench-face metadata, traces_all.json, the window library, the release cluster
model and folds (fold roles checked against the geobg release split, as rev_fig5_holdout.py).
Values to out/figures/Figure_2_values.json."""
import json, math, glob, csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import figstyle as S
import figdata as D
import rev_common as RC
import geobg_common as G
import round3_common as R3
C = D.C

ROOT = C.BASE; ORDER = C.ORDER; PX = 0.02; R = 0.10
rows = {}
for f in sorted(glob.glob(str(ROOT / 'to_map_metadata' / 'W0?_*.json'))):
    m = json.load(open(f)); tag = m['image'][:3]
    if tag in ORDER:
        rows[tag] = dict(meta=m, H=m['height_px'] * PX, rl_top=float(m['RL_top']), dip=math.radians(m['face_dip_deg']), name=m['image'][:-4])
U0, U1 = -135.0, 29.0; GAP = 1.0
ytop, yy = {}, 0.0
for t in ORDER:
    ytop[t] = yy; yy += rows[t]['H'] + GAP
TOT = yy - GAP
NU = int(round((U1 - U0) / R)); u_cols = np.arange(NU) * R + U0 + R / 2
plain = np.full((int(round(TOT / R)), NU, 3), 255, np.uint8)
for t, r in rows.items():
    h = int(round(r['H'] / R))
    if 'stitched_from' in r['meta']:
        col = (u_cols - r['meta']['u_along_wall_left_m']) / PX - 0.5
    else:
        g = np.load(ROOT / 'to_map_metadata' / (r['name'] + '_geometry.npz'))
        uu = np.asarray(g['u_along_wall_every_50px'], float); cc = np.arange(len(uu)) * 50.0; o = np.argsort(uu)
        col = np.interp(u_cols, uu[o], cc[o], left=np.nan, right=np.nan)
    ok = np.isfinite(col) & (col >= 0) & (col <= r['meta']['width_px'] - 1)
    y0 = int(round(ytop[t] / R)); plain[y0:y0 + h, ok] = 238

T = json.load(open(C.TRACES))['traces']
boxes = C.load_library()
ang_all = np.concatenate([C.common.geom(b['lines'])[2] for b in boxes.values() if len(b['lines'])])
CM_ALL, th_rel = G.fit_all_panels()
assert len(th_rel) == len(ang_all) == 735
seg = []
for tr in T:
    r = rows[tr['image'][:3]]; s = math.sin(r['dip'])
    u1, y1, u2, y2 = tr['u1_m'], (r['rl_top'] - tr['RL1']) / s, tr['u2_m'], (r['rl_top'] - tr['RL2']) / s
    th = math.atan2(y2 - y1, u2 - u1) % math.pi
    seg.append((tr['image'][:3], u1, y1, u2, y2, int(G.clusters(np.array([[0.0, 0.0, math.cos(th), math.sin(th)]]), CM_ALL)[0])))
man = list(csv.DictReader(open(C.LIB / 'box_manifest.csv')))

# roles of fold 3 of the hold-out test (window A)
eA = R3.EXAMPLES[0]; A = eA['box']; FI = eA['fold']
sp = C.split('S1', FI, boxes); ctx = C.context(sp, A); spG = G.split('S1', FI)
assert sorted(ctx) == sorted(G.neighbours(spG, A)) and sorted(sp['val']) == sorted(spG['val']) and sorted(sp['test']) == sorted(spG['test'])
STY = {'A': dict(fc='#000000', alpha=0.55), 'sur': dict(fc='#4A4A4A', alpha=0.5), 'test': dict(fc='white', alpha=1.0, hatch='xxx'),
       'val': dict(fc='white', alpha=1.0, hatch='...'), 'fit': dict(fc='white', alpha=0.0), 'unused': dict(fc='0.15', alpha=0.45, hatch='///')}
role = {}
for m in man:
    b = m['box']
    if m['usable'] != 'True':
        role[b] = 'unused'
    elif b == A:
        role[b] = 'A'
    elif b in ctx:
        role[b] = 'sur+val' if b in sp['val'] else 'sur'
    elif b in sp['test']:
        role[b] = 'test'
    elif b in sp['val']:
        role[b] = 'val'
    else:
        role[b] = 'fit'

FW = 14.65
A_TOP, AX0, AWmax = 0.75, 1.15, 13.35
BS = 4.6
AH = 19.45 - A_TOP - 2.45 - BS - 0.55; AW = min(AWmax, AH * (U1 - U0) / TOT); AH = AW * TOT / (U1 - U0)
AX0 = AX0 + (AWmax - AW) / 2
B_TOP = A_TOP + AH + 2.45
FH = B_TOP + BS + 0.55
assert FH <= 19.5, FH
fig = plt.figure(figsize=(RC.W, FH * S.CM))
ax = RC.axes_cm(fig, AX0, A_TOP, AW, AH)
ax.imshow(plain, extent=(U0, U1, TOT, 0), interpolation='none', zorder=0)
for t, r in rows.items():
    ax.text(U0 - 1.5, ytop[t] + r['H'] / 2, t, ha='right', va='center', fontsize=10)
GRID = '#111111'
for m in man:
    b = m['box']; y = ytop[m['row']] + float(m['y_top']); x = float(m['u_left']); h = float(m['height_m'])
    rl = role[b]
    st = STY['sur'] if rl.startswith('sur') else STY[rl]
    ax.add_patch(Rectangle((x, y), 20, h, ec='none', zorder=1, **{k: v for k, v in st.items() if k != 'hatch'}))
    if 'hatch' in st:
        ax.add_patch(Rectangle((x, y), 20, h, fill=False, ec='0.35', lw=0, hatch=st['hatch'], zorder=1.5))
    if rl == 'sur+val':
        ax.add_patch(Rectangle((x, y), 20, h, fill=False, ec='white', lw=0, hatch='...', zorder=1.5))
for tag, u1, y1, u2, y2, k in sorted(seg, key=lambda q: q[5] == 4, reverse=True):
    ln, = ax.plot([u1, u2], [ytop[tag] + y1, ytop[tag] + y2], color=G.CLU_COL[k], lw=0.9, solid_capstyle='round', zorder=2)
    ln.set_path_effects([pe.Stroke(linewidth=1.5, foreground='#202020'), pe.Normal()])
for m in man:
    b = m['box']; y = ytop[m['row']] + float(m['y_top']); x = float(m['u_left'])
    ax.add_patch(Rectangle((x, y), 20, float(m['height_m']), fill=False, ec=GRID, lw=2.2 if b == A else 0.8, zorder=3))
mA = [m for m in man if m['box'] == A][0]
ax.text(float(mA['u_left']) + 10, ytop[mA['row']] + float(mA['y_top']) + float(mA['height_m']) / 2, 'A', ha='center', va='center',
        color='white', fontweight='bold', zorder=4, path_effects=[pe.Stroke(linewidth=2.5, foreground='black'), pe.Normal()])
ax.set_xlim(U0, U1); ax.set_ylim(TOT, 0); ax.set_aspect('equal')
ax.set_xticks([-120, -80, -40, 0]); ax.set_yticks([]); ax.tick_params(labelsize=10)
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.set_xlabel('Position along the wall (m); west to the left\nFace dip 71.6–77.5°; dip direction about 184°', fontsize=10)
fig.text(0.3 / FW, 1 - (A_TOP - 0.15) / FH, '(a) Bench faces W00 (crest) to W06 (toe); window roles in fold 3', ha='left', va='bottom', fontsize=12)

# (b) rose of the clipped trace directions, stacked by cluster
axb = fig.add_axes([1.0 / FW, (FH - B_TOP - BS + 0.55) / FH, (BS - 1.0) / FW, (BS - 1.0) / FH], projection='polar')
lab = G.clusters(np.column_stack([np.zeros(len(ang_all)), np.zeros(len(ang_all)), np.cos(ang_all), np.sin(ang_all)]), CM_ALL)
deg = np.degrees(ang_all) % 180
bins = np.arange(0, 181, 10); cen = np.radians(np.r_[bins[:-1], bins[:-1] + 180] + 5)
bottom = np.zeros(36); rose_counts = {}
for k in range(5):
    h, _ = np.histogram(deg[lab == k], bins=bins); h = np.r_[h, h] / len(deg)
    axb.bar(cen, h, width=np.radians(10), bottom=bottom, color=G.CLU_COL[k], edgecolor='#202020', linewidth=0.3)
    bottom += h; rose_counts['C%d' % (k + 1) if k < 4 else 'unclustered'] = (h[:18] * len(deg)).round().astype(int).tolist()
axb.set_theta_zero_location('E'); axb.set_theta_direction(-1); axb.set_yticklabels([])
axb.set_xticks(np.radians(np.arange(0, 360, 45))); axb.set_xticklabels(['%d°' % d for d in range(0, 360, 45)], fontsize=10)
axb.tick_params(axis='x', pad=1); axb.grid(lw=0.3)
fig.text(0.3 / FW, 1 - (B_TOP - 0.45) / FH, '(b) Trace directions of the 735 clipped traces', ha='left', va='bottom', fontsize=12)

H1 = [Patch(fc='#000000', alpha=0.55, ec=GRID, lw=2.0, label='Held-out window A'),
      Patch(fc='#4A4A4A', alpha=0.5, ec=GRID, lw=0.8, label='Its 8 surrounding windows'),
      Patch(fc='white', ec='0.35', lw=0.8, hatch='xxx', label='Other held-out windows'),
      Patch(fc='white', ec='0.35', lw=0.8, hatch='...', label='Validation windows'),
      Patch(fc='#EEEEEE', ec=GRID, lw=0.8, label='Training windows'),
      Patch(fc='0.55', ec='0.35', lw=0.8, hatch='///', label='Not used (inner berm)')]
H2 = [Patch(fc=G.CLU_COL[k], ec='#202020', lw=0.5, label='C%d (about %.0f°)' % (k + 1, G.REF[k])) for k in range(4)] + \
     [Patch(fc=G.CLU_COL[4], ec='#202020', lw=0.5, label='Unclustered traces')]
cc = CM_ALL['centres_deg']
assert all(abs(c_ - r_) <= 1.0 for c_, r_ in zip(cc, G.REF)), (cc, G.REF)
fig.legend(handles=H1, loc='upper left', bbox_to_anchor=(5.55 / FW, 1 - (B_TOP - 0.1) / FH), frameon=False, fontsize=10,
           title='Window roles (a)', title_fontsize=10, alignment='left', handlelength=1.6, labelspacing=0.35, borderaxespad=0, borderpad=0)
fig.legend(handles=H2, loc='upper left', bbox_to_anchor=(10.45 / FW, 1 - (B_TOP - 0.1) / FH), frameon=False, fontsize=10,
           title='Trace-direction cluster', title_fontsize=10, alignment='left', handlelength=1.6, labelspacing=0.35, borderaxespad=0, borderpad=0)
RC.save(fig, 'Figure_2', allow=(12, 10))
from collections import Counter
vals = dict(fold='hold-out test, fold %d (release fold index %d)' % (FI + 1, FI), held_out_window_A=RC.wid(A),
            surrounding_windows=[RC.wid(b) for b in ctx], other_held_out=[RC.wid(b) for b in sp['test'] if b != A],
            validation=[RC.wid(b) for b in sp['val']], role_counts=dict(Counter(role.values())),
            clipped_traces=int(len(ang_all)), traces=len(T), clipped_traces_per_cluster=np.bincount(lab, minlength=5).tolist(),
            rose_bins_deg=bins[:-1].tolist(), rose_counts_per_cluster=rose_counts, cluster_centres_deg=list(map(float, cc)))
json.dump(vals, open(RC.VAL / 'Figure_2_values.json', 'w'), indent=1)
print(vals['role_counts'], vals['clipped_traces_per_cluster'])
