# Data visualisation skill for AI agents

A data visualisation skill usable with many AI agents (Claude Code, Codex and others that
read `SKILL.md`).

It creates a reproducible Python 3.14+ project managed with uv (with a plain `venv`
fallback) and built with Snakemake: Polars for data, Matplotlib/Seaborn for figures,
and 450-dpi PNG plus SVG outputs (600 dpi on request).

## Install

With [`npx skills`](https://skills.sh) (Node.js 22.20+), for all your projects:

```bash
npx skills add jtkorhonen/data-visualisation --skill data-visualisation -g -a claude-code
```

Or with the GitHub CLI (`gh skill` is in preview):

```bash
gh skill install jtkorhonen/data-visualisation data-visualisation --agent claude-code --scope user
```

Use another `-a` / `--agent` value (for example `codex`) for other agents, or leave out
`-g` / `--scope user` to install into the current project only. Update later with
`npx skills update` or `gh skill update --all`.

`agents/openai.yaml` provides the display name and default prompt for Codex.

## Contents

| Path | Purpose |
| --- | --- |
| `skills/data-visualisation/` | The skill itself; this folder is what gets installed |
| `skills/data-visualisation/SKILL.md` | Stack-neutral contract the agent always follows |
| `skills/data-visualisation/references/stacks/` | One file per language stack, loaded only for that stack |
| `skills/data-visualisation/references/styles/` | Language-neutral style specs (default and Nature), loaded only when chosen |
| `skills/data-visualisation/assets/<stack>/template/` | Runnable starter project per stack (uv, Snakemake, two example charts) |
| `skills/data-visualisation/assets/<stack>/styles/` | Each stack's implementation of every style spec |
| `skills/data-visualisation/scripts/check_project.py` | Standard-library checker for a generated project |
| `evals/` | Sample prompts and data for trying the skill (not installed) |
| `tests/` | Layout, checker, and end-to-end template tests (not installed) |

## Development

Run the tests (the end-to-end tests need uv and network access or a warm uv cache, and
take a few minutes):

```bash
uv run --no-project --python 3.14 --with pytest pytest tests
```
