# -*- coding: utf-8 -*-
"""Decision 2 (MY_VIEW_ON_FINAL_REVIEW Section 8): why the baselines get two trace-direction components.

Per fold (15 folds, training windows only, the same traces the release fits use), with RELEASE code only:
  (a) plain axial von Mises mixture on 2 theta = the baselines' own fit (REL/src/evaluation/common.py fit_set_rule,
      EM seed 20260907, 5 restarts, 300 iterations), K = 1..6, BIC with 3K - 1 free parameters;
      the K = 2 fit is checked against the stored baseline fit (REL/data/baseline_fits/<fold>.json);
  (b) the same mixture plus a uniform component, WITHOUT the tightness rule (REL/src/study/setbg.py fit with
      kappa_min = 1e-3 instead of 8), K = 1..6, BIC with 3K free parameters (setbg's own count);
  (c) the constrained model of the paper (kappa >= 8 on 2 theta, uniform component; REL/data/orientation_clusters,
      K = 4 in every fold) and its BIC at K = 4 (stored; a re-fit with setbg.fit, K = 1..6, is asserted to give it).
Question: in how many folds does (a) / (b) pick K = 2, and is the unconstrained K = 2 BIC lower than the constrained
K = 4 BIC in every fold? Sensitivity: the independent EM of the review check (k_check.py: 10 restarts, 400
iterations, seed 20261001, same BIC) for (a).
Read-only on the release; no bytecode is written there. Output: this script's log (kfit_unconstrained_log.txt) and
../tables/kfit_unconstrained.csv."""
# Repository copy (2 October 2026): only the paths were changed (repository root, outputs to work/side_check).
import sys, os, math, json
sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np
from scipy.special import i0e, i1e

def _repo_root():                                       # repository version: the folder holding .repo-root (or EVAE_REPO)
    if os.environ.get('EVAE_REPO'):
        return Path(os.environ['EVAE_REPO']).resolve()
    for d in Path(__file__).resolve().parents:
        if (d / '.repo-root').exists():
            return d
    raise RuntimeError('repository root not found: no .repo-root marker (or set EVAE_REPO)')


REL = _repo_root()
OUT = Path(os.environ.get('SIDE_CHECK_OUT', str(REL / 'work' / 'side_check')))
OUT.mkdir(parents=True, exist_ok=True)   # repository: a rerun never writes over side_check/tables
os.environ.setdefault('S1_WORK_DIR', str(REL / 'work' / 'side_check' / 'scratch'))
sys.path[:0] = [str(REL / 'src' / 'study'), str(REL / 'src'), str(REL / 'src' / 'evaluation')]
import study as C          # noqa: E402
import setbg as SB         # noqa: E402
import pandas as pd        # noqa: E402

TWO_PI = 2 * math.pi


def sd_theta(k2):
    """axial circular SD on theta (deg) of a von Mises with concentration k2 on 2 theta"""
    A = float(i1e(k2) / i0e(k2))
    return math.degrees(math.sqrt(-2 * math.log(max(A, 1e-12)))) / 2


def plain_release(theta, K):
    f = C.common.fit_set_rule(theta, k=K)
    n = len(theta); p = 3 * K - 1
    return dict(K=K, ll=f['loglik'], bic=-2 * f['loglik'] + p * math.log(n), cent=[math.degrees(x) for x in f['centres_theta']],
                kap=list(f['kappa2']), w=list(f['weights']))


def _vm(z, mu, k):
    return np.exp(k * (np.cos(z - mu) - 1.0)) / (TWO_PI * i0e(k))


def _kap(R):
    R = min(max(float(R), 1e-6), 0.999); return R * (2 - R * R) / (1 - R * R)


def plain_kcheck(theta, K, restarts=10, iters=400, seed=20261001):
    """the independent EM of the review check (k_check.py fit_nounif), kept as a sensitivity"""
    z = np.mod(2 * np.asarray(theta), TWO_PI); n = len(z); rng = np.random.default_rng(seed); best = None
    for _ in range(restarts):
        mu = rng.uniform(0, TWO_PI, K); kp = np.full(K, 2.0); w = np.full(K, 1 / K); llo = -np.inf
        for _ in range(iters):
            d = np.column_stack([w[j] * _vm(z, mu[j], kp[j]) for j in range(K)]); t = d.sum(1, keepdims=True) + 1e-300; r = d / t
            ll = float(np.log(t).sum()); w = r.mean(0)
            for j in range(K):
                c = float((r[:, j] * np.cos(z)).sum()); s = float((r[:, j] * np.sin(z)).sum())
                mu[j] = math.atan2(s, c) % TWO_PI; kp[j] = min(_kap(math.hypot(c, s) / max(r[:, j].sum(), 1e-12)), 200)
            if abs(ll - llo) < 1e-8: break
            llo = ll
        if best is None or ll > best[0]: best = (ll, mu.copy(), kp.copy(), w.copy())
    return dict(K=K, ll=best[0], bic=-2 * best[0] + (3 * K - 1) * math.log(n))


def main():
    lib = C.load_library(); rows = []; log = []
    say = lambda s: (print(s), log.append(s))
    say('kfit_unconstrained.py: BIC re-fit of the trace-direction model without the tightness rule (release code, read-only)')
    for s in C.SCHEMES:
        for fi in range(len(C.folds(s, lib))):
            sp = C.split(s, fi, lib)
            th = np.concatenate([C.common.geom(sp['panels'][k]['lines'])[2] for k in sp['fit'] if len(sp['panels'][k]['lines'])])
            n = len(th)
            # (a) plain mixture, release fit_set_rule
            A = [plain_release(th, K) for K in range(1, 7)]; a_best = min(A, key=lambda f: f['bic'])
            # check K = 2 against the stored baseline fit
            bf = json.load(open(REL / 'data' / 'baseline_fits' / ('%s_f%d.json' % (s, fi))))['orientation_fit']
            a2 = A[1]; same_bf = np.allclose(sorted(a2['cent']), sorted(bf['centres_deg']), atol=1e-6) and np.allclose(sorted(a2['kap']), sorted(bf['kappa2']), atol=1e-6)
            # sensitivity: k_check EM
            Kc = [plain_kcheck(th, K) for K in range(1, 7)]; k_best = min(Kc, key=lambda f: f['bic'])
            # (b) mixture + uniform, no tightness rule
            m0 = SB.fit(th, K_range=(1, 2, 3, 4, 5, 6), kappa_min=1e-3)
            # (c) constrained (paper): stored model, and a re-fit with K = 1..6
            mc = C.cluster_model(s, fi); m8 = SB.fit(th, K_range=(1, 2, 3, 4, 5, 6))
            assert mc['K'] == 4 and m8['K'] == 4 and abs(float(mc['bic']['4']) - m8['bic'][4]) < 1e-6 and mc['n'] == n, (s, fi)
            bic_c4 = float(mc['bic']['4'])
            r = dict(test={'S1': 'gap-filling', 'S2': 'new-bench', 'S3': 'new-stretch'}[s], scheme=s, fold=fi, n_traces=n,
                     plain_K_bic=a_best['K'], **{'plain_bic_K%d' % f['K']: round(f['bic'], 2) for f in A},
                     plain_K2_centres_deg='%.1f / %.1f' % tuple(a2['cent']), plain_K2_sd_deg='%.1f / %.1f' % tuple(sd_theta(k) for k in a2['kap']),
                     plain_K2_weights='%.2f / %.2f' % tuple(a2['w']), plain_K2_equals_stored_baseline_fit=bool(same_bf),
                     kcheck_K_bic=k_best['K'], kcheck_bic_K2=round(Kc[1]['bic'], 2),
                     unif_K_bic=m0['K'], unif_bic_K2=round(m0['bic'][2], 2), unif_bic_best=round(m0['bic'][m0['K']], 2), unif_w_bg=round(m0['w_bg'], 3),
                     unif_centres_deg=' / '.join('%.0f' % c for c in m0['centres_deg']),
                     constrained_K=mc['K'], constrained_bic_K4=round(bic_c4, 2),
                     plain_K2_below_constrained_K4=bool(a2['bic'] < bic_c4), unif_K2_below_constrained_K4=bool(m0['bic'][2] < bic_c4),
                     plain_best_below_constrained_K4=bool(a_best['bic'] < bic_c4),
                     delta_plain_K2_minus_constrained_K4=round(a2['bic'] - bic_c4, 1), delta_unif_K2_minus_constrained_K4=round(m0['bic'][2] - bic_c4, 1))
            rows.append(r)
            say('%s f%d n=%d | plain vM (release fit_set_rule) BIC picks K=%d; BIC K1..6 %s; K=2 centres %s deg, SD %s deg, weights %s; = stored baseline fit: %s'
                % (s, fi, n, a_best['K'], [round(f['bic']) for f in A], r['plain_K2_centres_deg'], r['plain_K2_sd_deg'], r['plain_K2_weights'], same_bf))
            say('     k_check EM picks K=%d | vM + uniform, no tightness rule: K=%d (centres %s, uniform weight %.2f), BIC K1..6 %s | constrained K=4 BIC %.0f'
                % (k_best['K'], m0['K'], r['unif_centres_deg'], m0['w_bg'], {k: round(v) for k, v in m0['bic'].items()}, bic_c4))
            say('     unconstrained K=2 BIC - constrained K=4 BIC: plain %+.1f, with uniform %+.1f' % (r['delta_plain_K2_minus_constrained_K4'], r['delta_unif_K2_minus_constrained_K4']))
    D = pd.DataFrame(rows); OUT.mkdir(exist_ok=True); D.to_csv(OUT / 'kfit_unconstrained.csv', index=False)
    say('')
    say('SUMMARY (15 folds)')
    say('  plain axial von Mises mixture (baselines\' own fit, release code) picks K=2 in %d of 15 folds (K picked: %s)' % ((D.plain_K_bic == 2).sum(), D.plain_K_bic.value_counts().sort_index().to_dict()))
    say('     folds not K=2: %s' % ['%s f%d -> K=%d' % (r.scheme, r.fold, r.plain_K_bic) for r in D.itertuples() if r.plain_K_bic != 2])
    say('  sensitivity, independent EM of k_check.py: K=2 in %d of 15 (K picked: %s)' % ((D.kcheck_K_bic == 2).sum(), D.kcheck_K_bic.value_counts().sort_index().to_dict()))
    say('  vM mixture + uniform without the tightness rule picks K=2 in %d of 15 folds (K picked: %s); uniform weight %.2f to %.2f'
        % ((D.unif_K_bic == 2).sum(), D.unif_K_bic.value_counts().sort_index().to_dict(), D.unif_w_bg.min(), D.unif_w_bg.max()))
    say('  K=2 fit = stored baseline fit (release data/baseline_fits) in %d of 15 folds' % D.plain_K2_equals_stored_baseline_fit.sum())
    say('  constrained model (kappa >= 8, uniform): K=4 in %d of 15 folds' % (D.constrained_K == 4).sum())
    say('  plain K=2 BIC lower than constrained K=4 BIC in %d of 15 folds (difference %.1f to %.1f)' % (D.plain_K2_below_constrained_K4.sum(), D.delta_plain_K2_minus_constrained_K4.min(), D.delta_plain_K2_minus_constrained_K4.max()))
    say('  vM + uniform K=2 (no tightness rule) BIC lower than constrained K=4 BIC in %d of 15 folds (difference %.1f to %.1f)' % (D.unif_K2_below_constrained_K4.sum(), D.delta_unif_K2_minus_constrained_K4.min(), D.delta_unif_K2_minus_constrained_K4.max()))
    say('  plain BIC-best fit lower than constrained K=4 BIC in %d of 15 folds' % D.plain_best_below_constrained_K4.sum())
    (OUT / 'kfit_unconstrained_log.txt').write_text('\n'.join(log) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
