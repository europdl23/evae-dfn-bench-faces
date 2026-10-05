# -*- coding: utf-8 -*-
"""Fig. 1 (workflow) = slide 1 of the deck, edited per MENTOR D1. FIXLIST G-4: Fig. 1 prints at 0.933 of slide size, so
every label is at least 9 pt on the slide (8.4 pt printed); the Step 4 boxes are re-divided so the 9 pt labels fit.
DECISIONS_V2 (geobg, 1 Oct 2026): training-loss text adds "Cluster-share loss"; Step 4 text "15 parameters, 38 scores, paired
tests, natural-variability reference"; icons from make_icons_geobg.py (panel grid coloured by trace-direction cluster; new
example panel A W03_C2, run seed 1337, draw 0; comparison icon in the method colours EVAE #009E73, ADFNE #E69F00,
KDE #56B4E9, held-out black).
FIXLIST_V2: G-06 Step 4 rose and length thumbnails redrawn as in Fig. 7 (held-out black outline, EVAE green fill, no tick
labels); G-07 Step 3 "(3 run seeds × 8 neighbouring panels)".
GLOSSARY round (1 Oct 2026): every label in GLOSSARY terms (window, trace direction, realisation, trace-direction distribution
loss); Step 2 labels "Trace centre", "Trace length", "Trace direction"; Step 4 text "15 parameters, 38 scores, engineering
inputs, paired tests, natural-variability reference" (five lines). The training-loss box needs five lines and Step 4 one more
line, so Step 3 is 0.35 cm and Step 4 0.38 cm taller (crop 0.73 cm taller); nothing else moves.
Final-paper review m-15: "Auxiliary penalties" -> "Auxiliary penalty terms" (the term of the text and Table S2).
Fix pass of 2 Oct 2026 (final review D7, authors' answer 7): "Open pit mine" -> "Open-pit mine".
Author decision of 2 Oct 2026 (the mine operator does not permit photographs): Fig. 1 has NO photograph. edit() itself now
replaces the two Step 1 photographs of the original slide by drawn icons (a bench profile of the open pit with a UAV, and
a traces-only crop of bench faces W02 to W04) and places the window-grid thumbnail drawn without the orthomosaic
(make_icons_nophoto.py); the step names the photogrammetric model ("Open-pit mine (photogrammetric model)"). The former
no-photo copy of the slide (edit_nophoto, slide 20) is no longer made: slide 1 is that drawing."""
import os
import pp
from pp import by_id, move, delete, text, picture, arrow, box, set_font_size, PAL

import schem_paths as _SP
ICON = str(_SP.ICONS)
# explicit crop (cm) used by the exporter: left column to right edge of the panels
CROP = (8.30, 0.40, 24.00, 18.95)


def edit(prs):
    s = prs.slides[0]
    g = lambda i: by_id(s, i)

    # ---------------------------------------------------------------- global: heavy outer frame removed
    delete(g(1071))

    # ---------------------------------------------------------------- row geometry
    R1, H1 = 0.55, 3.35
    R2, H2 = 4.25, 3.84
    R3, H3 = 8.44, 5.70                                                  # GLOSSARY: +0.35 (five-line loss box)
    R4, H4 = 14.49, 4.28                                                 # GLOSSARY: +0.38 (five-line Step 4 text)

    # ---------------------------------------------------------------- Step 1: data preparation
    move(g(59), y=R1, h=H1)
    for i in (16, 17, 30, 1026, 1024, 1028):
        move(g(i), dy=-0.70)
    runs = g(30).text_frame.paragraphs[0].runs                         # 2 Oct 2026: "Open pit mine" -> "Open-pit mine"
    runs[0].text = 'Open-pit mine'
    for r in runs[1:]:
        r.text = ''
    delete(g(21))                                          # the two 36 m x 12 m extraction panels
    delete(g(1027))                                        # "Fracture extraction"
    pic = picture(s, os.path.join(ICON, 'f1_panelgrid_nophoto.png'), 21.28, 0.81, 1.757, 1.98)   # drawn, no orthomosaic
    text(s, 19.98, 2.80, 3.70, 1.00, ['Window grid: 50 windows', 'of 20 m × 20 m, 705 traces'], 9.5, margin=0.0)   # GLOSSARY
    _step1_drawn(s)                                       # 2 Oct 2026: the two Step 1 photographs replaced by drawings

    # ---------------------------------------------------------------- Step 2: feature extraction (content unchanged)
    dy2 = R2 - 4.72
    for i in (60, 1053, 1054, 1055, 1056, 1030, 1031, 1036):
        move(g(i), dy=dy2)
    for i, f in ((24, 'f1_centre.png'), (27, 'f1_length.png'), (26, 'f1_angle.png')):
        old = g(i)
        x, y, w, h = pp.cm(old.left), pp.cm(old.top) + dy2, pp.cm(old.width), pp.cm(old.height)
        delete(old)
        picture(s, os.path.join(ICON, f), x, y, 2.40, 1.98)
    for i, lab in ((1030, 'Trace centre'), (1031, 'Trace length'), (1036, 'Trace direction')):   # GLOSSARY (were "... of line")
        runs = g(i).text_frame.paragraphs[0].runs
        runs[0].text = lab
        for r in runs[1:]:
            r.text = ''
    move(g(1036), dx=-0.15)                                               # "Trace direction" clear of the dotted border

    # ---------------------------------------------------------------- Step 3: EVAE training and generation
    move(g(61), y=R3, h=H3)
    move(g(1060), x=12.90, y=R3 + 0.01, w=6.40, h=0.60)                 # "Dual-latent EVAE"
    g(1060).text_frame.margin_top = g(1060).text_frame.margin_bottom = 0
    move(g(63), x=12.90, y=9.12, w=6.40, h=4.86)                         # dotted outer
    move(g(41), x=13.02, y=9.18, w=6.16, h=2.52)                          # inner
    dyi = 9.18 - 9.72
    for i in (52, 25, 28, 1043):                                          # encoder bars + label
        move(g(i), dx=-0.14, dy=dyi)
    for i in (40, 2):                                                     # the two latent ovals
        move(g(i), dx=-0.35, dy=dyi)
    for i in (37, 38, 39, 1051):                                          # decoder bars + label
        move(g(i), dx=-0.62, dy=dyi)
    move(g(1051), dx=-0.12)                                               # 9 pt "Decoder" clear of the dotted border (G-4)
    delete(g(45))                                                         # "+" between the latents (they are not summed)
    for i in (40, 2, 1043, 1051):                                         # latent ovals, "Encoder", "Decoder": 8 -> 9 pt (G-4)
        set_font_size(g(i), 9)
    for i, y in ((40, 9.33), (2, 10.54)):                                 # ovals slightly taller, thin insets, for two 9 pt lines
        move(g(i), y=y, h=1.04)
        tf = g(i).text_frame
        tf.margin_top = tf.margin_bottom = pp.E(0.02)
        tf.margin_left = tf.margin_right = pp.E(0.10)
    for i in (1034, 1037, 1038, 1049):
        delete(g(i))
    arrow(s, 14.05, 10.44, 14.74, 10.44, color=PAL['black'], lw=1.25)    # encoder -> latents
    arrow(s, 17.49, 10.44, 17.98, 10.44, color=PAL['black'], lw=1.25)    # latents -> decoder
    arrow(s, 16.12, 11.72, 16.12, 12.02, color=PAL['black'], lw=1.0)     # -> training loss
    move(g(42), x=12.98, y=12.02, w=6.24, h=1.90)                         # loss box (G-4; GLOSSARY: 1.55 -> 1.90 for five lines)
    lt = g(3)
    move(lt, x=12.98, y=12.02, w=6.24, h=1.90)
    tf = lt.text_frame
    tf.margin_left = tf.margin_right = pp.E(0.04)
    tf.margin_top = tf.margin_bottom = pp.E(0.02)
    tf.auto_size = pp.MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = pp.MSO_ANCHOR.MIDDLE
    pp.set_paragraphs(tf, ['Training loss',                                # 8.6 pt = 8.0 pt printed (G-4); GLOSSARY wording
                           'Reconstruction + Existence + KL divergence +',
                           'Geology-informed loss + Trace-direction',
                           'distribution loss + Cluster-share loss +',
                           'Auxiliary terms'], 8.6)   # review m-15: term of the text and Table S2
    # round 3 (3 Oct 2026, PLAN_ROUND3 Section C): Step 3 names the two generation modes, local generation (8 surrounding
    # windows) and representative generation (8 randomly chosen mapped windows); no history wording
    for i in (1057, 7, 4, 9):
        delete(g(i))
    G3 = 0.17                                                             # GLOSSARY: right-hand group re-centred in the taller Step 3
    text(s, 19.50, 8.50 + G3, 4.30, 1.30, ['Local generation (8', 'surrounding windows) and', 'representative generation'], 10, margin=0.0)   # round 3
    picture(s, os.path.join(ICON, 'f1_neighbours.png'), 20.50, 9.86 + G3, 2.30, 2.30)
    text(s, 19.30, 12.20 + G3, 4.50, 1.25, ['24 realisations per', 'held-out window', '(3 run seeds × 8)'], 9, margin=0.0)   # G-07
    arrow(s, 19.36, 11.01 + G3, 20.46, 11.01 + G3, color=PAL['black'], lw=1.25)

    # ---------------------------------------------------------------- Step 4: evaluation and validation
    move(g(62), y=R4, h=H4)
    delete(g(29)); delete(g(6))                                           # correlation-matrix "Connectivity" icon
    delete(g(1058)); delete(g(1059))                                      # old single-word labels
    top, bh = R4 + 0.17, H4 - 0.34
    # Step 4 labels at 8.6 pt (8.0 pt printed), boxes re-divided so that no label touches a border (G-4)
    S4 = 8.6
    C4 = 0.19                                                             # GLOSSARY: (a) and (b) contents re-centred in the taller boxes
    # (a) hold-out tests (box widened from 4.40 to 4.80 cm for the test names)
    move(g(31), x=12.78, y=top, w=4.80, h=bh)
    picture(s, os.path.join(ICON, 'f1_holdout.png'), 12.88, top + 0.55 + C4, 4.60, 1.42)
    text(s, 12.78, top + 2.10 + C4, 4.80, 0.80, [[('Hold-out test', {})], [('(blue: held-out windows)', {})]], S4, margin=0.0)
    # (b) comparison with ADFNE and KDE
    move(g(32), x=17.70, y=top, w=2.50, h=bh)
    picture(s, os.path.join(ICON, 'f1_compare.png'), 17.80, top + 0.07 + C4, 2.30, 2.62)
    text(s, 17.70, top + bh - 0.80 - C4, 2.50, 0.74, ['Comparison with', 'ADFNE and KDE'], S4, margin=0.0)
    # (c) measures: rose and length thumbnails redrawn as Fig. 7 (FIXLIST_V2 G-06: held-out black outline, EVAE green
    # fill, no tick labels; make_icons_geobg.py), at the places of the original blue icons
    move(g(33), x=20.32, y=top, w=3.39, h=bh)
    delete(g(22)); delete(g(23))
    picture(s, os.path.join(ICON, 'f1_rose.png'), 20.42, top + 0.14, 1.50, 1.49)
    picture(s, os.path.join(ICON, 'f1_lengths.png'), 22.02, top + 0.20, 1.62, 1.36)
    text(s, 20.30, top + 1.60, 1.74, 0.40, ['Direction'], S4, margin=0.0)
    text(s, 21.96, top + 1.60, 1.74, 0.40, ['Length'], S4, margin=0.0)
    text(s, 20.32, top + 1.98, 3.39, 1.92, ['15 parameters, 38 scores,', 'engineering inputs,', 'paired tests,', 'natural-variability',
                                           'reference'], S4, margin=0.0)                         # GLOSSARY: engineering inputs added

    # ---------------------------------------------------------------- step labels and the arrows between them
    for i, yc in ((12, R1 + H1 / 2), (13, R2 + H2 / 2), (14, R3 + H3 / 2), (15, R4 + H4 / 2)):
        sh = g(i)
        move(sh, y=yc - pp.cm(sh.height) / 2)
    for i in (49, 1032, 1033):
        delete(g(i))
    xa = 10.38
    labs = [g(i) for i in (12, 13, 14, 15)]
    for a, b in zip(labs[:-1], labs[1:]):
        y1 = pp.cm(a.top + a.height) + 0.25
        y2 = pp.cm(b.top) - 0.25
        arrow(s, xa, y1, xa, y2, color=PAL['black'], lw=1.25)
    return s


def _swap_picture(s, old, path):
    x, y, w, h = pp.cm(old.left), pp.cm(old.top), pp.cm(old.width), pp.cm(old.height)
    delete(old)
    return picture(s, path, x, y, w, h)


def _step1_drawn(s):
    """Step 1 without photographs (author decision of 2 Oct 2026): the aerial pit photograph (shape 16) becomes a drawn
    bench profile with a UAV, the orthophoto with traces (shape 17) a traces-only drawing; the pit label gets the second
    line "(photogrammetric model)". The swapped pictures' image relationships are dropped by build_all.py."""
    g = lambda i: by_id(s, i)
    _swap_picture(s, g(16), os.path.join(ICON, 'f1_pit_drawn.png'))           # aerial pit photograph -> drawn bench profile
    _swap_picture(s, g(17), os.path.join(ICON, 'f1_traces_drawn.png'))        # orthophoto with traces -> traces only
    # the step keeps the photogrammetric model: "(photogrammetric model)" as a 9.5 pt second line under "Open-pit mine"
    # (the drawn pit shows the UAV survey); a three-line "Fracture labelling" label would cross the Step 1 frame
    pit = g(30)
    move(pit, dx=-0.205, w=pp.cm(pit.width) + 0.41)
    pp.set_paragraphs(pit.text_frame, [[('Open-pit mine', {'size': 12})], [('(photogrammetric model)', {'size': 9.5})]], 12)
    for lab in (pit, g(1026)):                                                # both labels: same top, no top inset
        move(lab, y=2.83, h=0.98)
        lab.text_frame.margin_top = 0
        lab.text_frame.vertical_anchor = pp.MSO_ANCHOR.TOP
    pit.text_frame.margin_left = pit.text_frame.margin_right = pp.E(0.05)     # 3.46 cm second line fits without wrapping
