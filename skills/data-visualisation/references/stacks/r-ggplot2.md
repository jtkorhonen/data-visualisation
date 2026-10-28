# Stack: R + ggplot2

Read this when the project uses R: readr, dplyr and tidyr for data (purrr only when
needed), ggplot2 for figures, renv for the R packages. It adds the R specifics to the
shared contract in `SKILL.md`; everything there still applies.

## Assets

| Asset | Copy to |
| --- | --- |
| [`assets/r-ggplot2/template/`](../../assets/r-ggplot2/template/) | the project folder, including the hidden `.Rprofile` and `renv/` |
| [`assets/r-ggplot2/styles/visualisation.R`](../../assets/r-ggplot2/styles/visualisation.R) | `styles/` (default style) |
| [`assets/r-ggplot2/styles/nature.R`](../../assets/r-ggplot2/styles/nature.R) | `styles/` (Nature style, instead of the default) |

Each style file implements one spec in [`../styles/`](../styles/) as a complete ggplot2
theme. It starts from `theme_void()`, so nothing is drawn unless the style says so, and
then sets every element that `theme_grey()` sets, so no ggplot2 default reaches the
figure. Never shorten a style to only the changed elements. It defines `figure_theme`;
select it with `style: styles/<name>.R` in `config.yaml`.

## Project files

On top of the shared layout:

```text
project/
├── scripts/
│   └── figure_style.R     # arguments, style loading, horizontal y title, export
├── styles/
│   └── visualisation.R    # complete ggplot2 theme
├── DESCRIPTION            # direct R dependencies (Type: project)
├── renv.lock              # exact R package versions and the R version
├── .Rprofile              # activates renv when R starts in the project
└── renv/                  # activate.R and settings.json are committed; library/ is not
```

`pyproject.toml`, `uv.lock` and `requirements.txt` hold only Snakemake.

## Environment

renv locks the R packages the way uv locks Python ones. `.Rprofile` sources
`renv/activate.R`, which installs renv itself into the project on first start, so R is
the only prerequisite. `renv/settings.json` uses `"snapshot.type": "explicit"`, so
`DESCRIPTION` is the list of direct dependencies, like `pyproject.toml`.

New project, from the template:

```bash
Rscript -e "renv::install(prompt = FALSE)" -e "renv::snapshot(prompt = FALSE)"
uv sync
uv export --format requirements.txt --no-emit-project --output-file requirements.txt
```

Existing project with a `renv.lock`: `Rscript -e "renv::restore(prompt = FALSE)"`, then
`uv sync`. Add a package by listing it under `Imports:` in `DESCRIPTION`, then run
`renv::install()` and `renv::snapshot()`. Commit `DESCRIPTION`, `renv.lock`, `.Rprofile`
and `renv/activate.R` and `renv/settings.json`; never commit `renv/library/`.

The Snakefile runs scripts with `Rscript --no-site-file --no-environ`: the project's
`.Rprofile` activates renv and replaces any user `~/.Rprofile`, while site-wide profiles
and environment files are skipped, so only files inside the project affect the output.
The first `renv::install()` downloads every package; renv's global cache makes later
projects fast. If R is missing, report the prerequisite instead of switching stacks.

## Data

Load source files with readr, giving `col_types` explicitly so types never depend on
guessing, and check `problems()` before use. Transform with dplyr and tidyr; use purrr
only when a task needs it. Do not load plyr: it is retired and masks dplyr functions.

## Figure construction

Use the helpers in the template's `scripts/figure_style.R`:

```r
script_dir <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)))
source(file.path(script_dir, "figure_style.R"))

args <- figure_arguments()
use_style(args$style)                     # project theme becomes the default
plot <- ggplot(data, aes(day, value, linetype = group)) +
  geom_line() +
  labs(title = "Chart title", x = "day", y = "quantity (unit)")
save_figure(plot, args$png, args$svg, args$dpi, args$`width-mm`, args$`height-mm`)
```

What the helpers do, if you need to write equivalent code:

- `use_style()` sources the style file into its own environment and calls `theme_set()`
  with its `figure_theme`. Do not add `theme_*()` calls or global `theme()` settings in
  scripts; plot-specific tweaks such as `theme(legend.position = "none")` are fine.
- `horizontal_ylab()` moves the y-axis title into a new row above the panels (and facet
  strips), left-aligned with the tick labels. Font, size, alignment and the gap to the
  panel come from the theme's `axis.title.y`. It returns a gtable, so it runs last,
  inside `save_figure()`: never add layers to its result. Use `labs(y = ...)` as usual;
  do not put the y title in `subtitle` or `tag` (the tag is for panel labels).
- `save_figure()` writes PNG with ragg and SVG with svglite at the exact physical size.
  It builds the layout after opening each device: building it earlier opens R's default
  PDF device, which measures text with the wrong fonts, warns, and leaves `Rplots.pdf`.
  Do not call `ggsave()` or `ggplotGrob()` before a device is open.
- Neither device embeds a date, so a forced rebuild is byte-identical.

Point markers take their outline width from the theme's `borderwidth`; a style that needs
a different marker edge sets it with `update_geom_defaults("point", ...)` in the style
file. Box plots draw the median at twice the box line width by default; pass
`median.linewidth` equal to the theme's `borderwidth` so no line exceeds the style.

## Color

The styles set `palette.*` theme elements: the black line-type order for discrete
series and viridis for any colour or fill scale. A mapped colour still needs the
justification the color policy asks for; set a palette explicitly when viridis does
not fit the data.

## Snakefile

Follow the template's Snakefile:

```python
RSCRIPT = "Rscript --no-site-file --no-environ"

rule plot_measurement_by_day:
    input:
        data="inputs/measurements.csv",
        script="scripts/plot_measurement_by_day.R",
        helpers="scripts/figure_style.R",
        style=config["style"],
        lock="renv.lock",
    output:
        png="outputs/figures/measurement_by_day.png",
        svg="outputs/figures/measurement_by_day.svg",
    params:
        dpi=config["png_dpi"],
        width_mm=config["figure_width_mm"],
        height_mm=config["figure_height_mm"],
    shell:
        RSCRIPT + " {input.script:q} --data {input.data:q} --style {input.style:q} "
        "--png {output.png:q} --svg {output.svg:q} --dpi {params.dpi} "
        "--width-mm {params.width_mm} --height-mm {params.height_mm}"
```

Declare `renv.lock` as an input of every R rule, so a package update reruns them.

## README specifics

- Requirements: R 4.5+ (renv installs itself), and Python 3.14+ with uv for Snakemake,
  with `venv` as the fallback.
- Setup: `renv::restore()` and `uv sync`, plus the `requirements.txt` fallback.
- Style: `styles/<name>.R` fully defines the theme; the y title placement uses its
  `axis.title.y` settings.
- Updating dependencies: edit `DESCRIPTION`, run `renv::update()` and `renv::snapshot()`;
  `uv lock --upgrade` and re-export `requirements.txt` for Snakemake.

## Checks

For a project with R scripts, the checker also requires `DESCRIPTION`, `renv.lock`,
`.Rprofile` and `renv/activate.R`, fails on any use of plyr under `scripts/`, on any
`styles/*.R` not referenced by the Snakefile or `config.yaml`, and on a stray `Rplots.pdf`.

## Skill routing

Use these skills as complementary guidance **if they are available**:

- `ggplot2` or `r-visualisation`: layers, scales, facets and coordinate systems. Keep the
  project theme; do not apply their example themes.
- `tidyverse` or `dplyr`: loading, validation, joins, reshaping and aggregation.
