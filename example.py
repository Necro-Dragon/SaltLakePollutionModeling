from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, YearLocator

from data_loading_utils import add_surface_area_features, load_nearby_daily


def main() -> None:
    records = load_nearby_daily(
        county_site_id="035-3014",  # Lake Park (Salt Lake County)
        max_backup_radius=0.25,
        params=("61101", "81102", "88101"),  # request wind + PM parameters
    )
    # Attach lake-surface features (north/south areas + volumes) by date.
    records = add_surface_area_features(records)

    if not records:
        print("No records returned; check cleaned_data directory or parameters.")
        return

    sample = records[0]
    print(
        "Sample record with surface areas:",
        sample["date_local"],
        f"north_area_ft2={sample.get('north_area_ft2')}",
        f"south_area_ft2={sample.get('south_area_ft2')}",
    )

    # Build three aligned series: wind speed (61101), PM2.5 (88101), north/south surface area.
    series = []
    for rec in records:
        date = datetime.fromisoformat(rec["date_local"])
        wind = rec["readings"].get("61101")
        pm25 = rec["readings"].get("88101")
        north_area = rec.get("north_area_ft2")
        south_area = rec.get("south_area_ft2")
        if wind is None or pm25 is None or north_area is None or south_area is None:
            continue
        series.append((date, wind, pm25, north_area, south_area))
    if not series:
        print("No records with complete wind/pm25/north+south area data.")
        return
    series.sort(key=lambda x: x[0])
    dates, winds, pm25s, north_areas, south_areas = zip(*series)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    axes[0].scatter(dates, winds, s=10, color="#1f77b4")
    axes[0].set_ylabel("Wind speed")
    axes[0].grid(True, alpha=0.3)

    axes[1].scatter(dates, pm25s, s=10, color="#d62728")
    axes[1].set_ylabel("PM2.5 (µg/m³)")
    axes[1].grid(True, alpha=0.3)

    axes[2].scatter(dates, south_areas, s=10, color="#2ca02c", label="South")
    axes[2].scatter(dates, north_areas, s=10, color="#9467bd", label="North", alpha=0.7)
    axes[2].set_ylabel("Surface area (ft²)")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    axes[2].set_xlabel("Date")

    for ax in axes:
        ax.xaxis.set_major_locator(YearLocator(1))
        ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    fig.suptitle("Daily wind, PM2.5, and north/south surface area")
    fig.autofmt_xdate()
    plt.tight_layout(rect=(0, 0, 1, 0.97))
    plt.show()


if __name__ == "__main__":
    main()
