import csv
import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR / "cleaned_data"
DEFAULT_PARAMS = ("61101", "81102", "88101")

SITE_COORDS = {
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

SITE_INFO = {
    site_id: {
        "latitude": lat,
        "longitude": lon,
        "county_code": site_id.split("-")[0],
        "site_number": site_id.split("-")[1],
    }
    for site_id, (lat, lon) in SITE_COORDS.items()
}

def _distance(site_a: Dict[str, float], site_b: Dict[str, float]) -> float:
    return math.hypot(site_a["latitude"] - site_b["latitude"], site_a["longitude"] - site_b["longitude"])


def _nearby_sites(site_info: Dict[str, Dict[str, str]], center_id: str, radius: float) -> List[Tuple[str, float]]:
    center = site_info[center_id]
    nearby = []
    for sid, info in site_info.items():
        d = _distance(center, info)
        if d <= radius:
            nearby.append((sid, d))
    # ensure the center site is included even if radius==0
    if center_id not in {sid for sid, _ in nearby}:
        nearby.append((center_id, 0.0))
    nearby.sort(key=lambda x: x[1])
    return nearby


def _load_param_data(base: Path, county_codes: Sequence[str], param_codes: Sequence[str], candidate_sites: set):
    """
    Return nested mapping param -> {(site_id, date): value} for the counties of interest.
    Only keep rows for candidate_sites.
    """
    data = {p: {} for p in param_codes}
    for county in county_codes:
        for param in param_codes:
            csv_path = base / county / param / "data.csv"
            if not csv_path.exists():
                continue
            with csv_path.open() as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    site_id = row["county_site_id"]
                    if site_id not in candidate_sites:
                        continue
                    key = (site_id, row["date_local"])
                    try:
                        val = float(row["arithmetic_mean"])
                    except ValueError:
                        continue
                    data[param][key] = val
    return data




def load_nearby_daily(
    county_site_id: Optional[str] = "035-3014",
    max_backup_radius: float = 0.25,
    params: Optional[Sequence[str]] = None,
):
    """
    Build a daily record using the nearest sites within max_backup_radius.
    For each date, pick the closest site that has all requested parameters.

    Returns: list of dicts with keys: date_local, site_id, readings (param_code -> value), source_distance
    """
    if params is None:
        params = list(DEFAULT_PARAMS)
    else:
        params = [str(p) for p in params]

    if county_site_id not in SITE_INFO:
        raise ValueError(f"Unknown county_site_id: {county_site_id}")

    nearby = _nearby_sites(SITE_INFO, county_site_id, max_backup_radius)
    candidate_sites = {sid for sid, _ in nearby}
    counties_needed = {SITE_INFO[sid]["county_code"] for sid in candidate_sites}
    param_data = _load_param_data(BASE, counties_needed, params, candidate_sites)

    # collect all dates across candidate sites/params
    all_dates = set()
    for param in params:
        for (sid, date) in param_data[param].keys():
            if sid in candidate_sites:
                all_dates.add(date)

    results = []
    for date in sorted(all_dates):
        chosen = None
        chosen_distance = None
        readings = None
        for sid, dist in nearby:
            vals = {}
            ok = True
            for param in params:
                val = param_data[param].get((sid, date))
                if val is None:
                    ok = False
                    break
                vals[param] = val
            if ok:
                chosen = sid
                chosen_distance = dist
                readings = vals
                break
        if chosen is not None:
            results.append(
                {
                    "date_local": date,
                    "site_id": chosen,
                    "readings": readings,
                    "source_distance_deg": chosen_distance,
                }
            )
    return results


if __name__ == "__main__":
    data = load_nearby_daily()
    print(f"Loaded {len(data)} daily records using default site/radius.")
    if data:
        print("First record:", data[0])
