# Validates the measurement table and writes per-group summary statistics.
# Missing values are counted, not filled, so the summary shows how many observations are absent.

import argparse
from pathlib import Path

import polars as pl

EXPECTED_SCHEMA = {"day": pl.Int64, "group": pl.String, "value": pl.Float64}


def load_measurements(path: Path) -> pl.DataFrame:
    """Load the measurement table and fail early if its columns or types are unexpected."""
    data = pl.read_csv(path, schema=EXPECTED_SCHEMA)
    duplicates = data.filter(pl.struct("day", "group").is_duplicated())
    if duplicates.height:
        raise ValueError(f"duplicate day/group rows in {path}:\n{duplicates}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise measurements per group")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = (
        load_measurements(args.data)
        .group_by("group")
        .agg(
            pl.len().alias("rows"),
            pl.col("value").null_count().alias("missing"),
            pl.col("value").mean().alias("mean"),
            pl.col("value").std().alias("sd"),
        )
        .sort("group")
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.write_csv(args.output)


if __name__ == "__main__":
    main()
