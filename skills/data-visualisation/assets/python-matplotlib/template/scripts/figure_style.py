# Shared figure helpers: isolated style loading, physical sizing, horizontal y-labels and export.
# Every style value comes from the project's style sheet and its YAML sidecar, never from this file.

import argparse
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import matplotlib.style
import yaml
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


@dataclass(frozen=True)
class FigureStyle:
    """Style settings a Matplotlib style sheet cannot express, read from its YAML sidecar.

    Lengths are in points. A missing or unknown key in the sidecar is an error.
    """

    figure_frame_linewidth: float
    ylabel_rotation: float
    ylabel_labelpad: float
    ylabel_horizontal_alignment: str
    ylabel_vertical_alignment: str
    title_pad_in_ylabel_heights: float


@contextmanager
def style_context(style_path: Path) -> Iterator[FigureStyle]:
    """Reset to Matplotlib defaults, apply the project style sheet, and yield its sidecar settings.

    Starting from "default" means a user-level matplotlibrc cannot change the output.
    The sidecar is the style sheet's path with a .yaml suffix.
    """
    sidecar = yaml.safe_load(style_path.with_suffix(".yaml").read_text())
    with matplotlib.style.context(["default", str(style_path)]):
        yield FigureStyle(**sidecar)


def new_figure(width_mm: float, height_mm: float, style: FigureStyle) -> tuple[Figure, Axes]:
    """One axes on a figure of exact physical size, without pyplot.

    The figure frame is drawn in the style sheet's figure.edgecolor at the sidecar's width;
    Matplotlib has no style setting for the frame width itself.
    """
    figure = Figure(
        figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
        layout="constrained",
        linewidth=style.figure_frame_linewidth,
    )
    return figure, figure.add_subplot()


def set_horizontal_ylabel(axes: Axes, text: str, style: FigureStyle) -> None:
    """Place the y-axis label horizontally above the top-left corner of the axes.

    The position along the axis comes from yaxis.labellocation in the style sheet.
    """
    axes.set_ylabel(text, rotation=style.ylabel_rotation, labelpad=style.ylabel_labelpad)
    axes.yaxis.label.set_horizontalalignment(style.ylabel_horizontal_alignment)
    axes.yaxis.label.set_verticalalignment(style.ylabel_vertical_alignment)


def set_title_above_ylabel(axes: Axes, text: str, style: FigureStyle) -> None:
    """Add a title with enough padding (in points) to clear a horizontal y-label."""
    label_height = axes.yaxis.label.get_fontsize()
    axes.set_title(text, pad=label_height * style.title_pad_in_ylabel_heights)


def save_figure(figure: Figure, png: Path, svg: Path, dpi: int) -> None:
    """Write PNG and SVG without timestamps so identical inputs give identical files."""
    png.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(png, format="png", dpi=dpi, metadata={"Software": None})
    figure.savefig(svg, format="svg", metadata={"Date": None})
