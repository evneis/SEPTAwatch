"""Unit tests for the SEPTA API client against documented and live response shapes."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from septa_api import (
    DEFAULT_BASE_URL,
    SeptaAPIError,
    SeptaClient,
    coerce_bool,
    format_delay,
    parse_arrivals,
    route_has_issue,
    strip_html,
)
from stations import api_name_from_choice, resolve_station


ARRIVALS_FIXTURE = {
    "Suburban Station Departures: September 8, 2026, 12:57 pm": [
        {
            "Northbound": [
                {
                    "direction": "N",
                    "path": "R4N",
                    "train_id": "432",
                    "origin": "Airport Terminal E-F",
                    "destination": "Warminster",
                    "line": "Warminster",
                    "status": "5 min",
                    "service_type": "LOCAL",
                    "next_station": "Penn Medical Station",
                    "sched_time": "2026-09-08 13:04:00.000",
                    "depart_time": "2026-09-08 13:05:00.000",
                    "track": "2",
                    "track_change": None,
                    "platform": "A",
                    "platform_change": None,
                }
            ]
        },
        {
            "Southbound": [
                {
                    "direction": "S",
                    "path": "R2/3S",
                    "train_id": "2393",
                    "origin": "Elm St",
                    "destination": "Penn Medicine",
                    "line": "Manayunk/Norristown",
                    "status": "4 min",
                    "service_type": "LOCAL",
                    "next_station": "North Broad St",
                    "sched_time": "2026-09-08 13:08:00.000",
                    "depart_time": "2026-09-08 13:09:00.000",
                    "track": "4",
                    "track_change": None,
                    "platform": "A",
                    "platform_change": None,
                }
            ]
        },
    ]
}

TRAINVIEW_FIXTURE = [
    {
        "lat": "39.955290833333",
        "lon": "-75.1757405",
        "trainno": "3218",
        "service": "LOCAL",
        "dest": "Norristown",
        "currentstop": "Gray 30th Street",
        "nextstop": "Suburban Station",
        "line": "Manayunk/Norristown",
        "consist": "389,388,402,404",
        "heading": "98.70318733345",
        "late": 2,
        "SOURCE": "Penn Medicine Station",
        "TRACK": "1",
        "TRACK_CHANGE": "",
    },
    {
        "lat": "39.9538889",
        "lon": "-75.1677778",
        "trainno": "1072",
        "service": "",
        "dest": "Suburban Sta",
        "currentstop": "",
        "nextstop": "Cynwyd",
        "line": "Cynwyd",
        "consist": "",
        "heading": 0,
        "late": 999,
        "SOURCE": "Cynwyd",
        "TRACK": "",
        "TRACK_CHANGE": "",
    },
]

NEXT_TO_ARRIVE_FIXTURE = [
    {
        "orig_train": "2393",
        "orig_line": "Media/Wawa",
        "orig_departure_time": "1:09PM",
        "orig_arrival_time": "1:14PM",
        "orig_delay": "3 mins",
        "isdirect": "true",
    }
]

TRANSITVIEW_FIXTURE = {
    "bus": [
        {
            "lat": "40.00184",
            "lng": "-75.166223",
            "label": "7382",
            "route_id": "33",
            "trip": "876352",
            "VehicleID": "7382",
            "BlockID": "5155",
            "Direction": "Southbound",
            "destination": "5th-Market",
            "heading": 189.1,
            "late": 2,
            "next_stop_id": "3115",
            "next_stop_name": "22nd St & Clearfield Av",
            "next_stop_sequence": 8,
            "estimated_seat_availability": "FULL",
            "Offset": 2,
            "Offset_sec": "114",
            "timestamp": 1788886620,
        }
    ]
}

ALERTS_FIXTURE = [
    {
        "route": "CYN",
        "route_id": "rr_route_cyn",
        "route_name": "Cynwyd",
        "mode": "Regional Rail",
        "isadvisory": "Yes",
        "isdetour": "N",
        "isalert": "Y",
        "issuppend": "Y",
        "iselevator": "N",
        "issuspended": "Y",
        "isstrike": "N",
        "ismodifiedservice": "N",
        "isdelays": "N",
        "isdiversion": "N",
        "isdetouralert": "N",
        "isSnow": "N",
        "description": "Between Center City Philadelphia and Cynwyd",
        "alert": "<p>Service is suspended</p>",
    }
]

ELEVATOR_FIXTURE = {
    "meta": {"elevators_out": 10, "updated": "2026-09-08 12:57:04"},
    "results": [
        {
            "line": "Market Frankford Line",
            "station": "York-Dauphin",
            "elevator": "Westbound ",
            "message": "No access to/from station",
            "alternate_url": "https://www5.septa.org/about/accessibility/",
        }
    ],
}

METRO_TRIPS_FIXTURE = [
    {
        "route_id": "L1",
        "trip_id": "980251",
        "direction_id": 1,
        "trip_headsign": "69th St Transit Center",
        "vehicle_id": "None",
        "lat": None,
        "lon": None,
        "delay": 998,
        "status": "NO GPS",
    }
]


class StationResolutionTests(unittest.TestCase):
    def test_official_parameter_passthrough(self) -> None:
        self.assertEqual(resolve_station("Suburban Station"), "Suburban Station")
        self.assertEqual(resolve_station("Temple U"), "Temple U")

    def test_display_name_maps_to_api_parameter(self) -> None:
        self.assertEqual(resolve_station("Jefferson Station (Market East)"), "Market East")
        self.assertEqual(resolve_station("Temple University"), "Temple U")
        self.assertEqual(resolve_station("Penn Medicine Station (University City)"), "Penn Medicine Station")

    def test_aliases_and_combo_labels(self) -> None:
        self.assertEqual(resolve_station("Jefferson Station"), "Market East")
        self.assertEqual(resolve_station("Gray 30th Street"), "30th Street Station")
        self.assertEqual(
            api_name_from_choice("Jefferson Station (Market East) [Market East]"),
            "Market East",
        )

    def test_unknown_station_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_station("Not A Station")


class ParserTests(unittest.TestCase):
    def test_parse_arrivals_unwraps_dynamic_title_key(self) -> None:
        arrivals = parse_arrivals(ARRIVALS_FIXTURE)
        self.assertIn("Suburban Station Departures", arrivals.title)
        self.assertEqual(arrivals.northbound[0]["train_id"], "432")
        self.assertEqual(arrivals.southbound[0]["direction"], "S")
        self.assertIsNone(arrivals.northbound[0]["track_change"])

    def test_parse_arrivals_rejects_garbage(self) -> None:
        with self.assertRaises(SeptaAPIError):
            parse_arrivals([])

    def test_isdirect_string_from_live_api(self) -> None:
        self.assertTrue(coerce_bool("true"))
        self.assertFalse(coerce_bool("false"))
        self.assertTrue(coerce_bool(True))

    def test_delay_sentinel_values(self) -> None:
        self.assertEqual(format_delay(0), "On time")
        self.assertEqual(format_delay(-1), "On time")
        self.assertEqual(format_delay(2), "2 mins late")
        self.assertEqual(format_delay(999), "No GPS / unknown")
        self.assertEqual(format_delay(998), "No GPS / unknown")

    def test_alert_flags_and_html_stripping(self) -> None:
        self.assertTrue(route_has_issue(ALERTS_FIXTURE[0]))
        self.assertFalse(route_has_issue({"isalert": "N", "isadvisory": "No"}))
        self.assertEqual(strip_html("<p>Service is suspended</p>"), "Service is suspended")


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = MagicMock()
        self.client = SeptaClient(session=self.session)

    def _json_response(self, payload: object, content_type: str = "application/json") -> MagicMock:
        response = MagicMock()
        response.headers = {"Content-Type": content_type}
        response.text = json.dumps(payload)
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        return response

    def test_arrivals_uses_documented_query_params(self) -> None:
        self.session.get.return_value = self._json_response(ARRIVALS_FIXTURE)
        arrivals = self.client.get_arrivals("Suburban Station", results=5, direction="N")
        args, kwargs = self.session.get.call_args
        self.assertEqual(args[0], f"{DEFAULT_BASE_URL}/Arrivals/index.php")
        self.assertEqual(
            kwargs["params"],
            {"station": "Suburban Station", "results": 5, "direction": "N"},
        )
        self.assertEqual(arrivals.northbound[0]["train_id"], "432")

    def test_arrivals_resolves_jefferson_to_market_east(self) -> None:
        self.session.get.return_value = self._json_response(ARRIVALS_FIXTURE)
        self.client.get_arrivals("Jefferson Station")
        self.assertEqual(self.session.get.call_args.kwargs["params"]["station"], "Market East")

    def test_train_view_shape(self) -> None:
        self.session.get.return_value = self._json_response(TRAINVIEW_FIXTURE)
        trains = self.client.get_train_view()
        self.assertEqual(trains[0]["trainno"], "3218")
        self.assertEqual(trains[1]["late"], 999)

    def test_next_to_arrive_coerces_isdirect(self) -> None:
        self.session.get.return_value = self._json_response(NEXT_TO_ARRIVE_FIXTURE)
        rows = self.client.get_next_to_arrive("Suburban Station", "30th Street Station", 5)
        self.assertIs(rows[0]["isdirect"], True)
        params = self.session.get.call_args.kwargs["params"]
        self.assertEqual(params["req1"], "Suburban Station")
        self.assertEqual(params["req2"], "30th Street Station")
        self.assertEqual(params["req3"], 5)

    def test_transit_view_unwraps_bus_array(self) -> None:
        self.session.get.return_value = self._json_response(TRANSITVIEW_FIXTURE)
        buses = self.client.get_transit_view("33")
        self.assertEqual(buses[0]["VehicleID"], "7382")
        self.assertEqual(buses[0]["route_id"], "33")

    def test_alerts_and_elevators(self) -> None:
        self.session.get.return_value = self._json_response(ALERTS_FIXTURE)
        alerts = self.client.get_alerts("rr_route_cyn")
        self.assertEqual(alerts[0]["route_id"], "rr_route_cyn")
        self.session.get.return_value = self._json_response(ELEVATOR_FIXTURE)
        elevators = self.client.get_elevator_outages()
        self.assertEqual(elevators["meta"]["elevators_out"], 10)
        self.assertIn("alternate_url", elevators["results"][0])

    def test_metro_v2_paths(self) -> None:
        self.session.get.return_value = self._json_response(METRO_TRIPS_FIXTURE)
        trips = self.client.get_metro_trips("L1")
        self.assertEqual(self.session.get.call_args[0][0], f"{DEFAULT_BASE_URL}/v2/trips/")
        self.assertEqual(trips[0]["status"], "NO GPS")

        self.session.get.return_value = self._json_response({"trip": {}, "stop_times": []})
        self.client.get_metro_trip_update("980251")
        self.assertEqual(self.session.get.call_args[0][0], f"{DEFAULT_BASE_URL}/v2/trip-update/")

        self.session.get.return_value = self._json_response([])
        self.client.get_metro_stop_schedule("L1", "416")
        self.assertEqual(self.session.get.call_args[0][0], f"{DEFAULT_BASE_URL}/v2/stop-schedule/")

    def test_http_error_becomes_api_error(self) -> None:
        import requests

        self.session.get.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(SeptaAPIError):
            self.client.get_train_view()


@unittest.skipUnless(os.environ.get("SEPTA_LIVE") == "1", "set SEPTA_LIVE=1 to hit the public API")
class LiveApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = SeptaClient()

    def test_train_view_live(self) -> None:
        trains = self.client.get_train_view()
        self.assertIsInstance(trains, list)
        self.assertTrue(trains)
        self.assertIn("trainno", trains[0])

    def test_arrivals_live(self) -> None:
        arrivals = self.client.get_arrivals("Suburban Station", results=3)
        self.assertTrue(arrivals.title)
        self.assertTrue(arrivals.northbound or arrivals.southbound)

    def test_metro_trips_live(self) -> None:
        trips = self.client.get_metro_trips("L1")
        self.assertIsInstance(trips, list)
        self.assertEqual(trips[0]["route_id"], "L1")

    def test_next_to_arrive_and_jefferson_alias_live(self) -> None:
        rows = self.client.get_next_to_arrive("Jefferson Station", "Suburban Station", 3)
        self.assertIsInstance(rows, list)
        if rows:
            self.assertIn("orig_train", rows[0])
            self.assertIn("orig_delay", rows[0])

    def test_alerts_transit_and_elevators_live(self) -> None:
        alerts = self.client.get_alerts("rr_route_cyn")
        self.assertIsInstance(alerts, list)
        self.assertEqual(alerts[0]["route_id"], "rr_route_cyn")

        buses = self.client.get_transit_view("33")
        self.assertIsInstance(buses, list)
        if buses:
            self.assertTrue(buses[0].get("VehicleID") or buses[0].get("label"))

        elevators = self.client.get_elevator_outages()
        self.assertIn("meta", elevators)
        self.assertIn("results", elevators)


if __name__ == "__main__":
    unittest.main()
