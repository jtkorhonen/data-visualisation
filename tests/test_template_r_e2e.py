# End-to-end tests for the R stack: scaffold a project from assets/r-ggplot2/template, set up renv
# and uv, build it with Snakemake, and check the outputs. Needs R, uv and network or warm caches.

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "data-visualisation"
CHECKER = SKILL_ROOT / "scripts" / "check_project.py"
STACK_ASSETS = SKILL_ROOT / "assets" / "r-ggplot2"
FIGURES = ("measurement_by_day", "measurement_distribution")
RSCRIPT = ["Rscript", "--no-site-file", "--no-environ"]
# The test runner's own virtual environment must not leak into the project's uv commands.
PROJECT_ENV = {name: value for name, value in os.environ.items() if name != "VIRTUAL_ENV"}

pytestmark = pytest.mark.skipif(
    shutil.which("uv") is None or shutil.which("Rscript") is None, reason="needs uv and R"
)


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=PROJECT_ENV)
    assert result.returncode == 0, f"{args} failed:\n{result.stdout}\n{result.stderr}"
    return result


def run_r(code: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run R code in the project, with its renv library, failing on any warning."""
    return run([*RSCRIPT, "-e", "options(warn = 2)", "-e", code], cwd)


def scaffold(destination: Path, style: str = "visualisation") -> Path:
    """Copy the template and one bundled style, then set up uv and renv as the stack reference instructs."""
    shutil.copytree(STACK_ASSETS / "template", destination)
    (destination / "styles").mkdir(exist_ok=True)
    shutil.copy(STACK_ASSETS / "styles" / f"{style}.R", destination / "styles")
    run(["uv", "sync", "--quiet"], destination)
    run(
        ["uv", "export", "--quiet", "--format", "requirements.txt", "--no-emit-project",
         "--output-file", "requirements.txt"],
        destination,
    )
    run([*RSCRIPT, "-e", "renv::install(prompt = FALSE)", "-e", "renv::snapshot(prompt = FALSE)"], destination)
    return destination


def assert_no_warnings(result: subprocess.CompletedProcess) -> None:
    output = result.stdout + result.stderr
    for marker in ("Warning", "warning", "Error"):
        assert marker not in output, output


def svg_texts(path: Path) -> dict[str, list[tuple[float, float, str]]]:
    """Map each text in an svglite SVG to its (x, y, attributes) placements."""
    texts: dict[str, list[tuple[float, float, str]]] = {}
    for attributes, label in re.findall(r"<text([^>]*)>([^<]*)</text>", path.read_text()):
        x = float(re.search(r"x='([\d.]+)'", attributes).group(1))
        y = float(re.search(r"y='([\d.]+)'", attributes).group(1))
        texts.setdefault(label, []).append((x, y, attributes))
    return texts


@pytest.fixture(scope="module")
def built_project(tmp_path_factory) -> Path:
    root = scaffold(tmp_path_factory.mktemp("r-e2e") / "project with spaces")
    assert_no_warnings(run(["uv", "run", "snakemake", "--cores", "1", "--quiet"], root))
    return root


def test_build_creates_every_declared_output(built_project: Path) -> None:
    assert (built_project / "outputs" / "data" / "summary.csv").exists()
    for name in FIGURES:
        assert (built_project / "outputs" / "figures" / f"{name}.png").exists()
        assert (built_project / "outputs" / "figures" / f"{name}.svg").exists()


def test_checker_passes_and_rerun_is_up_to_date(built_project: Path) -> None:
    result = run(["uv", "run", "python", str(CHECKER), ".", "--up-to-date"], built_project)
    assert "OK" in result.stdout


def test_forced_rebuild_is_byte_identical(built_project: Path) -> None:
    figures = sorted((built_project / "outputs").rglob("*.*"))
    before = {path: path.read_bytes() for path in figures}
    run(["uv", "run", "snakemake", "--cores", "1", "--quiet", "--forceall"], built_project)
    assert {path: path.read_bytes() for path in figures} == before


@pytest.mark.parametrize("name", FIGURES)
def test_y_title_is_horizontal_above_the_tick_labels(built_project: Path, name: str) -> None:
    texts = svg_texts(built_project / "outputs" / "figures" / f"{name}.svg")
    [(title_x, title_y, attributes)] = texts["value (a.u.)"]
    assert "rotate" not in attributes
    tick_labels = [placement for label, placements in texts.items() if label.isdigit() for placement in placements]
    left_ticks = [(x, y) for x, y, _ in tick_labels if x == min(x for x, _, _ in tick_labels)]
    assert title_y < min(y for _, y in left_ticks), "y title must sit above the highest y tick label"
    assert title_x <= min(x for x, _ in left_ticks), "y title must start at or left of the y tick labels"
    [(_, chart_title_y, _)] = next(v for k, v in texts.items() if k.startswith("Measurement"))
    assert chart_title_y < title_y, "chart title must sit above the y title"


def test_y_title_goes_above_facet_strips(built_project: Path) -> None:
    result = run_r(
        """
        source("scripts/figure_style.R"); use_style("styles/visualisation.R")
        data <- data.frame(x = 1:4, y = 1:4, g = c("a", "a", "b", "b"))
        plot <- ggplot(data, aes(x, y)) + geom_line() + facet_wrap(~g) + labs(y = "value")
        invisible(svglite::svgstring())
        layout <- horizontal_ylab(plot)$layout
        cat(min(layout$t[layout$name == "ylab-l"]) < min(layout$t[startsWith(layout$name, "strip-t")]))
        """,
        built_project,
    )
    assert result.stdout.strip() == "TRUE"


def test_plot_without_y_title_is_left_unchanged(built_project: Path) -> None:
    result = run_r(
        """
        source("scripts/figure_style.R"); use_style("styles/visualisation.R")
        plot <- ggplot(data.frame(x = 1:2, y = 1:2), aes(x, y)) + geom_line() + labs(y = NULL)
        invisible(svglite::svgstring())
        cat(identical(dim(horizontal_ylab(plot)), dim(ggplotGrob(plot))))
        """,
        built_project,
    )
    assert result.stdout.strip() == "TRUE"


def test_missing_figure_argument_is_an_error(built_project: Path) -> None:
    result = subprocess.run(
        [*RSCRIPT, "-e", 'source("scripts/figure_style.R"); figure_arguments(c("--data", "x"))'],
        cwd=built_project, capture_output=True, text=True, env=PROJECT_ENV,
    )
    assert result.returncode != 0
    assert "--style" in result.stderr


@pytest.mark.parametrize("style", ["visualisation", "nature"])
def test_style_sets_every_theme_grey_element(built_project: Path, style: str) -> None:
    """ggplot2 fills any element a theme leaves out from theme_grey(); the style must leave none out."""
    style_file = STACK_ASSETS / "styles" / f"{style}.R"
    result = run_r(
        f"""
        style <- new.env(); sys.source({str(style_file)!r}, envir = style)
        grey <- names(Filter(Negate(is.null), as.list(ggplot2::theme_grey())))
        cat(setdiff(grey, names(style$figure_elements)), sep = "\\n")
        """,
        built_project,
    )
    assert result.stdout.strip() == "", f"{style}.R leaves these to ggplot2 defaults:\n{result.stdout}"


def test_editing_the_style_reruns_every_plot(built_project: Path) -> None:
    style = built_project / "styles" / "visualisation.R"
    style.write_text(style.read_text() + "\n")
    result = run(["uv", "run", "snakemake", "--cores", "1", "--dry-run"], built_project)
    for name in FIGURES:
        assert f"plot_{name}" in result.stdout
    assert "rule summarise" not in result.stdout
    run(["uv", "run", "snakemake", "--cores", "1", "--quiet"], built_project)


def test_600_dpi_option(built_project: Path) -> None:
    run(["uv", "run", "snakemake", "--cores", "1", "--quiet", "--config", "png_dpi=600"], built_project)
    run(["uv", "run", "python", str(CHECKER), "."], built_project)
    run(["uv", "run", "snakemake", "--cores", "1", "--quiet"], built_project)


def test_nature_style_build(tmp_path: Path) -> None:
    root = scaffold(tmp_path / "nature", style="nature")
    config = root / "config.yaml"
    config.write_text(
        config.read_text()
        .replace("styles/visualisation.R", "styles/nature.R")
        .replace("figure_width_mm: 120", "figure_width_mm: 89")
        .replace("figure_height_mm: 80", "figure_height_mm: 60")
    )
    assert_no_warnings(run(["uv", "run", "snakemake", "--cores", "1", "--quiet"], root))
    run(["uv", "run", "python", str(CHECKER), ".", "--size-mm", "89x60", "--up-to-date"], root)
