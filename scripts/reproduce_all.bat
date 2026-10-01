@echo off
REM Release check first (checksums are of the files as released), then figures, tables and statistical tests
REM recomputed from the stored networks and compared with tables/reference/, the Excel file, and the ablation table.
cd /d "%~dp0.."
python scripts\verify_release.py || exit /b 1
python scripts\make_figures.py --check || exit /b 1
python scripts\statistical_tests.py --check || exit /b 1
python scripts\export_excel.py || exit /b 1
python scripts\ablation_table.py --check || exit /b 1
