# -*- coding: utf-8 -*-
"""Step 1a (before the protocol): percolation parameter p = sum(l^2) / A of the MAPPED panels only (intact, all 50
usable panels). No generator is looked at. Decides whether an equivalent permeability is meaningful (needs p above
the 2D threshold of about 5.6)."""
import numpy as np, pandas as pd
import eng_common as E
C = E.C

lib = C.load_library(); rows = []
for k, b in lib.items():
    L = np.asarray(b['lines'], float).reshape(-1, 4)
    A = b['y_max'] * C.M * C.M
    ln = C.common.geom(L)[1] * C.M if len(L) else np.zeros(0)
    rows.append(dict(panel=k, bench=b['row'], n=len(L), area_m2=A, p=float((ln ** 2).sum() / A), P21=float(ln.sum() / A)))
D = pd.DataFrame(rows).sort_values('panel'); D.to_csv(E.TAB / 'step1a_percolation_mapped_panels.csv', index=False)
print(D.p.describe().round(2).to_string())
print('panels with p >= %.1f: %d of %d' % (E.P_CRIT, (D.p >= E.P_CRIT).sum(), len(D)))
print('max p: %.2f (%s); 90th percentile %.2f' % (D.p.max(), D.loc[D.p.idxmax(), 'panel'], D.p.quantile(0.9)))
