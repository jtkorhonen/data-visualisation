# Nature-style figures

Read this only when the requested destination is Nature or a Nature-style manuscript.
Everything here overrides the general defaults in `SKILL.md`; the rest of the project
contract (layout, uv, Snakemake, README, checks) still applies.

## Style preset

Copy [`assets/nature.mplstyle`](../assets/nature.mplstyle) to `styles/nature.mplstyle`
and set `style: styles/nature.mplstyle` in `config.yaml`. It is a starting preset, not a
compliance certificate.

- Ordinary text 5–7 pt; panel labels 8 pt, lowercase, bold, upright.
- Lines 0.25–1.5 pt as in the general defaults; axes and ticks 0.5 pt.
- Editable vector text: `pdf.fonttype` and `ps.fonttype` 42, `svg.fonttype` none.
- PNG at the default 450 dpi, or 600 dpi (`--config png_dpi=600`) where the guide asks
  for more for image-containing artwork.

## Physical size

Set `figure_width_mm` and `figure_height_mm` in `config.yaml` explicitly:

- 89 mm for single-column;
- 120–136 mm for an intermediate figure;
- 183 mm for full-width artwork;
- height at or below 247 mm.

Run the checker with the chosen size, for example `--size-mm 89x60`.

Nature's accepted final format and color-mode rules vary by artwork type and submission
phase. Record the chosen width, height, export format, DPI, and any deviations in the
project README.

## Multi-panel figures (only when explicitly requested)

Build a multi-panel figure only when the user asks for one. Then follow the
[panel-building and export guide](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/):

- Build the complete figure at its final physical size, with consistent panel widths,
  gutters, fonts, axis treatment, and line weights. Do not assemble panels from
  screenshots or rasterized previews.
- Use lowercase, bold, upright panel labels (`a`, `b`, `c`, …), normally 8 pt at final
  size, in a consistent upper-left position. Keep labels and other text clear of data and
  do not rely on a figure title to identify panels.
- Keep line art, text, labels, and panel geometry editable. Embed image panels at their
  required effective resolution and never upsample them to create apparent detail.
  Preserve the editable source alongside the exported deliverable.
- Export one combined file for one multi-panel figure. Use PDF/EPS or another
  journal-accepted vector format for line-art or combination figures; use the required
  high-resolution raster format for photographs or raster panels. Keep the project's
  PNG/SVG exports as reproducible previews, declare the production export as a Snakemake
  output too, and record it separately in the README.
- Inspect the combined export at final size for clipping, unintended whitespace,
  inconsistent baselines, missing fonts, transparency changes, and panel-label
  collisions. Do not use `bbox_inches="tight"`; it changes the declared final dimensions.

## Sources to re-check before submission

The guide's production requirements can change by journal, article type, and submission
stage. Treat this as a documented starting workflow and verify the live Nature
instructions immediately before submission:

- [Nature's figure specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)
- [Building and exporting figure panels](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)
