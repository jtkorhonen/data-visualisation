# Line chart of the measured value per day for each group.
# Groups are told apart by line style and direct labels; missing days stay as gaps.

import polars as pl

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
    args = figure_arguments("Plot measurement by day").parse_args()
    data = load_measurements(args.data).sort("group", "day")

    with style_context(args.style) as style:
        figure, axes = new_figure(args.width_mm, args.height_mm, style)
        for (group,), rows in data.group_by("group", maintain_order=True):
            days = rows["day"].to_numpy()
            values = rows["value"].fill_null(float("nan")).to_numpy()
            (line,) = axes.plot(days, values, marker="o", label=group)
            last = rows.filter(pl.col("value").is_not_null()).tail(1)
            axes.annotate(
                group,
                xy=(last["day"][0], last["value"][0]),
                xytext=(4, 0),
                textcoords="offset points",
                va="center",
                color=line.get_color(),
            )
        axes.set_xlabel("day")
        set_horizontal_ylabel(axes, "value (a.u.)", style)
        set_title_above_ylabel(axes, "Measurement by day", style)
        save_figure(figure, args.png, args.svg, args.dpi)


if __name__ == "__main__":
    main()
