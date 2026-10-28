---
name: data-visualisation
description: Create or maintain self-contained, reproducible data visualisation projects (charts, plots, graphs, scientific figures) in Python (Polars, Matplotlib/Seaborn, uv) or R (readr/dplyr/tidyr, ggplot2, renv), driven by Snakemake, with inputs/ for source data, scripts/ for analysis and plotting, styles/ for a fully defined figure style, and outputs/ for derived data and 450-dpi PNG plus SVG figures. Use when the user wants to plot, chart or graph data from files (e.g. CSV) as a reusable, reproducible project, or wants publication or journal figures; do not use for inline-only exploratory visuals.
license: Unlicense
compatibility: Requires Python 3.14+ with uv (or the standard-library venv as a fallback) for Snakemake and the Python stack, R 4.5+ for the R stack, and network access to install packages.
metadata:
  short-description: Reproducible Snakemake visualisation projects
---

# Visualisation

Create reproducible, self-contained visualisation projects. The project itself is the
source of truth: source data live in `inputs/`, transformations and plotting code live
in `scripts/`, and every generated file is written under `outputs/` through Snakemake.

This file holds the contract shared by every language. The language-specific details
live in one stack reference, and the visual values in one style spec; read only the
ones the project uses.

## Choose the stack and style

1. **Stack.** Use the language the user asks for. Otherwise, for an existing project,
   use the language its `scripts/` are written in. Otherwise use Python. Then read
   that stack's reference before writing any code:

   | Stack | Reference |
   | --- | --- |
   | Python | [references/stacks/python-matplotlib.md](references/stacks/python-matplotlib.md) |
   | R | [references/stacks/r-ggplot2.md](references/stacks/r-ggplot2.md) |

2. **Style.** Use [references/styles/visualisation.md](references/styles/visualisation.md)
   by default, or [references/styles/nature.md](references/styles/nature.md) for Nature or
   Nature-style work. The stack reference names the file that implements the style.

Start every new project from the stack's bundled, tested template and check it with
[`scripts/check_project.py`](scripts/check_project.py) before handing off.

## Required project contract

Every project must be runnable from its root with uv and Snakemake. Use this layout,
plus the stack-specific files its reference lists:

```text
project/
├── inputs/            # user-supplied, immutable source data
├── outputs/           # Snakemake-managed derived data and figures
├── scripts/           # analysis and plotting scripts called by the Snakefile,
│                      # including the shared figure helpers
├── styles/            # the style implementation for visual formatting
├── Snakefile
├── config.yaml        # style path, PNG dpi, figure size
├── README.md          # exact setup, run, output, and reproduction instructions
├── pyproject.toml     # Snakemake and other direct dependencies (uv, non-packaged)
├── uv.lock            # exact resolved versions
├── requirements.txt   # exported from uv.lock for the venv fallback
└── .venv/             # local environment; do not commit it
```

Do not silently download data, write outside `outputs/`, or modify files in `inputs/`.
Keep all input paths, transformations, random seeds, filters, aggregation choices,
and output paths explicit in the Snakefile, `config.yaml`, or scripts. If an external
resource is unavoidable, declare it as an input or an explicitly documented prerequisite.

**Reproducibility means the outputs depend only on files inside the project folder.**
Caches outside the folder (package caches, font caches) are fine because they do not
change results. Things that could change results must be excluded: user-level plotting
configuration (the templates reset to library defaults before applying the project
style), environment variables, network access, unseeded randomness, and timestamps
embedded in figure files (the templates strip them, so a forced rebuild is byte-identical).

## New project setup

1. Copy the stack's template to the project folder. Do not overwrite existing files
   without inspecting them first.
2. Copy the stack's implementation of the chosen style into `styles/` and select it in
   `config.yaml`. For Nature-style work, also follow [references/styles/nature.md](references/styles/nature.md).
3. Replace the example data, scripts, rules, and README content with the real ones.
   Keep the patterns: one rule per chart, the figure helpers, quoted interpreter.
4. Create and lock the environment as the stack reference describes. Commit the lock files.

Run everything through the project environment:

```bash
uv run snakemake --cores 1
```

If uv or the stack's language runtime is unavailable, report the prerequisite clearly
instead of silently using an older or different interpreter.

## Standard workflow

1. Inspect the project before editing. Preserve existing inputs, scripts, outputs,
   dependency files, and Snakefile rules unless the requested change clearly owns them.
2. Load source files with the stack's data library. Validate column names, data types,
   units, row counts, missing-value codes, ordering, and replicate/subject identifiers
   before plotting. Preserve raw data and write any derived tables to `outputs/`.
3. Select an honest encoding before styling. Preserve missing observations as gaps,
   distinguish zero from missing or censored values, state the estimator and interval,
   and avoid decorative 3-D or dual-axis encodings unless scientifically justified.
4. Build figures with the stack's figure helpers. Keep plotting deterministic with
   explicit random seeds and declared bootstrap/aggregation settings.
5. Export every chart as its own PNG and SVG pair.
6. Write or update `README.md` (see [README requirement](#readme-requirement)).
7. Run the workflow, then the checker, then look at every figure (see
   [Validation](#validation)).

## Figure defaults

Unless the user specifies otherwise:

- physical size: 120 × 80 mm (`figure_width_mm` / `figure_height_mm` in `config.yaml`);
- typography, line widths, ticks, grid and frame as in the chosen style spec: the
  default style follows `ggthemes::theme_clean()` (bold 14 pt title, 10 pt axis
  titles, 9 pt ticks, dotted horizontal grid, framed figure); the Nature style uses 5–8 pt;
- text between 5 and 14 pt and lines between 0.25 pt (fine structure) and 1.5 pt
  (thickest plotted line, border, or error bar) in every style;
- PNG at 450 dpi, or 600 dpi when asked (`png_dpi` in `config.yaml`, or
  `uv run snakemake --cores 1 --config png_dpi=600` for one build);
  the Snakefile rejects other values;
- SVG: vector output from the same figure, with editable text;
- y-axis labels: horizontal and above the top-left of the axis.

Store global visual formatting in the style implementation in `styles/`, not inside
plotting scripts. The style files must define the style **fully**: every setting that
can change a figure is written out, never left to library defaults, so the project
reproduces the same figures after a library upgrade. Keep data semantics, plot-specific annotations, and scientifically
meaningful encodings in the script; keep reusable typography, line widths, the
color/line-style cycle, and font-embedding settings in the style. Build settings that
may change per run (style path, dpi, size) live in `config.yaml` and reach scripts as
Snakemake `params`, so changing them reruns the affected rules.

The styles are a starting point, not a declaration of journal compliance; verify
the target journal's current artwork instructions before submission.

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
the panel guidance in [references/styles/nature.md](references/styles/nature.md#multi-panel-figures-only-when-explicitly-requested),
which applies to any journal-style multi-panel figure, and name the combined figure
as its own product in the README.

## Snakemake conventions

Follow the stack template's Snakefile; the stack reference shows a complete rule.

- Use one rule per chart or derived table. Keep `all` as the complete public output
  contract, including every chart file.
- Use `shell:` rules with `:q`-quoted paths and command-line arguments, not the
  `script:` directive. Snakemake's `script:` runs the interpreter through an unquoted
  path and fails when the project path contains spaces (common on macOS, e.g.
  `~/Library/Application Support`). A side benefit: every script can also run by hand.
- Declare every file a rule reads as an input: data, the script, imported helper
  modules, and the style implementation. Snakemake then reruns exactly the affected
  rules when any of them changes.
- Pass the style path, dpi and size from `config.yaml` to every plotting script as
  command-line arguments.
- Use `--dry-run` or `--dag` when checking dependencies and `--rerun-incomplete` when
  recovering from an interrupted run.

## README requirement

Before handing off any project, create or update `README.md` (the stack template has
the structure). It must tell a new user:

1. what the project does and which input files it expects, with units and missing-value codes;
2. which runtimes and tools are required, with the fallback;
3. how to set up the environment, with uv and with the fallback;
4. the exact Snakemake command that recreates the outputs, and how to get 600 dpi;
5. which files appear under `outputs/` and what they contain;
6. where the style implementation lives and which visual properties it controls;
7. any use of color and its justification;
8. how to force a rerun after an intentional code, style, or input change; and
9. how to update dependencies and the lock files.

In the final response, repeat the README's reproduction command and summarize the
generated outputs so the user does not need to discover the usage instructions alone.

## Skill routing

This skill owns the project layout and reproducibility contract. The stack reference
lists the library skills for its language. Use these other skills as complementary
guidance **if they are available**; skip any that are not installed:

- `scientific-visualization`: scientific integrity, uncertainty, missing-data handling,
  accessibility, color semantics, and final figure audit. Use its publication guidance
  only when the user supplies a target journal or venue.
- `visualize`: optional in-conversation preview. It does not replace the tracked
  Snakemake pipeline or its static outputs.
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
The checker verifies the layout and lock files, the stack's code rules, a PNG and SVG
for every figure, PNG at 450 or 600 dpi, exact physical size, SVG text 5–14 pt, SVG
strokes 0.25–1.5 pt, no embedded timestamps, every style file referenced by the
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
- [ ] If Nature styling was requested, the project follows [references/styles/nature.md](references/styles/nature.md)
      and records the chosen size, export settings, and pending journal verification.
- [ ] `README.md` covers every point in the README requirement.
- [ ] Workflow and checker output is clean: no warnings or errors.
