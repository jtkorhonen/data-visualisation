# End-to-end tests: scaffold a project from assets/python-matplotlib/template, build it with uv and Snakemake,
# and check the outputs with scripts/check_project.py. Needs uv and network or a warm uv cache.

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "data-visualisation"
CHECKER = SKILL_ROOT / "scripts" / "check_project.py"
STACK_ASSETS = SKILL_ROOT / "assets" / "python-matplotlib"
FIGURES = ("measurement_by_day", "measurement_distribution")

pytestmark = pytest.mark.skipif(shutil.which("uv") is None, reason="uv is not installed")


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, f"{args} failed:\n{result.stdout}\n{result.stderr}"
    return result


def scaffold(destination: Path, style: str = "visualisation.mplstyle") -> Path:
    """Copy the template and one bundled style, as SKILL.md instructs."""
    shutil.copytree(STACK_ASSETS / "template", destination)
    (destination / "styles").mkdir(exist_ok=True)
    shutil.copy(STACK_ASSETS / "styles" / style, destination / "styles" / style)
    run(["uv", "sync", "--quiet"], destination)
    run(
        ["uv", "export", "--quiet", "--format", "requirements.txt", "--no-emit-project",
         "--output-file", "requirements.txt"],
        destination,
    )
    return destination


def assert_no_warnings(result: subprocess.CompletedProcess) -> None:
    output = result.stdout + result.stderr
    for marker in ("Warning", "WARNING", "findfont", "Traceback"):
        assert marker not in output, output


@pytest.fixture(scope="module")
def built_project(tmp_path_factory) -> Path:
    root = scaffold(tmp_path_factory.mktemp("e2e") / "project with spaces")
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


def test_editing_a_plot_script_reruns_only_its_rule(built_project: Path) -> None:
    script = built_project / "scripts" / "plot_measurement_by_day.py"
    script.write_text(script.read_text() + "\n")
    result = run(["uv", "run", "snakemake", "--cores", "1", "--dry-run"], built_project)
    assert "plot_measurement_by_day" in result.stdout
    assert "plot_measurement_distribution" not in result.stdout
    run(["uv", "run", "snakemake", "--cores", "1", "--quiet"], built_project)


def test_600_dpi_option(tmp_path: Path) -> None:
    root = scaffold(tmp_path / "high dpi")
    run(["uv", "run", "snakemake", "--cores", "1", "--quiet", "--config", "png_dpi=600"], root)
    run(["uv", "run", "python", str(CHECKER), "."], root)
    png = (root / "outputs" / "figures" / "measurement_by_day.png").read_bytes()
    assert b"pHYs" in png
    result = run(["uv", "run", "snakemake", "--cores", "1", "--dry-run", "--config", "png_dpi=600"], root)
    assert "Nothing to be done" in result.stdout + result.stderr


def test_unsupported_dpi_is_rejected(tmp_path: Path) -> None:
    root = scaffold(tmp_path / "bad dpi")
    result = subprocess.run(
        ["uv", "run", "snakemake", "--cores", "1", "--dry-run", "--config", "png_dpi=300"],
        cwd=root, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "png_dpi" in result.stdout + result.stderr


def test_nature_style_build(tmp_path: Path) -> None:
    root = scaffold(tmp_path / "nature", style="nature.mplstyle")
    config = root / "config.yaml"
    config.write_text(
        config.read_text()
        .replace("styles/visualisation.mplstyle", "styles/nature.mplstyle")
        .replace("figure_width_mm: 120", "figure_width_mm: 89")
        .replace("figure_height_mm: 80", "figure_height_mm: 60")
    )
    assert_no_warnings(run(["uv", "run", "snakemake", "--cores", "1", "--quiet"], root))
    run(["uv", "run", "python", str(CHECKER), ".", "--size-mm", "89x60", "--up-to-date"], root)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="fallback needs Python 3.14+")
def test_venv_fallback_from_exported_requirements(tmp_path: Path) -> None:
    root = scaffold(tmp_path / "venv fallback")
    shutil.rmtree(root / ".venv")
    run([sys.executable, "-m", "venv", ".venv"], root)
    python = root / ".venv" / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--quiet", "-r", "requirements.txt"], root)
    assert_no_warnings(run([str(root / ".venv" / "bin" / "snakemake"), "--cores", "1", "--quiet"], root))
    run([str(python), str(CHECKER), ".", "--up-to-date"], root)
