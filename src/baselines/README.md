# Baselines: ADFNE 1.5 and KDE

**You do not need either of them to reproduce the figures, tables and tests.** All ADFNE and KDE networks are stored in
`networks/`. This page is for regenerating them.

## How both are fitted

Both are fitted on the fitting boxes of each fold only, never on a test box, with the standard fitted distributions
(`src/evaluation/generators.py`, `fit_baseline_stats`). The parameters are written out in `data/baseline_fits/`:

* **Orientation.** The 2-set axial von Mises fit (EM, seed 20260907). Each fitting trace goes to its most likely set.
* **Per set:**
  * centre and directional concentration;
  * a truncated-exponential length fit (low, mean, high);
  * the mean trace count per fitting box.
* **Count.** The trace count in a test box is the set's mean count, scaled from the mean fitting-box height to the
  test-box height (`quota`).
* **ADFNE.** Draws direction, length and a uniform position per set. Traces are over-requested, filtered to centres
  inside the box, then subsampled to the count.
* **KDE.** Draws positions from a kernel density of the set's fitting trace centres, and resamples lengths and
  directions from the set's fitting traces.
* **Clipping.** Both are clipped to the box with the same routine as the EVAE.
* **No learned clusters.** The baselines are not given the learned orientation clusters.

## Seeds

* Every network has its own generator seed: `crc32("ADFNE|scheme|main|fold|box|run seed|draw")`, or `KDE|...` for KDE.
* The run seeds (1337, 20260903, 7) and draws (0-7) are the same as for the EVAE.
* For ADFNE, Octave is seeded with `rng(seed mod 2^31)` before each network, so networks written in one Octave session are
  the same as networks written one at a time.

## KDE

Needs nothing beyond `requirements.txt`:

```bash
python scripts/generate_networks.py baselines S1 2 --no-adfne
```

## ADFNE 1.5

ADFNE 1.5 is third-party software by Younes Fadakar Alghalandis, distributed under its own licence. **It is not
redistributed here.** To install it:

1. **Octave.** Install GNU Octave (the released networks used 11.3.0) with the `statistics` package:
   `pkg install -forge statistics`.
2. **ADFNE.** Download ADFNE 1.5 from its own distribution and unpack it to `src/baselines/adfne_octave/ADFNE1.5/`.
   Alternatively, set `ADFNE_ROOT` to a folder holding `adfne_init.m`, the launchers and `ADFNE1.5/`.
3. **Launcher.** Set `OCTAVE_CLI` to your `octave-cli` executable, or put it on `PATH`.
4. **Check.** `cd src/baselines/adfne_octave` and run `./run_adfne.sh verify_adfne.m` (or `run_adfne.bat` on Windows).

Then:

```bash
python scripts/generate_networks.py baselines S1 2
```

| File | Purpose |
|---|---|
| `adfne_octave/adfne_init.m` | loads `statistics`, puts the shim ahead of ADFNE on the path, runs ADFNE's `Globals` |
| `adfne_octave/octave_compat/setstructfields.m` | the one function ADFNE needs that Octave lacks; a shim, ADFNE itself is used unmodified |
| `adfne_octave/run_adfne.bat`, `run_adfne.sh` | launchers; both read `OCTAVE_CLI` |
| `adfne_octave/verify_adfne.m` | checks that ADFNE loads and generates under Octave |
