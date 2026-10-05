# -*- coding: utf-8 -*-
"""House style for the paper figures and an automatic layout check (copy of manuscript_revision_2026-10-01/code/figstyle.py;
final-paper version: polar tick labels are mapped to their own axes, as in the release check, and every rendered
text is scanned against the banned terms of work/GLOSSARY.md Section 2, check_terms()).
Style: every text in Times New Roman, 12 pt by default (10 or 8 pt only where a figure states why), figure width
14.65 cm (placement width) unless stated. check_layout() fails a figure if any two texts overlap, any text leaves the
figure, any text of one plot covers another plot, or any rendered text holds a banned term."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

CM = 1 / 2.54
FULL_W = 16.0 * CM
assert any('Times New Roman' == f.name for f in font_manager.fontManager.ttflist), 'Times New Roman not installed'
plt.rcParams.update({
    'font.family': 'Times New Roman', 'font.serif': ['Times New Roman'], 'mathtext.fontset': 'custom',
    'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic', 'mathtext.bf': 'Times New Roman:bold',
    'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 12, 'xtick.labelsize': 12, 'ytick.labelsize': 12,
    'legend.fontsize': 12, 'figure.titlesize': 12, 'axes.linewidth': 0.8, 'savefig.dpi': 600,
    'pdf.fonttype': 42, 'svg.fonttype': 'none'})
# colours of the two trace-direction components of the baselines (Okabe-Ito) and method colours
SET_COL = {0: '#0072B2', 1: '#D55E00'}
METHOD_COL = {'REAL': '#000000', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}

# GLOSSARY Section 2: banned in any rendered figure text (case-insensitive). Allowlist (Section 3): "box plot",
# "network parameters", "neural network", "Fig. S1"-type labels. GLOSSARY Section 4b (2 Oct 2026): window IDs are
# written W03-2 and window columns 1 to 8, so the release IDs W03_C2 and the column labels C5 to C8 are banned (C1 to C4
# stay: they are the trace-direction clusters), and window D is "difficult", never "hard".
import re as _re
BANNED = [r'\bpanels?\b', r'\bbox(?:es)?\b(?! plot)', r'\btil(?:e|es|ing)\b', r'\bpatch(?:es)?\b', r'\bjoint sets?\b',
          r'\bsets?\b', r'\bfamil(?:y|ies)\b', r'\borientation', r'\bnetworks?\b(?! parameters)', r'\bDFNs?\b',
          r'\bdraws?\b', r'\bsamples?\b', r'\bschemes?\b', r'\bS[123]\b', r'geology guidance', r'geology-guided',
          r'\bguided?\b', r'yardstick', '~', '\u2248', '\u2014', r'upper bound', r'pre-registered', r'isolated clusters',
          r'better connectivity', r'termination answered', r'full engineering case study', r'120 (?:panels|windows)', r'83\s?%',
          r'\bequal\b', r'on par', r'no closer', r'non-identical', r'GeoQ', r'2\.5D', r'\bvs\.?\b',
          r'W0\d_C\d', r'\bC[5-8]\b', r'\bhard\b', r'less successful',
          # round 3 (3 Oct 2026, PLAN_ROUND3 Section B and H3): "connectivity" is allowed (Fig. 10), the test and mode
          # names of the earlier builds are banned
          r'gap-filling', r'new[- ]bench', r'new[- ]stretch', r'random context', r'neighbou?r']


def check_terms(fig):
    """GLOSSARY check of every visible text of the figure; returns a list of problems (empty = clean)"""
    probs = []
    for t in _texts(fig):
        txt = t.get_text().replace('neural network', '')
        for pat in BANNED:
            if _re.search(pat, txt, flags=_re.I):
                probs.append('banned term %r in %r' % (pat, t.get_text()[:60]))
    return probs


def _undrawn_ticklabels(fig):
    """tick labels whose tick lies outside the axis view range are never drawn; exclude them from the check"""
    skip = set()
    for ax in fig.axes:
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = min(lim), max(lim); eps = 1e-9 * max(1.0, hi - lo)
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                if not (lo - eps <= tk.get_loc() <= hi + eps):
                    skip.update({id(tk.label1), id(tk.label2)})
    return skip


def _texts(fig):
    out = []
    skip = _undrawn_ticklabels(fig)
    for t in fig.findobj(matplotlib.text.Text):
        if id(t) in skip or not t.get_visible() or not t.get_text().strip():
            continue
        ax = t.axes
        if ax is not None and not ax.get_visible():
            continue
        out.append(t)
    return out


def check_layout(fig, allow_font_sizes=(12,), pad_px=0.5):
    """returns a list of problems (empty = clean). Checks: font family and size of every text, text-text overlap,
    text outside the figure, text of one axes inside another axes' drawing area."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    T = _texts(fig)
    probs = check_terms(fig)
    boxes = []
    for t in T:
        fam = t.get_fontfamily()
        name = font_manager.FontProperties(family=fam).get_name() if fam else ''
        if 'Times New Roman' not in (fam if isinstance(fam, list) else [fam]) and name != 'Times New Roman':
            probs.append('font %r in %r' % (fam, t.get_text()[:40]))
        if round(t.get_fontsize(), 1) not in allow_font_sizes:
            probs.append('size %.1f pt in %r' % (t.get_fontsize(), t.get_text()[:40]))
        bb = t.get_window_extent(r)
        boxes.append(bb)
        if bb.x0 < -pad_px or bb.y0 < -pad_px or bb.x1 > W + pad_px or bb.y1 > H + pad_px:
            probs.append('outside figure: %r' % t.get_text()[:40])
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            a, b = boxes[i], boxes[j]
            if min(a.x1, b.x1) - max(a.x0, b.x0) > pad_px and min(a.y1, b.y1) - max(a.y0, b.y0) > pad_px:
                probs.append('overlap: %r / %r' % (T[i].get_text()[:30], T[j].get_text()[:30]))
    axes = [ax for ax in fig.axes if ax.get_visible() and ax.axison]
    owner = {}                       # tick labels of polar axes carry no axes reference; map them to their axes (as the release check)
    for ax in fig.axes:
        for tk in ax.xaxis.get_major_ticks() + ax.xaxis.get_minor_ticks() + ax.yaxis.get_major_ticks() + ax.yaxis.get_minor_ticks():
            owner[id(tk.label1)] = ax; owner[id(tk.label2)] = ax
    for t, bb in zip(T, boxes):
        for ax in axes:
            if t.axes is ax or owner.get(id(t)) is ax:
                continue
            ab = ax.get_window_extent(r)
            if min(bb.x1, ab.x1) - max(bb.x0, ab.x0) > pad_px and min(bb.y1, ab.y1) - max(bb.y0, ab.y0) > pad_px:
                if t.axes is None and t in getattr(ax, 'texts', []):
                    continue
                probs.append('text %r covers another plot' % t.get_text()[:40])
    # axes must not overlap each other
    for i in range(len(axes)):
        for j in range(i + 1, len(axes)):
            a, b = axes[i].get_window_extent(r), axes[j].get_window_extent(r)
            if min(a.x1, b.x1) - max(a.x0, b.x0) > pad_px and min(a.y1, b.y1) - max(a.y0, b.y0) > pad_px:
                probs.append('plots overlap: %d / %d' % (i, j))
    return probs


def save(fig, path_no_ext, allow_font_sizes=(12,)):
    probs = check_layout(fig, allow_font_sizes)
    if probs:
        raise RuntimeError('layout check failed for %s:\n  ' % path_no_ext + '\n  '.join(probs))
    for ext in ('png', 'pdf'):
        fig.savefig('%s.%s' % (path_no_ext, ext), dpi=600 if ext == 'png' else None)
    plt.close(fig)
    return 'clean (fonts, sizes %s pt, no overlaps, nothing outside, no text over other plots)' % (allow_font_sizes,)
