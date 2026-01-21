"""Sofia Native Client - Extended API with Sofia-specific features."""

from datetime import datetime, timedelta
from typing import Any

import httpx

from sofiaclient.cache import GTFSCache
from sofiaclient.exceptions import EfaConnectionError, EfaResponseInvalid
from sofiaclient.gtfs_parser import GTFSStaticParser
from sofiaclient.models import Line, Location, StopArrival, TripTime
from sofiaclient.realtime_parser import GTFSRealtimeParser


class SofiaNativeClient:
    """
    Native Sofia Traffic API client with extended features.
    
    Provides Sofia-specific functionality beyond EfaClient compatibility.
    """

    def __init__(self, url: str, cache_ttl_hours: int = 24) -> None:
        """
        Initialize client.
        
        Args:
            url: Base URL (e.g., https://gtfs.sofiatraffic.bg/api/v1/)
            cache_ttl_hours: Cache TTL in hours
        """
        self.base_url = url.rstrip("/")
        self._http_client: httpx.AsyncClient | None = None
        self._cache = GTFSCache(ttl_hours=cache_ttl_hours)
        self._static_parser: GTFSStaticParser | None = None
        self._realtime_parser = GTFSRealtimeParser()

    async def __aenter__(self) -> "SofiaNativeClient":
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

    async def search_stops(self, query: str) -> list[Location]:
        """
        Search for stops by name.
        
        Args:
            query: Search query (substring match, case-insensitive)
            
        Returns:
            List of matching stops
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return []

        return self._static_parser.search_stops(query)

    async def get_stop(self, stop_id: str) -> Location | None:
        """
        Get stop by ID.
        
        Args:
            stop_id: Stop ID
            
        Returns:
            Location object or None if not found
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return None

        return self._static_parser.get_stop(stop_id)

    async def search_routes(self, query: str) -> list[dict[str, Any]]:
        """
        Search for routes by name or number.
        
        Args:
            query: Search query (substring match, case-insensitive)
            
        Returns:
            List of matching routes
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return []

        return self._static_parser.search_routes(query)

    async def get_arrivals(
        self,
        stop_ids: list[str],
        time_offset_minutes: int | None = None,
        include_realtime: bool = True,
    ) -> list[StopArrival]:
        """
        Get arrivals for multiple stops with time filtering.
        
        Args:
            stop_ids: List of stop IDs
            time_offset_minutes: Only show arrivals within this many minutes (None = all)
            include_realtime: Include real-time delay information
            
        Returns:
            List of StopArrival objects sorted by arrival time
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return []

        # Calculate time filter
        now = datetime.now()
        max_time = None
        if time_offset_minutes is not None:
            max_time = now + timedelta(minutes=time_offset_minutes)

        # Get real-time updates if requested
        realtime_updates: dict[str, list[dict[str, Any]]] = {}
        vehicle_positions: dict[str, dict[str, Any]] = {}
        alerts_data: dict[str, Any] = {}
        
        if include_realtime:
            try:
                realtime_updates = await self._fetch_trip_updates()
                vehicle_positions = await self._fetch_vehicle_positions()
                alerts_data = await self._fetch_service_alerts()
            except Exception:
                # Continue with static data only if real-time fails
                pass

        arrivals: list[StopArrival] = []

        # Process each stop
        for stop_id in stop_ids:
            stop = self._static_parser.get_stop(stop_id)
            if not stop:
                continue

            # Find all trips visiting this stop
            for trip_id, stop_times in self._static_parser._stop_times.items():
                for st in stop_times:
                    if st["stop_id"] != stop_id:
                        continue

                    trip = self._static_parser._trips.get(trip_id)
                    if not trip:
                        continue

                    route_id = trip["route_id"]
                    route = self._static_parser.get_route(route_id)
                    if not route:
                        continue

                    # Parse scheduled time
                    arrival_time_str = st["arrival_time"]
                    scheduled_time = self._parse_gtfs_time_to_datetime(arrival_time_str)
                    
                    if not scheduled_time:
                        continue

                    # Apply time filter
                    if scheduled_time < now:
                        continue
                    if max_time and scheduled_time > max_time:
                        continue

                    # Get real-time estimate and vehicle info
                    estimated_time = None
                    vehicle_id = None
                    delay_minutes = None

                    if include_realtime and stop_id in realtime_updates:
                        for update in realtime_updates[stop_id]:
                            if update["trip_id"] == trip_id:
                                if update.get("arrival_time"):
                                    estimated_time = update["arrival_time"]
                                elif update.get("arrival_delay") is not None:
                                    estimated_time = scheduled_time + timedelta(
                                        seconds=update["arrival_delay"]
                                    )
                                    delay_minutes = update["arrival_delay"] // 60
                                break

                    # Find vehicle
                    for veh_id, veh_data in vehicle_positions.items():
                        if veh_data.get("trip_id") == trip_id:
                            vehicle_id = veh_id
                            break

                    # Get alerts for this route/stop
                    alert_messages = []
                    if "routes" in alerts_data and route_id in alerts_data["routes"]:
                        for alert in alerts_data["routes"][route_id]:
                            if alert.get("header"):
                                alert_messages.append(alert["header"])
                    
                    if "stops" in alerts_data and stop_id in alerts_data["stops"]:
                        for alert in alerts_data["stops"][stop_id]:
                            if alert.get("header"):
                                alert_messages.append(alert["header"])

                    arrival = StopArrival(
                        stop_id=stop_id,
                        stop_name=stop.name,
                        route_id=route_id,
                        route_name=route.get("route_short_name", route.get("route_long_name", "")),
                        vehicle_id=vehicle_id,
                        scheduled_time=scheduled_time,
                        estimated_time=estimated_time,
                        delay_minutes=delay_minutes,
                        trip_id=trip_id,
                        headsign=trip.get("trip_headsign"),
                        alerts=alert_messages,
                    )
                    arrivals.append(arrival)

        # Sort by scheduled time
        arrivals.sort(key=lambda a: a.scheduled_time)

        return arrivals

    async def calculate_trip_time(
        self, start_stop_id: str, end_stop_id: str, route_id: str
    ) -> TripTime | None:
        """
        Calculate trip time between two stops on a route.
        
        Args:
            start_stop_id: Starting stop ID
            end_stop_id: Ending stop ID
            route_id: Route ID (line ID)
            
        Returns:
            TripTime object with scheduled and real-time durations, or None if not found
        """
        await self._ensure_static_data_loaded()
        
        if not self._static_parser:
            return None

        # Get scheduled time from static data
        scheduled_minutes = self._static_parser.get_scheduled_time_between_stops(
            route_id, start_stop_id, end_stop_id
        )

        if scheduled_minutes is None:
            return None

        # Try to get real-time data
        realtime_minutes = None
        delay_minutes = None

        try:
            realtime_updates = await self._fetch_trip_updates()
            
            # Find a trip on this route that visits both stops
            trips = self._static_parser.get_trips_for_route(route_id)
            
            for trip in trips:
                trip_id = trip["trip_id"]
                
                # Get updates for both stops
                start_delay = None
                end_delay = None

                if start_stop_id in realtime_updates:
                    for update in realtime_updates[start_stop_id]:
                        if update["trip_id"] == trip_id and update.get("departure_delay") is not None:
                            start_delay = update["departure_delay"] // 60  # Convert to minutes
                            break

                if end_stop_id in realtime_updates:
                    for update in realtime_updates[end_stop_id]:
                        if update["trip_id"] == trip_id and update.get("arrival_delay") is not None:
                            end_delay = update["arrival_delay"] // 60  # Convert to minutes
                            break

                # Calculate real-time duration
                if start_delay is not None and end_delay is not None:
                    realtime_minutes = scheduled_minutes + (end_delay - start_delay)
                    delay_minutes = end_delay - start_delay
                    break

        except Exception:
            # If real-time data fails, return with scheduled time only
            pass

        return TripTime(
            start_stop_id=start_stop_id,
            end_stop_id=end_stop_id,
            route_id=route_id,
            scheduled_duration=scheduled_minutes,
            realtime_duration=realtime_minutes,
            delay_minutes=delay_minutes,
        )

    async def _fetch_trip_updates(self) -> dict[str, list[dict[str, Any]]]:
        """Fetch real-time trip updates."""
        if not self._http_client:
            raise EfaConnectionError("HTTP client not initialized")

        try:
            trip_url = f"{self.base_url}/trip"
            response = await self._http_client.get(trip_url)
            response.raise_for_status()
            return self._realtime_parser.parse_trip_updates(response.content)
        except httpx.HTTPError as e:
            raise EfaConnectionError(f"Failed to fetch trip updates: {e}") from e
        except Exception as e:
            raise EfaResponseInvalid(f"Failed to parse trip updates: {e}") from e

    async def _fetch_vehicle_positions(self) -> dict[str, dict[str, Any]]:
        """Fetch real-time vehicle positions."""
        if not self._http_client:
            raise EfaConnectionError("HTTP client not initialized")

        try:
            vehicle_url = f"{self.base_url}/vehicle-positions"
            response = await self._http_client.get(vehicle_url)
            response.raise_for_status()
            return self._realtime_parser.parse_vehicle_positions(response.content)
        except httpx.HTTPError as e:
            raise EfaConnectionError(f"Failed to fetch vehicle positions: {e}") from e
        except Exception as e:
            raise EfaResponseInvalid(f"Failed to parse vehicle positions: {e}") from e

    async def _fetch_service_alerts(self) -> dict[str, Any]:
        """Fetch service alerts."""
        if not self._http_client:
            raise EfaConnectionError("HTTP client not initialized")

        try:
            alerts_url = f"{self.base_url}/alerts"
            response = await self._http_client.get(alerts_url)
            response.raise_for_status()
            return self._realtime_parser.parse_service_alerts(response.content)
        except httpx.HTTPError as e:
            raise EfaConnectionError(f"Failed to fetch service alerts: {e}") from e
        except Exception as e:
            raise EfaResponseInvalid(f"Failed to parse service alerts: {e}") from e

    def _parse_gtfs_time_to_datetime(self, time_str: str) -> datetime | None:
        """
        Parse GTFS time string to datetime.
        
        GTFS times can exceed 24 hours (e.g., "25:30:00" for 1:30 AM next day).
        """
        try:
            from datetime import time
            
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2]) if len(parts) > 2 else 0

            # Handle times >= 24 hours
            days = hours // 24
            hours = hours % 24

            base_datetime = datetime.combine(datetime.now().date(), time(hours, minutes, seconds))
            
            if days > 0:
                base_datetime += timedelta(days=days)

            return base_datetime
        except (ValueError, IndexError):
            return None

    def get_cache_info(self) -> dict[str, Any]:
        """Get cache information."""
        return self._cache.get_cache_info()

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear_cache()
        self._static_parser = None
