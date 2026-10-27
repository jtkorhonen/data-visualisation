# Data visualisation skill for AI agents

A data visualisation skill usable with many AI agents (Claude Code, Codex and others that
read `SKILL.md`).

It creates a reproducible Python 3.14+ project managed with uv (with a plain `venv`
fallback) and built with Snakemake: Polars for data, Matplotlib/Seaborn for figures,
and 450-dpi PNG plus SVG outputs (600 dpi on request).

## Install

Clone the repository into your agent's skills folder, for example for Claude Code:

```bash
git clone https://github.com/jtkorhonen/data-visualisation ~/.claude/skills/data-visualisation
```

For a single project, clone into `<project>/.claude/skills/data-visualisation` instead.
`agents/openai.yaml` provides the display name and default prompt for Codex.

## Contents

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Instructions the agent follows |
| `references/nature.md` | Nature-style sizing, export, and multi-panel guidance, loaded only when needed |
| `assets/template/` | Runnable starter project (uv, Snakemake, two example charts) |
| `assets/*.mplstyle` | Default and Nature-oriented Matplotlib style sheets |
| `scripts/check_project.py` | Standard-library checker for a generated project |
| `evals/` | Sample prompts and data for trying the skill |
| `tests/` | Unit tests for the checker and end-to-end tests for the template |

## Development

Run the tests (the end-to-end tests need uv and network access or a warm uv cache, and
take a few minutes):

```bash
uv run --no-project --python 3.14 --with pytest pytest tests
```
