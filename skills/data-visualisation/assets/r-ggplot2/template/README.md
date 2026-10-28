# <Project title>

<One or two sentences: what question these figures answer and for whom.>

## Inputs

| File | Contents | Units / codes |
| --- | --- | --- |
| `inputs/measurements.csv` | one row per day and group: `day`, `group`, `value` | `value` in a.u.; empty cell = not measured |

Files in `inputs/` are never modified by the workflow.

## Requirements

- R 4.5 or newer (renv installs itself into the project on first start)
- Python 3.14 or newer with [uv](https://docs.astral.sh/uv/) (recommended) for Snakemake,
  or the standard-library `venv` module as a fallback

## Reproduce the outputs

Install the exact R package versions recorded in `renv.lock`, and Snakemake from `uv.lock`:

```bash
Rscript -e "renv::restore(prompt = FALSE)"
uv sync
uv run snakemake --cores 1
```

Without uv (uses `requirements.txt`, exported from `uv.lock`):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/snakemake --cores 1
```

On Windows, use `.venv\Scripts\python` and `.venv\Scripts\snakemake`.

PNG files are written at 450 dpi. For 600 dpi, run:

```bash
uv run snakemake --cores 1 --config png_dpi=600
```

## Outputs

| File | Contents |
| --- | --- |
| `outputs/data/summary.csv` | rows, missing values, mean and SD of `value` per group |
| `outputs/figures/measurement_by_day.{png,svg}` | value per day, one line style per group; missing days are gaps |
| `outputs/figures/measurement_distribution.{png,svg}` | box plot per group (median, IQR, whiskers at 1.5 × IQR); missing values excluded |

All figures are 120 × 80 mm. Settings for the build live in `config.yaml`.

## Style

The style is fully defined inside this project, so a package upgrade cannot change it.
`styles/visualisation.R` is a complete ggplot2 theme built on `theme_void()` that sets
every element itself: fonts and text sizes, line and tick widths, grid, frame, legend, the
black line-type order, and the colour scales. `scripts/figure_style.R` places the y-axis
title horizontally above the plot, using the theme's `axis.title.y` settings. Figure
size and PNG resolution come from `config.yaml`. Changing any of these files rebuilds
the figures.

Color: <none — figures are black, groups are distinguished by line style and direct labels.
If color is used, state what it encodes, why a non-color encoding was not enough, and the palette.>

## Rerunning

Snakemake rebuilds only what changed: editing an input, a script, the style, `config.yaml`
or `renv.lock` reruns the affected rules. To rebuild everything anyway:

```bash
uv run snakemake --cores 1 --forceall
```

After an interrupted run, add `--rerun-incomplete`. To preview what would run, add `--dry-run`.

## Updating dependencies

R packages are listed in `DESCRIPTION`. After changing it, or to move to newer versions:

```bash
Rscript -e "renv::update(prompt = FALSE)" -e "renv::snapshot(prompt = FALSE)"
```

Snakemake:

```bash
uv lock --upgrade
uv export --format requirements.txt --no-emit-project --output-file requirements.txt
```
