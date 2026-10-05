# -*- coding: utf-8 -*-
"""Fig. 3 (EVAE architecture) = slide 4 of the deck, redrawn in the same layout and colours and corrected to the code
(DECISIONS Section 2; MENTOR D2): two inputs, encoders 256 -> 128, z_s (24D) and z_g (32D), z_s -> centre decoder
(128, 256), z_g -> length decoder (128, 256) and three direction heads (128 each), only the existence head (128) reads
[z_s, z_g] (56D); KL to N(0, I) with free bits 0.22 nats; 20 m panels as input.
FIXLIST G-4: body text 17 pt (8.0 pt printed at 0.473), Mean / Log-var boxes widened about 6%, units added to the free
bits, existence-mask icon in black (kept) and grey dashed (empty) slots as in Fig. 4.
GLOSSARY round (1 Oct 2026): input label "20 m × 20 m windows" (was panels); nothing else changed.
Fix pass of 2 Oct 2026 (final review D2): the subscripts of z_s, z_g and N_max printed at 5.3 pt (PowerPoint draws a
subscript at about 2/3 of its run size). Their runs are now FSUB = 23 pt, drawn at about 15.3 pt on the slide, 7.2 pt at
14.65 cm; the boxes that hold them get an exact line spacing of 1.2 x FS so the larger runs do not open the lines."""
import os
from pptx.util import Pt
import pp
from pp import text, box, arrow, line, picture, delete, PAL

import schem_paths as _SP
ICON = str(_SP.ICONS)
CROP = (0.25, 0.30, 31.25, 19.05)
FS = 17          # body text (prints at 8.0 pt; G-4)
FH = 20          # column headers
FSUB = 23        # subscript runs (2 Oct 2026): 23 x 2/3 x 0.473 = 7.2 pt printed
SUBOFF = 12000    # 2 Oct 2026: subscript offset 12% of the (enlarged) run, so it stays inside its box
LS = Pt(FS * 1.2)  # exact line spacing for boxes with subscripts
DOT = 0.44
PITCH = 0.57


def N(suffix):
    """N_max with a subscript, followed by suffix"""
    return [('N', {'italic': True}), ('max', {'sub': SUBOFF, 'size': FSUB}), (suffix, {})]


def z(sub, suffix):
    return [('z', {'italic': True}), (sub, {'sub': SUBOFF, 'size': FSUB}), (suffix, {})]


def dots(s, xc, yc, n, color, dx=0.0):
    y0 = yc - (n - 1) * PITCH / 2
    for i in range(n):
        box(s, xc - DOT / 2 + dx, y0 + i * PITCH - DOT / 2, DOT, DOT, fill=color, line=None, kind='oval')


def hdots(s, xc, yc, n, color):
    x0 = xc - (n - 1) * PITCH / 2
    for i in range(n):
        box(s, x0 + i * PITCH - DOT / 2, yc - DOT / 2, DOT, DOT, fill=color, line=None, kind='oval')


def units(s, xc, ytop, num, spacing=None):
    text(s, xc - 0.75, ytop, 1.5, 1.45, [num, 'units'], FS, margin=0.0, anchor='t', spacing=spacing)


def edit(prs):
    s = prs.slides[3]
    for sh in list(s.shapes):
        delete(sh)

    # ------------------------------------------------------------ columns
    cols = [(0.40, 5.60, 'Input processing'), (5.70, 19.00, 'Encoder with dual latent architecture'),
            (19.10, 26.40, 'Decoder architecture'), (26.50, 31.10, 'Output')]
    TOP, HDR, BOT = 0.45, 1.60, 18.90
    for x0, x1, t in cols:
        box(s, x0, TOP + HDR, x1 - x0, BOT - TOP - HDR, fill=PAL['grey'], line=PAL['navy'], lw=1.5)
        text(s, x0, TOP, x1 - x0, HDR, [t], FH, fill=PAL['green_hdr'], line=PAL['navy'], lw=1.5, margin=0.1)

    # ------------------------------------------------------------ encoder branches
    YS, YG = 4.80, 13.60
    C1, C2 = 6.45, 7.85                 # dot columns 256 and 128
    MB0, MBW = 8.65, 2.80               # mean / log-var boxes (2.50 -> 2.80, G-4: no text on the border)
    RB0, RBW = 12.85, 2.20              # reparameterisation boxes
    ZX = 16.65                          # latent dots
    TRUNK = 17.75                       # tap to the concatenation box
    BUS = 19.30                         # decoder input bus
    for yc, col, name, nz, zsub, zdim in ((YS, PAL['blue'], 'spatial', 3, 's', ' (24D)'),
                                          (YG, PAL['orange'], 'geometric', 4, 'g', ' (32D)')):
        text(s, (C1 + C2) / 2 - 1.4, yc - 2.70, 2.8, 1.45, [name.capitalize(), 'encoder'], FS, margin=0.0)
        dots(s, C1, yc, 4, col)
        dots(s, C2, yc, 3, col)
        units(s, C1, yc + 1.20, '256')
        units(s, C2, yc + 1.20, '128')
        arrow(s, C1 + 0.26, yc, C2 - 0.28, yc)
        for sign, lab in ((-1, 'Mean'), (1, 'Log-var')):
            y0 = yc - 2.20 if sign < 0 else yc + 0.10
            box(s, MB0, y0, MBW, 2.10, fill=None, line=col, lw=1.25, dash='sysDash', kind='round', adj=0.18)
            text(s, MB0, y0 + 0.02, MBW, 1.45, [lab, name], FS, margin=0.0, anchor='t')
            hdots(s, MB0 + MBW / 2, y0 + 1.70, 2, col)
            arrow(s, C2 + 0.24, yc + sign * 0.12, MB0 - 0.04, y0 + 1.05)
            arrow(s, MB0 + MBW + 0.04, y0 + 1.05, RB0 - 0.04, yc + sign * 0.18)
        text(s, RB0 + RBW / 2 - 2.50, yc - 1.85, 5.0, 0.75, ['Reparameterisation'], FS, margin=0.0)
        box(s, RB0, yc - 0.85, RBW, 1.70, fill=None, line=PAL['magenta'], lw=1.25, dash='sysDash', kind='round', adj=0.18)
        text(s, RB0 + RBW / 2 - 0.68, yc - 0.68, 1.36, 1.36, ['μ, σ'], FS, line=PAL['magenta'], lw=1.25, dash='sysDash', kind='oval',
             margin=0.0)
        arrow(s, RB0 + RBW + 0.04, yc, ZX - 0.30, yc)
        dots(s, ZX, yc, nz, PAL['magenta'])
        text(s, ZX - 1.25, yc + (nz - 1) * PITCH / 2 + 0.30, 2.5, 0.75, [z(zsub, zdim)], FS, margin=0.0, spacing=LS)
        # latent line to the decoder bus
        line(s, ZX + 0.24, yc, BUS, yc)

    # KL tag on both latents
    kl = text(s, 11.45, 8.27, 4.70, 1.56, [[('KL to ', {}), ('N', {'italic': True}), ('(0, ', {}), ('I', {'italic': True}), ('),', {})],
                                           'free bits 0.22 nats'], FS, fill=PAL['white'], line=PAL['magenta'], lw=1.25, dash='sysDash',
              kind='round', margin=0.05)
    line(s, 15.55, 8.27, ZX - 0.05, YS + 1.55, color=PAL['magenta'], lw=1.25, dash='sysDash')
    line(s, 15.55, 9.83, ZX - 0.05, YG - 1.10, color=PAL['magenta'], lw=1.25, dash='sysDash')

    # ------------------------------------------------------------ decoder rows
    RX0, RX1 = 19.45, 26.35
    D1, D2, D3, D4 = 2.25, 6.15, 10.05, 13.95
    DC1, DC2 = 20.35, 21.75
    GB0, GBW = 22.85, 3.20

    def row(y0, h, title_lines):
        box(s, RX0, y0, RX1 - RX0, h, fill=None, line=PAL['magenta'], lw=1.25, dash='sysDash', kind='round', adj=0.08)
        text(s, RX0, y0 + 0.05, RX1 - RX0, 0.74 * len(title_lines), title_lines, FS, margin=0.0)

    def green(x, y, w, h, runs):
        return text(s, x, y, w, h, [runs], FS, fill=PAL['green_box'], line=PAL['black'], lw=1.0, margin=0.03, spacing=LS)

    # D1 centre decoder (z_s): 128 -> 256 -> Nmax x 2
    row(D1, 3.75, ['Centre decoder'])
    yd1 = D1 + 1.50
    dots(s, DC1, yd1, 3, PAL['orange']); dots(s, DC2, yd1, 3, PAL['orange'])
    units(s, DC1, yd1 + 0.80, '128', 0.9); units(s, DC2, yd1 + 0.80, '256', 0.9)
    arrow(s, DC1 + 0.26, yd1, DC2 - 0.28, yd1); arrow(s, DC2 + 0.26, yd1, GB0 - 0.04, yd1)
    green(GB0, yd1 - 0.45, GBW, 0.90, N(' × 2'))
    # D2 existence head ([z_s, z_g]): 128 -> Nmax
    row(D2, 3.75, ['Existence head'])
    yd2 = D2 + 1.50
    dots(s, DC1, yd2, 3, PAL['orange']); units(s, DC1, yd2 + 0.80, '128', 0.9)
    arrow(s, DC1 + 0.26, yd2, GB0 - 0.04, yd2)
    green(GB0, yd2 - 0.45, GBW, 0.90, N(''))
    # D3 length decoder (z_g): 128 -> 256 -> Nmax
    row(D3, 3.75, ['Length decoder'])
    yd3 = D3 + 1.50
    dots(s, DC1, yd3, 3, PAL['orange']); dots(s, DC2, yd3, 3, PAL['orange'])
    units(s, DC1, yd3 + 0.80, '128', 0.9); units(s, DC2, yd3 + 0.80, '256', 0.9)
    arrow(s, DC1 + 0.26, yd3, DC2 - 0.28, yd3); arrow(s, DC2 + 0.26, yd3, GB0 - 0.04, yd3)
    green(GB0, yd3 - 0.45, GBW, 0.90, N(''))
    # D4 three direction heads (z_g): 128 each -> Nmax x 3 (weight, mean, concentration of a von Mises mixture)
    row(D4, 4.80, ['Direction heads: weight α,', 'mean μ, concentration κ'])   # title box 0.70 per line
    yd4 = D4 + 2.65
    for off, colr in ((0.44, 'FFE699'), (0.22, 'FFD34D'), (0.0, PAL['orange'])):     # three heads, stacked
        dots(s, DC1 + off, yd4 - off, 3, colr)
    text(s, DC1 - 0.70, yd4 + 1.18, 3.40, 0.75, ['3 × 128 units'], FS, margin=0.0)
    yb = [yd4 - 0.80, yd4, yd4 + 0.80]
    for sym, yy in zip(('α: ', 'μ: ', 'κ: '), yb):
        green(GB0, yy - 0.35, GBW, 0.70, [(sym, {})] + N(' × 3'))
        arrow(s, DC1 + 0.70, yd4 - 0.22, GB0 - 0.04, yy)

    # ------------------------------------------------------------ routing: z_s -> D1, [z_s, z_g] -> D2, z_g -> D3 and D4
    line(s, BUS, YS, BUS, yd1); arrow(s, BUS, yd1, DC1 - 0.30, yd1)
    line(s, BUS, yd3, BUS, yd4); arrow(s, BUS, yd3, DC1 - 0.30, yd3); arrow(s, BUS, yd4, DC1 - 0.60, yd4)
    cb = text(s, TRUNK - 1.15, yd2 - 0.78, 2.30, 1.56, [[('[', {})] + z('s', ', ') + z('g', ']'), '(56D)'], FS,
              fill=PAL['magenta'], line=PAL['black'], lw=1.0, margin=0.03, spacing=LS)
    line(s, TRUNK, YS, TRUNK, yd2 - 0.78); line(s, TRUNK, YG, TRUNK, yd2 + 0.78)
    arrow(s, TRUNK + 1.15, yd2, DC1 - 0.30, yd2)
    for yy in (YS, YG):                                   # junction dots
        box(s, TRUNK - 0.07, yy - 0.07, 0.14, 0.14, fill=PAL['black'], line=None, kind='oval')
    for yy in (YS, yd3, YG):
        pass

    # ------------------------------------------------------------ inputs: 20 m panels -> centres, and lengths and directions
    text(s, 0.75, YS - 0.76, 4.50, 1.52, [[('Centres (', {}), ('x', {'italic': True}), (', ', {}), ('y', {'italic': True}), (')', {})],
                                          '× 120'], FS, fill=PAL['white'], line=PAL['black'], lw=1.0, margin=0.05)
    arrow(s, 5.25, YS, C1 - 0.30, YS)
    text(s, 0.75, YG - 0.76, 4.50, 1.52, ['Length, direction', '× 120'], FS, fill=PAL['white'], line=PAL['black'], lw=1.0,
         margin=0.05)
    arrow(s, 5.25, YG, C1 - 0.30, YG)
    for k in range(3):
        picture(s, os.path.join(ICON, 'f3_panel_%d.png' % (k + 1)), 1.30 + 0.28 * k, 6.40 + 0.28 * k, 2.80, 2.80)
    text(s, 0.60, 9.92, 4.80, 1.45, ['20 m × 20 m', 'windows'], FS, margin=0.0)
    arrow(s, 3.00, 6.36, 3.00, YS + 0.80)
    arrow(s, 3.00, 11.38, 3.00, YG - 0.80)

    # ------------------------------------------------------------ outputs
    OX, OW, OH = 26.85, 3.90, 2.50
    for yd, f, lab in ((yd1, 'f3_out_centres.png', 'Centres'), (yd2, 'f3_out_exist.png', 'Existence mask'),
                       (yd3, 'f3_out_length.png', 'Length'), (yd4, 'f3_out_direction.png', 'Direction mixture')):
        picture(s, os.path.join(ICON, f), OX, yd - OH / 2, OW, OH)
        text(s, 26.50, yd + OH / 2 + 0.03, 4.60, 0.75, [lab], FS, margin=0.0)
        arrow(s, GB0 + GBW + 0.04, yd, OX - 0.06, yd)
    return s
