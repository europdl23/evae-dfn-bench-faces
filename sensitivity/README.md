# Sensitivity tests (Supplementary Text S3, Table S1)

Three tests of the settings of the EVAE, each in the gap-filling test (S1, 4 folds x 3 run seeds), scored with the
same 38 error scores, n.d. rule and paired tests as the main comparison.

| Folder | Setting tested | Models |
|---|---|---|
| `nmax/` | slot limit Nmax = 50 and 200 (released models: 120) | retrained, 12 per setting (not released) |
| `weight/` | each loss-weight group halved and doubled | retrained, 12 per setting (not released) |
| `threshold/` | existence threshold 0.4 and 0.6 (released: 0.5) | the released models of the hold-out test |

Each folder holds `PROTOCOL.md` (fixed before the runs), `REPORT.md` (results), the result tables (`Table_*.csv`,
`Table_*.md`, `Table_*_tests.csv`), the scripts, `outputs/` (scores per realisation and window, test results) and
`networks/` (every generated realisation). `code_changes/` holds only the files of this repository that the test changed
(for example the slot limit or the loss weights read from the command line); to rerun a test, copy the repository into
`<test>/code/` and copy `code_changes/` over it.

The retrained model checkpoints are not in the repository (about 590 MB). The realisations generated from them are, so
every score and table can be recomputed without them.
