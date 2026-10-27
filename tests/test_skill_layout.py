# Checks the repository follows the skills/<name>/SKILL.md publisher layout and the
# Agent Skills frontmatter rules, so `gh skill` and `npx skills` can discover and install it.

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(REPO_ROOT.glob("skills/*/SKILL.md"))
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DEVELOPMENT_ONLY = ("tests", "evals", ".git", ".pytest_cache")


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


def test_skill_md_relative_links_resolve() -> None:
    for skill_md in SKILLS:
        for target in re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", skill_md.read_text()):
            assert (skill_md.parent / target).exists(), f"broken link in {skill_md}: {target}"


def test_skill_ships_its_license() -> None:
    for skill_md in SKILLS:
        assert (skill_md.parent / "LICENSE").exists()
