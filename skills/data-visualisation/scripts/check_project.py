# Checks a visualisation project against the mechanical parts of the skill's contract.
# Standard library only, so it runs with any Python 3.14+ interpreter, including the project's own.

import argparse
import ast
import re
import struct
import subprocess
import sys
from pathlib import Path

MM_PER_INCH = 25.4
POINTS_PER_INCH = 72
ALLOWED_PNG_DPI = (450, 600)
FONT_SIZE_RANGE_PT = (5, 14)
STROKE_WIDTH_RANGE_PT = (0.25, 1.5)
SIZE_TOLERANCE_MM = 0.5
REQUIRED_PATHS = (
    "inputs",
    "outputs",
    "scripts",
    "styles",
    "Snakefile",
    "config.yaml",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    "requirements.txt",
)
FORBIDDEN_MODULES = ("pandas", "matplotlib.pyplot")
# R projects keep their packages in DESCRIPTION, locked by renv and activated by .Rprofile.
REQUIRED_R_PATHS = ("DESCRIPTION", "renv.lock", ".Rprofile", "renv/activate.R")
# plyr is retired and masks dplyr functions when both are loaded.
FORBIDDEN_R_PACKAGES = ("plyr",)
STYLE_PATTERNS = ("*.mplstyle", "*.R")
# Written by R's default device when a plot is laid out before an output device is open.
STRAY_FILES = ("Rplots.pdf",)


def is_r_project(root: Path) -> bool:
    return any((root / "scripts").rglob("*.R"))


def check_layout(root: Path) -> list[str]:
    required = REQUIRED_PATHS + (REQUIRED_R_PATHS if is_r_project(root) else ())
    problems = [f"missing required path: {name}" for name in required if not (root / name).exists()]
    problems += [
        f"{name}: stray file from R's default graphics device; open the output device first"
        for name in STRAY_FILES
        if (root / name).exists()
    ]
    return problems


def _imported_modules(tree: ast.AST) -> set[str]:
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            modules.update(f"{node.module}.{alias.name}" for alias in node.names)
    return modules


def check_imports(root: Path) -> list[str]:
    problems = []
    for script in sorted((root / "scripts").rglob("*.py")):
        modules = _imported_modules(ast.parse(script.read_text(), filename=str(script)))
        for forbidden in FORBIDDEN_MODULES:
            if any(m == forbidden or m.startswith(forbidden + ".") for m in modules):
                problems.append(f"{script.relative_to(root)}: imports {forbidden}")
    return problems


def _r_code_without_comments(text: str) -> str:
    """Drop # comments; good enough for package references, which never sit inside strings."""
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def check_r_packages(root: Path) -> list[str]:
    problems = []
    for script in sorted((root / "scripts").rglob("*.R")):
        code = _r_code_without_comments(script.read_text())
        for package in FORBIDDEN_R_PACKAGES:
            loaded = re.search(rf"\b(library|require)\(\s*['\"]?{package}['\"]?\s*\)", code)
            if loaded or re.search(rf"\b{package}::", code):
                problems.append(f"{script.relative_to(root)}: uses {package}")
    return problems


def check_figure_pairs(root: Path) -> list[str]:
    problems = []
    for figure in sorted((root / "outputs").rglob("*")):
        partner_suffix = {".png": ".svg", ".svg": ".png"}.get(figure.suffix)
        if partner_suffix and not figure.with_suffix(partner_suffix).exists():
            partner = figure.with_suffix(partner_suffix).relative_to(root)
            problems.append(f"{figure.relative_to(root)}: missing partner {partner}")
    return problems


def _png_size_and_dpi(path: Path) -> tuple[int, int, float | None]:
    data = path.read_bytes()
    width_px, height_px = struct.unpack(">II", data[16:24])
    offset = 8
    while offset < len(data):
        length, kind = struct.unpack(">I4s", data[offset : offset + 8])
        if kind == b"pHYs":
            x_per_unit, _, unit = struct.unpack(">IIB", data[offset + 8 : offset + 17])
            return width_px, height_px, x_per_unit * 0.0254 if unit == 1 else None
        if kind == b"IDAT":
            break
        offset += 12 + length
    return width_px, height_px, None


def _size_problem(name: str, width_mm: float, height_mm: float, size_mm) -> list[str]:
    if size_mm is None:
        return []
    expected_w, expected_h = size_mm
    if abs(width_mm - expected_w) > SIZE_TOLERANCE_MM or abs(height_mm - expected_h) > SIZE_TOLERANCE_MM:
        return [f"{name}: size is {width_mm:.1f} x {height_mm:.1f} mm, expected {expected_w:g} x {expected_h:g} mm"]
    return []


def check_png(path: Path, root: Path, size_mm) -> list[str]:
    name = str(path.relative_to(root))
    width_px, height_px, dpi = _png_size_and_dpi(path)
    if dpi is None:
        return [f"{name}: no resolution (pHYs) recorded"]
    dpi = round(dpi)
    if dpi not in ALLOWED_PNG_DPI:
        return [f"{name}: {dpi} dpi, expected one of {ALLOWED_PNG_DPI}"]
    return _size_problem(name, width_px / dpi * MM_PER_INCH, height_px / dpi * MM_PER_INCH, size_mm)


def check_svg(path: Path, root: Path, size_mm) -> list[str]:
    name = str(path.relative_to(root))
    text = path.read_text()
    problems = []
    size = re.search(r"""<svg[^>]*\swidth=["']([\d.]+)pt["'][^>]*\sheight=["']([\d.]+)pt["']""", text)
    if size is None:
        problems.append(f"{name}: no width/height in points")
    else:
        width_mm, height_mm = (float(v) / POINTS_PER_INCH * MM_PER_INCH for v in size.groups())
        problems += _size_problem(name, width_mm, height_mm, size_mm)

    low, high = FONT_SIZE_RANGE_PT
    for value in sorted({float(v) for v in re.findall(r"font-size:\s*([\d.]+)px", text)}):
        if not low <= value <= high:
            problems.append(f"{name}: font size {value:g} pt outside {low}-{high} pt")

    low, high = STROKE_WIDTH_RANGE_PT
    for value in sorted({float(v) for v in re.findall(r"stroke-width:\s*([\d.]+)", text)}):
        if value and not low <= value <= high:
            problems.append(f"{name}: stroke width {value:g} pt outside {low}-{high} pt")

    if "<dc:date>" in text:
        problems.append(f"{name}: contains a creation date, so it changes on every run")
    return problems


def check_figures(root: Path, size_mm) -> list[str]:
    problems = check_figure_pairs(root)
    for path in sorted((root / "outputs").rglob("*.png")):
        problems += check_png(path, root, size_mm)
    for path in sorted((root / "outputs").rglob("*.svg")):
        problems += check_svg(path, root, size_mm)
    return problems


def check_styles_declared(root: Path) -> list[str]:
    """Each style sheet must be named in the Snakefile or in the config it loads."""
    text = "".join(
        (root / name).read_text() for name in ("Snakefile", "config.yaml") if (root / name).exists()
    )
    styles = sorted(path for pattern in STYLE_PATTERNS for path in (root / "styles").glob(pattern))
    return [
        f"{style.relative_to(root)}: not referenced in the Snakefile or config.yaml"
        for style in styles
        if style.name not in text
    ]


def check_style_sidecars(root: Path) -> list[str]:
    """Each style sheet needs its YAML sidecar for the settings a style sheet cannot express."""
    return [
        f"{style.relative_to(root)}: missing sidecar {style.with_suffix('.yaml').relative_to(root)}"
        for style in sorted((root / "styles").glob("*.mplstyle"))
        if not style.with_suffix(".yaml").exists()
    ]


def check_up_to_date(root: Path) -> list[str]:
    """Run a Snakemake dry run with the interpreter's own Snakemake and expect no jobs."""
    snakemake = Path(sys.executable).parent / "snakemake"
    result = subprocess.run(
        [str(snakemake), "--cores", "1", "--dry-run", "--quiet"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        return [f"snakemake dry run failed:\n{output}"]
    if "Nothing to be done" not in output:
        return [f"snakemake dry run would still run jobs:\n{output}"]
    return []


def check(root: Path, size_mm, up_to_date: bool = False) -> list[str]:
    root = root.resolve()
    problems = check_layout(root)
    if (root / "scripts").is_dir():
        problems += check_imports(root)
        problems += check_r_packages(root)
    if (root / "outputs").is_dir():
        problems += check_figures(root, size_mm)
    if (root / "styles").is_dir():
        problems += check_styles_declared(root)
        problems += check_style_sidecars(root)
    if up_to_date:
        problems += check_up_to_date(root)
    return problems


def parse_size(value: str):
    if value == "any":
        return None
    width, height = value.lower().split("x")
    return float(width), float(height)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a visualisation project against the skill contract.")
    parser.add_argument("project", type=Path, help="project root folder")
    parser.add_argument(
        "--size-mm",
        type=parse_size,
        default=(120.0, 80.0),
        help="expected figure size as WIDTHxHEIGHT in mm, or 'any' (default: 120x80)",
    )
    parser.add_argument(
        "--up-to-date",
        action="store_true",
        help="also require a Snakemake dry run to report nothing to do",
    )
    args = parser.parse_args()
    problems = check(args.project, args.size_mm, up_to_date=args.up_to_date)
    for problem in problems:
        print(f"FAIL: {problem}")
    if problems:
        return 1
    figures = len(list((args.project / "outputs").rglob("*.png")))
    print(f"OK: project layout and {figures} figure pair(s) pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
