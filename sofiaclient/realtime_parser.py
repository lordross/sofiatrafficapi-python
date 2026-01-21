"""GTFS Realtime data parser."""

from datetime import datetime, timezone
from typing import Any

from google.transit import gtfs_realtime_pb2

from sofiaclient.exceptions import DataParseError


class GTFSRealtimeParser:
    """Parser for GTFS Realtime protobuf data."""

    @staticmethod
    def parse_trip_updates(feed_data: bytes) -> dict[str, list[dict[str, Any]]]:
        """
        Parse TripUpdate feed and return stop time updates by stop_id.
        
        Returns dict mapping stop_id to list of updates for that stop.
        """
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)
        except Exception as e:
            raise DataParseError(f"Failed to parse TripUpdate feed: {e}") from e

        updates_by_stop: dict[str, list[dict[str, Any]]] = {}

        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue

            trip_update = entity.trip_update
            trip_id = trip_update.trip.trip_id
            route_id = trip_update.trip.route_id if trip_update.trip.HasField("route_id") else None

            for stop_time_update in trip_update.stop_time_update:
                stop_id = stop_time_update.stop_id
                
                arrival_delay = None
                arrival_time = None
                departure_delay = None
                departure_time = None

                if stop_time_update.HasField("arrival"):
                    if stop_time_update.arrival.HasField("delay"):
                        arrival_delay = stop_time_update.arrival.delay
                    if stop_time_update.arrival.HasField("time"):
                        arrival_time = datetime.fromtimestamp(
                            stop_time_update.arrival.time, tz=timezone.utc
                        )

                if stop_time_update.HasField("departure"):
                    if stop_time_update.departure.HasField("delay"):
                        departure_delay = stop_time_update.departure.delay
                    if stop_time_update.departure.HasField("time"):
                        departure_time = datetime.fromtimestamp(
                            stop_time_update.departure.time, tz=timezone.utc
                        )

                update = {
                    "trip_id": trip_id,
                    "route_id": route_id,
                    "stop_id": stop_id,
                    "stop_sequence": stop_time_update.stop_sequence,
                    "arrival_delay": arrival_delay,
                    "arrival_time": arrival_time,
                    "departure_delay": departure_delay,
                    "departure_time": departure_time,
                }

                if stop_id not in updates_by_stop:
                    updates_by_stop[stop_id] = []
                updates_by_stop[stop_id].append(update)

        return updates_by_stop

    @staticmethod
    def parse_vehicle_positions(feed_data: bytes) -> dict[str, dict[str, Any]]:
        """
        Parse VehiclePosition feed and return positions by vehicle_id.
        
        Returns dict mapping vehicle_id to position data.
        """
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)
        except Exception as e:
            raise DataParseError(f"Failed to parse VehiclePosition feed: {e}") from e

        positions: dict[str, dict[str, Any]] = {}

        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue

            vehicle = entity.vehicle
            
            vehicle_id = None
            if vehicle.vehicle.HasField("id"):
                vehicle_id = vehicle.vehicle.id
            elif vehicle.vehicle.HasField("label"):
                vehicle_id = vehicle.vehicle.label

            if not vehicle_id:
                continue

            trip_id = vehicle.trip.trip_id if vehicle.HasField("trip") else None
            route_id = vehicle.trip.route_id if vehicle.HasField("trip") and vehicle.trip.HasField("route_id") else None
            
            position_data = {
                "vehicle_id": vehicle_id,
                "trip_id": trip_id,
                "route_id": route_id,
                "latitude": vehicle.position.latitude if vehicle.HasField("position") else None,
                "longitude": vehicle.position.longitude if vehicle.HasField("position") else None,
                "timestamp": datetime.fromtimestamp(vehicle.timestamp, tz=timezone.utc) if vehicle.HasField("timestamp") else None,
                "current_stop_sequence": vehicle.current_stop_sequence if vehicle.HasField("current_stop_sequence") else None,
                "stop_id": vehicle.stop_id if vehicle.HasField("stop_id") else None,
            }

            positions[vehicle_id] = position_data

        return positions

    @staticmethod
    def parse_service_alerts(feed_data: bytes) -> dict[str, list[dict[str, Any]]]:
        """
        Parse ServiceAlert feed and return alerts by route_id or stop_id.
        
        Returns dict with 'routes' and 'stops' keys containing alerts.
        """
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)
        except Exception as e:
            raise DataParseError(f"Failed to parse ServiceAlert feed: {e}") from e

        alerts_by_route: dict[str, list[dict[str, Any]]] = {}
        alerts_by_stop: dict[str, list[dict[str, Any]]] = {}

        for entity in feed.entity:
            if not entity.HasField("alert"):
                continue

            alert = entity.alert
            
            # Extract alert text
            header = ""
            description = ""
            
            for text in alert.header_text.translation:
                header = text.text
                break
            
            for text in alert.description_text.translation:
                description = text.text
                break

            alert_data = {
                "alert_id": entity.id,
                "header": header,
                "description": description,
                "cause": alert.cause if alert.HasField("cause") else None,
                "effect": alert.effect if alert.HasField("effect") else None,
            }

            # Associate alert with affected routes and stops
            for informed_entity in alert.informed_entity:
                if informed_entity.HasField("route_id"):
                    route_id = informed_entity.route_id
                    if route_id not in alerts_by_route:
                        alerts_by_route[route_id] = []
                    alerts_by_route[route_id].append(alert_data)

                if informed_entity.HasField("stop_id"):
                    stop_id = informed_entity.stop_id
                    if stop_id not in alerts_by_stop:
                        alerts_by_stop[stop_id] = []
                    alerts_by_stop[stop_id].append(alert_data)

        return {
            "routes": alerts_by_route,
            "stops": alerts_by_stop,
        }
