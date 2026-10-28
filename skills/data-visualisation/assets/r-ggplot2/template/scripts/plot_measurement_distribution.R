# Box plot of the measured value for each group.
# The median is drawn at the box outline's width so no line exceeds the style's widths.

script_dir <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)))
source(file.path(script_dir, "figure_style.R"))
source(file.path(script_dir, "summarise.R"))

args <- figure_arguments()
style <- use_style(args$style)
observed <- load_measurements(args$data) |> filter(!is.na(value)) |> arrange(group)
outline <- calc_element("geom", style)@borderwidth

plot <- ggplot(observed, aes(group, value)) +
  geom_boxplot(width = 0.5, colour = "black", fill = "white", median.linewidth = outline) +
  labs(title = "Measurement distribution", x = "group", y = "value (a.u.)")

save_figure(plot, args$png, args$svg, args$dpi, args$`width-mm`, args$`height-mm`)
