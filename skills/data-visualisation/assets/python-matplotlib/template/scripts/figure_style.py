# Shared figure helpers: isolated style loading, physical sizing, horizontal y-labels and export.
# Every plotting script uses these so typography and export settings stay consistent.

import argparse
from pathlib import Path

import matplotlib.style
from matplotlib.axes import Axes
from matplotlib.figure import Figure

MM_PER_INCH = 25.4


def figure_arguments(description: str) -> argparse.ArgumentParser:
    """Command-line arguments shared by all plotting scripts; the Snakefile fills them in."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--style", type=Path, required=True)
    parser.add_argument("--png", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--dpi", type=int, required=True)
    parser.add_argument("--width-mm", type=float, required=True)
    parser.add_argument("--height-mm", type=float, required=True)
    return parser


def style_context(style_path: Path):
    """Reset to Matplotlib defaults, then apply the project style.

    Starting from "default" means a user-level matplotlibrc cannot change the output.
    """
    return matplotlib.style.context(["default", str(style_path)])


def new_figure(width_mm: float, height_mm: float) -> tuple[Figure, Axes]:
    """One axes on a figure of exact physical size, without pyplot.

    The figure frame is drawn in the style's figure.edgecolor at its patch.linewidth;
    Matplotlib has no style setting for the frame width itself.
    """
    figure = Figure(
        figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
        layout="constrained",
        linewidth=matplotlib.rcParams["patch.linewidth"],
    )
    return figure, figure.add_subplot()


def set_horizontal_ylabel(axes: Axes, text: str) -> None:
    """Place the y-axis label horizontally above the top-left corner of the axes."""
    axes.set_ylabel(text, rotation=0, loc="top", labelpad=6)
    axes.yaxis.label.set_horizontalalignment("left")
    axes.yaxis.label.set_verticalalignment("bottom")


def set_title_above_ylabel(axes: Axes, text: str) -> None:
    """Add a title with enough padding (in points) to clear a horizontal y-label."""
    label_height = axes.yaxis.label.get_fontsize()
    axes.set_title(text, pad=label_height * 2)


def save_figure(figure: Figure, png: Path, svg: Path, dpi: int) -> None:
    """Write PNG and SVG without timestamps so identical inputs give identical files."""
    png.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(png, format="png", dpi=dpi, metadata={"Software": None})
    figure.savefig(svg, format="svg", metadata={"Date": None})
