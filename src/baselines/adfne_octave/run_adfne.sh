#!/bin/bash
# Run an ADFNE script under GNU Octave.   Usage:  ./run_adfne.sh verify_adfne.m
# Set OCTAVE_CLI to your octave-cli executable, or put octave-cli on PATH.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
"${OCTAVE_CLI:-octave-cli}" --no-gui --quiet "$@"
