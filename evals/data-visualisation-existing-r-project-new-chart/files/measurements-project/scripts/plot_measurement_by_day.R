# Line chart of the measured value per day for each group.
# Groups are told apart by line style and direct labels; missing days stay as gaps.

script_dir <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)))
source(file.path(script_dir, "figure_style.R"))
source(file.path(script_dir, "summarise.R"))

args <- figure_arguments()
use_style(args$style)
data <- load_measurements(args$data) |> arrange(group, day)
last_observed <- data |> filter(!is.na(value)) |> group_by(group) |> slice_max(day, n = 1)

plot <- ggplot(data, aes(day, value, linetype = group)) +
  geom_line() +
  geom_point(na.rm = TRUE) +
  geom_text(
    data = last_observed, aes(label = group), hjust = 0, nudge_x = 0.15
  ) +
  scale_x_continuous(expand = expansion(mult = c(0.05, 0.15))) +
  labs(title = "Measurement by day", x = "day", y = "value (a.u.)") +
  theme(legend.position = "none")

save_figure(plot, args$png, args$svg, args$dpi, args$`width-mm`, args$`height-mm`)
