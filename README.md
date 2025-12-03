# SaltLakePollutionModeling

## Data sources

- `data/utah_daily`: Daily air quality data (wind speed, PM2.5, PM10) for selected Utah counties downloaded from the U.S. EPA Air Quality System (AQS) API (`https://aqs.epa.gov/`, using the `dailyData/byCounty` endpoint; see `download_utah_counties_daily.sh`).
- `data/water_level`: Great Salt Lake water-surface elevation time series for the north and south arms (`north_arm_10010100.rdb`, `south_arm_10010000.rdb`) downloaded from the USGS National Water Information System (NWIS) Water Data for the Nation (`https://waterdata.usgs.gov/`).
- `data/EAV_table.csv`: Elevation–area–volume table for Great Salt Lake downloaded from the USGS ScienceBase item `https://www.sciencebase.gov/catalog/item/6467b42fd34ec11ae4a8afb1`.
- `data/eav_*.csv`: Arm/bay-specific EAV tables (north_arm, south_arm, Bear River Bay, Farmington Bay) from the same USGS release.
- `cleaned_data/surface_areas/surfaces_areas.csv`: Precomputed daily north/south surface areas and volumes. Built by converting north/south gage stages (NGVD29) to NAVD88 and looking up:
  - North = EAV(north_arm) + EAV(Bear River Bay) using USGS 10010100 stage
  - South = EAV(south_arm) + EAV(Farmington Bay) using USGS 10010000 stage

## Cleaning of Utah daily AQS data

The cleaned county-level daily datasets in `cleaned_data/` are derived from the raw AQS JSON files in `data/utah_daily` using `clean_utah_daily.py` (documented in `cleaned_data/README.md`):

- All AQS `dailyData` records are grouped by `(state_code, county_code, site_number, parameter_code, date_local)`.
- For each group, records are filtered by `event_type` using the preference order `Events Included` > `No Events` > `Concurred Events Excluded` > `Events Excluded` > other/empty.
- Within the chosen event type, records with `validity_indicator != "Y"` are dropped.
- Any remaining duplicates for the same day/site/parameter (e.g., multiple POCs or sensors) are averaged to produce a single `arithmetic_mean`.
- The output CSVs contain one row per day/site/parameter with columns `county_site_id` (county_code–site_number), `parameter_code`, `date_local`, and `arithmetic_mean`, stored as `cleaned_data/<county_code>/<parameter_code>/data.csv`.

## Cleaning of Great Salt Lake elevation–area–volume table

The original `data/EAV_table.csv` from USGS ScienceBase contained multiple elevation datums and area/volume units. It has been reduced to the most recent vertical datum and the primary imperial area/volume units:

- Retained columns: `elev_ft_NAVD88` (elevation in feet, NAVD88), `area_ft2` (surface area in square feet), `volume_ft3` (volume in cubic feet).
- Removed columns: `elev_ft_NGVD29`, `area_m2`, `area_km2`, `area_mi2`, `area_acre`, `volume_m3`, `volume_km3`, `volume_mi3`, `volume_acreft`.

This yields a compact table suitable for direct use in modeling with a single elevation datum and consistent units.

## Cleaning of Great Salt Lake water-level data

The raw USGS NWIS `data/water_level/*.rdb` files have been simplified to match the structure of the cleaned AQS daily data:

- The original NWIS tab-delimited tables (columns such as `agency_cd`, `site_no`, `datetime`, `<TS_ID>_62614_00003`, and qualifier-code fields) were replaced with a four-column, tab-delimited layout: `site_id`, `parameter_code`, `date_local`, `arithmetic_mean`.
- For each file, `site_id` is the USGS site number (`10010100` for the north arm, `10010000` for the south arm), and `parameter_code` is fixed at `62614` (lake or reservoir water-surface elevation above NGVD 1929, daily mean).
- `date_local` is copied from the NWIS `datetime` column (YYYY-MM-DD), and `arithmetic_mean` is the daily mean lake elevation in feet from the NWIS daily statistics column.
- USGS qualifier codes (e.g., `A`, `e`, `P`) are dropped from the tabular data, but the original USGS warning and metadata comment lines at the top of each `.rdb` file are preserved, including the notes about provisional and revised data.

After cleaning, the water-level files `data/water_level/north_arm_10010100.rdb` and `data/water_level/south_arm_10010000.rdb` can be read in the same style as the AQS daily CSVs, with one row per site and date and a single mean value column.
