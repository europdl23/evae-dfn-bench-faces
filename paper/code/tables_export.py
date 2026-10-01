# -*- coding: utf-8 -*-
"""Excel files for the paper (paper/tables/): Table_R1.xlsx and checks.xlsx, from the CSVs of checks.py.
Undefined values are written as n.d. Same bytes on every run."""
import pandas as pd
import pr_common as P
import export_excel as EX
from xl import book, sheet
from discussion import score_name, GROUP_PAPER

T = P.TAB
REN = {'Reference': 'natural-variability reference', 'Random context': 'random context'}
rd = lambda f: pd.read_csv(T / f, na_values=['n.d.'], keep_default_na=True)


def df_sheet(wb, title, D, widths=None):
    D = D.astype(object).where(D.notna(), 'n.d.')
    return sheet(wb, title, list(D.columns), D.values.tolist(), None, widths)


def paper_names(D):
    D = D.copy()
    if 'score' in D: D['score'] = D.score.map(score_name)
    if 'group' in D: D['group'] = D.group.map(lambda g: GROUP_PAPER.get(g, g))
    return D


if __name__ == '__main__':
    # ---- Table R1
    TBL = rd('Table_R1.csv'); wb = book(); fm = [f for _, _, f in EX.ROWS]
    cols = [('Held-out', 'held-out'), ('Reference', 'natural-variability reference'), ('EVAE', 'EVAE')]
    head = ['Parameter', 'Unit'] + ['%s test: %s' % (P.TEST[s], lab) for s in P.C.SCHEMES for _, lab in cols]
    rows = [[p, u] + [round(float(TBL.iloc[i]['%s %s' % (s, m)]), EX.DEC[f]) for s in P.C.SCHEMES for m, _ in cols] for i, (p, u, f) in enumerate(EX.ROWS)]
    sheet(wb, 'Table R1', head, rows, fm, [38, 18] + [14] * 9, 'C2')
    full = [[p, u] + [float(TBL.iloc[i]['%s %s' % (s, m)]) for s in P.C.SCHEMES for m, _ in cols] for i, (p, u, f) in enumerate(EX.ROWS)]
    sheet(wb, 'Full precision', head, full, None, [38, 18] + [14] * 9)
    sheet(wb, 'Notes', ['Notes'], [[n] for n in [
        'Held-out = the mapped held-out panels. EVAE = per panel the median over its 24 realisations (3 run seeds x 8 draws).',
        'Natural-variability reference = the 8 neighbouring panels of each held-out panel (the EVAE context panels, every held-out fracture removed), per panel the median over the 8. Because held-out fractures are removed, the reference carries fewer traces and intersections than intact neighbouring panels.',
        'Per test the median over its held-out panels; median length, 90th percentile length, cluster shares, directions and spreads are taken over all traces of the test (each realisation weighted 1/24, each neighbouring panel 1/8).',
        'Tests: gap-filling (20 held-out panels), new-bench (50), new-stretch (50). Cluster = trace-direction cluster (learned on the training panels of each fold).',
        'Made by paper/code/checks.py and tables_export.py.']], None, [170])
    wb.save(T / 'Table_R1.xlsx'); EX._freeze(T / 'Table_R1.xlsx')

    # ---- checks
    wb = book()
    CNT = rd('check_counts.csv').replace(REN)
    for second, title in (('natural-variability reference', 'Natural variability'), ('random context', 'Random context')):
        q = paper_names(CNT[CNT.second == second])
        sheet(wb, title + ' (counts)', ['Test', 'Score group', 'EVAE better', 'No difference', 'EVAE worse'], q[['test', 'group', 'better', 'no_difference', 'worse']].values.tolist(),
              None, [14, 30, 12, 14, 12])
    for f, title, lab in (('check_natural_variability.csv', 'Natural variability per score', 'reference'), ('check_random_context.csv', 'Random context per score', 'random context')):
        D = paper_names(rd(f))
        df_sheet(wb, title, D[['test', 'group', 'score', 'n_panels', 'median_first', 'median_second', 'median_diff', 'rank_sum_plus', 'rank_sum_minus', 'p', 'result']]
                 .rename(columns={'median_first': 'EVAE median error', 'median_second': lab + ' median error'}), [14, 28, 44] + [14] * 8)
    M = rd('check_memorisation.csv')
    M['measure'] = M.measure.replace({'near-copy share, vs source panel': 'Near-copy share: realisation vs its source neighbouring panel; held-out panel vs the same panel',
                                      'distance to closest trace of source panel (m)': 'Source-panel distance (m): mean distance from each trace to the closest trace of the source neighbouring panel',
                                      'near-copy share, nearest training panel': 'Near-copy share with the nearest training panel'})
    df_sheet(wb, 'Memorisation', M.rename(columns={'realisation_median': 'EVAE realisation (median over panels)', 'heldout_median': 'held-out panel (median over panels)',
                                                   'realisation_max': 'EVAE realisation (max)', 'heldout_max': 'held-out panel (max)', 'p_wilcoxon': 'p (paired Wilcoxon over panels)'}),
             [14, 60] + [16] * 6)
    df_sheet(wb, 'Panel-to-panel Spearman', rd('check_panel_spearman.csv').rename(columns={'rho Reference': 'rho natural-variability reference', 'rho Random context': 'rho random context'}),
             [14, 28, 12, 18, 16])
    df_sheet(wb, 'Per-seed verdict', rd('check_per_seed_verdict_summary.csv'), [12, 10, 10, 12])
    df_sheet(wb, 'Per-seed verdict per score', paper_names(rd('check_per_seed_verdict.csv')), [12, 28, 44, 14])
    df_sheet(wb, 'Benjamini-Hochberg', rd('check_benjamini_hochberg_summary.csv').rename(columns={'second': 'EVAE against'}), [14, 10, 14, 10])
    D = paper_names(rd('check_benjamini_hochberg.csv'))
    df_sheet(wb, 'BH per comparison', D[['test', 'group', 'score', 'second', 'n_panels', 'median_diff', 'p', 'q_bh', 'result_bh']].rename(columns={'second': 'EVAE against'}),
             [14, 28, 44, 12, 10, 12, 12, 12, 14])
    L = rd('check_local_baselines_counts.csv'); L['group'] = L.group.map(lambda g: GROUP_PAPER.get(g, g))
    df_sheet(wb, 'Local baselines (counts)', L.rename(columns={'against': 'EVAE against (gap-filling test, refitted on the 8 neighbouring panels)'}), [40, 30, 10, 14, 10])
    df_sheet(wb, 'Local baselines per score', paper_names(rd('check_local_baselines.csv')), [14, 28, 44, 20, 10, 12, 12, 14])
    df_sheet(wb, 'Bootstrap 95% CI', rd('check_bootstrap_ci_summary.csv').rename(columns={'against': 'EVAE against'}), [14, 12, 12, 12])
    df_sheet(wb, 'Bootstrap CI per comparison', paper_names(rd('check_bootstrap_ci.csv')), [14, 28, 44, 10, 12, 12, 12, 14])
    df_sheet(wb, 'Changes after n.d. rule', rd('changes_nd.csv'), [44, 60, 16, 16, 10])
    sheet(wb, 'Notes', ['Notes'], [[n] for n in [
        'All checks on the held-out panels of the three tests, with the 38 error scores (error against the held-out panel; smaller = closer; definitions in paper/SCORE_DEFINITIONS.md).',
        'n.d. = not defined: an empty realisation, or fewer than 2 members of a trace-direction cluster that the held-out panel has. Panel value = median over the realisations where the score is defined; n.d. panels are excluded from tests and intervals.',
        'Natural-variability reference: the 8 neighbouring panels scored against the held-out panel as if they were realisations (counts, length and crossings per unit area). EVAE vs reference: paired two-sided Wilcoxon over panels, alpha 0.05; better = EVAE error smaller.',
        'Random context: the same EVAE models with 8 random training panels as context instead of the neighbouring panels, same generator seeds. Two-sided Wilcoxon; direction from the signed-rank sums (better = neighbouring context has the smaller error).',
        'Memorisation: each realisation against its source neighbouring panel (the context panel of its draw), compared with the held-out panel against the same panel; near-copy = a trace with both end points within 0.5 m of a trace of the other panel. Source-panel distance = mean, over the traces of a panel, of the distance to the closest trace of the source panel (larger of the two end-point distances). p = paired two-sided Wilcoxon over held-out panels (realisation value = median of 24).',
        'Per-seed verdict: three-way verdict (EVAE, ADFNE, KDE) with panel values from one run seed (8 draws). Benjamini-Hochberg over all 228 EVAE-vs-baseline comparisons (38 scores x 3 tests x 2 baselines).',
        'Local baselines: gap-filling test, ADFNE and KDE refitted on the 8 neighbouring panels of each held-out panel; Holm over the 2 baselines.',
        'Bootstrap: 95% percentile interval of the median paired difference (EVAE minus baseline) over panels, 2,000 resamples, seed 20261001.',
        'Made by paper/code/checks.py, discussion.py and tables_export.py.']], None, [170])
    wb.save(T / 'checks.xlsx'); EX._freeze(T / 'checks.xlsx')
    print('written Table_R1.xlsx, checks.xlsx')
