"""Tests for data models."""

import pytest
from datetime import datetime

from sofiaclient.enums import TransportType
from sofiaclient.models import Departure, Destination, Line, Location, StopArrival, TripTime


def test_location_from_gtfs():
    """Test Location creation from GTFS data."""
    location = Location.from_gtfs("123", "Test Stop", 42.696506, 23.318909)
    
    assert location.id == "123"
    assert location.name == "Test Stop"
    assert location.type == "stop"
    assert location.coord == (42.696506, 23.318909)


def test_location_from_gtfs_no_coords():
    """Test Location creation without coordinates."""
    location = Location.from_gtfs("123", "Test Stop", None, None)
    
    assert location.id == "123"
    assert location.coord is None


def test_destination_from_gtfs():
    """Test Destination creation from GTFS data."""
    dest = Destination.from_gtfs("456", "Final Stop")
    
    assert dest.id == "456"
    assert dest.name == "Final Stop"
    assert dest.type == "stop"


def test_line_from_dict():
    """Test Line creation from dictionary."""
    data = {
        "id": "84",
        "name": "84",
        "number": "84",
        "product": "CITY_BUS",
        "description": "Bus 84",
        "destination": {
            "id": "789",
            "name": "Final Stop",
            "type": "stop"
        }
    }
    
    line = Line.from_dict(data)
    
    assert line.id == "84"
    assert line.name == "84"
    assert line.number == "84"
    assert line.product == TransportType.CITY_BUS
    assert line.description == "Bus 84"
    assert line.destination.id == "789"
    assert line.destination.name == "Final Stop"


def test_line_to_dict():
    """Test Line conversion to dictionary."""
    dest = Destination(id="789", name="Final Stop")
    line = Line(
        id="84",
        name="84",
        number="84",
        product=TransportType.CITY_BUS,
        description="Bus 84",
        destination=dest
    )
    
    data = line.to_dict()
    
    assert data["id"] == "84"
    assert data["product"] == "CITY_BUS"
    assert data["destination"]["id"] == "789"


def test_line_from_gtfs():
    """Test Line creation from GTFS data."""
    line = Line.from_gtfs(
        route_id="84",
        route_short_name="84",
        route_long_name="Bus 84",
        route_type=3,
        destination_stop_id="789",
        destination_stop_name="Final Stop"
    )
    
    assert line.id == "84"
    assert line.name == "84"
    assert line.product == TransportType.CITY_BUS
    assert line.destination.id == "789"


def test_departure_delay_calculation():
    """Test Departure delay calculation."""
    planned = datetime(2026, 1, 21, 14, 30)
    estimated = datetime(2026, 1, 21, 14, 35)
    
    departure = Departure(
        line_id="84",
        planned_time=planned,
        estimated_time=estimated
    )
    
    assert departure.delay_minutes == 5


def test_departure_no_delay():
    """Test Departure with no delay information."""
    planned = datetime(2026, 1, 21, 14, 30)
    
    departure = Departure(
        line_id="84",
        planned_time=planned,
        estimated_time=None
    )
    
    assert departure.delay_minutes is None


def test_trip_time_formatted_durations():
    """Test TripTime duration formatting."""
    trip_time = TripTime(
        start_stop_id="123",
        end_stop_id="456",
        route_id="84",
        scheduled_duration=75,  # 1h 15m
        realtime_duration=80,   # 1h 20m
        delay_minutes=5
    )
    
    assert trip_time.scheduled_duration_str == "1h 15m"
    assert trip_time.realtime_duration_str == "1h 20m"


def test_trip_time_minutes_only():
    """Test TripTime with minutes only."""
    trip_time = TripTime(
        start_stop_id="123",
        end_stop_id="456",
        route_id="84",
        scheduled_duration=30,
        realtime_duration=None,
        delay_minutes=None
    )
    
    assert trip_time.scheduled_duration_str == "30m"
    assert trip_time.realtime_duration_str is None


def test_stop_arrival_with_alerts():
    """Test StopArrival with alerts."""
    arrival = StopArrival(
        stop_id="123",
        stop_name="Test Stop",
        route_id="84",
        route_name="84",
        vehicle_id="BUS_123",
        scheduled_time=datetime(2026, 1, 21, 14, 30),
        estimated_time=datetime(2026, 1, 21, 14, 33),
        delay_minutes=3,
        trip_id="trip_123",
        headsign="Final Stop",
        alerts=["Service disruption", "Delays expected"]
    )
    
    assert arrival.stop_id == "123"
    assert arrival.vehicle_id == "BUS_123"
    assert arrival.delay_minutes == 3
    assert len(arrival.alerts) == 2
    assert "Service disruption" in arrival.alerts
