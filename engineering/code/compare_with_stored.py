# -*- coding: utf-8 -*-
"""Compare a rerun (work/engineering/tables) with the stored tables (engineering/tables) used in the paper.
Added for the repository. Numbers are compared to 1e-9 (relative), text exactly. Usage: python compare_with_stored.py"""
import sys
import numpy as np, pandas as pd
import eng_common as E

bad, n = [], 0
for f in sorted(E.STORED.glob('*.csv')):
    g = E.TAB / f.name
    if not g.exists():
        print('not rerun: %s' % f.name); continue
    a, b = pd.read_csv(f, keep_default_na=False), pd.read_csv(g, keep_default_na=False)
    same = list(a.columns) == list(b.columns) and a.shape == b.shape
    if same:
        for c in a.columns:
            x, y = pd.to_numeric(a[c], errors='coerce'), pd.to_numeric(b[c], errors='coerce')
            num = x.notna() & y.notna()
            if not (a[c][~num].astype(str).values == b[c][~num].astype(str).values).all():
                same = False; break
            if num.any() and not np.allclose(x[num], y[num], rtol=1e-9, atol=1e-12):
                same = False; break
    n += 1
    print('%-45s %s' % (f.name, 'identical' if same else 'DIFFERENT'))
    if not same:
        bad.append(f.name)
print('%d tables compared, %d different' % (n, len(bad)))
sys.exit(1 if bad else 0)
