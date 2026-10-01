# -*- coding: utf-8 -*-
"""Ablation of the EVAE (docs/ABLATION.md): single vs dual latent, without vs with the geology-informed terms (2 x 2).

  geology-informed terms = the released geology term (weight 0.005) + the trace-direction term (EVGEO_W 1.0)
          + the trace-direction-cluster share term (EVBG_W 1.0); "without terms" switches all three off
  (internal names: "guide" = with the terms, "noguide" = without)
  single latent = the Paper 1 SingleLatentVAE (one joint encoder, every decoder head reads the whole 56-d code)

The dual-latent arm with the terms is the full EVAE itself (models/evae, networks/<scheme>/EVAE). Every arm is generated
with the EVAE's own generator seeds, crc32('EVAE|scheme|geobg|fold|box|run seed|draw'), so all arms use the same
seeds (paired draws) and the same run seeds (1337, 20260903, 7) and draws (0-7)."""
import sys, math
from pathlib import Path
import numpy as np

import study as C
import repo_paths as RP

MODEL_ABL_DIR = RP.SRC_DIR / 'model_ablation'
# arm -> (label, single latent?, terms on?, environment knobs for training, internal run tag)
ARMS = {
    'single_noguide': ('Single-latent EVAE without geology-informed terms', True, False, {'EVGEO_W': '0', 'EVBG_W': '0', 'EVFIX_WGEO': '0', 'EVFIX_SINGLE_LATENT': '1'}, 'ablSLG0'),
    'single_guide': ('Single-latent EVAE', True, True, {'EVGEO_W': '1.0', 'EVBG_W': '1.0', 'EVFIX_SINGLE_LATENT': '1'}, 'ablSLGEOBG'),
    'dual_noguide': ('EVAE without geology-informed terms', False, False, {'EVGEO_W': '0', 'EVBG_W': '0', 'EVFIX_WGEO': '0'}, 'ablDLG0'),
    'EVAE': ('Full EVAE', False, True, {'EVGEO_W': '1.0', 'EVBG_W': '1.0'}, 'geobg'),
}
ORDER = ['single_noguide', 'single_guide', 'dual_noguide', 'EVAE']
TRAINED_HERE = ['single_noguide', 'single_guide', 'dual_noguide']      # the EVAE models are in models/evae


def model_dir(arm, scheme, fi, seed, root=None):
    if arm == 'EVAE':
        return RP.MODELS_DIR / ('%s_f%d_s%d' % (scheme, fi, seed))
    return Path(root or (RP.REPO_ROOT / 'models' / 'ablation')) / arm / ('%s_f%d_s%d' % (scheme, fi, seed))


def net_path(arm, scheme, fi, box, seed, d, root=None):
    return C.net_path(scheme, arm, fi, box, seed, d, root=root)          # networks/<scheme>/<arm>/...; EVAE = the EVAE's own


def generator_seed(scheme, fi, box, seed, d):
    """the EVAE's generator seed, used by every arm"""
    return C.network_seed('EVAE', scheme, fi, box, seed, d)


_mod = None


def ablation_training():
    """src/model_ablation/training.py, loaded once under its own module name"""
    global _mod
    if _mod is None:
        import importlib.util
        if str(MODEL_ABL_DIR) not in sys.path:
            sys.path.insert(0, str(MODEL_ABL_DIR))
        spec = importlib.util.spec_from_file_location('training_ablation', str(MODEL_ABL_DIR / 'training.py'))
        _mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(_mod)
    return _mod


def load_model(ckpt, single):
    """dual: the released loader (generators.load_evae). single: SingleLatentVAE, strict load, same device rule."""
    if not single:
        return C.generators.load_evae(str(ckpt))
    import torch
    model = ablation_training().SingleLatentVAE(spatial_dim=24, geometry_dim=32, K_angle=3)
    model.load_state_dict(torch.load(str(ckpt), map_location='cpu'), strict=True)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    return model.to(dev).eval(), dev


def generate(model, dev, y_max, seed_gen, post, draw, single):
    """study.generate for dual models; for single-latent models every head reads z = cat(z_s, z_g).
    Same random-number order in both cases. Returns (clipped lines, top-10 fallback fired?)."""
    import torch
    import torch.nn.functional as F
    torch.manual_seed(seed_gen)
    rng = np.random.default_rng(seed_gen)
    sm, ss, gm, gs = post[draw % len(post)]
    with torch.no_grad():
        eps_s = torch.randn(1, 24, device=dev)
        eps_g = torch.randn(1, 32, device=dev)
        sz = sm + eps_s * ss
        gz = gm + eps_g * gs
        m = model
        zc = torch.cat([sz, gz], 1)
        zs, zg = (zc, zc) if single else (sz, gz)
        centers = torch.sigmoid(m.spatial_decoder(zs)).view(-1, m.max_lines, 2)[0]
        lengths = torch.sigmoid(m.length_decoder(zg)).view(-1, m.max_lines)[0]
        logits = m.angle_logits_head(zg).view(-1, m.max_lines, m.K_angle)[0]
        mu_raw = m.angle_mu_head(zg).view(-1, m.max_lines, m.K_angle)[0]
        kappa_raw = m.angle_kappa_head(zg).view(-1, m.max_lines, m.K_angle)[0]
        alpha = F.softmax(logits, dim=-1).cpu().numpy()
        mu = (math.pi * torch.tanh(mu_raw)).cpu().numpy()
        kappa = (F.softplus(kappa_raw) + 1e-4).cpu().numpy()
        exist = m.existence_head(zc).view(-1, m.max_lines)[0]
        keep = (torch.sigmoid(exist) >= 0.5).cpu().numpy()
        fallback = bool(keep.sum() < 2)
        if fallback:
            keep = np.zeros(m.max_lines, bool)
            keep[torch.topk(exist, 10).indices.cpu().numpy()] = True
        c = centers.cpu().numpy()[keep]
        L = lengths.cpu().numpy()[keep]
        aa, am, ak = alpha[keep], mu[keep], kappa[keep]
    th = []
    for j in range(len(c)):
        k = rng.choice(m.K_angle, p=aa[j] / aa[j].sum())
        th.append((rng.vonmises(2.0 * am[j, k], max(ak[j, k], 1e-4)) / 2.0) % math.pi)
    th = np.asarray(th)
    dx, dy = np.cos(th) * L / 2, np.sin(th) * L / 2
    segs = np.column_stack([c[:, 0] - dx, c[:, 1] - dy, c[:, 0] + dx, c[:, 1] + dy])
    return C.common.clip_lines(segs, y_max), fallback
