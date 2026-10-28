# Box plot of the measured value for each group, drawn with Seaborn on an explicit axes.
# Polars stays the data API; Seaborn receives plain NumPy arrays at the plotting boundary.

import polars as pl
import seaborn as sns

from figure_style import (
    figure_arguments,
    new_figure,
    save_figure,
    set_horizontal_ylabel,
    set_title_above_ylabel,
    style_context,
)
from summarise import load_measurements


def main() -> None:
    args = figure_arguments("Plot measurement distribution").parse_args()
    observed = load_measurements(args.data).filter(pl.col("value").is_not_null()).sort("group")

    with style_context(args.style):
        figure, axes = new_figure(args.width_mm, args.height_mm)
        sns.boxplot(
            x=observed["group"].to_numpy(),
            y=observed["value"].to_numpy(),
            ax=axes,
            color="white",
            linecolor="black",
            fliersize=2,
            width=0.5,
            showcaps=False,
        )
        axes.set_xlabel("group")
        set_horizontal_ylabel(axes, "value (a.u.)")
        set_title_above_ylabel(axes, "Measurement distribution")
        save_figure(figure, args.png, args.svg, args.dpi)


if __name__ == "__main__":
    main()
