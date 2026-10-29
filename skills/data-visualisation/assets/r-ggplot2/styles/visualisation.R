# Default style for the Visualisation skill: ggplot2 implementation of the visualisation spec,
# which follows ggthemes::theme_clean() at base size 12 plus the skill's customisations.
#
# Sourced by scripts/figure_style.R, which uses the `figure_theme` object defined at the end.
# It starts from ggplot2::theme_void(), so anything not set here is not drawn, and then sets
# every element that ggplot2::theme_grey() sets, so no ggplot2 default reaches the figure.
# Leave nothing out of `figure_elements` when editing it.
# All sizes below are written in points (1/72 inch) as they appear in the exported figure.

library(ggplot2)

# ggplot2 line widths are in its own units; this converts a stroke width in points.
line_pt <- function(points) points / (ggplot2::.pt * 72 / 96)
pt <- function(points) unit(points, "bigpts")

# First available of Arial, Helvetica and DejaVu Sans, as in the spec.
font_family <- local({
  candidates <- c("Arial", "Helvetica", "DejaVu Sans")
  available <- candidates[candidates %in% systemfonts::system_fonts()$family]
  if (length(available) == 0) stop("none of the style's fonts is installed: ", toString(candidates))
  available[[1]]
})

half_line <- 6  # pt; spacing unit of theme_clean at base size 12
line_width <- line_pt(1.16)  # plotted lines, ticks, grid, rectangle outlines
axis_width <- line_pt(1.07)  # axis lines

figure_elements <- theme(
  # Root elements, fully specified.
  line = element_line(
    colour = "black", linewidth = line_width, linetype = 1, lineend = "butt",
    linejoin = "round", arrow = FALSE, arrow.fill = "black", inherit.blank = FALSE
  ),
  rect = element_rect(
    fill = "white", colour = "black", linewidth = line_width, linetype = 1,
    linejoin = "round", inherit.blank = FALSE
  ),
  text = element_text(
    family = font_family, face = "plain", colour = "black", size = 12, lineheight = 0.9,
    hjust = 0.5, vjust = 0.5, angle = 0, margin = margin(), debug = FALSE, inherit.blank = FALSE
  ),
  title = element_text(family = font_family),
  point = element_point(colour = "black", shape = 19, fill = "white", size = 1.5 * 12 / 11, stroke = line_width),
  polygon = element_polygon(fill = "white", colour = "black", linewidth = line_width, linetype = 1, linejoin = "round"),
  # In-figure text (geom_text, geom_label, annotate) at 9 pt, matching the tick labels.
  geom = element_geom(
    ink = "black", paper = "white", accent = "black",
    linewidth = line_width, borderwidth = line_width, linetype = 1L, bordertype = 1L,
    family = font_family, fontsize = 9, pointsize = 1.5 * 12 / 11, pointshape = 19
  ),
  spacing = pt(half_line),
  margins = margin(half_line, half_line, half_line, half_line, unit = "bigpts"),
  aspect.ratio = NULL,

  # Axes: lines on the left and bottom only, 3 pt outward ticks, no minor ticks.
  axis.line = element_line(colour = "black", linewidth = axis_width, linetype = "solid"),
  axis.text = element_text(size = 9, colour = "black"),
  axis.text.x = element_text(margin = margin(t = 0.8 * half_line / 2, unit = "bigpts"), vjust = 1),
  axis.text.x.top = element_text(margin = margin(b = 0.8 * half_line / 2, unit = "bigpts"), vjust = 0),
  axis.text.y = element_text(margin = margin(r = 0.8 * half_line / 2, unit = "bigpts"), hjust = 1),
  axis.text.y.right = element_text(margin = margin(l = 0.8 * half_line / 2, unit = "bigpts"), hjust = 0),
  axis.text.r = element_text(margin = margin(l = 0.8 * half_line / 2, r = 0.8 * half_line / 2, unit = "bigpts"), hjust = 0.5),
  axis.ticks = element_line(colour = "black"),
  axis.ticks.length = pt(3),
  axis.minor.ticks.length = pt(2),
  axis.title = element_text(size = 10),
  axis.title.x = element_text(margin = margin(t = half_line / 2, unit = "bigpts"), vjust = 1),
  axis.title.x.top = element_text(margin = margin(b = half_line / 2, unit = "bigpts"), vjust = 0),
  # Customisation: horizontal y-axis title; scripts/figure_style.R moves it above the
  # top-left corner of the panel, and the bottom margin is the gap to the panel.
  axis.title.y = element_text(angle = 0, hjust = 0, vjust = 0, margin = margin(b = half_line, unit = "bigpts")),
  axis.title.y.right = element_text(angle = -90, margin = margin(l = half_line / 2, unit = "bigpts"), vjust = 1),

  # Legend: on the right, in a square 1.16 pt black frame.
  legend.background = element_rect(colour = "black"),
  legend.margin = margin(half_line, half_line, half_line, half_line, unit = "bigpts"),
  legend.spacing = pt(2 * half_line),
  legend.key = element_rect(fill = "white", colour = NA),
  legend.key.size = unit(1.2, "lines"),
  legend.text = element_text(size = 11),
  legend.title = element_text(size = 12, face = "bold", hjust = 0),
  legend.ticks.length = pt(0.2 * half_line),
  legend.position = "right",
  legend.justification = "center",
  legend.box.margin = margin(0, 0, 0, 0, unit = "bigpts"),
  legend.box.background = element_blank(),
  legend.box.spacing = pt(2 * half_line),

  # Panel: no background or border; dotted grey horizontal major grid lines only.
  panel.background = element_blank(),
  panel.border = element_blank(),
  panel.grid = element_line(colour = "white"),
  panel.grid.major.x = element_blank(),
  panel.grid.major.y = element_line(colour = "#BEBEBE", linetype = "dotted"),
  panel.grid.minor = element_blank(),
  panel.spacing = pt(half_line),
  panel.ontop = FALSE,

  # Facet strips: plain text, no box.
  strip.background = element_rect(fill = "white", colour = NA),
  strip.clip = "on",
  strip.text = element_text(size = 9.6, margin = margin(0.8 * half_line, 0.8 * half_line, 0.8 * half_line, 0.8 * half_line, unit = "bigpts")),
  strip.text.x = element_text(vjust = 0.5),
  strip.text.y = element_text(angle = -90),
  strip.text.y.left = element_text(angle = 90),
  strip.placement = "inside",
  strip.switch.pad.grid = pt(half_line / 2),
  strip.switch.pad.wrap = pt(half_line / 2),

  # Whole figure: white, no frame; bold 14 pt title left-aligned with the panel.
  plot.background = element_rect(fill = "white", colour = NA),
  plot.title = element_text(size = 14, face = "bold", hjust = 0, vjust = 1, margin = margin(b = half_line, unit = "bigpts")),
  plot.title.position = "panel",
  plot.subtitle = element_text(size = 13, hjust = 0, vjust = 1, margin = margin(b = half_line, unit = "bigpts")),
  plot.caption = element_text(size = 9.6, hjust = 1, vjust = 1, margin = margin(t = half_line, unit = "bigpts")),
  plot.caption.position = "panel",
  plot.tag = element_text(size = 14.4, hjust = 0.5, vjust = 0.5),
  plot.tag.position = "topleft",
  plot.margin = margin(half_line, half_line, half_line, half_line, unit = "bigpts"),

  # Series: black, told apart by line style; colour scales only when a documented
  # data encoding needs them (see the colour policy).
  palette.linetype.discrete = c("solid", "dashed", "dotted", "dotdash"),
  palette.colour.discrete = "viridis",
  palette.fill.discrete = "viridis",
  palette.colour.continuous = "viridis",
  palette.fill.continuous = "viridis",
  complete = TRUE
)

figure_theme <- theme_void(base_size = 12, base_family = font_family) %+replace% figure_elements
