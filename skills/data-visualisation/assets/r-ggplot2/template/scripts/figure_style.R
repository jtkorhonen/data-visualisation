# Shared figure helpers: command-line arguments, style loading, horizontal y-axis titles and export.
# Every style value comes from the project's style file in styles/, never from this file.

library(ggplot2)

MM_PER_INCH <- 25.4
FIGURE_ARGUMENTS <- c("data", "style", "png", "svg", "dpi", "width-mm", "height-mm")

# Command-line arguments shared by all plotting scripts, as `--name value` pairs; the
# Snakefile fills them in. Returns a named list; dpi and sizes are numeric.
figure_arguments <- function(args = commandArgs(trailingOnly = TRUE)) {
  if (length(args) %% 2 != 0 || !all(startsWith(args[c(TRUE, FALSE)], "--"))) {
    stop("expected --name value pairs, got: ", paste(args, collapse = " "))
  }
  values <- as.list(args[c(FALSE, TRUE)])
  names(values) <- sub("^--", "", args[c(TRUE, FALSE)])
  missing <- setdiff(FIGURE_ARGUMENTS, names(values))
  if (length(missing) > 0) stop("missing arguments: ", paste0("--", missing, collapse = ", "))
  for (name in c("dpi", "width-mm", "height-mm")) values[[name]] <- as.numeric(values[[name]])
  values
}

# Loads the project style file and makes its theme the default for every plot in this script.
# The style file is sourced into its own environment and must define `figure_theme`.
use_style <- function(style_path) {
  style <- new.env()
  sys.source(style_path, envir = style)
  if (!exists("figure_theme", envir = style, inherits = FALSE)) {
    stop(style_path, " does not define figure_theme")
  }
  theme_set(style$figure_theme)
  invisible(style$figure_theme)
}

# Moves the left y-axis title from its column into a new row above the panels and strips,
# so it reads horizontally above the top-left corner of the plot. The title is drawn from
# the theme's axis.title.y.left element: font, size, colour, angle, alignment and the
# bottom margin (the gap to the panel) all come from the style. Returns a gtable.
horizontal_ylab <- function(plot) {
  layout <- ggplotGrob(plot)
  index <- which(layout$layout$name == "ylab-l")
  label <- get_labs(plot)$y
  if (length(index) == 0 || is.null(label) || inherits(layout$grobs[[index]], "zeroGrob")) {
    return(layout)
  }
  element <- calc_element("axis.title.y.left", complete_theme(plot$theme))
  title <- element_grob(element, label = label, margin_x = FALSE, margin_y = TRUE)
  column <- layout$layout$l[index]
  layout <- gtable::gtable_filter(layout, "^ylab-l$", invert = TRUE)
  layout$widths[column] <- unit(0, "pt")
  above <- layout$layout[grepl("^(panel|strip-t)", layout$layout$name), ]
  top <- min(above$t)
  layout <- gtable::gtable_add_rows(layout, grid::grobHeight(title), pos = top - 1)
  gtable::gtable_add_grob(
    layout, title, t = top, l = column, r = max(above$r), clip = "off", name = "ylab-l"
  )
}

# Writes the plot as PNG (ragg) and SVG (svglite) at an exact physical size. Neither device
# embeds a date, so identical inputs give identical files.
# The layout is built after each device opens, so text is measured with the fonts that
# device draws; building it earlier would open R's default PDF device and leave Rplots.pdf.
save_figure <- function(plot, png, svg, dpi, width_mm, height_mm) {
  dir.create(dirname(png), recursive = TRUE, showWarnings = FALSE)
  dir.create(dirname(svg), recursive = TRUE, showWarnings = FALSE)
  width <- width_mm / MM_PER_INCH
  height <- height_mm / MM_PER_INCH
  ragg::agg_png(png, width = width, height = height, units = "in", res = dpi)
  grid::grid.draw(horizontal_ylab(plot))
  invisible(grDevices::dev.off())
  svglite::svglite(svg, width = width, height = height)
  grid::grid.draw(horizontal_ylab(plot))
  invisible(grDevices::dev.off())
}
