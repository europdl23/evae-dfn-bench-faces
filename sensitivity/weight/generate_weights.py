# Generate the 24 realisations per held-out S1 window for one weight variant, exactly as scripts/generate_networks.py evae
# (CUDA, as the release; same generator seeds for every variant). Usage: python generate_weights.py <variant>
import os, sys
from pathlib import Path
W = Path(__file__).resolve().parent
V = sys.argv[1]
os.environ['EVAE_NMAX'] = '120'; os.environ['S1_WORK_DIR'] = str(W / 'work')
sys.path.insert(0, str(W / 'code' / 'src' / 'study'))
import study as C
import torch
torch.set_num_threads(4)
mroot = W / 'models' / V; out = W / 'networks' / V; n = 0
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
                C.save_net(C.net_path('S1', 'EVAE', fi, b, seed, d, root=out), C.generate(model, dev, P[b]['y_max'], g, post, d)); n += 1
print(V, 'realisations', n, 'device', dev)
