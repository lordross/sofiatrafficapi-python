"""Data models for Sofia Traffic API client."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sofiaclient.enums import TransportType


@dataclass
class Location:
    """Represents a transit stop location."""

    id: str
    name: str
    type: str = "stop"
    coord: tuple[float, float] | None = None

    @classmethod
    def from_gtfs(cls, stop_id: str, stop_name: str, lat: float | None, lon: float | None) -> "Location":
        """Create Location from GTFS stop data."""
        coord = (lat, lon) if lat is not None and lon is not None else None
        return cls(id=stop_id, name=stop_name, type="stop", coord=coord)


@dataclass
class Destination:
    """Represents a route destination (final stop)."""

    id: str
    name: str
    type: str = "stop"

    @classmethod
    def from_gtfs(cls, stop_id: str, stop_name: str) -> "Destination":
        """Create Destination from GTFS stop data."""
        return cls(id=stop_id, name=stop_name, type="stop")


@dataclass
class Line:
    """Represents a transit line/route."""

    id: str
    name: str
    number: str
    product: TransportType
    description: str
    destination: Destination

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Line":
        """Create Line from dictionary."""
        dest_data = data.get("destination", {})
        destination = Destination(
            id=dest_data.get("id", ""),
            name=dest_data.get("name", ""),
            type=dest_data.get("type", "stop"),
        )
        
        product = data.get("product")
        if isinstance(product, int):
            product = TransportType(product)
        elif isinstance(product, str):
            product = TransportType[product]
        
        return cls(
            id=data["id"],
            name=data["name"],
            number=data["number"],
            product=product,
            description=data["description"],
            destination=destination,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert Line to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "number": self.number,
            "product": self.product.name,
            "description": self.description,
            "destination": {
                "id": self.destination.id,
                "name": self.destination.name,
                "type": self.destination.type,
            },
        }

    @classmethod
    def from_gtfs(
        cls,
        route_id: str,
        route_short_name: str,
        route_long_name: str,
        route_type: int,
        destination_stop_id: str,
        destination_stop_name: str,
    ) -> "Line":
        """Create Line from GTFS route data."""
        try:
            transport_type = TransportType(route_type)
        except ValueError:
            # Default to bus if route_type is unknown
            transport_type = TransportType.CITY_BUS

        return cls(
            id=route_id,
            name=route_short_name or route_long_name,
            number=route_short_name,
            product=transport_type,
            description=route_long_name,
            destination=Destination.from_gtfs(destination_stop_id, destination_stop_name),
        )


@dataclass
class Departure:
    """Represents a departure from a stop."""

    line_id: str
    planned_time: datetime | None
    estimated_time: datetime | None

    @property
    def delay_minutes(self) -> int | None:
        """Calculate delay in minutes."""
        if self.planned_time and self.estimated_time:
            delta = self.estimated_time - self.planned_time
            return int(delta.total_seconds() / 60)
        return None


@dataclass
class TripTime:
    """Represents trip time between two stops."""

    start_stop_id: str
    end_stop_id: str
    route_id: str
    scheduled_duration: int  # minutes
    realtime_duration: int | None  # minutes
    delay_minutes: int | None

    @property
    def scheduled_duration_str(self) -> str:
        """Format scheduled duration as string."""
        hours = self.scheduled_duration // 60
        minutes = self.scheduled_duration % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @property
    def realtime_duration_str(self) -> str | None:
        """Format real-time duration as string."""
        if self.realtime_duration is None:
            return None
        hours = self.realtime_duration // 60
        minutes = self.realtime_duration % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


@dataclass
class StopArrival:
    """Extended arrival information with more details."""

    stop_id: str
    stop_name: str
    route_id: str
    route_name: str
    vehicle_id: str | None
    scheduled_time: datetime
    estimated_time: datetime | None
    delay_minutes: int | None
    trip_id: str
    headsign: str | None = None
    alerts: list[str] = field(default_factory=list)
