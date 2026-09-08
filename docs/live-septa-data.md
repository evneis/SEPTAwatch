# Live SEPTA data sources

Researched 8 September 2026. Endpoints were hit live from this environment around 17:35 UTC. No API key is required for the official feeds below.

**Goal:** pick sources that can show **where buses and trains are right now**, plus delay / next-arrival info that is actually live rather than a printed timetable.

**Short answer:** use SEPTA’s own feeds. Do not scrape Google Maps, the Transit app, or SEPTA’s public map. Those products consume the same official data (or less of it). Swiftly’s old SEPTA URLs are no longer a public source.

---

## Ranking (best first)

Ranked for **live vehicle movement and delay accuracy**, then for how usable the feed is in an app. “Accuracy” here means: GPS that is actually onboard, timestamps that are recent, and predicted arrivals that change with the vehicle — not just the schedule.

| Rank | Source | Best for | Live movement? | Accuracy | Effort |
| ---: | --- | --- | --- | ---: | --- |
| 1 | GTFS-RT vehicle positions (bus + rail) | Map dots for buses, trolleys, NHSL, Regional Rail | Yes (except L1 / Broad Street) | Highest | Medium (protobuf) |
| 2 | GTFS-RT trip updates (bus feed) | Stop-level ETAs for buses / trolleys | Indirect (predictions, not a map) | Highest for bus ETAs | Medium |
| 3 | TrainView JSON | Regional Rail map + delay + track | Yes | Highest for RR *fields*; GPS matches rail GTFS-RT | Low |
| 4 | Arrivals + NextToArrive JSON | Station boards and A→B rail trips | Station-centric, not a map | High for RR commuters | Low |
| 5 | `/api/v2/trips/` JSON | One JSON dump of almost every active trip | Yes when GPS exists | High where GPS exists; honest `NO GPS` elsewhere | Low |
| 6 | TransitView / TransitViewAll JSON | Bus/trolley map without protobuf | Yes | Same AVL as (1), slightly less structured | Low |
| 7 | Metro v2 trips / trip-update (filtered) | L1 / B1 / trolley-specific views | Partial | GPS only on surface trolleys + NHSL | Low |
| 8 | Alerts JSON + GTFS-RT service alerts | Disruptions, not positions | No | Good enough for banners | Low |
| 9 | Static GTFS zip | Stops, shapes, trip IDs | No | Authoritative *schedule* | Medium |
| 10 | Metro stop-schedule, BusSchedules, RRSchedules, SMS | Timetables | No | Scheduled only | Low |
| — | Swiftly `api.goswift.ly` | — | — | **Do not use** (replaced, 401) | — |
| — | Google / Transit / trains.fyi / SEPTA website | Consumer UIs | — | **Do not use as a data source** | — |

Recommended build for SEPTAwatch: **(1) + (2) + (3) + (4) + (8)**, with **(9)** for stop names and route lines. Use **(5)** if you want a faster JSON-only prototype of the same map. Treat **L1 and Broad Street as not GPS-trackable**.

---

## What is actually live today

Snapshot from the live probes (afternoon, 8 Sep 2026):

| Feed | Vehicles / entities | Typical age | Notes |
| --- | ---: | --- | --- |
| GTFS-RT bus vehicle positions | 562 | ~60 s | 126 routes. Includes T1–T5, G1, D1/D2, M1. **No L1.** Almost no B1. |
| GTFS-RT bus trip updates | 589 | ~28 s header | Median **33 upcoming stop ETAs** per trip (absolute POSIX times). |
| GTFS-RT rail vehicle positions | 41 | ~40–45 s | Matches TrainView’s ~42 trains. |
| GTFS-RT rail trip updates | 59 | ~28 s header | **Only one stop** per trip; delay seconds, not a full ETA list. |
| TransitViewAll JSON | 649 vehicles / 128 routes | ~1 min documented | Same bus/trolley universe, easier JSON. |
| TrainView JSON | 42 trains | seconds | 15 of 42 had `late: 999` (no GPS / unknown delay). |
| `/api/v2/trips/` | 717 trips | mixed | Unified bus + metro + Regional Rail. 611 with GPS, 62 `NO GPS`, 44 `CANCELED`. |

**Hard coverage gap:** Market–Frankford (L1) and Broad Street (B1 / B2 / B3) do **not** publish usable onboard GPS. Live L1 trips returned `"status": "NO GPS"`, `lat`/`lon` null, `delay: 998`. OpenDataPhilly documents this for L1/B1. Their note that **M1 also lacks GPS is outdated** — both live M1 (Norristown High Speed Line) vehicles had coordinates.

Trolleys (T1–T5, G1) have **partial GPS** (surface running). Underground / subway-surface segments often show `NO GPS`. Media–Sharon Hill (D1) had GPS on all live cars in this snapshot.

Regional Rail GPS is generally present, but delay is missing for a large minority (`late: 999` in TrainView). Older SEPTA notes also warn that some Amtrak-owned “dark territory” positions are estimated.

---

## 1. GTFS-RT vehicle positions — best live map

Official GTFS-Realtime 2.0 protobuf. Full dataset, no key, listed in [Mobility Database](https://mobilitydatabase.org/feeds?q=septa&gtfs_rt=true) after SEPTA moved off Swiftly (Feb 2026).

**Bus / trolley / NHSL** (path `septa-pa-us`):

- Positions: `https://www3.septa.org/gtfsrt/septa-pa-us/Vehicle/rtVehiclePosition.pb`
- Trip updates: `https://www3.septa.org/gtfsrt/septa-pa-us/Trip/rtTripUpdates.pb`
- Alerts: `https://www3.septa.org/gtfsrt/septa-pa-us/Service/rtServiceAlerts.pb`

**Regional Rail** (path `septarail-pa-us`):

- Positions: `https://www3.septa.org/gtfsrt/septarail-pa-us/Vehicle/rtVehiclePosition.pb`
- Trip updates: `https://www3.septa.org/gtfsrt/septarail-pa-us/Trip/rtTripUpdates.pb`
- Alerts: `https://www3.septa.org/gtfsrt/septarail-pa-us/Service/rtServiceAlerts.pb`

Each vehicle includes `trip_id`, `route_id`, lat/lon, bearing, current stop, timestamp, and often occupancy. Python can parse this with `gtfs-realtime-bindings`.

Human-readable debug pages exist (`.../Vehicle/print.php`, etc.) but **only print the first five entities**. Do not use `print.php` in the app.

**Why this ranks first:** it is the same AVL Google and other trip planners consume, it is a stable public spec, and the bus position timestamps were ~1 minute old. It is the right long-term map source.

**Why it is not enough alone:** rail trip updates are thin; L1/B1 still have no dots; you need static GTFS to turn `stop_id` / `trip_id` into names and shapes.

---

## 2. GTFS-RT trip updates (bus) — best live ETAs

The bus trip-update feed is the only official source that gives **a list of predicted arrival times for upcoming stops**, not just “this vehicle is N minutes late.”

Live probe: median 33 `stop_time_update` rows per trip, with `arrival.time` as POSIX seconds. That is what a “next buses at this stop” screen should use.

The **rail** trip-update feed is much weaker: typically one stop, `delay` only. For Regional Rail ETAs, prefer Arrivals / NextToArrive / TrainView instead of rail GTFS-RT trip updates.

---

## 3. TrainView JSON — best Regional Rail tracker

`GET https://www3.septa.org/api/TrainView/index.php`

Swagger: [app.septa.org](https://app.septa.org/) (v1.0.2). Working host is `www3.septa.org` (the Swagger UI’s `/api` base path is misleading).

Each train includes lat/lon, heading, train number, line, origin (`SOURCE`), destination, `currentstop`, `nextstop`, consist (car numbers), track, track-change flag, and `late` in minutes.

Sentinel: **`late` 999 (sometimes 998)** means no GPS / unknown, not “999 minutes late.”

**Why it ranks above rail GTFS-RT for product UX:** GTFS-RT rail has the dots; TrainView has the fields riders care about (next station, track, consist, human delay). Positions matched the rail GTFS-RT count in the live probe (~41–42 trains). Use both if you want spec-standard IDs *and* rider-facing fields.

---

## 4. Arrivals and NextToArrive — best rail commute UI

Documented real-time JSON on the same host. Station names must match [Regional Rail Inputs](https://www3.septa.org/VIRegionalRail.html) exactly (`Temple U`, `Market East` for Jefferson, `30th Street Station`, etc.).

| Endpoint | Purpose |
| --- | --- |
| `/api/Arrivals/index.php?station=...&results=N` | Northbound / Southbound board for one station: train id, line, scheduled vs depart time, delay text, **track and platform** |
| `/api/NextToArrive/index.php?req1=FROM&req2=TO&req3=N` | Next trips between two stations, including transfers (`isdirect`) |

Live Suburban Station board returned delay strings (`"On Time"`, `"4 min"`, `"24 min"`) plus track/platform. NextToArrive from 30th Street Station → Temple U returned delay-aware clock times.

**Northbound / Southbound are railroad directions**, not compass directions (Reading vs Pennsylvania sides of Suburban Station).

These do not replace a moving map. They are the right API for “when is my train / which track.”

---

## 5. Unified v2 trips JSON — best JSON-only prototype

`GET https://www3.septa.org/api/v2/trips/`  
Optional: `?route_id=L1` (or `33`, `AIR`, `T4`, …)

Not in Swagger 1.0.2. Documented on [OpenDataPhilly — SEPTA Metro APIs](https://opendataphilly.org/datasets/septa-metro-apis/) for Metro, but the unfiltered URL currently returns **bus, trolley, subway, NHSL, and Regional Rail** together (~717 trips, ~300 KB).

Useful fields: `lat`/`lon`, `delay`, `status` (`ON-TIME` / `LATE` / `EARLY` / `NO GPS` / `CANCELED`), `vehicle_id`, `next_stop_id`, `trip_headsign`, `schedule_relationship`.

Related:

| Endpoint | Role |
| --- | --- |
| `/api/v2/trip-update/?trip_id=...` | Stop-time list for one trip (works for Metro; richer than L1 GPS) |
| `/api/v2/stops/?route_id=L1` | Ordered stops + coordinates |
| `/api/v2/kml/?route_id=L1` | Route geometry |
| `/api/v2/stop-schedule/?route_id=L1&stop_id=416` | **Timetable** at a stop (1,000+ scheduled rows at 69th Street) — not live GPS |

**Caveat:** undocumented for system-wide use. SEPTA could narrow it back to Metro-only. Fine for a prototype; for a shipping map prefer GTFS-RT + TrainView.

---

## 6. TransitView JSON — easy bus map

| Endpoint | Role |
| --- | --- |
| `/api/TransitView/index.php?route=33` | Vehicles on one route |
| `/api/TransitViewAll/index.php` | All bus/trolley/metro-surface vehicles (~260 KB) |

Fields: lat/lng, heading, `VehicleID`, trip, BlockID, destination, `late` / `Offset` minutes, next stop id/name/sequence, occupancy label, timestamp.

OpenDataPhilly lists refresh as `R/PT1M` (about every minute). Route IDs are the **new Metro names**: `T1`–`T5`, `G1`, `D1`/`D2`, `L1`, `B1`, `M1`. Old trolley numbers (`10`, `11`, `13`, `34`, `36`) returned empty.

This is almost certainly the same AVL as the bus GTFS-RT feed, already decoded. Ranked below GTFS-RT because trip-update ETAs and occupancy enums are better in protobuf, and TransitView is a SEPTA-specific schema.

---

## 7. Metro-only v2 (L1 / Broad Street / trolleys)

Same v2 URLs as §5, filtered by Metro `route_id`.

| Line | Live GPS? |
| --- | --- |
| L1 (Market–Frankford) | No |
| B1 / B2 / B3 (Broad Street) | No |
| M1 (Norristown High Speed Line) | **Yes** (docs still say no; live data had GPS) |
| T1–T5, G1 | Partial (surface) |
| D1 / D2 | Yes in this snapshot |

For subway, the honest UI is: scheduled trips + alerts + elevator outages, **not** a moving train. Stop-schedule is a timetable dump, not predictions.

---

## 8. Alerts, detours, elevators

Live, but not vehicle tracking. Still required for a trustworthy monitor.

| Endpoint | Role |
| --- | --- |
| `/api/Alerts/index.php` | Flags per route (`isalert`, `isdelays`, `issuspended`, …). 185 rows live. |
| `/api/Alerts/get_alert_data.php?route_id=bus_route_33` | Longer messages |
| `/api/BusDetours/index.php` | Bus/trolley detours |
| `/api/elevator/index.php` | Elevator outages |
| GTFS-RT `Service/rtServiceAlerts.pb` | Standard alerts (bus feed also mentions `L1 OWL`, etc.) |

JSON alerts are easier to filter by the rider’s route. GTFS-RT alerts are better if you already parse protobuf.

---

## 9. Static GTFS — schedule backbone, not live

- Zip: `https://www3.septa.org/developer/gtfs_public.zip`
- License click-through: [www3.septa.org/developer](https://www3.septa.org/developer/) (“as is”, revocable, GTFS only)
- Extra notes: [github.com/septadev/GTFS](https://github.com/septadev/GTFS)

Contains stops, routes, trips, stop_times, and shapes for **both** bus and rail packages inside the zip. Required to:

- Draw route lines
- Resolve `trip_id` / `stop_id` from GTFS-RT
- Know which trips *should* be running when GPS is missing (L1/B1)

This is not a movement feed. Combine it with GTFS-RT; do not poll the zip every few seconds.

GIS extracts (stops/routes as GeoJSON/shapefile) also live on [OpenDataPhilly — Routes, Stops, and Locations](https://opendataphilly.org/datasets/septa-routes-stops-locations/). Those lag the GTFS zip; prefer GTFS for IDs.

---

## 10. Schedule-only APIs (not live tracking)

| Endpoint | What you get |
| --- | --- |
| `/api/BusSchedules/index.php?stop_id=` | Timetable at a bus/trolley stop |
| `/api/RRSchedules/index.php?req1=TRAINNO` | Timetable for one Regional Rail train number |
| `/api/sms/index.php` or `/sms/{stop}/...` | Next scheduled trips as text (the old 41411 SMS) |
| `/api/Stops/index.php` | Stops for a route |
| `/api/locations/get_locations.php` | Nearby SEPTA locations |

Useful fallbacks when GPS is down. They will happily show a bus that already passed.

---

## Do not use as a data source

**Swiftly.** Until early 2026, Mobility Database pointed at `https://api.goswift.ly/real-time/septa/...`. Those URLs now return **401**. Official producer URLs are the `www3.septa.org/gtfsrt/...` protobufs.

**SEPTA websites / apps.** [ng-realtime.septa.org/map](https://ng-realtime.septa.org/map) and [beta-realtime.septa.org](https://beta-realtime.septa.org/) are rider UIs on top of the same feeds. Scraping them is brittle and against the point of the public APIs.

**Third-party maps** (Transit, Google Maps, Apple Maps, [trains.fyi](https://trains.fyi/philadelphia/), community projects like septa-live). They republish official GTFS-RT / TrainView. Using them adds ToS risk, extra latency, and no new GPS. Google/Transit also cannot invent L1 positions SEPTA does not publish.

**`print.php` GTFS-RT pages.** Debug only; truncated to five records.

---

## Suggested architecture for this app

```
                    ┌─────────────────────────────┐
                    │  Static GTFS (daily refresh) │
                    │  stops, shapes, trip names   │
                    └──────────────┬──────────────┘
                                   │
     ┌─────────────────────────────┼─────────────────────────────┐
     │                             │                             │
     ▼                             ▼                             ▼
 Bus / trolley map          Regional Rail map              Subway (L1 / B1)
 GTFS-RT Vehicle            TrainView JSON                 v2/trips (NO GPS)
 Positions (bus)            + rail GTFS-RT positions       + stop-schedule
                            (IDs / backup)                 + alerts
     │                             │
     ▼                             ▼
 Stop ETAs                    Station board / A→B
 GTFS-RT Trip Updates         Arrivals + NextToArrive
 (bus feed)

 Cross-cutting: Alerts JSON, BusDetours, elevator outages
```

Poll live feeds every **15–30 seconds**. SEPTA does not publish a rate limit; OpenDataPhilly’s TransitView cadence is one minute. Identify the client with a real User-Agent.

Route IDs to use in new code: **L1, B1/B2/B3, M1, T1–T5, G1, D1/D2** for Metro; numeric bus routes; Regional Rail `AIR`, `PAO`, `LAN`, `WAR`, … in GTFS / v2, vs human line names (`Airport`, `Paoli/Thorndale`) in TrainView.

---

## Accuracy caveats (show these in the UI)

1. **L1 and Broad Street are not live-trackable** in public data. Showing a moving subway car would be fiction.
2. **Trolley GPS drops underground.** Expect gaps on T and G lines.
3. **`late: 999` / `delay: 998` / `NO GPS`** means unknown, not a huge delay.
4. **Regional Rail “Northbound/Southbound”** is not compass direction.
5. **Bus GTFS-RT trip updates** are the live ETA; BusSchedules/SMS are not.
6. **v2 system-wide `/trips/`** is convenient and currently complete, but not in the official Swagger. Prefer GTFS-RT + TrainView for anything you ship.

---

## Official references

- Swagger UI: https://app.septa.org/ (also https://api.septa.org/)
- Swagger JSON: https://app.septa.org/apidoc.json
- Live JSON host: https://www3.septa.org/api/
- Regional Rail station parameters: https://www3.septa.org/VIRegionalRail.html
- GTFS license + zip: https://www3.septa.org/developer/
- OpenDataPhilly SEPTA org: https://opendataphilly.org/organizations/septa/
- OpenDataPhilly TransitView: https://opendataphilly.org/datasets/septa-transitview/
- OpenDataPhilly GTFS-RT: https://opendataphilly.org/datasets/septa-gtfs-alerts-updates/
- OpenDataPhilly Metro v2: https://opendataphilly.org/datasets/septa-metro-apis/
- Mobility Database (current producer URLs): https://mobilitydatabase.org/feeds?q=septa&gtfs_rt=true
- GTFS-RT spec: https://gtfs.org/documentation/realtime/reference/
- SEPTAdev contact listed in Swagger: septoid@gmail.com / [@septadev](https://twitter.com/septadev)

---

## Probe log (8 Sep 2026)

Commands used to validate the ranking (representative):

- `TrainView` → 42 trains, keys `lat,lon,trainno,late,currentstop,nextstop,TRACK,...`
- `TransitView?route=33` → 7 buses with next-stop + occupancy
- `TransitViewAll` → 649 vehicles, 128 routes including `L1,B1,M1,T1–T5,G1,D1`
- GTFS-RT bus VP protobuf → 562 entities, ~60 s old, metro GPS on T/G/D/M1, not L1
- GTFS-RT bus TU protobuf → 589 entities, median 33 stop predictions
- GTFS-RT rail VP protobuf → 41 entities, ~44 s old
- `/api/v2/trips/` → 717 trips, 611 with GPS; all L1 and B1 `NO GPS`; M1 GPS present
- `Arrivals?station=Suburban Station` → delay + track/platform
- Swiftly vehicle-positions URL → HTTP 401
