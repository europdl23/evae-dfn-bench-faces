# Reproduction check: retrained N_max 120 vs released checkpoints and released S1 EVAE realisations.
_REPO = __import__('pathlib').Path(__file__).resolve().parents[2]   # repository root (sensitivity/<test>/ lies two levels down)
import json, hashlib, filecmp
from pathlib import Path
import numpy as np
W = Path(__file__).resolve().parent; R = (_REPO)
same = sum(json.load(open(p))['checkpoint_sha256'] == json.load(open(R / 'models/evae' / p.parent.name / 'run_status.json'))['checkpoint_sha256'] for p in (W / 'models/N120').glob('*/run_status.json'))
print('N120 checkpoints identical to release:', same, 'of 12')
fs = sorted((W / 'networks/N120/S1/EVAE').glob('*.csv')); mx = 0.0; eq = 0
for f in fs:
    a = np.loadtxt(f, delimiter=',').reshape(-1, 4); b = np.loadtxt(R / 'networks/S1/EVAE' / f.name, delimiter=',').reshape(-1, 4)
    if a.shape == b.shape: eq += 1; mx = max(mx, float(np.abs(a - b).max()) if a.size else 0.0)
print('N120 realisations same shape as release:', eq, 'of', len(fs), '; max abs coordinate difference', mx)
rel = sorted((W / 'networks/N120_release/S1/EVAE').glob('*.csv'))
print('regenerated from release checkpoints byte-identical to retrained-120 realisations:', sum(filecmp.cmp(f, W / 'networks/N120/S1/EVAE' / f.name, shallow=False) for f in rel), 'of', len(rel))
