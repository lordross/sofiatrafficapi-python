"""Sofia Traffic API Client - EfaClient compatible implementation."""

from datetime import datetime, time
from typing import Any

import httpx

from sofiaclient.cache import GTFSCache
from sofiaclient.enums import LineRequestType, LocationFilter, TransportType
from sofiaclient.exceptions import EfaConnectionError, EfaResponseInvalid
from sofiaclient.gtfs_parser import GTFSStaticParser
from sofiaclient.models import Departure, Line, Location
from sofiaclient.realtime_parser import GTFSRealtimeParser


class SofiaClient:
    """
    Sofia Traffic API client - drop-in replacement for EfaClient.
    
    Compatible with Home Assistant ha-departures component.
    """

    def __init__(self, url: str) -> None:
        """
        Initialize client.
        
        Args:
            url: Base URL (e.g., https://gtfs.sofiatraffic.bg/api/v1/)
        """
        self.base_url = url.rstrip("/")
        self._http_client: httpx.AsyncClient | None = None
        self._cache = GTFSCache()
        self._static_parser: GTFSStaticParser | None = None
        self._realtime_parser = GTFSRealtimeParser()

    async def __aenter__(self) -> "SofiaClient":
        """Async context manager entry."""
        self._http_client = httpx.AsyncClient(timeout=30.0)
        await self._ensure_static_data_loaded()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def _ensure_static_data_loaded(self) -> None:
        """Ensure static GTFS data is loaded."""
        if self._static_parser is not None:
            return

        try:
            static_url = f"{self.base_url}/static"
            cache_path = await self._cache.get_static_data(static_url)
            self._static_parser = GTFSStaticParser(cache_path)
            self._static_parser.parse()
        except Exception as e:
            raise EfaConnectionError(f"Failed to load static GTFS data: {e}") from e

    async def locations_by_name(
        self, name: str, filters: list[LocationFilter] | None = None
    ) -> list[Location]:
        """
        Search for locations (stops) by name.
        
        Args:
            name: Search query (substring match, case-insensitive)
            filters: Optional filters (only STOPS supported)
            
        Returns:
            List of matching Location objects
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return []

        # For now, we only support stops (not addresses or POIs)
        if filters and LocationFilter.STOPS not in filters:
            return []

        return self._static_parser.search_stops(name)

    async def lines_by_location(
        self,
        location_id: str,
        req_types: list[LineRequestType] | None = None,
        show_trains_explicit: bool = False,
    ) -> list[Line]:
        """
        Get all lines/routes serving a specific location.
        
        Args:
            location_id: Stop ID
            req_types: Request types (not used, for compatibility)
            show_trains_explicit: Whether to show trains (not used, for compatibility)
            
        Returns:
            List of Line objects serving the stop
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return []

        return self._static_parser.get_routes_for_stop(location_id)

    async def departures_by_location(
        self,
        location_id: str,
        arg_date: str | None = None,
        realtime: bool = False,
    ) -> list[Departure]:
        """
        Get departures for a specific location.
        
        Args:
            location_id: Stop ID
            arg_date: Time filter in "HH:MM" format (filters departures after this time)
            realtime: Whether to include real-time delay information
            
        Returns:
            List of Departure objects
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return []

        # Parse time filter
        filter_time = None
        if arg_date:
            try:
                time_obj = datetime.strptime(arg_date, "%H:%M").time()
                filter_time = datetime.combine(datetime.now().date(), time_obj)
            except ValueError:
                pass

        # Get all trips that visit this stop
        departures: list[Departure] = []
        stop_times_by_trip: dict[str, list[dict[str, Any]]] = {}

        # Collect all trips visiting this stop
        for trip_id, stop_times in self._static_parser._stop_times.items():
            for st in stop_times:
                if st["stop_id"] == location_id:
                    if trip_id not in stop_times_by_trip:
                        stop_times_by_trip[trip_id] = []
                    stop_times_by_trip[trip_id].append(st)

        # Get real-time updates if requested
        realtime_updates: dict[str, list[dict[str, Any]]] = {}
        if realtime:
            try:
                realtime_updates = await self._fetch_trip_updates()
            except Exception:
                # If real-time data fails, continue with static data only
                pass

        # Build departure list
        for trip_id, stop_times in stop_times_by_trip.items():
            trip = self._static_parser._trips.get(trip_id)
            if not trip:
                continue

            route_id = trip["route_id"]

            for st in stop_times:
                # Parse scheduled time
                departure_time_str = st["departure_time"]
                scheduled_time = self._parse_gtfs_time_to_datetime(departure_time_str)
                
                if not scheduled_time:
                    continue

                # Apply time filter
                if filter_time and scheduled_time < filter_time:
                    continue

                # Get real-time estimate
                estimated_time = None
                if realtime and location_id in realtime_updates:
                    best_match = None
                    best_time_diff = None

                    for update in realtime_updates[location_id]:
                        # Match by trip_id first (exact match)
                        if update["trip_id"] == trip_id:
                            best_match = update
                            break

                        # Match by route_id and find closest scheduled time
                        if update.get("route_id") == route_id:
                            update_time = update.get("departure_time") or update.get("arrival_time")
                            if update_time:
                                # Convert UTC to local time for comparison
                                if update_time.tzinfo is not None:
                                    update_time_local = update_time.astimezone().replace(tzinfo=None)
                                else:
                                    update_time_local = update_time

                                # Calculate time difference (positive = late, negative = early)
                                time_diff_seconds = (update_time_local - scheduled_time).total_seconds()
                                abs_time_diff = abs(time_diff_seconds)

                                # Only match if within 5 minutes of scheduled time
                                # This prevents matching wrong trips
                                if abs_time_diff < 300 and (best_time_diff is None or abs_time_diff < best_time_diff):
                                    best_time_diff = abs_time_diff
                                    best_match = update

                    if best_match:
                        if best_match.get("departure_time"):
                            # Convert UTC to local time
                            dep_time = best_match["departure_time"]
                            if dep_time.tzinfo is not None:
                                estimated_time = dep_time.astimezone().replace(tzinfo=None)
                            else:
                                estimated_time = dep_time
                        elif best_match.get("departure_delay") is not None:
                            from datetime import timedelta
                            estimated_time = scheduled_time + timedelta(
                                seconds=best_match["departure_delay"]
                            )

                # Get route info for line name and transport type
                route = self._static_parser._routes.get(route_id, {})
                line_name = route.get("route_short_name") or route.get("route_long_name")
                route_type_val = route.get("route_type", 3)
                try:
                    transport_type = TransportType(route_type_val)
                except ValueError:
                    transport_type = TransportType.CITY_BUS

                # Get headsign from trip data
                headsign = trip.get("trip_headsign")

                departure = Departure(
                    line_id=route_id,
                    planned_time=scheduled_time,
                    estimated_time=estimated_time,
                    line_name=line_name,
                    transport_type=transport_type,
                    headsign=headsign,
                )
                departures.append(departure)

        # Sort by planned time
        departures.sort(key=lambda d: d.planned_time or datetime.min)

        return departures

    async def _fetch_trip_updates(self) -> dict[str, list[dict[str, Any]]]:
        """Fetch real-time trip updates."""
        if not self._http_client:
            raise EfaConnectionError("HTTP client not initialized")

        try:
            trip_url = f"{self.base_url}/trip-updates"
            response = await self._http_client.get(trip_url)
            response.raise_for_status()
            return self._realtime_parser.parse_trip_updates(response.content)
        except httpx.HTTPError as e:
            raise EfaConnectionError(f"Failed to fetch trip updates: {e}") from e
        except Exception as e:
            raise EfaResponseInvalid(f"Failed to parse trip updates: {e}") from e

    def _parse_gtfs_time_to_datetime(self, time_str: str) -> datetime | None:
        """
        Parse GTFS time string to datetime.
        
        GTFS times can exceed 24 hours (e.g., "25:30:00" for 1:30 AM next day).
        """
        try:
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2]) if len(parts) > 2 else 0

            # Handle times >= 24 hours
            days = hours // 24
            hours = hours % 24

            base_datetime = datetime.combine(datetime.now().date(), time(hours, minutes, seconds))
            
            if days > 0:
                from datetime import timedelta
                base_datetime += timedelta(days=days)

            return base_datetime
        except (ValueError, IndexError):
            return None
