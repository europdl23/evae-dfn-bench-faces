# -*- coding: utf-8 -*-
"""Extra realisations for the checks (written to paper/networks/ only).

  random_context   the EVAE models of the release, but the posterior is drawn around 8 RANDOM training (fitting)
                   panels instead of the 8 neighbouring panels; context seed crc32('ctx|scheme|fold|panel|run seed');
                   generator seeds = the EVAE's own, so each realisation is paired with its EVAE realisation
  local_baselines  gap-filling test: ADFNE and KDE refitted on the 8 neighbouring panels of each held-out panel
                   (the 2-set orientation fit of the fold stays); generator seeds crc32('ADFNE|S1|localbase|...') and
                   'KDE|...'. The stored realisations (networks/local_baselines/) are checked: all KDE realisations are
                   regenerated and compared byte for byte, and, when ADFNE 1.5 is installed, the run seed 1337, draw 0
                   ADFNE realisations too (--all-adfne: every ADFNE realisation).
Usage: python make_realisations.py [random_context] [local_baselines]"""
import sys, json, shutil
import numpy as np
import pr_common as P
C = P.C

OUT = P.NET


def random_context():
    lib = C.load_library(); log = {}
    for s in C.SCHEMES:
        for fi in range(len(C.folds(s, lib))):
            sp = C.split(s, fi, lib); Pn = sp['panels']
            for sd in C.SEEDS:
                model, dev = C.generators.load_evae(str(P.RP.MODELS_DIR / ('%s_f%d_s%d' % (s, fi, sd)) / 'checkpoint.pt'))
                for b in sp['test']:
                    rng = np.random.default_rng(C.gen_seed('ctx', s, fi, b, sd))
                    ctx = [str(x) for x in rng.choice(sp['fit'], size=8, replace=False)]
                    log['%s|%d|%s|%d' % (s, fi, b, sd)] = ctx
                    post = C.aggregate_posterior(model, dev, Pn, ctx)
                    for d in range(C.NDRAW):
                        L = C.generate(model, dev, Pn[b]['y_max'], C.network_seed('EVAE', s, fi, b, sd, d), post, d)
                        C.save_net(C.net_path(s, 'EVAE', fi, b, sd, d, root=OUT / 'random_context'), L)
    json.dump(log, open(OUT / 'random_context' / 'context_panels.json', 'w'), indent=1)
    print('random context: %d panel x seed contexts, %d realisations' % (len(log), len(log) * C.NDRAW))


def local_baselines():
    import os
    lib = C.load_library(); adfne = (P.Path(os.environ['ADFNE_ROOT']) / 'ADFNE1.5').exists(); all_adfne = '--all-adfne' in sys.argv
    bad, n_kde, n_adf = [], 0, 0
    for fi in range(len(C.folds('S1', lib))):
        sp = C.split('S1', fi, lib); Pn = sp['panels']; rule = C.family_rule(sp)
        for b in sp['test']:
            stats = C.generators.fit_baseline_stats([Pn[k] for k in C.context(sp, b)], rule)
            for sd in C.SEEDS:
                for d in range(C.NDRAW):
                    L = C.generators.generate_kde(stats, Pn[b]['y_max'], C.gen_seed('KDE', 'S1', 'localbase', fi, b, sd, d)); n_kde += 1
                    ref = C.load_net(C.net_path('S1', 'KDE', fi, b, sd, d, root=OUT / 'local_baselines'))
                    if not np.array_equal(np.asarray(L, float).reshape(-1, 4), ref): bad.append(('KDE', b, sd, d))
            if not adfne: continue
            sel = [(sd, d) for sd in C.SEEDS for d in range(C.NDRAW)] if all_adfne else [(1337, 0)]
            res = C.adfne_batch(stats, Pn[b]['y_max'], [(C.gen_seed('ADFNE', 'S1', 'localbase', fi, b, sd, d), 's%d_d%02d' % (sd, d)) for sd, d in sel], 'local_%d_%s' % (fi, b))
            for sd, d in sel:
                n_adf += 1; ref = C.load_net(C.net_path('S1', 'ADFNE', fi, b, sd, d, root=OUT / 'local_baselines'))
                if not np.array_equal(np.asarray(res['s%d_d%02d' % (sd, d)], float).reshape(-1, 4), ref): bad.append(('ADFNE', b, sd, d))
    print('local baselines: regenerated %d KDE and %d ADFNE realisations%s; different: %d %s' % (n_kde, n_adf, '' if adfne else ' (ADFNE 1.5 not installed)', len(bad), bad[:5]))
    return not bad


if __name__ == '__main__':
    what = sys.argv[1:] or ['random_context', 'local_baselines']
    if 'random_context' in what: random_context()
    if 'local_baselines' in what: local_baselines()
