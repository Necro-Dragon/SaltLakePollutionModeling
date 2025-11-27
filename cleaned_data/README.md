# Cleaned Utah daily data

Columns in each CSV:
- `county_site_id`: county_code-site_number string (e.g., 005-0004)
- `parameter_code`: AQS parameter code
- `date_local`: yyyy-mm-dd
- `arithmetic_mean`: daily mean after deduping and averaging sensors (if multiple)

Deduping policy applied in order:
1. Event preference: `Events Included` > `No Events` > `Concurred Events Excluded` > `Events Excluded` > other/empty.
2. Drop records with `validity_indicator` != `Y`.
3. Any remaining duplicates for the same day/site (multiple POCs) are averaged.

Directory layout: `cleaned_data/<county_code>/<parameter_code>/data.csv` contains all years for that county/parameter.

## State and county codes
| state_code | county_code | state | county |
| --- | --- | --- | --- |
| 49 | 005 | Utah | Cache |
| 49 | 011 | Utah | Davis |
| 49 | 035 | Utah | Salt Lake |
| 49 | 049 | Utah | Utah |
| 49 | 051 | Utah | Wasatch |
| 49 | 057 | Utah | Weber |

## Parameter codes
| parameter_code | parameter |
| --- | --- |
| 61101 | Wind Speed - Scalar |
| 81102 | PM10 Total 0-10um STP |
| 88101 | PM2.5 - Local Conditions |

## Site coordinates (county_code-site_number)
| county_site_id | state_code | county_code | site_number | latitude | longitude | local_site_name |
| --- | --- | --- | --- | --- | --- | --- |
| 005-0002 | 49 | 005 | 0002 | 41.732987 | -111.836333 | UTM COORDINATES = PROBE LOCATION |
| 005-0004 | 49 | 005 | 0004 | 41.731111 | -111.8375 | LOGAN #4 |
| 005-0005 | 49 | 005 | 0005 | 41.8594 | -111.8952 | AMALGA |
| 005-0006 | 49 | 005 | 0006 | 41.63546 | -111.86819 | HYRUM |
| 005-0007 | 49 | 005 | 0007 | 41.842649 | -111.852199 | Smithfield |
| 011-0001 | 49 | 011 | 0001 | 40.886389 | -111.882222 | UTM COORDINATES = PROBE LOCATION ON ROOF OF TRAILER |
| 011-0004 | 49 | 011 | 0004 | 40.902967 | -111.884467 | Bountiful Viewmont |
| 011-6001 | 49 | 011 | 6001 | 41.041609 | -112.233281 | Antelope Island |
| 011-6002 | 49 | 011 | 6002 | 41.088554 | -112.117167 | UTM COORDINATES AT MET TOWER |
| 035-0003 | 49 | 035 | 0003 | 40.646667 | -111.849722 | Cottonwood |
| 035-0010 | 49 | 035 | 0010 | 40.758333 | -111.898056 | UTM COORDINATES = NORTH END OF BLDG. ROOF (METAL TAG MARKER) |
| 035-0012 | 49 | 035 | 0012 | 40.8075 | -111.921111 | UTM COORDINATES = INLET PROBE LOCATION ON ROOF OF TRAILER |
| 035-1001 | 49 | 035 | 1001 | 40.708611 | -112.094722 | Magna |
| 035-1006 | 49 | 035 | 1006 | 40.709668 | -112.086886 | None |
| 035-1007 | 49 | 035 | 1007 | 40.712146 | -112.111275 | None |
| 035-2003 | 49 | 035 | 2003 | 40.734111 | -112.209112 | None |
| 035-2004 | 49 | 035 | 2004 | 40.736389 | -112.210278 | UTM COORDINATES AT PROBE LOCATION |
| 035-2005 | 49 | 035 | 2005 | 40.598056 | -111.894167 | Copper View |
| 035-3001 | 49 | 035 | 3001 | 40.755278 | -111.885556 | UTM COORDINATES = INLET PROBE LOCATION ON ROOF OF BUILDING |
| 035-3003 | 49 | 035 | 3003 | 40.518056 | -112.022222 | UTM COORDINATES = PROBE LOCATION ON ROOF OF TRAILER |
| 035-3004 | 49 | 035 | 3004 | 40.616614 | -111.99855 | UTM COORDINATES = BASE OF WIND TOWER |
| 035-3005 | 49 | 035 | 3005 | 40.807723 | -112.048831 | Saltair |
| 035-3006 | 49 | 035 | 3006 | 40.736389 | -111.872222 | Hawthorne |
| 035-3007 | 49 | 035 | 3007 | 40.704444 | -111.968611 | UTM COORDINATES = PROBE LOCATION |
| 035-3008 | 49 | 035 | 3008 | 40.517946 | -112.023051 | None |
| 035-3009 | 49 | 035 | 3009 | 40.614733 | -112.000267 | WEST JORDAN |
| 035-3010 | 49 | 035 | 3010 | 40.78422 | -111.931 | ROSE PARK |
| 035-3013 | 49 | 035 | 3013 | 40.496392 | -112.036298 | Herriman #3 |
| 035-3014 | 49 | 035 | 3014 | 40.709762 | -112.00876 | Lake Park |
| 035-3015 | 49 | 035 | 3015 | 40.777145 | -111.945849 | Utah Technical Center |
| 035-3016 | 49 | 035 | 3016 | 40.807897 | -112.087717 | Inland Port |
| 035-3018 | 49 | 035 | 3018 | 40.766528 | -111.82835 | Red Butte |
| 035-4002 | 49 | 035 | 4002 | 40.662961 | -111.901851 | Near Road |
| 049-0002 | 49 | 049 | 0002 | 40.253611 | -111.663056 | North Provo |
| 049-2001 | 49 | 049 | 2001 | 40.359674 | -111.726317 | None |
| 049-4001 | 49 | 049 | 4001 | 40.341389 | -111.713611 | Lindon |
| 049-5001 | 49 | 049 | 5001 | 40.303611 | -111.722778 | UTM COORDINATES = INLET PROBE LOCATION ON ROOF OF TRAILER |
| 049-5002 | 49 | 049 | 5002 | 40.313565 | -111.657145 | None |
| 049-5004 | 49 | 049 | 5004 | 40.31162 | -111.700481 | REPLACED BY NEW NORTH OREM SITE LATER IN 1994 (SEE 49-049-5009) |
| 049-5005 | 49 | 049 | 5005 | 40.268889 | -111.681944 | UTM COORDINATES = INLET PROBE LOCATION OVER SIDEWALK |
| 049-5006 | 49 | 049 | 5006 | 40.164956 | -111.611309 | None |
| 049-5007 | 49 | 049 | 5007 | 40.180556 | -111.606944 | UTM COORDINATES = INLET PROBE LOCATION ON ROOF OF TRAILER |
| 049-5008 | 49 | 049 | 5008 | 40.430278 | -111.803889 | Highland |
| 049-5010 | 49 | 049 | 5010 | 40.136378 | -111.657936 | Spanish Fork |
| 049-6003 | 49 | 049 | 6003 | 40.294397 | -111.73604 | None |
| 051-0001 | 49 | 051 | 0001 | 40.497962 | -111.39763 | Heber |
| 057-0001 | 49 | 057 | 0001 | 41.219167 | -111.972778 | UTM COORDINATES = INLET PROBE ON ROOF OF BUILDING |
| 057-0002 | 49 | 057 | 0002 | 41.206321 | -111.975524 | Ogden |
| 057-0007 | 49 | 057 | 0007 | 41.179722 | -111.983056 | UTM COORDINATES = INLET PROBE LOCATION ON ROOF OF TRAILER |
| 057-1001 | 49 | 057 | 1001 | 41.171944 | -112.031667 | UTM COORDINATES = INLET PROBE ON ROOF OF TRAILER |
| 057-1002 | 49 | 057 | 1002 | 41.305 | -111.965278 | UTM COORDINATES = INLET PROBE LOCATION ON ROOF |
| 057-1003 | 49 | 057 | 1003 | 41.303614 | -111.987871 | Harrisville |
