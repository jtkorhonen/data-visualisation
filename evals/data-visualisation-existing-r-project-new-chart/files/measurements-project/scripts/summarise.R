# Validates the measurement table and writes per-group summary statistics.
# Missing values are counted, not filled, so the summary shows how many observations are absent.

suppressPackageStartupMessages(library(dplyr))
library(readr)

EXPECTED_COLUMNS <- cols(day = col_integer(), group = col_character(), value = col_double())

# Loads the measurement table and fails early if its columns, types or keys are unexpected.
load_measurements <- function(path) {
  data <- read_csv(path, col_types = EXPECTED_COLUMNS, na = "", progress = FALSE)
  problems <- problems(data)
  if (nrow(problems) > 0) stop("unexpected values in ", path, ":\n", format_csv(problems))
  if (!identical(names(data), names(EXPECTED_COLUMNS$cols))) {
    stop("unexpected columns in ", path, ": ", toString(names(data)))
  }
  duplicates <- data |> count(day, group) |> filter(n > 1)
  if (nrow(duplicates) > 0) stop("duplicate day/group rows in ", path, ":\n", format_csv(duplicates))
  data
}

main <- function(args = commandArgs(trailingOnly = TRUE)) {
  values <- setNames(as.list(args[c(FALSE, TRUE)]), sub("^--", "", args[c(TRUE, FALSE)]))
  summary <- load_measurements(values$data) |>
    group_by(group) |>
    summarise(
      rows = n(),
      missing = sum(is.na(value)),
      mean = mean(value, na.rm = TRUE),
      sd = sd(value, na.rm = TRUE)
    ) |>
    arrange(group)
  dir.create(dirname(values$output), recursive = TRUE, showWarnings = FALSE)
  write_csv(summary, values$output)
}

# Run only when called as a script, not when sourced by the plotting scripts.
if (sys.nframe() == 0) main()
