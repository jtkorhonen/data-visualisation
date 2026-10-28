# Nature-oriented style for the Visualisation skill: ggplot2 implementation of the Nature spec
# (5-8 pt text, 0.5 pt axes, no grid, no frame), matching the Python nature.mplstyle.
#
# Based on the Nature Research Figure Guide conventions (reviewed 2026-10-01; see
# references/styles/nature.md for the source links). This is a practical starting point,
# not a declaration of current journal compliance. Verify the live guide before submission.
# Panel labels and final panel geometry are intentionally script/layout concerns.
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

half_line <- 3.5  # pt; spacing unit at 7 pt base text
line_width <- line_pt(1.0)  # plotted lines
thin_width <- line_pt(0.5)  # axis lines and ticks
outline_width <- line_pt(0.25)  # rectangle outlines (boxes, bars) and hatching

figure_elements <- theme(
  # Root elements, fully specified.
  line = element_line(
    colour = "black", linewidth = thin_width, linetype = 1, lineend = "butt",
    linejoin = "round", arrow = FALSE, arrow.fill = "black", inherit.blank = FALSE
  ),
  rect = element_rect(
    fill = "white", colour = "black", linewidth = outline_width, linetype = 1,
    linejoin = "round", inherit.blank = FALSE
  ),
  text = element_text(
    family = font_family, face = "plain", colour = "black", size = 7, lineheight = 0.9,
    hjust = 0.5, vjust = 0.5, angle = 0, margin = margin(), debug = FALSE, inherit.blank = FALSE
  ),
  title = element_text(family = font_family),
  # Markers 3 pt across with a 0.4 pt edge.
  point = element_point(colour = "black", shape = 19, fill = "white", size = 1.22, stroke = 0.4 / (ggplot2::.stroke / 2 * 72 / 96)),
  polygon = element_polygon(fill = "white", colour = "black", linewidth = outline_width, linetype = 1, linejoin = "round"),
  geom = element_geom(
    ink = "black", paper = "white", accent = "black",
    linewidth = line_width, borderwidth = outline_width, linetype = 1L, bordertype = 1L,
    family = font_family, fontsize = 7, pointsize = 1.22, pointshape = 19
  ),
  spacing = pt(half_line),
  margins = margin(3, 3, 3, 3, unit = "bigpts"),
  aspect.ratio = NULL,

  # Axes: 0.5 pt lines on the left and bottom only, outward ticks 2.5 pt (minor 1.5 pt).
  axis.line = element_line(colour = "black", linewidth = thin_width, linetype = "solid"),
  axis.text = element_text(size = 6, colour = "black"),
  axis.text.x = element_text(margin = margin(t = 3.5, unit = "bigpts"), vjust = 1),
  axis.text.x.top = element_text(margin = margin(b = 3.5, unit = "bigpts"), vjust = 0),
  axis.text.y = element_text(margin = margin(r = 3.5, unit = "bigpts"), hjust = 1),
  axis.text.y.right = element_text(margin = margin(l = 3.5, unit = "bigpts"), hjust = 0),
  axis.text.r = element_text(margin = margin(l = 3.5, r = 3.5, unit = "bigpts"), hjust = 0.5),
  axis.ticks = element_line(colour = "black", linewidth = thin_width),
  axis.ticks.length = pt(2.5),
  axis.minor.ticks.length = pt(1.5),
  axis.title = element_text(size = 7),
  axis.title.x = element_text(margin = margin(t = 3.5, unit = "bigpts"), vjust = 1),
  axis.title.x.top = element_text(margin = margin(b = 3.5, unit = "bigpts"), vjust = 0),
  # Customisation: horizontal y-axis title; scripts/figure_style.R moves it above the
  # top-left corner of the panel, and the bottom margin is the gap to the panel.
  axis.title.y = element_text(angle = 0, hjust = 0, vjust = 0, margin = margin(b = half_line, unit = "bigpts")),
  axis.title.y.right = element_text(angle = -90, margin = margin(l = half_line, unit = "bigpts"), vjust = 1),

  # Legend: 6 pt text, no frame.
  legend.background = element_blank(),
  legend.margin = margin(half_line, half_line, half_line, half_line, unit = "bigpts"),
  legend.spacing = pt(2 * half_line),
  legend.key = element_blank(),
  legend.key.size = unit(1.2, "lines"),
  legend.text = element_text(size = 6),
  legend.title = element_text(size = 6, hjust = 0),
  legend.ticks.length = pt(0.2 * half_line),
  legend.position = "right",
  legend.justification = "center",
  legend.box.margin = margin(0, 0, 0, 0, unit = "bigpts"),
  legend.box.background = element_blank(),
  legend.box.spacing = pt(2 * half_line),

  # Panel: no background, border or grid.
  panel.background = element_blank(),
  panel.border = element_blank(),
  panel.grid = element_blank(),
  panel.grid.minor = element_blank(),
  panel.spacing = pt(2 * half_line),
  panel.ontop = FALSE,

  # Facet strips: plain 7 pt text, no box.
  strip.background = element_blank(),
  strip.clip = "on",
  strip.text = element_text(size = 7, margin = margin(half_line, half_line, half_line, half_line, unit = "bigpts")),
  strip.text.y = element_text(angle = -90),
  strip.text.y.left = element_text(angle = 90),
  strip.placement = "inside",
  strip.switch.pad.grid = pt(half_line / 2),
  strip.switch.pad.wrap = pt(half_line / 2),

  # Whole figure: white, no frame; regular 7 pt title; 8 pt bold lowercase panel tags.
  plot.background = element_rect(fill = "white", colour = NA),
  plot.title = element_text(size = 7, hjust = 0, vjust = 1, margin = margin(b = 8, unit = "bigpts")),
  plot.title.position = "panel",
  plot.subtitle = element_text(size = 7, hjust = 0, vjust = 1, margin = margin(b = half_line, unit = "bigpts")),
  plot.caption = element_text(size = 6, hjust = 1, vjust = 1, margin = margin(t = half_line, unit = "bigpts")),
  plot.caption.position = "panel",
  plot.tag = element_text(size = 8, face = "bold", hjust = 0, vjust = 1),
  plot.tag.position = "topleft",
  plot.margin = margin(3, 3, 3, 3, unit = "bigpts"),

  # Series: black, told apart by line style; colour scales only when a documented
  # data encoding needs them (see the colour policy).
  palette.linetype.discrete = c("solid", "dashed", "dotted", "dotdash"),
  palette.colour.discrete = "viridis",
  palette.fill.discrete = "viridis",
  palette.colour.continuous = "viridis",
  palette.fill.continuous = "viridis",
  complete = TRUE
)

figure_theme <- theme_void(base_size = 7, base_family = font_family) %+replace% figure_elements

# Points take their outline from the theme's borderwidth (0.25 pt here, for boxes and bars),
# but the spec gives markers a 0.4 pt edge; ggplot2 converts stroke by .stroke / 2 to points.
update_geom_defaults("point", aes(stroke = 0.4 / (ggplot2::.stroke / 2 * 72 / 96)))
