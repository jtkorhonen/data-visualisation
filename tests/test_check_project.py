# Unit and integration tests for scripts/check_project.py.
# Builds small synthetic projects in temporary folders and checks the reported problems.

import struct
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "data-visualisation"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import check_project  # noqa: E402

MM_PER_INCH = 25.4


def write_png(path: Path, width_mm: float, height_mm: float, dpi: int) -> None:
    """Write a blank grayscale PNG with the given physical size and pHYs resolution."""
    width_px = round(width_mm / MM_PER_INCH * dpi)
    height_px = round(height_mm / MM_PER_INCH * dpi)

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", width_px, height_px, 8, 0, 0, 0, 0)
    pixels_per_metre = round(dpi / 0.0254)
    phys = struct.pack(">IIB", pixels_per_metre, pixels_per_metre, 1)
    rows = b"".join(b"\x00" + b"\xff" * width_px for _ in range(height_px))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"pHYs", phys)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def write_svg(
    path: Path,
    width_mm: float,
    height_mm: float,
    font_sizes=(9,),
    stroke_widths=(0.5,),
    dated: bool = False,
) -> None:
    """Write a minimal Matplotlib-like SVG with the given text and stroke sizes."""
    width_pt = width_mm / MM_PER_INCH * 72
    height_pt = height_mm / MM_PER_INCH * 72
    texts = "".join(
        f'<text style="font-size: {size}px; font-family: \'Arial\'">t</text>'
        for size in font_sizes
    )
    strokes = "".join(
        f'<path style="fill: none; stroke: #000000; stroke-width: {width}"/>'
        for width in stroke_widths
    )
    metadata = "<metadata><dc:date>2026-10-27T00:00:00</dc:date></metadata>" if dated else ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg width="{width_pt:.6f}pt" height="{height_pt:.6f}pt" '
        f'xmlns="http://www.w3.org/2000/svg">{metadata}{texts}{strokes}</svg>'
    )


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A minimal valid project with one 120 x 80 mm figure pair at 450 dpi."""
    root = tmp_path / "project with spaces"
    for folder in ("inputs", "outputs", "scripts", "styles"):
        (root / folder).mkdir(parents=True)
    (root / "styles" / "visualisation.mplstyle").write_text("font.size: 9\n")
    (root / "styles" / "visualisation.yaml").write_text("figure_frame_linewidth: 1.16\n")
    (root / "Snakefile").write_text('STYLE = "styles/visualisation.mplstyle"\n')
    (root / "config.yaml").write_text("png_dpi: 450\n")
    (root / "README.md").write_text("# Project\n")
    (root / "pyproject.toml").write_text("[project]\nname = 'p'\n")
    (root / "uv.lock").write_text("version = 1\n")
    (root / "requirements.txt").write_text("matplotlib==3.11.2\n")
    (root / "scripts" / "plot.py").write_text("import polars as pl\nfrom matplotlib.figure import Figure\n")
    write_png(root / "outputs" / "figures" / "line.png", 120, 80, 450)
    write_svg(root / "outputs" / "figures" / "line.svg", 120, 80)
    return root


def test_valid_project_has_no_problems(project: Path) -> None:
    assert check_project.check(project, size_mm=(120, 80)) == []


def test_missing_layout_items_are_reported(project: Path) -> None:
    (project / "README.md").unlink()
    (project / "uv.lock").unlink()
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("README.md" in p for p in problems)
    assert any("uv.lock" in p for p in problems)


@pytest.mark.parametrize(
    "source",
    [
        "import pandas as pd\n",
        "from pandas import DataFrame\n",
        "import matplotlib.pyplot as plt\n",
        "from matplotlib import pyplot\n",
        "from matplotlib.pyplot import subplots\n",
    ],
)
def test_forbidden_imports_are_reported(project: Path, source: str) -> None:
    (project / "scripts" / "bad.py").write_text(source)
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("bad.py" in p for p in problems)


def test_forbidden_import_in_comment_is_ignored(project: Path) -> None:
    (project / "scripts" / "fine.py").write_text("# import pandas would be wrong here\n")
    assert check_project.check(project, size_mm=(120, 80)) == []


def test_unpaired_figures_are_reported(project: Path) -> None:
    write_png(project / "outputs" / "figures" / "orphan.png", 120, 80, 450)
    write_svg(project / "outputs" / "figures" / "lonely.svg", 120, 80)
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("orphan.svg" in p for p in problems)
    assert any("lonely.png" in p for p in problems)


@pytest.mark.parametrize("dpi", [450, 600])
def test_allowed_png_resolutions_pass(project: Path, dpi: int) -> None:
    write_png(project / "outputs" / "figures" / "line.png", 120, 80, dpi)
    assert check_project.check(project, size_mm=(120, 80)) == []


def test_other_png_resolution_is_reported(project: Path) -> None:
    write_png(project / "outputs" / "figures" / "line.png", 120, 80, 300)
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("300 dpi" in p for p in problems)


def test_wrong_physical_size_is_reported(project: Path) -> None:
    write_png(project / "outputs" / "figures" / "line.png", 100, 80, 450)
    write_svg(project / "outputs" / "figures" / "line.svg", 100, 80)
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("line.png" in p and "mm" in p for p in problems)
    assert any("line.svg" in p and "mm" in p for p in problems)


def test_size_check_can_be_skipped(project: Path) -> None:
    write_png(project / "outputs" / "figures" / "line.png", 89, 60, 450)
    write_svg(project / "outputs" / "figures" / "line.svg", 89, 60)
    assert check_project.check(project, size_mm=None) == []


@pytest.mark.parametrize("size", [4, 15])
def test_font_size_outside_range_is_reported(project: Path, size: float) -> None:
    write_svg(project / "outputs" / "figures" / "line.svg", 120, 80, font_sizes=(9, size))
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("font size" in p for p in problems)


@pytest.mark.parametrize("width", [0.1, 2.0])
def test_stroke_width_outside_range_is_reported(project: Path, width: float) -> None:
    write_svg(project / "outputs" / "figures" / "line.svg", 120, 80, stroke_widths=(0.5, width))
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("stroke width" in p for p in problems)


def test_zero_stroke_width_is_ignored(project: Path) -> None:
    write_svg(project / "outputs" / "figures" / "line.svg", 120, 80, stroke_widths=(0.5, 0))
    assert check_project.check(project, size_mm=(120, 80)) == []


def test_dated_svg_is_reported(project: Path) -> None:
    write_svg(project / "outputs" / "figures" / "line.svg", 120, 80, dated=True)
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("date" in p for p in problems)


def test_style_not_in_snakefile_is_reported(project: Path) -> None:
    (project / "styles" / "nature.mplstyle").write_text("font.size: 7\n")
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("nature.mplstyle" in p for p in problems)


def test_style_sheet_without_sidecar_is_reported(project: Path) -> None:
    (project / "styles" / "visualisation.yaml").unlink()
    problems = check_project.check(project, size_mm=(120, 80))
    assert any("visualisation.yaml" in p for p in problems)


def test_style_named_in_config_counts_as_declared(project: Path) -> None:
    (project / "Snakefile").write_text('configfile: "config.yaml"\nSTYLE = config["style"]\n')
    (project / "config.yaml").write_text("style: styles/visualisation.mplstyle\npng_dpi: 450\n")
    assert check_project.check(project, size_mm=(120, 80)) == []


def test_command_line_reports_success(project: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SKILL_ROOT / "scripts" / "check_project.py"), str(project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout
    assert result.stderr == ""


def test_command_line_reports_failure(project: Path) -> None:
    (project / "Snakefile").unlink()
    result = subprocess.run(
        [sys.executable, str(SKILL_ROOT / "scripts" / "check_project.py"), str(project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Snakefile" in result.stdout


def test_command_line_accepts_custom_size(project: Path) -> None:
    write_png(project / "outputs" / "figures" / "line.png", 89, 60, 450)
    write_svg(project / "outputs" / "figures" / "line.svg", 89, 60)
    result = subprocess.run(
        [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "check_project.py"),
            str(project),
            "--size-mm",
            "89x60",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout
