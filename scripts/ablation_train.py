# -*- coding: utf-8 -*-
"""Train one ablation model (docs/ABLATION.md). Same as scripts/train_evae.py except the model code
(src/model_ablation/training.py = the EVAE code + the single-latent switch and the geology-weight knob) and the arm's
switches. Arms: single_noguide, single_guide, dual_noguide (the dual latent with guide is the EVAE, models/evae).

Usage:  python scripts/ablation_train.py <arm> <S1|S2|S3> <fold> <run seed> [--out DIR]
        python scripts/ablation_train.py EVAE S1 2 1337      (check: the ablation code at the EVAE's settings must
                                                              reproduce the released EVAE checkpoint byte for byte)
Output: work/ablation_models_retrained/<arm>/<scheme>_f<fold>_s<seed>/ unless --out is given."""
import os, sys, json, time, random, hashlib, argparse, csv
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('arm'); ap.add_argument('scheme', choices=('S1', 'S2', 'S3')); ap.add_argument('fold', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--out', default=None)
A_ = ap.parse_args()
os.environ['LAMBDA_FREE'] = '0.22'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for k in ('EVGEO_W', 'EVBG_W', 'EVBG_MODEL', 'EVFIX_WGEO', 'EVFIX_SINGLE_LATENT'):
    os.environ.pop(k, None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'study'))
import study as C            # noqa: E402
import repo_paths as RP      # noqa: E402
import ablation as AB        # noqa: E402

label, single, guide, knobs, tag = AB.ARMS[A_.arm]
os.environ.update(knobs)
if os.environ.get('EVBG_W', '0') != '0':
    os.environ['EVBG_MODEL'] = str(RP.CLUSTERS_DIR / ('%s_f%d.json' % (A_.scheme, A_.fold)))
data = C.write_fold_data(A_.scheme, A_.fold)
RUN = '%s_%s_f%d_s%d' % (A_.scheme, tag, A_.fold, A_.seed)          # internal run name (it is part of the checkpoint file)
OUT = Path(A_.out).resolve() if A_.out else RP.WORK_DIR / 'ablation_models_retrained' / A_.arm / ('%s_f%d_s%d' % (A_.scheme, A_.fold, A_.seed))
if (OUT / 'run_status.json').exists():
    print('already trained', OUT); sys.exit(0)
for d in ('checkpoints', 'results', 'figures'):
    (OUT / d).mkdir(parents=True, exist_ok=True)
os.chdir(OUT)
sys.path.insert(0, str(AB.MODEL_ABL_DIR))
import numpy as np           # noqa: E402
import torch                 # noqa: E402
import training              # noqa: E402

assert Path(training.__file__).resolve() == (AB.MODEL_ABL_DIR / 'training.py').resolve(), training.__file__
torch.set_num_threads(4)
assert training.LAMBDA_FREE == 0.22 and training.ROUTEB_ISO is True
training.BASE_SAVE_DIR = str(OUT / 'never_used_generation_outputs')
random.seed(A_.seed); np.random.seed(A_.seed); torch.manual_seed(A_.seed); torch.cuda.manual_seed_all(A_.seed)
torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
try:
    torch.use_deterministic_algorithms(True, warn_only=True)
except Exception:
    pass
t0 = time.time()
device = training.device_select()
fit_samples = training.load_labelme(str(data / 'fit'))
val_samples = training.load_labelme(str(data / 'val'))
split = json.load(open(data / 'split.json'))
assert not set(split['test']) & {s['file'][:-5] for s in fit_samples + val_samples}   # no test box in training
for i, s in enumerate(fit_samples):
    s['sample_id'] = i
for i, s in enumerate(val_samples):
    s['sample_id'] = i
training.per, priors = training.extract_targets_and_priors(fit_samples)
priors['constraints'] = training.compute_data_driven_constraints_local(fit_samples)
train_dataset = training.EnhancedDataset(fit_samples, augment=False)
val_dataset = training.EnhancedDataset(val_samples, augment=False)
model, history = training.train_model_upgraded(train_dataset, val_dataset, priors, training.per, device,
                                               epochs=100, K_angle=3, run_name=RUN)
with torch.no_grad():
    batch = [train_dataset[i] for i in range(min(len(train_dataset), 400))]
    out = model(torch.stack([b['lines_norm'] for b in batch]).to(device), torch.stack([b['valid_mask'] for b in batch]).to(device),
                torch.stack([b['img_size'] for b in batch]).to(device))
    kls = float((0.5 * (out['smu'].pow(2) + out['slog'].exp() - out['slog'] - 1)).mean())
    klg = float((0.5 * (out['gmu'].pow(2) + out['glog'].exp() - out['glog'] - 1)).mean())
ckpt = OUT / 'checkpoints' / ('evai_best_%s.pt' % RUN)
(OUT / 'checkpoint.pt').write_bytes(ckpt.read_bytes())
sha = hashlib.sha256(ckpt.read_bytes()).hexdigest()
env = {k: os.environ.get(k) for k in ('EVGEO_W', 'EVBG_W', 'EVFIX_WGEO', 'EVFIX_SINGLE_LATENT', 'EVFIX_WQ', 'EVFIX_WLEN', 'LAMBDA_FREE', 'ROUTEB_ISO')}
json.dump(dict(arm=A_.arm, label=label, scheme=A_.scheme, fold=A_.fold, seed=A_.seed, internal_run_name=RUN, settings=env,
               model_class=type(model).__name__, n_params=int(sum(p.numel() for p in model.parameters())), model_code='src/model_ablation/training.py',
               device=str(device), n_fit=len(fit_samples), n_val=len(val_samples), traces_fit=sum(len(s['lines']) for s in fit_samples),
               epochs=len(history), elapsed_s=round(time.time() - t0, 1), best_val_loss=min(h['val_loss'] for h in history),
               kl_spatial=kls, kl_geometry=klg, classification='LATENT_COLLAPSE' if min(kls, klg) < 0.01 else 'STABLE',
               checkpoint='checkpoint.pt', checkpoint_sha256=sha), open(OUT / 'run_status.json', 'w'), indent=1, default=float)
with open(OUT / 'train_history.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['epoch', 'train_loss', 'val_loss']); w.writeheader()
    w.writerows([{k: h[k] for k in ('epoch', 'train_loss', 'val_loss')} for h in history])
reldir = AB.model_dir(A_.arm, A_.scheme, A_.fold, A_.seed); rel = reldir / 'run_status.json'
if OUT.resolve() == reldir.resolve():
    print('DONE', A_.arm, RUN, 'epochs', len(history), 'best val %.4f' % min(h['val_loss'] for h in history), '%.0fs' % (time.time() - t0), '| saved as the released model'); sys.exit(0)
same = rel.exists() and json.load(open(rel))['checkpoint_sha256'] == sha
print('DONE', A_.arm, RUN, 'epochs', len(history), 'best val %.4f' % min(h['val_loss'] for h in history), '%.0fs' % (time.time() - t0),
      '| identical to the released checkpoint' if same else ('| differs from the released checkpoint' if rel.exists() else '| (no released checkpoint yet)'))
