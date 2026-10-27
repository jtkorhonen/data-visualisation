# Default style: visualisation

The default look for every chart, whatever the stack. Each stack implements it in
`assets/<stack>/styles/visualisation.*`; this table is the source of truth, and an
implementation that disagrees with it is the one to fix. Values are at final printed
size, in points (1 pt = 1/72 inch) unless stated.

## Typography

| Element | Value |
| --- | --- |
| Font family | sans-serif: Arial, then Helvetica, then DejaVu Sans |
| Weight | regular everywhere; bold or italic only for intentional semantic emphasis |
| Base text | 9 pt |
| Chart title | 12 pt, regular, left above the y-axis label |
| Axis labels | 10 pt |
| Tick labels | 9 pt |
| Legend text | 9 pt, no frame |
| Annotations | 9 pt |
| Figure title (rare) | 14 pt |
| Maths and sub/superscripts | sans-serif, matching the text |

## Lines and marks

| Element | Value |
| --- | --- |
| Plotted lines | 0.75 pt |
| Markers | 3 pt across, 0.5 pt edge |
| Patch edges (bars, boxes) and hatching | 0.25 pt |
| Axis lines (all four sides) | 0.5 pt, black |
| Major ticks | 3.5 pt long, 0.5 pt wide, pointing out |
| Minor ticks | 2 pt long, 0.5 pt wide, pointing out |
| Grid | none |

## Series encoding

Series are black and told apart by line style, in this order: solid, dashed, dotted,
dash-dot. Color is added only as allowed by the color policy in `SKILL.md`.

## Layout

- The y-axis label is horizontal and sits above the top-left corner of the axes.
- The title sits above the y-axis label, padded so the two never overlap.
- White figure and plot backgrounds.

## Export

- Text stays text in SVG (and PDF), not outlines, so it remains editable.
- No creation dates or tool versions embedded in the files, so a rebuild is byte-identical
  where the stack allows it; any exception is stated in the stack reference.
- PNG resolution and figure size are not part of the style; they come from `config.yaml`.
