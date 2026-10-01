@echo off
REM Run an ADFNE script under GNU Octave.   Usage:  run_adfne.bat verify_adfne.m
REM Set OCTAVE_CLI to your octave-cli executable, or put octave-cli on PATH.
setlocal
if "%OCTAVE_CLI%"=="" set "OCTAVE_CLI=octave-cli"
set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"
cd /d "%HERE%"
"%OCTAVE_CLI%" --no-gui --quiet %*
endlocal
