"""SEPTA public JSON API client.

Validated against:
  * Official Swagger 1.0.2: https://app.septa.org/ (apidoc.json)
  * Live host: https://www3.septa.org/api/
  * Regional Rail inputs: https://www3.septa.org/VIRegionalRail.html
  * Metro v2 (not in Swagger): OpenDataPhilly SEPTA Metro APIs

The Swagger UI is hosted at app.septa.org with basePath `/api`, but the working
JSON endpoints are on www3.septa.org. No API key is required.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Any

import requests

from stations import resolve_station

DEFAULT_BASE_URL = "https://www3.septa.org/api"
DEFAULT_TIMEOUT = 15
USER_AGENT = "SEPTAwatch/1.0 (+https://github.com/evneis/SEPTAwatch)"

# TrainView uses 999 and Metro v2 uses 998 when GPS/status is unavailable.
UNKNOWN_DELAY_THRESHOLD = 998

_HTML_TAG_RE = re.compile(r"<[^>]+>")


class SeptaAPIError(Exception):
    """Raised when the SEPTA API cannot be reached or returns invalid data."""


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = _HTML_TAG_RE.sub(" ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def coerce_bool(value: Any, default: bool = False) -> bool:
    """NextToArrive documents isdirect as boolean, but live JSON uses 'true'/'false' strings."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def format_delay(value: Any) -> str:
    """Human-readable delay for TrainView `late` and Metro `delay` integers."""
    if value is None or value == "":
        return "Unknown"
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return str(value)
    if minutes >= UNKNOWN_DELAY_THRESHOLD:
        return "No GPS / unknown"
    if minutes <= 0:
        return "On time"
    unit = "min" if minutes == 1 else "mins"
    return f"{minutes} {unit} late"


@dataclass
class Arrivals:
    title: str
    northbound: list[dict[str, Any]] = field(default_factory=list)
    southbound: list[dict[str, Any]] = field(default_factory=list)


def parse_arrivals(payload: Any) -> Arrivals:
    """Unwrap the Arrivals payload.

    The documented schema is `{ "*": [ {Northbound: [...]}, {Southbound: [...]} ] }`
    where the object key is a generated title such as
    ``Suburban Station Departures: September 8, 2026, 12:57 pm``.
    """
    if not isinstance(payload, dict) or not payload:
        raise SeptaAPIError("Arrivals response was empty or not an object")

    title, body = next(iter(payload.items()))
    northbound: list[dict[str, Any]] = []
    southbound: list[dict[str, Any]] = []

    if isinstance(body, dict):
        buckets = [body]
    elif isinstance(body, list):
        buckets = body
    else:
        raise SeptaAPIError("Arrivals response did not contain direction lists")

    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        northbound.extend(bucket.get("Northbound") or [])
        southbound.extend(bucket.get("Southbound") or [])

    return Arrivals(title=str(title), northbound=northbound, southbound=southbound)


def route_has_issue(alert: dict[str, Any]) -> bool:
    flags = (
        "isalert",
        "isdetour",
        "issuspended",
        "issuppend",
        "isstrike",
        "ismodifiedservice",
        "isdelays",
        "isdiversion",
        "isdetouralert",
        "isSnow",
        "iselevator",
    )
    if str(alert.get("isadvisory", "")).lower() == "yes":
        return True
    return any(str(alert.get(flag, "")).upper() == "Y" for flag in flags)


class SeptaClient:
    """HTTP client for the documented SEPTA JSON APIs."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", USER_AGENT)
        self.session.headers.setdefault("Accept", "application/json")

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SeptaAPIError(f"Request failed for {url}: {exc}") from exc

        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type.lower() and not response.text.lstrip().startswith(("{", "[")):
            raise SeptaAPIError(f"Non-JSON response from {url}")
        try:
            return response.json()
        except ValueError as exc:
            raise SeptaAPIError(f"Invalid JSON from {url}") from exc

    def _get_text(self, path: str, params: dict[str, Any] | None = None) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SeptaAPIError(f"Request failed for {url}: {exc}") from exc
        return response.text

    # --- Real Time Data (Swagger) ---

    def get_arrivals(
        self,
        station: str,
        results: int = 10,
        direction: str | None = None,
    ) -> Arrivals:
        """GET /Arrivals/index.php — Regional Rail arrivals & departures."""
        params: dict[str, Any] = {
            "station": resolve_station(station),
            "results": results,
        }
        if direction:
            direction = direction.upper()
            if direction not in {"N", "S"}:
                raise ValueError("direction must be 'N' or 'S'")
            params["direction"] = direction
        return parse_arrivals(self._get("Arrivals/index.php", params))

    def get_train_view(self) -> list[dict[str, Any]]:
        """GET /TrainView/index.php — all Regional Rail trains currently on the system."""
        payload = self._get("TrainView/index.php")
        if not isinstance(payload, list):
            raise SeptaAPIError("TrainView response was not a list")
        return payload

    def get_next_to_arrive(
        self,
        start_station: str,
        end_station: str,
        results: int = 5,
    ) -> list[dict[str, Any]]:
        """GET /NextToArrive/index.php — times between two Regional Rail stations."""
        payload = self._get(
            "NextToArrive/index.php",
            {
                "req1": resolve_station(start_station),
                "req2": resolve_station(end_station),
                "req3": results,
            },
        )
        if not isinstance(payload, list):
            raise SeptaAPIError("NextToArrive response was not a list")
        for row in payload:
            if isinstance(row, dict) and "isdirect" in row:
                row["isdirect"] = coerce_bool(row["isdirect"], default=True)
        return payload

    def get_transit_view(self, route: str) -> list[dict[str, Any]]:
        """GET /TransitView/index.php — bus/trolley locations for one route."""
        payload = self._get("TransitView/index.php", {"route": route})
        if isinstance(payload, dict):
            buses = payload.get("bus")
            if buses is None:
                raise SeptaAPIError("TransitView response missing 'bus' list")
            return buses
        if isinstance(payload, list):
            return payload
        raise SeptaAPIError("TransitView response was not an object")

    def get_transit_view_all(self) -> Any:
        """GET /TransitViewAll/index.php — all bus and trolley locations."""
        return self._get("TransitViewAll/index.php")

    def get_bus_detours(self, route: str | None = None) -> list[dict[str, Any]]:
        """GET /BusDetours/index.php — detours, optionally filtered by route."""
        params = {"req1": route} if route else None
        payload = self._get("BusDetours/index.php", params)
        if not isinstance(payload, list):
            raise SeptaAPIError("BusDetours response was not a list")
        return payload

    def get_alerts(self, routes: str | None = None) -> list[dict[str, Any]]:
        """GET /Alerts/index.php — route alert flags (and often the message body too)."""
        params = {"routes": routes} if routes else None
        payload = self._get("Alerts/index.php", params)
        if not isinstance(payload, list):
            raise SeptaAPIError("Alerts response was not a list")
        return payload

    def get_alert_data(self, route_id: str | None = None) -> list[dict[str, Any]]:
        """GET /Alerts/get_alert_data.php — alert messages for a route_id."""
        params = {"route_id": route_id} if route_id else None
        payload = self._get("Alerts/get_alert_data.php", params)
        if not isinstance(payload, list):
            raise SeptaAPIError("Alert data response was not a list")
        return payload

    def get_elevator_outages(self) -> dict[str, Any]:
        """GET /elevator/index.php — elevator outages with meta.elevators_out."""
        payload = self._get("elevator/index.php")
        if not isinstance(payload, dict):
            raise SeptaAPIError("Elevator outage response was not an object")
        return payload

    # --- Static Data (Swagger) ---

    def get_rr_schedules(self, train_number: str) -> list[dict[str, Any]]:
        """GET /RRSchedules/index.php — schedule for a Regional Rail train number."""
        payload = self._get("RRSchedules/index.php", {"req1": train_number})
        if not isinstance(payload, list):
            raise SeptaAPIError("RRSchedules response was not a list")
        return payload

    def get_bus_schedules(self, stop_id: str | int) -> Any:
        """GET /BusSchedules/index.php — bus/trolley times at a stop_id."""
        return self._get("BusSchedules/index.php", {"stop_id": stop_id})

    def get_stops(self, route: str) -> list[dict[str, Any]]:
        """GET /Stops/index.php — bus/trolley stops for a route."""
        payload = self._get("Stops/index.php", {"req1": route})
        if not isinstance(payload, list):
            raise SeptaAPIError("Stops response was not a list")
        return payload

    def get_locations(
        self,
        lon: float,
        lat: float,
        location_type: str | None = None,
        radius: int | None = None,
    ) -> list[dict[str, Any]]:
        """GET /locations/get_locations.php — locations near a lat/lon."""
        params: dict[str, Any] = {"lon": lon, "lat": lat}
        if location_type:
            params["type"] = location_type
        if radius is not None:
            params["radius"] = radius
        payload = self._get("locations/get_locations.php", params)
        if not isinstance(payload, list):
            raise SeptaAPIError("Locations response was not a list")
        return payload

    # --- Metro v2 (OpenDataPhilly; not listed in Swagger 1.0.2) ---

    def get_metro_trips(self, route_id: str) -> list[dict[str, Any]]:
        """GET /v2/trips/?route_id= — active Metro trips. Rail lines have no GPS."""
        payload = self._get("v2/trips/", {"route_id": route_id})
        if not isinstance(payload, list):
            raise SeptaAPIError("Metro trips response was not a list")
        return payload

    def get_metro_trip_update(self, trip_id: str) -> dict[str, Any]:
        """GET /v2/trip-update/?trip_id= — stop-time details for a Metro trip."""
        payload = self._get("v2/trip-update/", {"trip_id": trip_id})
        if not isinstance(payload, dict):
            raise SeptaAPIError("Metro trip-update response was not an object")
        return payload

    def get_metro_stops(self, route_id: str) -> list[dict[str, Any]]:
        """GET /v2/stops/?route_id= — ordered stop list for a Metro route."""
        payload = self._get("v2/stops/", {"route_id": route_id})
        if not isinstance(payload, list):
            raise SeptaAPIError("Metro stops response was not a list")
        return payload

    def get_metro_stop_schedule(self, route_id: str, stop_id: str | int) -> list[dict[str, Any]]:
        """GET /v2/stop-schedule/?route_id=&stop_id= — scheduled Metro arrivals."""
        payload = self._get(
            "v2/stop-schedule/",
            {"route_id": route_id, "stop_id": stop_id},
        )
        if not isinstance(payload, list):
            raise SeptaAPIError("Metro stop-schedule response was not a list")
        return payload

    def get_metro_kml(self, route_id: str) -> str:
        """GET /v2/kml/?route_id= — KML geometry for a Metro route."""
        return self._get_text("v2/kml/", {"route_id": route_id})
