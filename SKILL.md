---
name: data-visualisation
description: Create or maintain self-contained, reproducible Python data visualisation projects (charts, plots, graphs, scientific figures) driven by Snakemake and uv, with inputs/ for source data, scripts/ for Polars-based analysis and Matplotlib/Seaborn plotting, and outputs/ for derived data and 450-dpi PNG plus SVG figures. Use when the user wants to plot, chart or graph data from files (e.g. CSV) as a reusable, reproducible project, or wants publication or journal figures; do not use for inline-only exploratory visuals.
license: Unlicense
compatibility: Requires Python 3.14+, uv (or the standard-library venv as a fallback) and network access to install Python packages.
metadata:
  short-description: Reproducible Snakemake visualisation projects
---

# Visualisation

Create reproducible, self-contained visualisation projects. The project itself is the
source of truth: source data live in `inputs/`, transformations and plotting code live
in `scripts/`, and every generated file is written under `outputs/` through Snakemake.

Start every new project from the bundled, tested [template](assets/template/) and
check it with [`scripts/check_project.py`](scripts/check_project.py) before handing off.

## Required project contract

Every project must be runnable from its root with uv and Snakemake. Use this layout:

```text
project/
├── inputs/            # user-supplied, immutable source data
├── outputs/           # Snakemake-managed derived data and figures
├── scripts/           # Python scripts called by the Snakefile
│   └── figure_style.py  # shared style, sizing, label and export helpers
├── styles/            # Matplotlib style sheets for visual formatting
│   └── visualisation.mplstyle
├── Snakefile
├── config.yaml        # style path, PNG dpi, figure size
├── README.md          # exact setup, run, output, and reproduction instructions
├── pyproject.toml     # direct dependencies (uv, non-packaged project)
├── uv.lock            # exact resolved versions
├── requirements.txt   # exported from uv.lock for the venv fallback
└── .venv/             # local Python environment; do not commit it
```

Do not silently download data, write outside `outputs/`, or modify files in `inputs/`.
Keep all input paths, transformations, random seeds, filters, aggregation choices,
and output paths explicit in the Snakefile, `config.yaml`, or scripts. If an external
resource is unavoidable, declare it as an input or an explicitly documented prerequisite.

**Reproducibility means the outputs depend only on files inside the project folder.**
Caches outside the folder (uv, Matplotlib font cache) are fine because they do not change
results. Things that could change results must be excluded: a user-level
`matplotlibrc` (the template resets to Matplotlib defaults before applying the project
style), environment variables, network access, unseeded randomness, and timestamps
embedded in figure files (the template strips them, so a forced rebuild is byte-identical).

## New project setup

1. Copy `assets/template/` to the project folder. Do not overwrite existing files
   without inspecting them first.
2. Copy the style sheet into `styles/`: [`assets/visualisation.mplstyle`](assets/visualisation.mplstyle)
   by default, or [`assets/nature.mplstyle`](assets/nature.mplstyle) for Nature-style work
   (then read [references/nature.md](references/nature.md)).
3. Replace the example data, scripts, rules, and README content with the real ones.
   Keep the patterns: one rule per chart, `figure_style.py` helpers, quoted interpreter.
4. Create the environment and lock it, then export the fallback requirements:

```bash
uv sync
uv export --format requirements.txt --no-emit-project --output-file requirements.txt
```

The project is a non-packaged uv project (`[tool.uv] package = false`; created by
`uv init --bare --no-package` when starting without the template): uv manages
dependencies and `.venv`, but never builds or installs the folder itself. Add
dependencies with `uv add <package>`, then re-export `requirements.txt`. Commit both
`uv.lock` and `requirements.txt`.

Run everything through the project environment:

```bash
uv run snakemake --cores 1
```

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

Seaborn currently has pandas as an upstream runtime dependency. Keep Polars as the
only user-facing table/data-frame API: do not import pandas or use pandas for loading,
cleaning, joining, reshaping, or analysis. Pass NumPy arrays or simple mappings at the
Seaborn plotting boundary.

## Standard workflow

1. Inspect the project before editing. Preserve existing inputs, scripts, outputs,
   dependency files, and Snakefile rules unless the requested change clearly owns them.
2. Load source files with Polars. Validate column names, data types, units, row
   counts, missing-value codes, ordering, and replicate/subject identifiers before
   plotting. Preserve raw data and write any derived tables to `outputs/`.
3. Select an honest encoding before styling. Preserve missing observations as gaps,
   distinguish zero from missing or censored values, state the estimator and interval,
   and avoid decorative 3-D or dual-axis encodings unless scientifically justified.
4. Use the object-oriented Matplotlib API for figure construction and Seaborn for
   statistical layers where useful. Keep plotting deterministic with explicit random
   seeds and declared bootstrap/aggregation settings.
5. Export every chart as its own PNG and SVG pair.
6. Write or update `README.md` (see [README requirement](#readme-requirement)).
7. Run the workflow, then the checker, then look at every figure (see
   [Validation](#validation)).

## Figure defaults

Unless the user specifies otherwise:

- physical size: 120 × 80 mm (`figure_width_mm` / `figure_height_mm` in `config.yaml`);
- sans-serif typography, preferring Arial, then Helvetica, then DejaVu Sans;
- regular font weight; use bold or italic only for intentional semantic emphasis;
- text between 5 and 14 pt — the default style uses 12 pt titles, 10 pt axis labels,
  and 9 pt ticks, legends, and annotations; the Nature preset uses 5–8 pt;
- lines between 0.25 pt (fine structure) and 1.5 pt (thickest plotted line, border,
  or error bar); axes and tick marks 0.5 pt;
- PNG at 450 dpi, or 600 dpi when asked (`png_dpi` in `config.yaml`, or
  `uv run snakemake --cores 1 --config png_dpi=600` for one build);
  the Snakefile rejects other values;
- SVG: vector output from the same figure, with editable text;
- y-axis labels: horizontal and above the top-left of the axis.

Store global visual formatting in the style sheet in `styles/` rather than in
`rcParams` dictionaries inside scripts. Keep data semantics, plot-specific annotations,
and scientifically meaningful encodings in the script; keep reusable typography, line
widths, the color/line-style cycle, and font-embedding settings in the style sheet.
Build settings that may change per run (style path, dpi, size) live in `config.yaml`
and reach scripts as Snakemake `params`, so changing them reruns the affected rules.

The style sheets are a starting point, not a declaration of journal compliance; verify
the target journal's current artwork instructions before submission.

### Figure construction

Use the helpers in the template's `scripts/figure_style.py`:

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
- Matplotlib exposes the y-label location as an rcParam (`yaxis.labellocation: top`)
  but not its rotation, so the horizontal label is set per axes. The title is then
  padded in points to clear it. Long titles are not constrained by the layout engine
  and can be clipped at the figure edge: keep titles short and check the output.
- Save with `metadata={"Date": None}` for SVG and `{"Software": None}` for PNG, and
  keep `svg.hashsalt` in the style, so rebuilds are byte-identical.

## Color policy

Use black as the default plotting color. The bundled styles cycle black lines through
solid, dashed, dotted, and dash-dot line styles, so several series stay distinguishable
without hue. Do not add color merely to make a figure more attractive.

Introduce color only when it carries necessary data meaning, such as a continuous
measurement encoded by a color scale, a categorical distinction that cannot be made
clear with position, markers, line styles, hatching, faceting, or direct labels, or a
scientifically established reference convention. Prefer those non-color encodings
first, and use redundant encoding when feasible so the figure remains interpretable
in grayscale and by readers with color-vision deficiencies.

Seaborn ignores the style's cycle when `hue=` is used and applies its own palette. Pass
`palette=` (or `color=`) explicitly whenever you call Seaborn with `hue`.

Every justified use of color must be explicit in the project README or figure
metadata/caption: state what variable color encodes, why a non-color encoding was not
sufficient, and which perceptually appropriate, color-vision-aware palette or
normalization is used. Keep backgrounds, axes, ticks, text, and default data marks
black or neutral unless a documented data encoding requires otherwise.

## Chart granularity

Create multiple independent charts when the data support multiple views. Each chart
is a separate output with its own PNG and SVG, its own Snakemake rule, a clear
filename, title, axis labels with units, and a README entry. Reuse shared loading,
validation, and styling code across the chart scripts.

Build a multi-panel figure **only when the user explicitly asks for one**. Then follow
the panel guidance in [references/nature.md](references/nature.md#multi-panel-figures-only-when-explicitly-requested),
which applies to any journal-style multi-panel figure, and name the combined figure
as its own product in the README.

## Snakemake conventions

Follow the template's Snakefile:

```python
import sys

configfile: "config.yaml"

PYTHON = sys.executable

rule all:
    input:
        multiext("outputs/figures/measurement_by_day", ".png", ".svg"),

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

- Use one rule per chart or derived table. Keep `all` as the complete public output
  contract, including every chart file.
- Use `shell:` rules with `:q`-quoted paths and command-line arguments, not the
  `script:` directive. Snakemake's `script:` runs the interpreter through an unquoted
  path and fails when the project path contains spaces (common on macOS, e.g.
  `~/Library/Application Support`). A side benefit: every script can also run by hand.
- Declare every file a rule reads as an input: data, the script, imported helper
  modules, and the style sheet. Snakemake then reruns exactly the affected rules when
  any of them changes.
- Use `--dry-run` or `--dag` when checking dependencies and `--rerun-incomplete` when
  recovering from an interrupted run.

## README requirement

Before handing off any project, create or update `README.md` (the template has the
structure). It must tell a new user:

1. what the project does and which input files it expects, with units and missing-value codes;
2. that Python 3.14+ and uv are required, with `venv` as the fallback;
3. how to set up the environment with uv and with the `requirements.txt` fallback;
4. the exact Snakemake command that recreates the outputs, and how to get 600 dpi;
5. which files appear under `outputs/` and what they contain;
6. where the Matplotlib style sheet lives and which visual properties it controls;
7. any use of color and its justification;
8. how to force a rerun after an intentional code, style, or input change; and
9. how to update dependencies and re-export `requirements.txt`.

In the final response, repeat the README's reproduction command and summarize the
generated outputs so the user does not need to discover the usage instructions alone.

## Skill routing

This skill owns the project layout and reproducibility contract. Use these other skills
as complementary guidance **if they are available**; skip any that are not installed:

- `polars`: loading, validation, joins, reshaping, aggregation, and derived tables.
  Do not replace it with pandas.
- `matplotlib`: OO figure construction, axes, artists, and export. Adapt its examples
  to the no-`pyplot` rule.
- `seaborn`: statistical layers, distributions, categorical plots, regression, and
  faceting. Use explicit estimators, intervals, seeds, and sampling units.
- `scientific-visualization`: scientific integrity, uncertainty, missing-data handling,
  accessibility, color semantics, and final figure audit. Use its publication guidance
  only when the user supplies a target journal or venue.
- `visualize`: optional in-conversation preview. It does not replace the tracked
  Python/Snakemake pipeline or its static outputs.
- `infographics`: only for an explicitly requested infographic. It is not a substitute
  for code-based scientific plots; treat it as an opt-in external step and record the
  prompt, model, sources, and non-deterministic prerequisites in the README.

## Validation

Run the build, then the bundled checker from the project root with the project's own
interpreter (the checker uses only the standard library):

```bash
uv run snakemake --cores 1
uv run python <skill-dir>/scripts/check_project.py . --up-to-date
```

Add `--size-mm WIDTHxHEIGHT` when the figure size is not 120 × 80 mm (or `--size-mm any`).
The checker verifies the layout and lock files, no pandas or `pyplot` imports, a PNG
and SVG for every figure, PNG at 450 or 600 dpi, exact physical size, SVG text 5–14 pt,
SVG strokes 0.25–1.5 pt, no embedded timestamps, every style sheet referenced by the
workflow, and (with `--up-to-date`) that a second Snakemake run has nothing to do.
Fix every `FAIL` line before handing off.

Then confirm by hand what the checker cannot see:

- [ ] Every figure was opened and inspected at final size: no clipped titles or labels,
      no collisions, readable text, sufficient contrast.
- [ ] The encoding is honest: missing values, exclusions, units, transformations,
      uncertainty definitions, and seeds are explicit where relevant.
- [ ] Figures are black by default; every use of color has a documented data or
      scientific justification, with non-color encodings considered first.
- [ ] Charts are separate outputs; a multi-panel figure exists only because the user asked.
- [ ] If Nature styling was requested, the project follows [references/nature.md](references/nature.md)
      and records the chosen size, export settings, and pending journal verification.
- [ ] `README.md` covers every point in the README requirement.
- [ ] Workflow and checker output is clean: no warnings or errors.
