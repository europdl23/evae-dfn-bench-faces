# Generate the 24 realisations per held-out S1 window from the RELEASED S1 EVAE checkpoints at one existence threshold,
# exactly as scripts/generate_networks.py evae (CUDA, as the release). Records slots passing, fallback use, traces.
# Usage: python generate_thr.py <threshold>
_REPO = __import__('pathlib').Path(__file__).resolve().parents[2]   # repository root (sensitivity/<test>/ lies two levels down)
import os, sys, csv
from pathlib import Path
W = Path(__file__).resolve().parent
THR = sys.argv[1]; os.environ['EVAE_THR'] = THR; os.environ['S1_WORK_DIR'] = str(W / 'work')
sys.path.insert(0, str(W / 'code' / 'src' / 'study'))
import study as C
import torch
torch.set_num_threads(4)
tag = 'T' + THR.replace('.', '')
mroot = (_REPO / 'models' / 'evae')
out = W / 'networks' / tag; rows = []
lib = C.load_library()
for fi in range(4):
    sp = C.split('S1', fi, lib); P = sp['panels']
    for seed in C.SEEDS:
        model, dev = C.generators.load_evae(str(mroot / ('S1_f%d_s%d' % (fi, seed)) / 'checkpoint.pt'))
        assert model.max_lines == 120
        for b in sp['test']:
            post = C.aggregate_posterior(model, dev, P, C.context(sp, b))
            for d in range(C.NDRAW):
                g = C.network_seed('EVAE', 'S1', fi, b, seed, d)
                L = C.generate(model, dev, P[b]['y_max'], g, post, d)
                C.save_net(C.net_path('S1', 'EVAE', fi, b, seed, d, root=out), L)
                torch.manual_seed(g); sm, ss, gm, gs = post[d % len(post)]
                with torch.no_grad():
                    sz = sm + torch.randn(1, 24, device=dev) * ss; gz = gm + torch.randn(1, 32, device=dev) * gs
                    p = torch.sigmoid(model.existence_head(torch.cat([sz, gz], 1)))
                    act = int((p >= float(THR)).sum())
                rows.append(dict(threshold=THR, fold=fi, box=b, run_seed=seed, draw=d, slots_passing=act, fallback=int(act < 2), traces=len(L)))
with open(W / 'outputs' / ('slots_%s.csv' % tag), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(tag, 'realisations', len(rows), 'device', dev)
