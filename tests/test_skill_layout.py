# Checks the repository follows the skills/<name>/SKILL.md publisher layout and the
# Agent Skills frontmatter rules, so `gh skill` and `npx skills` can discover and install it.

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(REPO_ROOT.glob("skills/*/SKILL.md"))
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DEVELOPMENT_ONLY = ("tests", "evals", ".git", ".pytest_cache")
SKILL_DIR = REPO_ROOT / "skills" / "data-visualisation"
SKILL_MD = SKILL_DIR / "SKILL.md"
STACKS = ("python-matplotlib", "r-ggplot2")
STYLES = ("nature", "visualisation")
# Library and file-format names that belong in a stack reference, never in SKILL.md.
STACK_SPECIFIC_TERMS = (
    "matplotlib", "mplstyle", "seaborn", "polars", "pandas", "pyplot", "numpy",
    "ggplot2", "ggplot", "renv", "dplyr", "tidyr", "readr", "purrr", "svglite", "ragg",
)


def frontmatter(skill_md: Path) -> dict[str, str]:
    """Top-level scalar keys of the YAML frontmatter (enough for the spec's checks)."""
    text = skill_md.read_text()
    assert text.startswith("---\n"), f"{skill_md} has no frontmatter"
    block = text.split("---\n", 2)[1]
    return dict(re.findall(r"^([a-z-]+):[ ]?(.*)$", block, flags=re.MULTILINE))


def test_exactly_one_skill_in_publisher_layout() -> None:
    assert [p.parent.name for p in SKILLS] == ["data-visualisation"]
    assert not (REPO_ROOT / "SKILL.md").exists(), "a root SKILL.md hides the skills/ layout"


def test_name_follows_spec_and_matches_folder() -> None:
    for skill_md in SKILLS:
        name = frontmatter(skill_md)["name"]
        assert len(name) <= 64
        assert NAME_PATTERN.match(name), name
        assert name == skill_md.parent.name


def test_description_and_compatibility_lengths() -> None:
    for skill_md in SKILLS:
        fields = frontmatter(skill_md)
        assert 1 <= len(fields["description"]) <= 1024
        assert 1 <= len(fields.get("compatibility", "x")) <= 500


def test_skill_folder_contains_no_development_files() -> None:
    for skill_md in SKILLS:
        present = {p.name for p in skill_md.parent.iterdir()}
        assert not present & set(DEVELOPMENT_ONLY), present & set(DEVELOPMENT_ONLY)


def test_markdown_relative_links_resolve() -> None:
    for skill_md in SKILLS:
        for document in [skill_md, *sorted(skill_md.parent.glob("references/**/*.md"))]:
            for target in re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", document.read_text()):
                assert (document.parent / target).exists(), f"broken link in {document}: {target}"


def test_skill_md_is_stack_neutral() -> None:
    """Stack-specific instructions live in references/stacks/, so one stack never loads another's.

    The frontmatter is exempt: its description must name the libraries to trigger the skill.
    """
    text = SKILL_MD.read_text().split("---\n", 2)[2].lower()
    for stack in STACKS:
        text = text.replace(f"references/stacks/{stack}.md", "")
    leaked = [term for term in STACK_SPECIFIC_TERMS if re.search(rf"\b{re.escape(term)}\b", text)]
    assert not leaked, f"SKILL.md mentions stack-specific terms: {leaked}"


def test_skill_md_links_every_stack_and_style() -> None:
    text = SKILL_MD.read_text()
    for stack in STACKS:
        assert f"references/stacks/{stack}.md" in text, stack
    for style in STYLES:
        assert f"references/styles/{style}.md" in text, style


def test_every_stack_has_a_reference_and_a_template() -> None:
    for stack in STACKS:
        assert (SKILL_DIR / "references" / "stacks" / f"{stack}.md").is_file(), stack
        assert (SKILL_DIR / "assets" / stack / "template" / "Snakefile").is_file(), stack


def test_every_stack_implements_every_style() -> None:
    for stack in STACKS:
        implemented = {p.stem for p in (SKILL_DIR / "assets" / stack / "styles").iterdir()}
        assert implemented == set(STYLES), f"{stack} implements {sorted(implemented)}"


def test_every_stack_reference_names_its_own_assets_only() -> None:
    for stack in STACKS:
        text = (SKILL_DIR / "references" / "stacks" / f"{stack}.md").read_text()
        assert f"assets/{stack}/" in text, stack
        for other in set(STACKS) - {stack}:
            assert other not in text, f"{stack}.md refers to {other}"


def test_skill_ships_its_license() -> None:
    for skill_md in SKILLS:
        assert (skill_md.parent / "LICENSE").exists()
