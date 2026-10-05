# -*- coding: utf-8 -*-
"""Fig. 4 (loss structure) = slide 5 of the deck, edited per MENTOR D3: set matching and reconstruction; geology-informed
loss (lambda = 0.005) with its eight terms; orientation-distribution loss (weight 1.0); KL with beta annealed 0.01 to 0.1
and free bits 0.22 nats; existence loss; auxiliary penalties (intersection rate 0.3, minimum spacing 0.2, sorted
log-length 1.0). The length ceiling (weight 0.005) is inactive in every fold and is not drawn (the text says so).
FIXLIST G-4: body text 17.5 pt (8.0 pt printed at 0.459), the loss column widened (10.05 to 28.15 cm) so that no text
touches a border (bottom-row boxes 5.20 -> 5.68 cm), "Ground truth" -> "Mapped".
DECISIONS_V2 (geobg, 1 Oct 2026): a cluster-share loss row (weight 1.0) is added directly below the orientation-distribution
loss row, in the same style (icon f4_clusters.png from make_icons_geobg.py, panel A W03_C2); the figure is 4.55 cm taller,
the prediction column is re-spaced over the new height and the total-loss circle re-centred. Everything else unchanged.
FIXLIST_V2 G-06 (palette of DECISIONS_V2 Section 5): mapped traces #333333, predicted traces #009E73, geology-informed icons in
greys (circle #666666, bars #999999, centre-density cells in grey levels).
GLOSSARY round (1 Oct 2026): "Orientation-distribution loss" -> "Trace-direction distribution loss"; its text reads
"Generated trace-direction density (green) against the mapped trace directions of the window (black)"; prediction panel
"Angles" -> "Directions"; "Set matching" -> "Trace matching" (no "set" for a group of traces); "unclustered (U)" -> "unclustered traces (U)". Layout unchanged.
Final-paper review (1 Oct 2026): F1 "Geology-informed loss (λ = 0.005)" -> "(weight 0.005)" (λ is the free-bits floor of
Eq. (8)); m-15 "Auxiliary penalties / intersection rate 0.3 / minimum spacing 0.2" -> "Auxiliary penalty terms / close
trace-centre pairs 0.3 / local spacing 0.2" (terms of the text and Table S2), bottom row 3.75 -> 5.50 cm, crop 1.75 cm taller.
Fix pass of 2 Oct 2026 (final review D2, GLOSSARY 4b): auxiliary box "intersection term Lint 0.3 / spacing term Lsp 0.2 /
log-length term Llen 1.0" (one name each in text, Table S2 and figure); the geology box names the eighth statistic
"connectivity" (was "soft intersections"); subscript runs of Ldir, Lint, Lsp, Llen at FSUB = 24 pt (drawn at about 2/3,
7.3 pt printed; Ldir was 6.1 pt) with exact line spacing; the "three black dots" connectors between the prediction and loss
columns replaced by plain arrows; bottom row 5.50 -> 4.60 cm (five lines instead of six), crop 0.90 cm shorter."""
import os, math
from pptx.util import Pt
from lxml import etree
from pptx.oxml.ns import qn
import pp
from pp import by_id, move, delete, text, box, arrow, line, picture, set_font_size, PAL

import schem_paths as _SP
ICON = str(_SP.ICONS)
CROP = (0.15, -0.25, 32.05, 27.35)   # review m-15: bottom row 1.75 cm taller; 2 Oct 2026: 0.90 cm shorter again
FS, FT, FH = 17.5, 19, 20          # G-4: 17.5 pt prints at 8.0 pt
FSUB = 24                          # 2 Oct 2026: subscript runs, 24 x 2/3 x 0.459 = 7.3 pt printed
SUBOFF = 12000    # 2 Oct 2026: subscript offset 12% of the (enlarged) run, so it stays inside its box
PANEL = 'D1D1D1'
GREEN_LINE = '009E73'      # FIXLIST_V2 G-06: predicted traces in the EVAE colour (was 47D45A)
MAPPED_LINE = '333333'     # FIXLIST_V2 G-06: mapped traces dark grey (was the palette orange FFC000)


def recolor(shape, fill=None, line=None):
    """FIXLIST_V2 G-06: set an explicit RGB fill and/or line colour on an original deck shape (spPr only; the theme style
    reference stays, an explicit spPr colour overrides it)"""
    spPr = shape._element.find(qn('p:spPr'))
    FILLS = (qn('a:solidFill'), qn('a:noFill'), qn('a:gradFill'), qn('a:pattFill'), qn('a:blipFill'))

    def solid(rgb):
        sf = etree.Element(qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', rgb); return sf
    if fill is not None:
        old = [c for c in spPr if c.tag in FILLS]
        anchor = spPr.find(qn('a:prstGeom')) if spPr.find(qn('a:prstGeom')) is not None else spPr.find(qn('a:custGeom'))
        for c in old:
            spPr.remove(c)
        anchor.addnext(solid(fill))
    if line is not None:
        ln = spPr.find(qn('a:ln'))
        assert ln is not None, shape.shape_id
        for c in [c for c in ln if c.tag in FILLS]:
            ln.remove(c)
        ln.insert(0, solid(line))


def flip_v(shape):
    xfrm = shape._element.find('.//' + qn('a:xfrm'))
    if xfrm.get('flipV') == '1':
        del xfrm.attrib['flipV']
    else:
        xfrm.set('flipV', '1')


def edit(prs):
    s = prs.slides[4]
    g = lambda i: by_id(s, i)
    keep_icons = [119, 121, 123] + list(range(125, 134)) + list(range(134, 144)) + list(range(164, 169))
    centres_grp = [4, 5, 6, 8, 9, 10, 11, 28, 29, 30, 31]
    lengths_grp = [12, 13, 14, 15, 16, 17, 18, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    angles_grp = [19, 20, 21, 22, 23, 24, 25, 26, 27, 41, 42, 43, 45, 46, 47, 48, 49, 50]
    left_misc = [51, 44, 62, 63, 64, 2, 7, 52, 53, 54, 55, 56, 57, 58]
    keep = set(keep_icons + centres_grp + lengths_grp + angles_grp + left_misc)
    for sh in list(s.shapes):
        if sh.shape_id not in keep:
            delete(sh)

    TOPY, BOTY = -0.10, 27.15   # review m-15: 26.30 + 1.75 (taller bottom row); 2 Oct 2026: - 0.90 (five-line penalty box)
    DEX = 0.85                  # existence panel moved down into the taller column
    # ------------------------------------------------------------ model predictions column
    move(g(51), x=0.30, y=TOPY, w=7.60, h=BOTY - TOPY)
    move(g(44), x=0.30, y=0.02, w=7.60, h=0.85)
    for gid, grp, (nx, ny) in ((4, centres_grp, (0.79, 1.80)), (12, lengths_grp, (0.79, 8.75)), (19, angles_grp, (0.79, 15.95))):
        r = g(gid); dx, dy = nx - pp.cm(r.left), ny - pp.cm(r.top)
        for i in grp:
            move(g(i), dx=dx, dy=dy)
    move(g(62), x=0.30, y=0.93, w=7.60, h=0.85); g(62).text_frame.paragraphs[0].runs[0].text = 'Centres'
    move(g(63), x=0.30, y=7.88, w=7.60, h=0.85)
    move(g(64), x=0.30, y=15.08, w=7.60, h=0.85); g(64).text_frame.paragraphs[0].runs[0].text = 'Directions'   # GLOSSARY
    for i in (44, 62, 63, 64):
        tf = g(i).text_frame
        tf.margin_top = tf.margin_bottom = 0
    # angles panel mirrored top-to-bottom: y points down the face and theta is measured clockwise from the along-wall axis
    r = g(19); yc2 = 2 * pp.cm(r.top) + pp.cm(r.height)
    for i in angles_grp:
        if i == 19:
            continue
        sh = g(i)
        move(sh, y=yc2 - pp.cm(sh.top) - pp.cm(sh.height))
        if not sh.has_text_frame or not sh.text_frame.text.strip():
            flip_v(sh)
    for i in (25, 32, 36, 37, 38, 40, 42):                 # l and theta labels: explicit size (was inherited 18 pt)
        set_font_size(g(i), 18)
        g(i).text_frame.word_wrap = False
        if i in (32, 36, 37, 38, 40):                     # the length symbol l in italics (reads as 1 when upright)
            for r in g(i).text_frame.paragraphs[0].runs:
                r.font.italic = True
    # existence prediction panel (added: the existence head feeds the existence loss and the auxiliary penalties)
    text(s, 0.30, 22.20 + DEX, 7.60, 0.80, ['Existence'], FH, margin=0.0)
    picture(s, os.path.join(ICON, 'f4_exist.png'), 0.79, 23.05 + DEX, 6.62, 2.60)
    # 2 Oct 2026 (final review): plain arrows from each prediction into the loss column replace the "three black dots"
    ycs = [1.80 + 2.16, 8.75 + 2.16, 15.95 + 2.16, 23.05 + DEX + 1.30]
    for i in (2, 7, 52, 53, 54, 55, 56, 57, 58):
        delete(g(i))
    for yc in ycs:
        arrow(s, 8.00, yc, 9.00, yc, lw=2.0)

    # ------------------------------------------------------------ loss components column
    X0, X1 = 9.10, 28.15                                   # widened (was 10.40 to 27.40; G-4); 2 Oct 2026: left edge 10.05 -> 9.10
    RX0, RX1 = 9.35, 27.90                                 # (the gap to the predictions now holds plain arrows only)
    DXC = (RX0 + RX1) / 2 - 18.90                          # shift of the set-matching sketch (drawn for a centre of 18.90)
    box(s, X0, TOPY, X1 - X0, BOTY - TOPY, fill=PAL['grey'], line=PAL['black'], lw=1.0)
    text(s, X0, 0.02, X1 - X0, 0.80, ['Loss components'], FH, margin=0.0)

    def row(y0, h):
        return box(s, RX0, y0, RX1 - RX0, h, fill=PAL['grey'], line=PAL['black'], lw=1.0, kind='round', adj=0.12)

    # L1 set matching and reconstruction
    L1, H1 = 1.00, 5.55
    row(L1, H1)
    text(s, RX0, L1 + 0.08, RX1 - RX0, 0.78, ['Reconstruction (weight 1.0)'], FH, margin=0.0)
    text(s, 11.40 + DXC, L1 + 0.92, 5.0, 0.80, ['Predicted'], FT, margin=0.0)
    text(s, 21.90 + DXC, L1 + 0.92, 5.0, 0.80, ['Mapped'], FT, margin=0.0)
    ell_cx, ell_cy, ew, eh = 18.90 + DXC, L1 + 2.72, 4.40, 1.85      # ellipse enlarged for 17.5 pt text (G-4)
    text(s, ell_cx - ew / 2, ell_cy - eh / 2, ew, eh, ['Hungarian', 'matching'], FS, line=PAL['black'], lw=1.0, dash='dash',
         kind='oval', margin=0.0)
    for k in range(4):
        yy = L1 + 1.90 + 0.55 * k
        line(s, 13.10 + DXC + 0.08 * k, yy, 14.40 + DXC + 0.08 * k, yy + 0.22, color=GREEN_LINE, lw=4.5)
        line(s, 23.35 + DXC + 0.08 * k, yy, 24.65 + DXC + 0.08 * k, yy + 0.22, color=MAPPED_LINE, lw=3.0)
        line(s, 14.55 + DXC + 0.08 * k, yy + 0.12, ell_cx - ew / 2 - 0.02, ell_cy, lw=1.0, dash='sysDot')
        line(s, ell_cx + ew / 2 + 0.02, ell_cy, 23.25 + DXC + 0.08 * k, yy + 0.08, lw=1.0, dash='sysDot')
    text(s, RX0 + 0.2, L1 + 3.98, RX1 - RX0 - 0.4, 1.52,
         ['Each generated trace is paired with a mapped trace; '
          'differences in centre, length and direction are penalised'], FS, margin=0.0)

    # L2 geology-informed loss
    L2, H2 = 6.85, 6.05
    row(L2, H2)
    text(s, RX0, L2 + 0.08, RX1 - RX0, 0.78, ['Geology-informed loss (weight 0.005)'], FH, margin=0.0)
    BY, BH, BW = L2 + 0.98, 3.40, 5.45
    GAP = (RX1 - RX0 - 3 * BW) / 4
    icon_boxes = ((11.89, 8.13, [119, 121, 123], 'Direction histogram'),
                  (17.51, 8.09, list(range(125, 134)), 'Length histogram'),
                  (23.10, 8.04, list(range(134, 144)) + list(range(164, 169)), 'Centre density'))
    for k, (ox, oy, ids, lab) in enumerate(icon_boxes):
        bx = RX0 + GAP + k * (BW + GAP)
        box(s, bx, BY, BW, BH, fill=PANEL, line=PAL['black'], lw=1.0)
        dx, dy = bx + (BW - 4.72) / 2 - ox, BY + 0.05 - oy
        for i in ids:
            sh = g(i); move(sh, dx=dx, dy=dy)
            sh._element.getparent().remove(sh._element); s.shapes._spTree.append(sh._element)   # bring above the new box
        text(s, bx, BY + BH - 0.80, BW, 0.72, [lab], FS, margin=0.0)
    # FIXLIST_V2 G-06: geology-informed icons in greys (were FFC000 orange-yellow, the theme blue and multicoloured cells)
    for i in (119, 121, 123):                                  # direction-histogram circle and its two radii
        recolor(g(i), line='666666')
    for i in range(125, 134):                                  # length-histogram bars
        recolor(g(i), fill='999999')
    DENS = {134: 'FFFFFF', 135: 'BFBFBF', 136: '999999', 137: 'BFBFBF', 138: 'FFFFFF', 143: '999999', 142: '666666', 141: '404040',
            140: '666666', 139: '262626', 164: 'FFFFFF', 165: 'BFBFBF', 166: '999999', 167: 'BFBFBF', 168: 'FFFFFF'}   # centre density: grey levels
    for i, c in DENS.items():
        recolor(g(i), fill=c)
    text(s, RX0 + 0.2, L2 + 4.45, RX1 - RX0 - 0.4, 1.52,
         ['+ direction likelihood, mean length, spacing, centre distances and connectivity '
          '(eight statistics)'], FS, margin=0.0)

    # L3 orientation-distribution loss
    L3, H3 = 13.20, 4.25
    row(L3, H3)
    text(s, RX0, L3 + 0.08, RX1 - RX0, 0.78, [[('Trace-direction distribution loss ', {}), ('ℒ', {'italic': True}),
                                              ('dir', {'sub': SUBOFF, 'size': FSUB}), (' (weight 1.0)', {})]], FH, margin=0.0,
         spacing=Pt(FH * 1.2))
    box(s, RX0 + GAP, L3 + 0.98, 5.00, 3.00, fill=PANEL, line=PAL['black'], lw=1.0)
    picture(s, os.path.join(ICON, 'f4_dirloss.png'), RX0 + GAP + 0.10, L3 + 1.08, 4.80, 2.80)
    text(s, RX0 + GAP + 5.30, L3 + 0.98, RX1 - RX0 - GAP - 5.50, 3.00,
         ['Generated trace directions (green)', 'against the mapped trace', 'directions (black)'], FS, margin=0.0)

    # L3b cluster-share loss (geobg): same style as the orientation-distribution loss row
    L3b, H3b = 17.75, 4.25
    row(L3b, H3b)
    text(s, RX0, L3b + 0.08, RX1 - RX0, 0.78, ['Cluster-share loss (weight 1.0)'], FH, margin=0.0)
    box(s, RX0 + GAP, L3b + 0.98, 7.00, 3.00, fill=PANEL, line=PAL['black'], lw=1.0)       # wider: five 18 pt labels
    picture(s, os.path.join(ICON, 'f4_clusters.png'), RX0 + GAP + 0.10, L3b + 1.08, 6.80, 2.80)
    text(s, RX0 + GAP + 7.25, L3b + 0.98, RX1 - RX0 - GAP - 7.40, 3.00,
         ['Generated against mapped', 'shares of clusters C1–C4', 'and unclustered traces (U)'], FS, margin=0.0)

    # L4 KL, existence and auxiliary penalties
    # review m-15: labels in the terms of the text and Table S2; the penalty box needs six lines, so the row is 1.75 cm taller
    # 2 Oct 2026: GLOSSARY 4b names (intersection term Lint, spacing term Lsp, log-length term Llen); five lines, row 4.60 cm
    L4, H4 = 22.30, 4.60
    row(L4, H4)

    def term(name, sub, w):
        return [(name + ' ', {}), ('ℒ', {'italic': True}), (sub, {'sub': SUBOFF, 'size': FSUB}), (' ' + w, {})]
    items = ([[('KL divergence', {'size': FT})], 'smooth latent spaces', 'weight 0.01 to 0.1'],
             [[('Existence', {'size': FT})], 'number of traces', 'weight 1.0'],
             [[('Auxiliary terms', {'size': FT})], term('intersection term', 'int', '0.3'),
              term('spacing term', 'sp', '0.2'), term('log-length term', 'len', '1.0')])
    IW = 5.68                                              # KL and existence boxes (was 5.20; G-4)
    IWS = (IW, IW, RX1 - RX0 - 4 * 0.14 - 2 * IW)          # 2 Oct 2026: the penalty box takes the extra width (6.63 cm)
    for k, it in enumerate(items):
        bx = RX0 + 0.14 + k * (IW + 0.14)
        tb = text(s, bx, L4 + 0.25, IWS[k], H4 - 0.50, it, FS, fill=PANEL, line=PAL['black'], lw=1.0, margin=0.05)
        for p in tb.text_frame.paragraphs:                 # exact line spacing: the 24 pt subscript runs do not open the lines
            big = any(r.font.size is not None and r.font.size.pt == FT for r in p.runs)
            p.line_spacing = Pt((FT if big else FS) * 1.2)

    # ------------------------------------------------------------ total loss
    cx, cy, rr = 30.20, 13.95, 1.75   # re-centred on the rows (1.00 to 26.90; 2 Oct 2026)
    circ = box(s, cx - rr, cy - rr, 2 * rr, 2 * rr, fill='AEAEAE', line=PAL['black'], lw=1.0, kind='oval')
    text(s, cx - 1.4, cy - 1.95, 2.8, 2.30, ['∑'], 54, margin=0.0, color=PAL['white'])
    text(s, cx - 1.6, cy + 0.32, 3.2, 0.85, ['Total loss'], FH, margin=0.0)
    for y0, h in ((L1, H1), (L2, H2), (L3, H3), (L3b, H3b), (L4, H4)):
        yr = y0 + h / 2
        ux, uy = cx - RX1, cy - yr; n = math.hypot(ux, uy)
        arrow(s, RX1 + 0.02, yr, cx - (rr + 0.06) * ux / n, cy - (rr + 0.06) * uy / n, lw=2.0)
    return s
