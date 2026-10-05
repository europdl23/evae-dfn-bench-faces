# -*- coding: utf-8 -*-
"""Engineering measures of one 2D trace network in a panel (PROTOCOL_ENGINEERING.md, Section 1).

Coordinates: traces in metres, x along the bench (0..W), y down the face (0..H); trace direction
theta = atan2(dy, dx) mod pi, the convention of the release (common.geom)."""
import math
import numpy as np
import eng_common as E

C = E.C
TOL, EDGE = 0.3, 0.1                  # m: end-on-trace contact and side-touch tolerances (release topology.py)
SPACING, BAND, MIN_LINE = 0.5, 0.25, 10.0   # m: persistence lines (perpendicular spacing, half band width, minimum length)


def to_m(L):
    return np.asarray(L, float).reshape(-1, 4) * C.M


# ---------------------------------------------------------------- deformability: crack-density tensor
def crack_tensor(Lm, area):
    """alpha = (1/A) sum a^2 n n^T, a = half-length, n = unit normal of the trace"""
    if not len(Lm):
        return np.zeros((2, 2))
    d = Lm[:, 2:] - Lm[:, :2]; l = np.hypot(d[:, 0], d[:, 1])
    th = np.arctan2(d[:, 1], d[:, 0]); n = np.column_stack((-np.sin(th), np.cos(th)))
    a2 = (l / 2) ** 2
    return (a2[:, None, None] * n[:, :, None] * n[:, None, :]).sum(0) / area


def deformability(Lm, W, H):
    al = crack_tensor(Lm, W * H)
    out = dict(rho=float(np.trace(al)), E_along=1.0 / (1.0 + 2 * math.pi * al[0, 0]), E_down=1.0 / (1.0 + 2 * math.pi * al[1, 1]))
    lam, vec = np.linalg.eigh(al)                       # ascending
    s = lam.sum()
    out['aniso'] = float((lam[1] - lam[0]) / s) if s > 0 else np.nan
    v = vec[:, 1]                                       # direction of largest m.alpha.m = softest loading direction
    out['soft_dir_deg'] = float(math.degrees(math.atan2(v[1], v[0])) % 180) if s > 0 else np.nan
    return out


# ---------------------------------------------------------------- connectivity
def percolation_p(Lm, area):
    if not len(Lm):
        return 0.0
    d = Lm[:, 2:] - Lm[:, :2]
    return float(((d ** 2).sum(1)).sum() / area)


def _pt_seg(P, A, B):
    d = B - A; l2 = np.maximum((d ** 2).sum(1), 1e-12)
    t = np.clip(((P[:, None, :] - A[None]) * d[None]).sum(2) / l2[None], 0, 1)
    return np.linalg.norm(P[:, None, :] - (A[None] + t[..., None] * d[None]), axis=2)


def clusters(Lm):
    """connected clusters: traces linked if they cross or an end lies within TOL of the other trace"""
    n = len(Lm); parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj: parent[ri] = rj
    if n > 1:
        for x in C.common.crossings_xy(Lm):
            union(int(x[0]), int(x[1]))
        Ends = np.vstack([Lm[:, :2], Lm[:, 2:]]); own = np.r_[np.arange(n), np.arange(n)]
        D = _pt_seg(Ends, Lm[:, :2], Lm[:, 2:]); D[np.arange(2 * n), own] = np.inf
        for e, j in zip(*np.where(D <= TOL)):
            union(int(own[e]), int(j))
    lab = np.array([find(i) for i in range(n)], int)
    return lab


def connectivity(Lm, W, H):
    if not len(Lm):
        return dict(span=0.0, largest_share=np.nan)
    lab = clusters(Lm); l = np.hypot(*(Lm[:, 2:] - Lm[:, :2]).T)
    span = 0
    for c in np.unique(lab):
        P = np.vstack([Lm[lab == c, :2], Lm[lab == c, 2:]])
        left, right = (P[:, 0] <= EDGE).any(), (P[:, 0] >= W - EDGE).any()
        top, bot = (P[:, 1] <= EDGE).any(), (P[:, 1] >= H - EDGE).any()
        if (left and right) or (top and bot):
            span = 1; break
    tot = l.sum(); big = max(l[lab == c].sum() for c in np.unique(lab))
    return dict(span=float(span), largest_share=float(big / tot) if tot > 0 else np.nan)


# ---------------------------------------------------------------- persistence (Jennings) along a cluster direction
def lines_in_panel(phi, W, H, spacing=SPACING, min_len=MIN_LINE):
    """parallel lines at direction phi (rad): list of (s, t0, t1) with s the offset along the normal v and
    [t0, t1] the part inside the panel along u; only lines of at least min_len"""
    u = np.array([math.cos(phi), math.sin(phi)]); v = np.array([-math.sin(phi), math.cos(phi)])
    corners = np.array([[0, 0], [W, 0], [0, H], [W, H]], float); vs = corners @ v
    out = []
    for s in np.arange(vs.min() + spacing / 2, vs.max(), spacing):
        lo, hi = -np.inf, np.inf
        for k, lim in ((0, W), (1, H)):
            if abs(u[k]) < 1e-12:
                if not (0 <= s * v[k] <= lim): lo, hi = 1, 0
                continue
            a, b = (0 - s * v[k]) / u[k], (lim - s * v[k]) / u[k]
            lo, hi = max(lo, min(a, b)), min(hi, max(a, b))
        if hi - lo >= min_len:
            out.append((s, lo, hi))
    return out, u, v


def persistence(Lm_cluster, phi, W, H, band=BAND):
    """mean and maximum persistence k over the lines; k = covered length / line length"""
    lines, u, v = lines_in_panel(phi, W, H)
    if not lines:
        return dict(k_mean=np.nan, k_max=np.nan, n_lines=0)
    ks = []
    P, Q = Lm_cluster[:, :2], Lm_cluster[:, 2:]
    vp, vq, tp, tq = P @ v, Q @ v, P @ u, Q @ u
    for s, t0, t1 in lines:
        iv = []
        for i in range(len(Lm_cluster)):
            dv = vq[i] - vp[i]
            if abs(dv) < 1e-12:
                if abs(vp[i] - s) > band: continue
                l0, l1 = 0.0, 1.0
            else:
                a, b = (s - band - vp[i]) / dv, (s + band - vp[i]) / dv
                l0, l1 = max(0.0, min(a, b)), min(1.0, max(a, b))
                if l1 <= l0: continue
            ta, tb = tp[i] + l0 * (tq[i] - tp[i]), tp[i] + l1 * (tq[i] - tp[i])
            ta, tb = max(min(ta, tb), t0), min(max(ta, tb), t1)
            if tb > ta: iv.append((ta, tb))
        cov = 0.0
        if iv:
            iv.sort(); cs, ce = iv[0]
            for a, b in iv[1:]:
                if a > ce: cov += ce - cs; cs, ce = a, b
                else: ce = max(ce, b)
            cov += ce - cs
        ks.append(cov / (t1 - t0))
    ks = np.array(ks)
    return dict(k_mean=float(ks.mean()), k_max=float(ks.max()), n_lines=len(ks))


# ---------------------------------------------------------------- all measures of one network
def cluster_dirs(model):
    """fold's cluster centres (rad) for canonical C1 (~125 deg) and C2 (~56 deg), via the release's canon()"""
    import make_figures as MF
    K = model['K']; can = MF.canon(np.arange(K), model)
    out = {}
    for j in (0, 1):
        i = np.where(can == j)[0]
        out[j] = math.radians(model['centres_deg'][int(i[0])]) if len(i) else None
    return out


def measures(L_units, y_max, model, dirs):
    import make_figures as MF
    L = np.asarray(L_units, float).reshape(-1, 4); Lm = to_m(L); W, H = C.M, y_max * C.M; A = W * H
    out = dict(n=len(L), p=percolation_p(Lm, A))
    out.update(deformability(Lm, W, H)); out.update(connectivity(Lm, W, H))
    tp = E.topology(L, y_max) if len(L) else dict(term_share=np.nan, pX=np.nan)
    out['term_share'] = tp['term_share']; out['pX'] = tp['pX']
    lab = MF.canon(E.SB.classify(C.common.geom(L)[2], model), model) if len(L) else np.zeros(0, int)
    for j, name in ((0, 'C1'), (1, 'C2')):
        if dirs.get(j) is None:
            out['k_mean_' + name] = out['k_max_' + name] = np.nan; continue
        r = persistence(Lm[lab == j], dirs[j], W, H)
        out['k_mean_' + name] = r['k_mean']; out['k_max_' + name] = r['k_max']
    return out
