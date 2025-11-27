#!/usr/bin/env python3
"""Example usage of load_cleaned.py: scatter plot wind speed (61101) over time."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from itertools import cycle

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, YearLocator

from load_cleaned import load_nearby_daily


def main() -> None:
    records = load_nearby_daily(
        county_site_id="035-3014",  # Lake Park (Salt Lake County)
        max_backup_radius=0.25,
        params=("61101", "81102", "88101"),  # request wind + PM parameters
    )

    if not records:
        print("No records returned; check cleaned_data directory or parameters.")
        return

    # Collect wind speed by site so each site can be colored independently.
    by_site = defaultdict(list)
    for rec in records:
        date = datetime.fromisoformat(rec["date_local"])
        wind_speed = rec["readings"]["61101"]
        by_site[rec["site_id"]].append((date, wind_speed))

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = cycle(plt.get_cmap("tab20").colors)

    for site_id, points in sorted(by_site.items()):
        points.sort(key=lambda p: p[0])
        dates, wind_speeds = zip(*points)
        ax.scatter(dates, wind_speeds, s=12, color=next(colors), label=site_id)

    ax.set_title("Wind Speed (61101) by Nearby Sites")
    ax.set_xlabel("Date")
    ax.set_ylabel("Wind speed")
    ax.legend(title="Site ID", markerscale=1.2)
    ax.grid(True, alpha=0.3)

    # Label x-axis ticks once per year.
    ax.xaxis.set_major_locator(YearLocator(1))
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
