#!/usr/bin/env sh
# Release check first (checksums are of the files as released), then figures, tables and statistical tests
# recomputed from the stored networks and compared with tables/reference/.
set -e
cd "$(dirname "$0")/.."
python scripts/verify_release.py
python scripts/make_figures.py --check
python scripts/statistical_tests.py --check
python scripts/export_excel.py
python scripts/ablation_table.py --check
