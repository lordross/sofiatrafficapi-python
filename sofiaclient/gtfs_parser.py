"""GTFS static data parser."""

import csv
import zipfile
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path
from typing import Any

from sofiaclient.exceptions import DataParseError
from sofiaclient.models import Destination, Line, Location


class GTFSStaticParser:
    """Parser for GTFS static data."""

    def __init__(self, gtfs_zip_path: Path) -> None:
        """Initialize parser with path to GTFS ZIP file."""
        self.gtfs_zip_path = gtfs_zip_path
        self._stops: dict[str, Location] = {}
        self._routes: dict[str, dict[str, Any]] = {}
        self._trips: dict[str, dict[str, Any]] = {}
        self._stop_times: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._route_destinations: dict[str, tuple[str, str]] = {}

    def parse(self) -> None:
        """Parse all GTFS static files."""
        try:
            with zipfile.ZipFile(self.gtfs_zip_path) as zf:
                self._parse_stops(zf)
                self._parse_routes(zf)
                self._parse_trips(zf)
                self._parse_stop_times(zf)
                self._compute_route_destinations()
        except (zipfile.BadZipFile, KeyError, ValueError) as e:
            raise DataParseError(f"Failed to parse GTFS data: {e}") from e

    def _parse_stops(self, zf: zipfile.ZipFile) -> None:
        """Parse stops.txt file."""
        with zf.open("stops.txt") as f:
            reader = csv.DictReader(TextIOWrapper(f, "utf-8"))
            for row in reader:
                stop_id = row["stop_id"]
                stop_name = row["stop_name"]
                lat = float(row["stop_lat"]) if row.get("stop_lat") else None
                lon = float(row["stop_lon"]) if row.get("stop_lon") else None
                self._stops[stop_id] = Location.from_gtfs(stop_id, stop_name, lat, lon)

    def _parse_routes(self, zf: zipfile.ZipFile) -> None:
        """Parse routes.txt file."""
        with zf.open("routes.txt") as f:
            reader = csv.DictReader(TextIOWrapper(f, "utf-8"))
            for row in reader:
                route_id = row["route_id"]
                self._routes[route_id] = {
                    "route_id": route_id,
                    "route_short_name": row.get("route_short_name", ""),
                    "route_long_name": row.get("route_long_name", ""),
                    "route_type": int(row["route_type"]) if row.get("route_type") else 3,
                }

    def _parse_trips(self, zf: zipfile.ZipFile) -> None:
        """Parse trips.txt file."""
        with zf.open("trips.txt") as f:
            reader = csv.DictReader(TextIOWrapper(f, "utf-8"))
            for row in reader:
                trip_id = row["trip_id"]
                self._trips[trip_id] = {
                    "trip_id": trip_id,
                    "route_id": row["route_id"],
                    "trip_headsign": row.get("trip_headsign", ""),
                    "direction_id": row.get("direction_id", "0"),
                }

    def _parse_stop_times(self, zf: zipfile.ZipFile) -> None:
        """Parse stop_times.txt file."""
        with zf.open("stop_times.txt") as f:
            reader = csv.DictReader(TextIOWrapper(f, "utf-8"))
            for row in reader:
                trip_id = row["trip_id"]
                self._stop_times[trip_id].append({
                    "trip_id": trip_id,
                    "stop_id": row["stop_id"],
                    "stop_sequence": int(row["stop_sequence"]),
                    "arrival_time": row["arrival_time"],
                    "departure_time": row["departure_time"],
                })

    def _compute_route_destinations(self) -> None:
        """Compute final destination for each route."""
        route_final_stops: dict[str, dict[int, str]] = defaultdict(dict)
        
        for trip_id, stop_times in self._stop_times.items():
            if not stop_times:
                continue
            
            trip = self._trips.get(trip_id)
            if not trip:
                continue
            
            route_id = trip["route_id"]
            direction_id = int(trip["direction_id"]) if trip.get("direction_id") else 0
            
            # Sort by stop_sequence and get last stop
            sorted_stops = sorted(stop_times, key=lambda x: x["stop_sequence"])
            final_stop_id = sorted_stops[-1]["stop_id"]
            
            # Store final stop for this route and direction
            route_final_stops[route_id][direction_id] = final_stop_id
        
        # For each route, use direction 0's final stop (or any available)
        for route_id, directions in route_final_stops.items():
            final_stop_id = directions.get(0) or next(iter(directions.values()))
            if final_stop_id in self._stops:
                stop = self._stops[final_stop_id]
                self._route_destinations[route_id] = (stop.id, stop.name)

    def get_stops(self) -> dict[str, Location]:
        """Get all parsed stops."""
        return self._stops

    def get_stop(self, stop_id: str) -> Location | None:
        """Get a specific stop by ID."""
        return self._stops.get(stop_id)

    def search_stops(self, query: str) -> list[Location]:
        """Search stops by name substring (case-insensitive)."""
        query_lower = query.lower()
        return [
            stop
            for stop in self._stops.values()
            if query_lower in stop.name.lower()
        ]

    def get_routes(self) -> dict[str, dict[str, Any]]:
        """Get all parsed routes."""
        return self._routes

    def get_route(self, route_id: str) -> dict[str, Any] | None:
        """Get a specific route by ID."""
        return self._routes.get(route_id)

    def search_routes(self, query: str) -> list[dict[str, Any]]:
        """Search routes by name or number (case-insensitive)."""
        query_lower = query.lower()
        return [
            route
            for route in self._routes.values()
            if query_lower in route.get("route_short_name", "").lower()
            or query_lower in route.get("route_long_name", "").lower()
        ]

    def get_routes_for_stop(self, stop_id: str) -> list[Line]:
        """Get all routes serving a specific stop."""
        routes_at_stop = set()
        
        # Find all trips that visit this stop
        for trip_id, stop_times in self._stop_times.items():
            if any(st["stop_id"] == stop_id for st in stop_times):
                trip = self._trips.get(trip_id)
                if trip:
                    routes_at_stop.add(trip["route_id"])
        
        # Build Line objects for each route
        lines = []
        for route_id in routes_at_stop:
            route = self._routes.get(route_id)
            if not route:
                continue
            
            dest_id, dest_name = self._route_destinations.get(
                route_id, ("unknown", "Unknown")
            )
            
            line = Line.from_gtfs(
                route_id=route["route_id"],
                route_short_name=route["route_short_name"],
                route_long_name=route["route_long_name"],
                route_type=route["route_type"],
                destination_stop_id=dest_id,
                destination_stop_name=dest_name,
            )
            lines.append(line)
        
        return lines

    def get_stop_times_for_trip(self, trip_id: str) -> list[dict[str, Any]]:
        """Get stop times for a specific trip."""
        return sorted(
            self._stop_times.get(trip_id, []),
            key=lambda x: x["stop_sequence"]
        )

    def get_trips_for_route(self, route_id: str) -> list[dict[str, Any]]:
        """Get all trips for a route."""
        return [
            trip
            for trip in self._trips.values()
            if trip["route_id"] == route_id
        ]

    def get_scheduled_time_between_stops(
        self, route_id: str, start_stop_id: str, end_stop_id: str
    ) -> int | None:
        """
        Get scheduled time between two stops on a route.
        
        Returns time in minutes, or None if stops not found on route.
        """
        trips = self.get_trips_for_route(route_id)
        
        for trip in trips:
            trip_id = trip["trip_id"]
            stop_times = self.get_stop_times_for_trip(trip_id)
            
            start_time = None
            end_time = None
            
            for st in stop_times:
                if st["stop_id"] == start_stop_id:
                    start_time = st["departure_time"]
                elif st["stop_id"] == end_stop_id:
                    end_time = st["arrival_time"]
            
            if start_time and end_time:
                # Parse GTFS time format (HH:MM:SS, can exceed 24 hours)
                start_minutes = self._parse_gtfs_time(start_time)
                end_minutes = self._parse_gtfs_time(end_time)
                
                if start_minutes is not None and end_minutes is not None:
                    return end_minutes - start_minutes
        
        return None

    @staticmethod
    def _parse_gtfs_time(time_str: str) -> int | None:
        """Parse GTFS time string to minutes since midnight."""
        try:
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        except (ValueError, IndexError):
            return None
