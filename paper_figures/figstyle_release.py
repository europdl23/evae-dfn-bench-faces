# -*- coding: utf-8 -*-
"""House style for the figures and an automatic layout check (copy of the release src/study/figstyle.py; final-paper
version of 1 Oct 2026: wording of the messages only, "plot" for the release word).

Style: every text in Times New Roman. 12 pt for normal text (plot titles, axis labels, row labels); 10 pt for short
text (tick labels, legends, values, counts); 8 pt only for small notes. Figures are drawn at their printed size,
16 cm wide (full page), so the point sizes are the sizes on the page.

check_layout() fails a figure if:
  * a text is not Times New Roman, or not 12, 10 or 8 pt;
  * two texts overlap;
  * a text leaves the figure;
  * a text of one plot covers another plot, or two plots overlap;
  * a text or legend inside a plot touches the plotted data (lines, bars, box plots);
  * a figure-level legend covers a plot."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

CM = 1 / 2.54
FULL_W = 16.0 * CM
SIZES = (12, 10, 8)
assert any('Times New Roman' == f.name for f in font_manager.fontManager.ttflist), 'Times New Roman not installed'
plt.rcParams.update({
    'font.family': 'Times New Roman', 'font.serif': ['Times New Roman'], 'mathtext.fontset': 'custom',
    'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic', 'mathtext.bf': 'Times New Roman:bold',
    'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 12, 'figure.titlesize': 12,
    'xtick.labelsize': 10, 'ytick.labelsize': 10, 'legend.fontsize': 10, 'legend.title_fontsize': 10,
    'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
    'lines.linewidth': 1.0, 'patch.linewidth': 0.6, 'savefig.dpi': 600, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
METHOD_COL = {'Held-out': '#333333', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}


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


def _overlap(a, b, pad):
    return min(a.x1, b.x1) - max(a.x0, b.x0) > pad and min(a.y1, b.y1) - max(a.y0, b.y0) > pad


def _line_hits(xy, bb, n=25):
    """does a polyline (display coordinates) pass through the box?"""
    xy = xy[np.isfinite(xy).all(1)]
    for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
        t = np.linspace(0, 1, n)
        x, y = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
        if np.any((x > bb.x0) & (x < bb.x1) & (y > bb.y0) & (y < bb.y1)):
            return True
    return False


def check_layout(fig, allow_font_sizes=SIZES, pad_px=0.5):
    """returns a list of problems (empty = clean)"""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    T = _texts(fig)
    probs, boxes = [], []
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
            if _overlap(boxes[i], boxes[j], pad_px):
                probs.append('overlap: %r / %r' % (T[i].get_text()[:30], T[j].get_text()[:30]))
    axes = [ax for ax in fig.axes if ax.get_visible() and ax.axison]
    owner = {}                       # tick labels of polar axes carry no axes reference; map them to their axes
    for ax in fig.axes:
        for tk in ax.xaxis.get_major_ticks() + ax.xaxis.get_minor_ticks() + ax.yaxis.get_major_ticks() + ax.yaxis.get_minor_ticks():
            owner[id(tk.label1)] = ax; owner[id(tk.label2)] = ax
    legend_texts = {id(t) for lg in fig.legends for t in lg.get_texts()}
    for t, bb in zip(T, boxes):
        for ax in axes:
            if t.axes is ax or owner.get(id(t)) is ax:
                continue
            if _overlap(bb, ax.get_window_extent(r), pad_px):
                if t.axes is None and t in getattr(ax, 'texts', []):
                    continue
                probs.append('text %r covers a plot' % t.get_text()[:40] if id(t) not in legend_texts else 'legend text %r covers a plot' % t.get_text()[:40])
    for i in range(len(axes)):
        for j in range(i + 1, len(axes)):
            if _overlap(axes[i].get_window_extent(r), axes[j].get_window_extent(r), pad_px):
                probs.append('plots overlap: %d / %d' % (i, j))
    # texts and legends inside a plot must not touch the plotted data
    for ax in axes:
        items = [(t.get_text()[:30], t.get_window_extent(r)) for t in ax.texts if t.get_visible() and t.get_text().strip()]
        lg = ax.get_legend()
        if lg is not None and lg.get_visible():
            items.append(('legend', lg.get_window_extent(r)))
        for name, bb in items:
            for ln in ax.lines:
                if ln.get_visible() and len(ln.get_xydata()) and _line_hits(ln.get_transform().transform(ln.get_xydata()), bb):
                    probs.append('%r touches a plotted line' % name); break
            for p in ax.patches:
                if p.get_visible() and _overlap(p.get_window_extent(r), bb, pad_px):
                    probs.append('%r touches a plotted bar or box' % name); break
    # figure-level legends must stay off the plots
    for lg in fig.legends:
        for ax in axes:
            if _overlap(lg.get_window_extent(r), ax.get_window_extent(r), pad_px):
                probs.append('figure legend covers a plot')
    return probs


def save(fig, path_no_ext, allow_font_sizes=SIZES):
    probs = check_layout(fig, allow_font_sizes)
    if probs:
        raise RuntimeError('layout check failed for %s:\n  ' % path_no_ext + '\n  '.join(probs))
    for ext in ('png', 'pdf'):          # no creation date in the PDF, so a rerun writes the same bytes
        fig.savefig('%s.%s' % (path_no_ext, ext), dpi=600 if ext == 'png' else None, metadata={'CreationDate': None} if ext == 'pdf' else None)
    w, h = fig.get_size_inches() / CM
    plt.close(fig)
    return 'clean: %.1f x %.1f cm, Times New Roman %s pt, no overlaps, nothing outside, no text on data or other plots' % (w, h, '/'.join(str(s) for s in allow_font_sizes))


def sizes_used(fig):
    """the font sizes used in a figure (for the report)"""
    fig.canvas.draw()
    return sorted({round(t.get_fontsize(), 1) for t in _texts(fig)}, reverse=True)
