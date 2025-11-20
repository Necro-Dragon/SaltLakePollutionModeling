#!/usr/bin/env python3
"""Load arithmetic_mean/date_local tuples for a single Davis County 2025 parameter."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DAILY_DIR = SCRIPT_DIR / "davis_2025" / "dailyData"

MeanDateTuple = tuple[float, str]


def load_mean_date_pairs(
    param_code: str,
    year: int = 2025,
    site_number: str = "0004",  # 0004 default is Bountiful
    sample_duration: str | None = None,
    daily_dir: Path = DEFAULT_DAILY_DIR,
) -> list[MeanDateTuple]:
    """
    Return (arithmetic_mean, date_local) tuples for a specific parameter code, filtered to site 0004.
    Optionally filter by sample_duration (e.g., "24-HR BLK AVG").
    """
    path = Path(daily_dir, param_code, f"{param_code}_{year}.json")
    if not path.is_file():
        raise FileNotFoundError(f"Daily data file not found: {path}")

    rows = json.loads(path.read_text()).get("Data", []) or []
    if sample_duration:
        rows = [row for row in rows if row.get("sample_duration") == sample_duration]

    # Deduplicate rows that only vary by pollutant_standard (keep first by file order).
    key_fields = ("date_local", "site_number", "parameter_code", "poc", "sample_duration", "arithmetic_mean")
    deduped = {}
    for row in rows:
        key = tuple(row.get(k) for k in key_fields)
        if key not in deduped:
            deduped[key] = row

    filtered_rows = [
        row
        for row in deduped.values()
        if row.get("site_number") == site_number and "arithmetic_mean" in row and "date_local" in row
    ]

    # If multiple POCs report the same day, average them so we emit one value per date (remove duplicates).
    by_date: dict[str, list[float]] = {}
    for row in filtered_rows:
        date = row["date_local"]
        by_date.setdefault(date, []).append(float(row["arithmetic_mean"]))

    return [(sum(vals) / len(vals), date) for date, vals in sorted(by_date.items())]


if __name__ == "__main__":
    wind_speed = load_mean_date_pairs("61101", 2025, "0004")  # Wind Speed - Scalar
    pm25 = load_mean_date_pairs("88101", sample_duration="24-HR BLK AVG")  # PM2.5 - Local Conditions
    pm10 = load_mean_date_pairs("81102")  # PM10 Total 0-10um

    print("\nArithmetic mean/date tuples (mean, date_local):")
    for label, pairs in [
        ("wind_speed", wind_speed),
        ("pm25", pm25),
        ("pm10", pm10),
    ]:
        print(f"  {label}: {len(pairs)} tuples; sample {pairs[:3]}")

    # Plot three vertically stacked panels: wind speed (knots), PM2.5, PM10. X-axis shows months.
    import matplotlib.pyplot as plt
    from matplotlib.dates import MonthLocator, DateFormatter

    def to_xy(pairs: list[MeanDateTuple]) -> tuple[list[datetime], list[float]]:
        dates = [datetime.fromisoformat(date) for _, date in pairs]
        values = [mean for mean, _ in pairs]
        return dates, values

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    plots = [
        ("Wind Speed (knots)", wind_speed, "#1f77b4"),
        ("PM2.5 (µg/m³)", pm25, "#d62728"),
        ("PM10 (µg/m³)", pm10, "#2ca02c"),
    ]
    for ax, (label, pairs, color) in zip(axes, plots):
        x, y = to_xy(pairs)
        ax.plot(x, y, color=color, linewidth=1.4)
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.3)

    month_locator = MonthLocator()
    axes[-1].xaxis.set_major_locator(month_locator)
    axes[-1].xaxis.set_major_formatter(DateFormatter("%b"))
    axes[-1].set_xlabel("Month")
    fig.suptitle("Daily Measurements in 2025 by Parameter")
    plt.tight_layout(rect=(0, 0, 1, 0.97))
    plt.show()
