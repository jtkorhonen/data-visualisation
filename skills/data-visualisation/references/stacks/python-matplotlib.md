# Stack: Python + Matplotlib

Read this when the project uses Python: Polars for data, Matplotlib (and optionally
Seaborn) for figures. It adds the Python specifics to the shared contract in `SKILL.md`;
everything there still applies.

## Assets

| Asset | Copy to |
| --- | --- |
| [`assets/python-matplotlib/template/`](../../assets/python-matplotlib/template/) | the project folder |
| [`assets/python-matplotlib/styles/visualisation.mplstyle`](../../assets/python-matplotlib/styles/visualisation.mplstyle) | `styles/` (default style) |
| [`assets/python-matplotlib/styles/nature.mplstyle`](../../assets/python-matplotlib/styles/nature.mplstyle) | `styles/` (Nature style, instead of the default) |

The style sheets implement the specs in [`../styles/`](../styles/). Select the style with
`style: styles/<name>.mplstyle` in `config.yaml`.

## Project files

On top of the shared layout:

```text
project/
├── scripts/
│   └── figure_style.py        # shared style, sizing, label and export helpers
├── styles/
│   └── visualisation.mplstyle # Matplotlib style sheet
└── .venv/                     # one uv environment for Snakemake and the scripts
```

`pyproject.toml` lists Snakemake and the analysis libraries together (Matplotlib, NumPy,
Polars, Seaborn); `uv.lock` and `requirements.txt` lock all of them.

## Environment

Create the environment and lock it, then export the fallback requirements:

```bash
uv sync
uv export --format requirements.txt --no-emit-project --output-file requirements.txt
```

The project is a non-packaged uv project (`[tool.uv] package = false`; created by
`uv init --bare --no-package` when starting without the template): uv manages
dependencies and `.venv`, but never builds or installs the folder itself. Add
dependencies with `uv add <package>`, then re-export `requirements.txt`. Commit both
`uv.lock` and `requirements.txt`.

**Fallback without uv** (any Python 3.14 or newer with the standard-library `venv`):

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/snakemake --cores 1
```

On Windows, use `.venv\Scripts\python` and `.venv\Scripts\snakemake`. If neither uv nor
Python 3.14+ is available, report the prerequisite clearly instead of silently using an
older interpreter. Do not add `venv` to the dependencies; it is part of the standard library.

## Data

Load source files with Polars. Seaborn currently has pandas as an upstream runtime
dependency. Keep Polars as the only user-facing table/data-frame API: do not import
pandas or use pandas for loading, cleaning, joining, reshaping, or analysis. Pass NumPy
arrays or simple mappings at the Seaborn plotting boundary.

## Figure construction

Use the object-oriented Matplotlib API for figure construction and Seaborn for
statistical layers where useful. Use the helpers in the template's `scripts/figure_style.py`:

```python
from figure_style import (
    figure_arguments, new_figure, save_figure,
    set_horizontal_ylabel, set_title_above_ylabel, style_context,
)

args = figure_arguments("Plot measurement by day").parse_args()
with style_context(args.style):                  # Matplotlib defaults + project style
    figure, axes = new_figure(args.width_mm, args.height_mm)
    ...                                            # plot; pass ax=axes to Seaborn
    set_horizontal_ylabel(axes, "quantity (unit)")
    set_title_above_ylabel(axes, "Chart title")
    save_figure(figure, args.png, args.svg, args.dpi)
```

What the helpers enforce, if you need to write equivalent code:

- Do not import `matplotlib.pyplot`. Create `matplotlib.figure.Figure` directly; it
  saves PNG and SVG without a backend or canvas setup.
- Use `layout="constrained"` and no other layout engine. Do not call `tight_layout()`
  or use `bbox_inches="tight"`; it changes the exported physical size.
- `import matplotlib.style` explicitly; `import matplotlib` alone does not expose it.
- `style_context` resets to Matplotlib defaults before applying the project style, so a
  user-level `matplotlibrc` cannot change the output.
- Matplotlib exposes the y-label location as an rcParam (`yaxis.labellocation: top`)
  but not its rotation, so the horizontal label is set per axes. The title is then
  padded in points to clear it. Long titles are not constrained by the layout engine
  and can be clipped at the figure edge: keep titles short and check the output.
- Save with `metadata={"Date": None}` for SVG and `{"Software": None}` for PNG, and
  keep `svg.hashsalt` in the style, so rebuilds are byte-identical.

Store global visual formatting in the style sheet rather than in `rcParams` dictionaries
inside scripts.

## Color

Seaborn ignores the style's cycle when `hue=` is used and applies its own palette. Pass
`palette=` (or `color=`) explicitly whenever you call Seaborn with `hue`.

## Snakefile

Follow the template's Snakefile. Rules call scripts through the interpreter that runs
Snakemake, quoted:

```python
import sys

configfile: "config.yaml"

PYTHON = sys.executable

rule plot_measurement_by_day:
    input:
        data="inputs/measurements.csv",
        script="scripts/plot_measurement_by_day.py",
        helpers="scripts/figure_style.py",
        style=config["style"],
    output:
        png="outputs/figures/measurement_by_day.png",
        svg="outputs/figures/measurement_by_day.svg",
    params:
        python=PYTHON,
        dpi=config["png_dpi"],
        width_mm=config["figure_width_mm"],
        height_mm=config["figure_height_mm"],
    shell:
        "{params.python:q} {input.script:q} --data {input.data:q} --style {input.style:q} "
        "--png {output.png:q} --svg {output.svg:q} --dpi {params.dpi} "
        "--width-mm {params.width_mm} --height-mm {params.height_mm}"
```

## README specifics

- Requirements: Python 3.14+ and uv, with `venv` as the fallback.
- Setup with uv and with the `requirements.txt` fallback.
- Style: `styles/<name>.mplstyle` controls fonts and text sizes, line and tick widths,
  the black line-style cycle, and SVG/PDF font handling.
- Updating dependencies: `uv lock --upgrade`, then re-export `requirements.txt`.

## Checks

The checker additionally fails on any `pandas` or `matplotlib.pyplot` import under
`scripts/`, and on any `styles/*.mplstyle` not referenced by the Snakefile or `config.yaml`.

## Skill routing

Use these skills as complementary guidance **if they are available**:

- `polars`: loading, validation, joins, reshaping, aggregation, and derived tables.
  Do not replace it with pandas.
- `matplotlib`: OO figure construction, axes, artists, and export. Adapt its examples
  to the no-`pyplot` rule.
- `seaborn`: statistical layers, distributions, categorical plots, regression, and
  faceting. Use explicit estimators, intervals, seeds, and sampling units.
