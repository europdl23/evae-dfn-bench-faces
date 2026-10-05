# Threshold 0.5 vs the released S1 EVAE realisations (byte comparison).
_REPO = __import__('pathlib').Path(__file__).resolve().parents[2]   # repository root (sensitivity/<test>/ lies two levels down)
import filecmp
from pathlib import Path
W = Path(__file__).resolve().parent; R = (_REPO)
fs = sorted((W / 'networks/T05/S1/EVAE').glob('*.csv'))
print('threshold 0.5 realisations byte-identical to release:', sum(filecmp.cmp(f, R / 'networks/S1/EVAE' / f.name, shallow=False) for f in fs), 'of', len(fs))
