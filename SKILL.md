---
name: visualisation
description: Create or maintain self-contained, reproducible Python visualisation projects driven by Snakemake, with inputs/ for source data, scripts/ for Polars-based analysis and Matplotlib/Seaborn plotting, and outputs/ for derived data and 300-dpi PNG plus SVG figures. Use when a charting task needs a reusable project workflow; do not use for inline-only exploratory visuals.
metadata:
  short-description: Reproducible Snakemake visualisation projects
---

# Visualisation

Create reproducible, self-contained visualisation projects. The project itself is the
source of truth: source data live in `inputs/`, transformations and plotting code live
in `scripts/`, and every generated file is written under `outputs/` through Snakemake.

## Required project contract

Every project must be runnable from its root with the local virtual environment and
Snakemake. Use this layout:

```text
project/
├── inputs/          # user-supplied, immutable source data
├── outputs/         # Snakemake-managed derived data and figures
├── scripts/         # Python scripts called by the Snakefile
├── styles/          # Matplotlib style sheets for visual formatting
│   └── visualisation.mplstyle
├── Snakefile
├── README.md         # exact setup, run, output, and reproduction instructions
├── requirements.txt
└── .venv/           # local Python environment; do not commit it
```

Do not silently download data, write outside `outputs/`, or modify files in `inputs/`.
Keep all input paths, transformations, random seeds, filters, aggregation choices,
and output paths explicit in the Snakefile or scripts. If an external resource is
unavoidable, declare it as an input or an explicitly documented prerequisite.

## Environment setup

Require Python 3.14 or newer and the standard-library `venv` module. Verify the
interpreter before creating or reusing the environment:

```bash
python3.14 --version
python3.14 -m venv --help
python3.14 -m venv .venv
```

Use the environment's interpreter and Snakemake executable for all commands:

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
XDG_CACHE_HOME="$PWD/.cache" .venv/bin/snakemake --cores 1 --printshellcmds
```

On Windows, use `.venv\\Scripts\\python` and `.venv\\Scripts\\snakemake`.
Do not add `venv` to `requirements.txt`; it is a Python standard-library module. If
Python 3.14 or `venv` is unavailable, report the prerequisite clearly instead of
silently using an older interpreter.

For a new project, begin `requirements.txt` with the direct runtime dependencies:

```text
matplotlib
numpy
polars
seaborn
snakemake
```

Resolve and install them in `.venv`, then record the resolved environment when exact
replay matters (for example, with `.venv/bin/python -m pip freeze > requirements.txt`).
Do not overwrite an existing requirements file without inspecting it first.

Seaborn currently has pandas as an upstream runtime dependency. Keep Polars as the
only user-facing table/data-frame API: do not import pandas or use pandas for loading,
cleaning, joining, reshaping, or analysis. If Seaborn installs pandas transitively,
record it as an indirect compatibility dependency and do not expose it in project
code. Prefer passing NumPy arrays or simple mappings at the Seaborn plotting boundary
when a function does not accept a Polars frame directly.

## Standard workflow

1. Inspect the project before editing. Preserve existing inputs, scripts, outputs,
   requirements, and Snakefile rules unless the requested change clearly owns them.
2. Create the required directories and a minimal Snakefile. Make each generated file
   a declared rule output; use `snakemake --cores 1` as the smoke test.
3. Load source files with Polars. Validate column names, data types, units, row
   counts, missing-value codes, ordering, and replicate/subject identifiers before
   plotting. Preserve raw data and write any derived tables to `outputs/`.
4. Select an honest encoding before styling. Preserve missing observations as gaps,
   distinguish zero from missing or censored values, state the estimator and interval,
   and avoid decorative 3-D or dual-axis encodings unless scientifically justified.
5. Use the object-oriented Matplotlib API for figure construction and Seaborn for
   statistical layers where useful. Keep plotting deterministic with explicit random
   seeds and declared bootstrap/aggregation settings.
6. Export every figure as both PNG at 300 dpi and SVG. Inspect the resulting files at
   their intended physical size, including labels, legends, clipping, contrast,
   missing-data behavior, and SVG text/font handling.
7. Write or update `README.md` with the exact prerequisites, environment setup,
   reproduction command, output inventory, and rerun instructions. The README is part
   of the deliverable, not an optional afterthought.
8. Run the full Snakemake workflow from a clean or appropriately updated state. Check
   that every declared output exists and that rerunning without input changes is
   up-to-date and does not create hidden files.

## Figure defaults

Unless the user specifies otherwise, use these defaults for every static figure:

- physical size: 120 × 80 mm (`figsize=(120 / 25.4, 80 / 25.4)` inches);
- sans-serif typography, preferring Arial, then Helvetica, then DejaVu Sans;
- regular font weight by default; use bold or italic only for intentional semantic
  emphasis, never as a default for tick labels;
- largest text: 14 pt; smallest text: 9 pt;
- thinnest lines: 0.25 pt;
- thick lines: at most 1.5 pt;
- PNG: 300 dpi;
- SVG: vector output from the same figure.

Use an explicit Matplotlib style context and keep all sizes within the 9–14 pt range.
A practical starting point is a 14 pt title, 10–11 pt axis labels, and 9 pt ticks,
legend text, and secondary annotations. Use 0.25 pt only for fine structure and never
exceed 1.5 pt for plotted lines, borders, or error bars.

Store global visual formatting in a separate Matplotlib style sheet, normally
`styles/visualisation.mplstyle`, rather than duplicating `rcParams` dictionaries in
plotting scripts. Load it explicitly with `matplotlib.style.context(style_path)` (or
the equivalent `matplotlib.style.use` call). Keep data semantics, plot-specific
annotations, and scientifically meaningful encodings in the script; keep reusable
typography, line widths, colors, grids, and export/font settings in the style sheet.
Declare the style sheet as a Snakemake input so changing it regenerates the figures.
For new projects, start from the bundled [default style template](assets/visualisation.mplstyle).
Its Arial-first fallback stack is appropriate for Nature-style scientific figures, but
it is not a declaration of journal compliance; verify the target journal's current
artwork instructions before submission.

Use `layout="constrained"` or another single layout engine. Do not combine it with
`tight_layout()`. Avoid `bbox_inches="tight"` when exact physical dimensions matter;
it changes the exported page size.

Do not import `matplotlib.pyplot` in project scripts. Use Matplotlib's explicit OO
objects and a non-interactive canvas, for example:

```python
import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

fig = Figure(figsize=(120 / 25.4, 80 / 25.4), layout="constrained")
FigureCanvasAgg(fig)
ax = fig.add_subplot(1, 1, 1)
```

Pass an explicit `ax` to Seaborn functions. Save before clearing the figure:

```python
fig.savefig(snakemake.output.png, dpi=300, format="png")
fig.savefig(snakemake.output.svg, format="svg")
fig.clear()
```

Use `font.family = "sans-serif"`, perceptually appropriate and color-vision-aware
palettes, and redundant encodings such as markers, line styles, hatching, or direct
labels. Label quantities and units. Record transformations and uncertainty definitions
alongside the output or in a machine-readable manifest when the analysis warrants it.

## Snakemake conventions

Use `snakemake.input` and `snakemake.output` in scripts rather than hard-coded output
paths. A minimal two-format rule looks like this:

```python
rule all:
    input:
        "outputs/figure.png",
        "outputs/figure.svg"

rule figure:
    input:
        data="inputs/data.csv",
        code="scripts/figure.py",
        style="styles/visualisation.mplstyle"
    output:
        png="outputs/figure.png",
        svg="outputs/figure.svg"
    script:
        "scripts/figure.py"
```

Declare every code file used by a rule as an input so a script edit invalidates the
affected outputs automatically. If the project path may contain spaces, do not rely on
an unquoted interpreter path generated by the Snakemake `script:` directive. Quote the
interpreter explicitly, for example with `shlex.quote(sys.executable)` in a `params`
value and a `shell:` rule, or use an equivalent path-safe runner. Keep Snakemake and
Matplotlib caches project-local (`XDG_CACHE_HOME="$PWD/.cache"` and
`MPLCONFIGDIR=.matplotlib`) when the project must run without writing to user-level
cache directories.

## README requirement

Before handing off any project, create or update `README.md`. It must tell a new user:

1. what the project does and which input files it expects;
2. that Python 3.14+ and `venv` are required;
3. how to create `.venv` and install `requirements.txt`;
4. the exact Snakemake command that recreates the outputs;
5. which files appear under `outputs/` and what they contain; and
6. where the Matplotlib style sheet lives and which visual properties it controls; and
7. how to force a rerun after an intentional code, style, or input change.

In the final response, repeat the README's reproduction command and summarize the
generated outputs so the user does not need to discover the usage instructions alone.

For multiple figures or derived tables, prefer one rule per reproducible product or a
small set of clearly named rules. Keep the `all` rule as the complete public output
contract. Use `--dag` or `--dry-run` when checking dependencies, and use
`--rerun-incomplete` when recovering from an interrupted run.

## Skill routing

Use the available skills as complementary guidance, while this skill owns the project
layout and reproducibility contract:

- `polars`: primary loading, validation, joins, reshaping, aggregation, and derived
  tabular outputs. Do not replace it with pandas.
- `matplotlib`: explicit OO figure construction, axes, artists, physical sizing, and
  PNG/SVG export. Adapt its examples to the no-`pyplot` rule above.
- `seaborn`: statistical layers, distributions, categorical plots, regression, and
  faceting. Use explicit estimators, intervals, seeds, and sampling units; keep
  Polars authoritative at the plotting boundary.
- `scientific-visualization`: scientific integrity, uncertainty, missing-data handling,
  accessibility, color semantics, metadata inspection, and final figure audit. Use
  its publication guidance only when the user supplies a target journal or venue.
- `visualize`: optional in-conversation preview or interactive explanation. It does
  not replace the tracked Python/Snakemake pipeline or its static outputs.
- `infographics`: optional for an explicitly requested infographic or visual explainer.
  It is not a substitute for exact code-based scientific plots. Because it may require
  network access, an API key, research, and AI-generated raster output, treat it as an
  opt-in external step and record the prompt, model, sources, and non-deterministic
  prerequisite in project provenance.

## Validation checklist

Before handing off a project, verify:

- [ ] Python 3.14+ and `venv` were used for `.venv`.
- [ ] `requirements.txt` contains the complete required environment or an intentional,
      documented direct-dependency specification.
- [ ] `README.md` explains setup, reproduction, outputs, and intentional reruns.
- [ ] A separate `.mplstyle` file describes global chart formatting and is declared as
      a Snakemake input.
- [ ] No project script imports pandas or `matplotlib.pyplot`.
- [ ] All source data remain under `inputs/`; all generated products remain under
      `outputs/`.
- [ ] Every generated file is declared by Snakemake and the `all` rule is complete.
- [ ] Figures are exactly 120 × 80 mm unless overridden, use 9–14 pt sans-serif text,
      and stay within 0.25–1.5 pt line widths.
- [ ] Each figure has both a 300-dpi PNG and an SVG.
- [ ] Missing values, exclusions, units, transformations, uncertainty, and seeds are
      explicit where relevant.
- [ ] The workflow runs successfully with the local Snakemake executable and is
      up-to-date on a second run.
- [ ] Editing a declared plotting script causes the relevant rule to rerun.
- [ ] Exported figures were visually inspected at final size and checked for clipping,
      contrast, readable text, and honest data encoding.
