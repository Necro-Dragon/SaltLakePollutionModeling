import csv
import math
from datetime import datetime
from pathlib import Path

site_coords = {
    "005-0002": (41.732987, -111.836333),
    "005-0004": (41.731111, -111.8375),
    "005-0005": (41.8594, -111.8952),
    "005-0006": (41.63546, -111.86819),
    "005-0007": (41.842649, -111.852199),
    "011-0001": (40.886389, -111.882222),
    "011-0004": (40.902967, -111.884467),
    "011-6001": (41.041609, -112.233281),
    "011-6002": (41.088554, -112.117167),
    "035-0003": (40.646667, -111.849722),
    "035-0010": (40.758333, -111.898056),
    "035-0012": (40.8075, -111.921111),
    "035-1001": (40.708611, -112.094722),
    "035-1006": (40.709668, -112.086886),
    "035-1007": (40.712146, -112.111275),
    "035-2003": (40.734111, -112.209112),
    "035-2004": (40.736389, -112.210278),
    "035-2005": (40.598056, -111.894167),
    "035-3001": (40.755278, -111.885556),
    "035-3003": (40.518056, -112.022222),
    "035-3004": (40.616614, -111.99855),
    "035-3005": (40.807723, -112.048831),
    "035-3006": (40.736389, -111.872222),
    "035-3007": (40.704444, -111.968611),
    "035-3008": (40.517946, -112.023051),
    "035-3009": (40.614733, -112.000267),
    "035-3010": (40.78422, -111.931),
    "035-3013": (40.496392, -112.036298),
    "035-3014": (40.709762, -112.00876),
    "035-3015": (40.777145, -111.945849),
    "035-3016": (40.807897, -112.087717),
    "035-3018": (40.766528, -111.82835),
    "035-4002": (40.662961, -111.901851),
    "049-0002": (40.253611, -111.663056),
    "049-2001": (40.359674, -111.726317),
    "049-4001": (40.341389, -111.713611),
    "049-5001": (40.303611, -111.722778),
    "049-5002": (40.313565, -111.657145),
    "049-5004": (40.31162, -111.700481),
    "049-5005": (40.268889, -111.681944),
    "049-5006": (40.164956, -111.611309),
    "049-5007": (40.180556, -111.606944),
    "049-5008": (40.430278, -111.803889),
    "049-5010": (40.136378, -111.657936),
    "049-6003": (40.294397, -111.73604),
    "051-0001": (40.497962, -111.39763),
    "057-0001": (41.219167, -111.972778),
    "057-0002": (41.206321, -111.975524),
    "057-0007": (41.179722, -111.983056),
    "057-1001": (41.171944, -112.031667),
    "057-1002": (41.305, -111.965278),
    "057-1003": (41.303614, -111.987871),
}

BASE = Path(__file__).resolve().parent / "cleaned_data"
SURFACE_AREAS_PATH = BASE / "surface_areas" / "surfaces_areas.csv"
counties_needed = sorted({sid.split("-")[0] for sid in site_coords})
SITE_INFO = {sid: {"latitude": lat, "longitude": lon} for sid, (lat, lon) in site_coords.items()}


def load_nearby_daily(county_site_id="035-3014", max_backup_radius=0.25, params=None):
    """Return daily records with the nearest site that has all params."""
    if params is None:
        params = ["61101", "81102", "88101"]
    if county_site_id not in site_coords:
        raise ValueError(f"Unknown county_site_id: {county_site_id}")

    center = SITE_INFO[county_site_id]
    nearby = []
    for sid, info in SITE_INFO.items():
        dist = math.hypot(info["latitude"] - center["latitude"], info["longitude"] - center["longitude"])
        if dist <= max_backup_radius or sid == county_site_id:
            nearby.append((sid, dist if sid != county_site_id else 0.0))
    if county_site_id not in {sid for sid, _ in nearby}:
        nearby.append((county_site_id, 0.0))
    nearby.sort(key=lambda x: x[1])
    candidate_sites = {sid for sid, _ in nearby}

    param_data = {p: {} for p in params}
    for county in counties_needed:
        for param in params:
            csv_path = BASE / county / param / "data.csv"
            if not csv_path.exists():
                continue
            with csv_path.open() as fh:
                for row in csv.DictReader(fh):
                    site_id = row.get("county_site_id")
                    if site_id not in candidate_sites:
                        continue
                    date = row.get("date_local")
                    try:
                        val = float(row.get("arithmetic_mean", ""))
                    except (TypeError, ValueError):
                        continue
                    param_data[param][(site_id, date)] = val

    all_dates = set()
    for param in params:
        all_dates.update(date for (_, date) in param_data[param].keys())

    results = []
    for date in sorted(all_dates):
        for sid, dist in nearby:
            readings = {}
            for param in params:
                val = param_data[param].get((sid, date))
                if val is None:
                    readings = None
                    break
                readings[param] = val
            if readings is not None:
                results.append({"date_local": date, "site_id": sid, "readings": readings, "source_distance_deg": dist})
                break
    return results


def _load_surface_areas(path=SURFACE_AREAS_PATH):
    """Load date -> {north/south areas and volumes}."""
    surface = {}
    if not path.is_file():
        return surface
    with path.open() as fh:
        for row in csv.DictReader(fh):
            date = row.get("date")
            if not date:
                continue
            try:
                n_area = float(row.get("north_area_ft2", ""))
                s_area = float(row.get("south_area_ft2", ""))
            except (TypeError, ValueError):
                continue  # require both areas to keep the date
            features = {
                "north_area_ft2": n_area,
                "south_area_ft2": s_area,
            }
            # volumes optional but attach if present
            for key in ("north_volume_ft3", "south_volume_ft3"):
                try:
                    features[key] = float(row.get(key, ""))
                except (TypeError, ValueError):
                    pass
            surface[date] = features
    return surface


def add_surface_area_features(records, surface_csv_path=SURFACE_AREAS_PATH):
    """Merge precomputed surface areas/volumes into records by date.

    If a date lacks either north/south area, the record is dropped (mirrors the
    all-or-nothing param requirement used in load_nearby_daily).
    """
    surface = _load_surface_areas(surface_csv_path)
    enriched = []
    for rec in records:
        merged = dict(rec)
        features = surface.get(rec.get("date_local"))
        if not features:
            continue  # skip dates without both surface areas
        merged.update(features)
        enriched.append(merged)
    return enriched


def load_windspeed_and_pm10(start_date, end_date, county_site_id="035-3014"):
    """Return (windspeed list, PM10 list) between start_date and end_date (inclusive)."""
    records = load_nearby_daily(county_site_id=county_site_id, max_backup_radius=0.25, params=["61101", "81102"])
    if not records:
        return [], []
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    series = []
    for rec in records:
        d = datetime.fromisoformat(rec["date_local"])
        if start <= d <= end:
            readings = rec["readings"]
            if "61101" in readings and "81102" in readings:
                series.append((d, readings["61101"], readings["81102"]))
    series.sort(key=lambda x: x[0])
    return [w for _, w, _ in series], [p for _, _, p in series]


if __name__ == "__main__":
    sample = add_surface_area_features(load_nearby_daily())
    print(f"Loaded {len(sample)} records with surface-area features")
    if sample:
        print("Sample record:", sample[0])
