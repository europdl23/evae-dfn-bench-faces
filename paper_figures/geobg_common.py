# -*- coding: utf-8 -*-
"""Read-only access to the geobg release (SECTION1_EVAE_ADFNE_KDE_RELEASE_2026-10-01) for Figs. 2 and 5 and the graphical
abstract (copy of manuscript_revision_2026-10-01/code/geobg_common.py, final-paper version of 1 Oct 2026). In the release
files a sampling window is called "box" or "panel" and a realisation "network"; those keys are kept in the code. Nothing is written into the release: the release modules are not
imported (setbg.py is loaded by file path with byte-code writing switched off), and the box library, splits, cluster
models, realisation files (networks/) and example windows are only read.

  load_library()                 the 50 usable 20 m windows (lines normalised by the longest side, as the release)
  split(scheme, fi)              held-out / validation / training windows of a fold (data/splits), held-out fractures removed
  neighbours(sp, box)            the 8 neighbouring windows of a held-out window (release study.context)
  net(scheme, method, fi, box)   one realisation (default run seed 1337, first realisation)
  cluster_model(scheme, fi)      the learned trace-direction cluster model of a fold
  clusters(L, model)             cluster index per trace in the fixed order C1..C4 (0..3), unclustered = 4
  fit_all_panels()               the same cluster model (release setbg.fit, seed 20261001) fitted to ALL 735 clipped
                                 traces of the 50 windows (descriptive, for the site figure; the folds use training windows)
"""
import sys, json, math, csv, importlib.util
from pathlib import Path
import numpy as np

sys.dont_write_bytecode = True
import repo_root as _RR                              # repository paths (paper_figures/repo_root.py)
REL = _RR.REPO
DATA = REL / 'data'
EXAMPLES = json.load(open(REL / 'paper' / 'example_panels.json'))['panels']   # release folder paper_revision renamed paper
M = 20.0
REF = [125.0, 56.0, 27.0, 89.0]                                       # fixed cluster order C1..C4
CLU_COL = ['#0072B2', '#D55E00', '#CC79A7', '#F0E442', '#8C8C8C']     # C1..C4, unclustered
CLU_NAME = ['C1', 'C2', 'C3', 'C4', 'unclustered']
METHOD_COL = {'Held-out': '#333333', 'Mapped': '#000000', 'EVAE': '#009E73', 'ADFNE': '#E69F00', 'KDE': '#56B4E9'}

_spec = importlib.util.spec_from_file_location('release_setbg', str(REL / 'src' / 'study' / 'setbg.py'))
SB = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SB)


def example(label):
    return [e for e in EXAMPLES if e['label'] == label][0]


def geom(L):
    L = np.asarray(L, float).reshape(-1, 4)
    dx, dy = L[:, 2] - L[:, 0], L[:, 3] - L[:, 1]
    return np.column_stack(((L[:, 0] + L[:, 2]) / 2, (L[:, 1] + L[:, 3]) / 2)), np.hypot(dx, dy), np.mod(np.arctan2(dy, dx), np.pi)


def load_library():
    boxes = {}
    for r in csv.DictReader(open(DATA / 'box_library' / 'box_manifest.csv')):
        if r['usable'] != 'True':
            continue
        d = json.load(open(DATA / 'box_library' / 'boxes' / (r['box'] + '.json')))
        s = float(max(d['imageWidth'], d['imageHeight']))
        L = np.array([[x['points'][0][0] / s, x['points'][0][1] / s, x['points'][1][0] / s, x['points'][1][1] / s] for x in d['shapes']],
                     float).reshape(-1, 4)
        boxes[r['box']] = dict(name=r['box'], row=r['row'], ri=int(r['row_index']), col=int(r['col']), lines=L,
                               ids=np.array([x['description'] for x in d['shapes']], dtype=object), y_max=d['imageHeight'] / s,
                               cu=float(r['centre_u']), cs=float(r['centre_stack']))
    return boxes


LIB = load_library()


def split(scheme, fi):
    st = json.load(open(DATA / 'splits' / ('%s_f%d.json' % (scheme, fi))))
    test = st['test']
    held = set(np.concatenate([LIB[k]['ids'] for k in test]))
    panels = {}
    for k, b in LIB.items():
        if k in test:
            panels[k] = b
        else:
            keep = np.array([i not in held for i in b['ids']], bool)
            panels[k] = dict(b, lines=b['lines'][keep], ids=b['ids'][keep])
    return dict(scheme=scheme, fold=fi, test=test, val=st['validation'], fit=st['fitting'], panels=panels)


def neighbours(sp, bid, n=8):
    P = sp['panels']; b = P[bid]
    cand = [k for k in P if k not in sp['test']]
    return sorted(cand, key=lambda k: (math.hypot(P[k]['cu'] - b['cu'], P[k]['cs'] - b['cs']), k))[:n]


def net(scheme, method, fi, box, seed=1337, d=0):
    p = REL / 'networks' / scheme / method / ('f%d_%s_s%d_d%02d.csv' % (fi, box, seed, d))
    raw = np.loadtxt(p, delimiter=',')
    return np.atleast_2d(raw) if raw.size else np.zeros((0, 4))


def cluster_model(scheme, fi):
    return json.load(open(DATA / 'orientation_clusters' / ('%s_f%d.json' % (scheme, fi))))


def clusters(L, model):
    """cluster per trace: 0..3 = C1..C4 (matched to the fixed reference directions), 4 = unclustered"""
    from scipy.optimize import linear_sum_assignment
    L = np.asarray(L, float).reshape(-1, 4)
    if not len(L):
        return np.zeros(0, int)
    lab = SB.classify(geom(L)[2], model)
    c = np.asarray(model['centres_deg']); dd = np.abs((c[:, None] - np.asarray(REF)[None] + 90) % 180 - 90)
    r, k = linear_sum_assignment(dd); mp = {int(i): int(j) for i, j in zip(r, k)}; mp[model['K']] = len(REF)
    return np.array([mp.get(int(x), len(REF)) for x in lab], int)


def to_reference_order(m):
    """as release scripts/fit_orientation_clusters.py: clusters listed in the fixed direction order"""
    from scipy.optimize import linear_sum_assignment
    c = np.asarray(m['centres_deg']); dd = np.abs((c[:, None] - np.asarray(REF)[None] + 90) % 180 - 90)
    r, k = linear_sum_assignment(dd); o = [int(r[list(k).index(j)]) for j in sorted(k)]
    for key in ('mu2', 'kappa2', 'w_sets', 'centres_deg'):
        m[key] = [m[key][i] for i in o]
    return m


def fit_all_panels():
    th = np.concatenate([geom(b['lines'])[2] for b in LIB.values() if len(b['lines'])])
    return to_reference_order(SB.fit(th)), th


def check_fold_reproduction(scheme='S1', fi=2):
    """refit one fold from its training windows with this module and compare with the stored release model"""
    sp = split(scheme, fi)
    th = np.concatenate([geom(sp['panels'][k]['lines'])[2] for k in sp['fit'] if len(sp['panels'][k]['lines'])])
    m = to_reference_order(SB.fit(th)); ref = cluster_model(scheme, fi)
    return max(abs(a - b) for key in ('mu2', 'kappa2', 'w_sets', 'centres_deg') for a, b in zip(m[key], ref[key]))


def mixture_density_deg(model, deg):
    """mixture density per degree of trace direction (axial von Mises on 2 theta + uniform), and each component"""
    th = np.radians(np.asarray(deg, float)); z = 2 * th
    comps = [w * np.exp(k * (np.cos(z - mu) - 1.0)) / (2 * math.pi * SB.i0e(k)) for w, mu, k in zip(model['w_sets'], model['mu2'], model['kappa2'])]
    comps.append(np.full_like(z, model['w_bg'] / (2 * math.pi)))
    f = 2 * math.pi / 180.0                                            # density on 2 theta (per radian) -> per degree of theta
    return [c * f for c in comps]
