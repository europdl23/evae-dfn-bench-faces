# -*- coding: utf-8 -*-
"""No-photograph check (author decision of 2 Oct 2026: the mine operator does not permit photographs).

Lists every image that can reach a reader and measures how "photographic" it is:
  1. every media part of out/figures/Ppt_edit_figures_REVISED.pptx (all slides, with the slide that uses it);
  2. every image object inside every PDF of out/figures (Figures 1-11, S1, graphical abstract);
  3. every PNG of out/figures (the rendered figure itself).
Photographic measure: the image is taken to at most 1600 px (nearest neighbour, colours kept) and cut into 8 x 8 blocks;
a block is "photo-like" when its 64 pixels hold 32 or more distinct colours (camera noise and natural texture); the
measure is the share of photo-like blocks among the mostly non-white blocks. Calibration on 2 Oct 2026: the withheld
photo figures score 0.07 (Fig. 1, photographs in Step 1 only) to 0.83 (Fig. 2), the photograph icons of the old deck 0.29
to 0.99; drawings and data figures score at most 0.02. An image is flagged above 0.05. The measure only flags
candidates: every figure must also be LOOKED at. Prints a table; exits 1 if any image is flagged.
Usage: python -B check_media.py [--report PATH]"""
import io, sys, zipfile, re
from pathlib import Path
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
import schem_paths as _SP                               # repository paths
FIG = Path(_SP.FIG_OUT)
DECK = FIG / 'Ppt_edit_figures_REVISED.pptx'
PHOTO_FLAG = 0.05           # flag an image if more than 5 % of its non-white blocks are photo-like


def measure(im):
    """(distinct colours, non-white share, photo-like block share) at most 1600 px"""
    im = im.convert('RGB')
    if max(im.size) > 1600:
        f = 1600 / max(im.size)
        im = im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.NEAREST)
    a = np.asarray(im).astype(np.int32)
    code = (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]
    ncol = len(np.unique(code))
    h, w = code.shape[0] // 8 * 8, code.shape[1] // 8 * 8
    if h == 0 or w == 0:
        return ncol, 0.0, 0.0
    b = code[:h, :w].reshape(h // 8, 8, w // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    nd = 1 + (np.diff(np.sort(b, axis=1), axis=1) != 0).sum(axis=1)
    nonwhite = (b != 0xFFFFFF).mean(axis=1) > 0.5
    share = float((nd[nonwhite] >= 32).mean()) if nonwhite.any() else 0.0
    return ncol, float(nonwhite.mean()), share


rows = []
# 1. deck media
with zipfile.ZipFile(DECK) as z:
    names = z.namelist()
    # slideN.xml -> position in the deck, read from the saved package itself (python-pptx renames slide parts in memory
    # when .slides is accessed, so its part names need not match the zip: the deck keeps slide1, slide4, slide5)
    _rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', z.read('ppt/_rels/presentation.xml.rels').decode('utf-8')))
    ORDER = {_rels[r]: k for k, r in enumerate(re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', z.read('ppt/presentation.xml').decode('utf-8')), 1)}
    use = {}
    for n in names:
        if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels', n):
            sl = re.findall(r'slide(\d+)', n)[0]
            for t in re.findall(r'Target="\.\./media/([^"]+)"', z.read(n).decode('utf-8')):
                k = ORDER.get('slide%s.xml' % sl)
                use.setdefault(t, []).append('slide %s (Fig. %s)' % (k, {1: '1', 2: '3', 3: '4'}.get(k, '?')) if k else 'slide part %s, NOT IN THE DECK' % sl)
    slides = sorted(n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n))
    for n in sorted(x for x in names if x.startswith('ppt/media/')):
        nm = n.split('/')[-1]
        try:
            im = Image.open(io.BytesIO(z.read(n))); im.load()
            ncol, nw, sh = measure(im)
            rows.append(('deck media', nm, '%s; used by %s' % ('x'.join(map(str, im.size)), ', '.join(use.get(nm, ['NO SLIDE']))), ncol, nw, sh))
        except Exception as e:                                # vector media (emf/wmf) cannot be photographs of the site
            rows.append(('deck media', nm, 'not a raster image (%s); used by %s' % (type(e).__name__, ', '.join(use.get(nm, ['NO SLIDE']))), 0, 0.0, 0.0))
    rows.append(('deck', DECK.name, '%d slides, %d media parts' % (len(slides), sum(1 for x in names if x.startswith('ppt/media/'))), 0, 0.0, 0.0))

# 2. image objects inside the figure PDFs
import fitz
for pdf in sorted(FIG.glob('*.pdf')):
    doc = fitz.open(str(pdf))
    imgs = [(p.number, x) for p in doc for x in p.get_images(full=True)]
    if not imgs:
        rows.append(('PDF image objects', pdf.name, 'none (vector only)', 0, 0.0, 0.0))
    for pno, x in imgs:
        pix = fitz.Pixmap(doc, x[0])
        if pix.n - pix.alpha >= 4:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        im = Image.open(io.BytesIO(pix.tobytes('png')))
        ncol, nw, sh = measure(im)
        rows.append(('PDF image objects', pdf.name, 'xref %d, %dx%d' % (x[0], x[2], x[3]), ncol, nw, sh))

# 3. the rendered figures
for png in sorted(FIG.glob('*.png')):
    im = Image.open(png)
    ncol, nw, sh = measure(im)
    rows.append(('figure PNG', png.name, 'x'.join(map(str, im.size)), ncol, nw, sh))

out = ['| Source | File | Detail | Distinct colours | Non-white block share | Photo-like block share | Flag |', '|---|---|---|---|---|---|---|']
flags = 0
for src, f, d, ncol, nw, sh in rows:
    flag = sh > PHOTO_FLAG
    flags += flag
    out.append('| %s | %s | %s | %d | %.2f | %.3f | %s |' % (src, f, d, ncol, nw, sh, 'CHECK' if flag else ''))
out.append('')
out.append('%d images measured, %d flagged (photo-like block share above %.2f).' % (len(rows), flags, PHOTO_FLAG))
out.append('A flag is a candidate only: small images that PowerPoint downsampled for the PDF (about 200 dpi) blend line colours and can')
out.append('score above the threshold. Every flagged image must be looked at (extract: checks/nophoto/pdf_images/).')
txt = '\n'.join(out)
print(txt)
if '--report' in sys.argv:
    Path(sys.argv[sys.argv.index('--report') + 1]).write_text(txt + '\n', encoding='utf-8')
sys.exit(1 if flags else 0)
