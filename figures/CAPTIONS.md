# Figure captions

The comparison tables are not drawn as figures: every number is in `tables/final_tables.xlsx`. The ablation table is drawn as `Table_ablation` (numbers in `tables/ablation_tables.xlsx`).

All figures are drawn at print size, 16 cm wide. Text is Times New Roman throughout:
* 12 pt for titles, axis labels and row labels;
* 10 pt for tick labels, values, counts and legends;
* 8 pt for the one-line notes at the bottom.

`scripts/make_figures.py` checks every figure before saving it (`src/study/figstyle.py`). It fails a figure if:
* any text is in another font or size;
* two texts overlap;
* a text leaves the figure or covers another panel;
* a text or legend touches the plotted data.

**Figure 1.** Held-out test boxes and generated networks. One test box per held-out scheme (rows): S1 fill a gap,
S2 new bench level, S3 new part of the wall. Columns: the mapped traces of the box (held-out), then EVAE, ADFNE and KDE,
with the number of traces in each box. For every method the network shown is run seed 1337, draw 0. It is the first
network, not selected. Generator seeds are in `seeds/figure_networks.json`.

**Figure 2.** Trace orientation over 0-360°, all held-out test boxes. Each trace is counted at theta and theta + 180°.
0° is along the bench; angles run clockwise as seen on the face. The black outline on the EVAE, ADFNE and KDE roses is
the held-out rose.

**Figure 3.** Trace length, all held-out test boxes. The black outline is the held-out histogram. The dashed line is the
median. Each generated network is weighted 1/24, so every box counts the same.

**Figure 4.** Per test box, 120 held-out box cases. Box value = median over the 24 networks of a method. The dashed line
is the held-out median. Under each box: the median over boxes and its difference from held-out.

**Table (ablation).** Held-out and the four ablation arms (single or dual latent, without or with the geology guide) in
each held-out scheme. The dual latent with the guide is the EVAE (green). Bold = closest to held-out in that scheme.
All columns use the same seeds.
