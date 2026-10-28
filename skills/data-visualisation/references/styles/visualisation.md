# Default style: visualisation

The default look for every chart, whatever the stack. It starts from
`ggthemes::theme_clean()` at base size 12 and adds the skill's customisations on top.
Each stack implements it in `assets/<stack>/styles/visualisation.*`; this file is the
source of truth, and an implementation that disagrees with it is the one to fix.

Values are what lands in the exported figure at final printed size, in points
(1 pt = 1/72 inch). ggplot2 sizes lines in its own units: multiply a `linewidth` by
`ggplot2::.pt` (2.845) and by 0.75 to get the stroke width in an SVG from svglite.

## Base: theme_clean

### Typography

| Element | Value |
| --- | --- |
| Font family | sans-serif: Arial, then Helvetica, then DejaVu Sans |
| Chart title | 14 pt, bold, left-aligned with the plot area |
| Axis titles | 10 pt, regular |
| Tick labels | 9 pt, black |
| Legend text | 11 pt |
| Legend title | 12 pt, bold |
| Annotations and other text | 12 pt |
| Maths and sub/superscripts | sans-serif, matching the text |

### Lines and marks

| Element | Value |
| --- | --- |
| Plotted lines, ticks, rectangle outlines (boxes, bars) | 1.16 pt, black |
| Axis lines | 1.07 pt, black, left and bottom only |
| Major ticks | 3 pt long, pointing out; no minor ticks |
| Grid | horizontal major lines only, grey `#BEBEBE`, 1.16 pt, dotted (1.55 pt on, 4.66 pt off) |
| Markers | filled circles, 4.26 pt across, 0.77 pt edge |
| Box plots | whiskers without end caps |

### Frame and layout

- A 1.16 pt black frame around the whole figure, on a white background.
- 6 pt margin inside the frame.
- No border around the plot area.
- A legend, when used, has a square 1.16 pt black frame and a white background.

## Customisations on top of theme_clean

- **Series:** black, told apart by line style in this order: solid, dashed, dotted,
  dash-dot. Color is added only as allowed by the color policy in `SKILL.md`.
- **y-axis label:** horizontal, above the top-left corner of the axes.
- **Title:** above the y-axis label, padded so the two never overlap.

## Export

- Text stays text in SVG (and PDF), not outlines, so it remains editable.
- No creation dates or tool versions embedded in the files, so a rebuild is byte-identical
  where the stack allows it; any exception is stated in the stack reference.
- PNG resolution and figure size are not part of the style; they come from `config.yaml`.
