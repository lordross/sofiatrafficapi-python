"""Tests for CLI commands."""

import io
import sys
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from cli.sofia_cli import print_arrival, print_departure, print_line, print_location, print_trip_time
from sofiaclient.models import Departure, Line, Location, StopArrival, TripTime
from sofiaclient.enums import TransportType


class TestPrintArrival:
    """Tests for print_arrival function."""

    def test_print_arrival_basic(self, capsys):
        """Test printing basic arrival without real-time data."""
        arrival = StopArrival(
            stop_id="1001",
            stop_name="Централна гара",
            route_id="84",
            route_name="84",
            vehicle_id=None,
            scheduled_time=datetime(2024, 1, 15, 8, 30, 0),
            estimated_time=None,
            delay_minutes=None,
            trip_id="trip_84_1",
            headsign=None,
            alerts=[],
        )

        print_arrival(arrival)
        captured = capsys.readouterr()

        assert "Stop ID: 1001" in captured.out
        assert "Stop Name: Централна гара" in captured.out
        assert "Route: 84 - 84" in captured.out
        assert "Scheduled: 08:30:00" in captured.out
        assert "Estimated:" not in captured.out
        assert "Delay:" not in captured.out
        assert "Vehicle:" not in captured.out

    def test_print_arrival_with_realtime_data(self, capsys):
        """Test printing arrival with real-time data."""
        arrival = StopArrival(
            stop_id="1002",
            stop_name="Орлов мост",
            route_id="84",
            route_name="84",
            vehicle_id="BUS_123",
            scheduled_time=datetime(2024, 1, 15, 9, 0, 0),
            estimated_time=datetime(2024, 1, 15, 9, 3, 0),
            delay_minutes=3,
            trip_id="trip_84_1",
            headsign="Лъвов мост",
            alerts=[],
        )

        print_arrival(arrival)
        captured = capsys.readouterr()

        assert "Stop ID: 1002" in captured.out
        assert "Stop Name: Орлов мост" in captured.out
        assert "Route: 84 - 84" in captured.out
        assert "Scheduled: 09:00:00" in captured.out
        assert "Estimated: 09:03:00" in captured.out
        assert "Delay: +3 min" in captured.out
        assert "Vehicle: BUS_123" in captured.out
        assert "Headsign: Лъвов мост" in captured.out

    def test_print_arrival_early(self, capsys):
        """Test printing arrival that is early."""
        arrival = StopArrival(
            stop_id="1003",
            stop_name="НДК",
            route_id="1",
            route_name="1",
            vehicle_id=None,
            scheduled_time=datetime(2024, 1, 15, 10, 0, 0),
            estimated_time=datetime(2024, 1, 15, 9, 58, 0),
            delay_minutes=-2,
            trip_id="trip_1_1",
            headsign=None,
            alerts=[],
        )

        print_arrival(arrival)
        captured = capsys.readouterr()

        assert "Delay: -2 min (early)" in captured.out

    def test_print_arrival_on_time(self, capsys):
        """Test printing arrival that is on time."""
        arrival = StopArrival(
            stop_id="1003",
            stop_name="НДК",
            route_id="1",
            route_name="1",
            vehicle_id=None,
            scheduled_time=datetime(2024, 1, 15, 10, 0, 0),
            estimated_time=datetime(2024, 1, 15, 10, 0, 0),
            delay_minutes=0,
            trip_id="trip_1_1",
            headsign=None,
            alerts=[],
        )

        print_arrival(arrival)
        captured = capsys.readouterr()

        assert "Delay: On time" in captured.out

    def test_print_arrival_with_alerts(self, capsys):
        """Test printing arrival with alerts."""
        arrival = StopArrival(
            stop_id="1001",
            stop_name="Централна гара",
            route_id="84",
            route_name="84",
            vehicle_id=None,
            scheduled_time=datetime(2024, 1, 15, 8, 30, 0),
            estimated_time=None,
            delay_minutes=None,
            trip_id="trip_84_1",
            headsign=None,
            alerts=["Service disruption", "Delays expected"],
        )

        print_arrival(arrival)
        captured = capsys.readouterr()

        assert "Alerts: 2" in captured.out
        assert "- Service disruption" in captured.out
        assert "- Delays expected" in captured.out


class TestPrintLocation:
    """Tests for print_location function."""

    def test_print_location_with_coords(self, capsys):
        """Test printing location with coordinates."""
        location = Location(
            id="1001",
            name="Централна гара",
            type="stop",
            coord=(42.713564, 23.323568),
        )

        print_location(location)
        captured = capsys.readouterr()

        assert "Stop ID: 1001" in captured.out
        assert "Name: Централна гара" in captured.out
        assert "Coordinates: 42.713564, 23.323568" in captured.out

    def test_print_location_without_coords(self, capsys):
        """Test printing location without coordinates."""
        location = Location(
            id="1002",
            name="Орлов мост",
            type="stop",
            coord=None,
        )

        print_location(location)
        captured = capsys.readouterr()

        assert "Stop ID: 1002" in captured.out
        assert "Name: Орлов мост" in captured.out
        assert "Coordinates:" not in captured.out


class TestPrintLine:
    """Tests for print_line function."""

    def test_print_line(self, capsys):
        """Test printing line details."""
        from sofiaclient.models import Destination

        line = Line(
            id="84",
            name="84",
            number="84",
            product=TransportType.CITY_BUS,
            description="Автобус 84",
            destination=Destination(id="1001", name="Централна гара", type="stop"),
        )

        print_line(line)
        captured = capsys.readouterr()

        assert "Route ID: 84" in captured.out
        assert "Name: 84" in captured.out
        assert "Type: TransportType.CITY_BUS" in captured.out
        assert "GTFS Route Type: 3" in captured.out


class TestPrintTripTime:
    """Tests for print_trip_time function."""

    def test_print_trip_time_scheduled_only(self, capsys):
        """Test printing trip time with scheduled duration only."""
        trip_time = TripTime(
            start_stop_id="1001",
            end_stop_id="1003",
            route_id="84",
            scheduled_duration=10,
            realtime_duration=None,
            delay_minutes=None,
        )

        print_trip_time(trip_time)
        captured = capsys.readouterr()

        assert "From: 1001" in captured.out
        assert "To: 1003" in captured.out
        assert "Route: 84" in captured.out
        assert "Scheduled Duration: 10m" in captured.out
        assert "Estimated Duration:" not in captured.out
        assert "Delay:" not in captured.out

    def test_print_trip_time_with_realtime(self, capsys):
        """Test printing trip time with real-time data."""
        trip_time = TripTime(
            start_stop_id="1001",
            end_stop_id="1003",
            route_id="84",
            scheduled_duration=10,
            realtime_duration=12,
            delay_minutes=2,
        )

        print_trip_time(trip_time)
        captured = capsys.readouterr()

        assert "Scheduled Duration: 10m" in captured.out
        assert "Estimated Duration: 12m" in captured.out
        assert "Delay: 120 seconds" in captured.out


class TestPrintDeparture:
    """Tests for print_departure function."""

    def test_print_departure_without_realtime(self, capsys):
        """Test printing departure without real-time data."""
        departure = Departure(
            line_id="84",
            planned_time=datetime(2024, 1, 15, 8, 0, 0),
            estimated_time=None,
        )

        print_departure(departure)
        captured = capsys.readouterr()

        assert "Line: 84" in captured.out
        assert "Scheduled: 08:00:00" in captured.out
        assert "Estimated:" not in captured.out

    def test_print_departure_with_realtime(self, capsys):
        """Test printing departure with real-time data."""
        departure = Departure(
            line_id="84",
            planned_time=datetime(2024, 1, 15, 8, 0, 0),
            estimated_time=datetime(2024, 1, 15, 8, 2, 0),
        )

        print_departure(departure)
        captured = capsys.readouterr()

        assert "Line: 84" in captured.out
        assert "Scheduled: 08:00:00" in captured.out
        assert "Estimated: 08:02:00" in captured.out
        assert "Delay: +2 min" in captured.out

    def test_print_departure_early(self, capsys):
        """Test printing departure that is early."""
        departure = Departure(
            line_id="84",
            planned_time=datetime(2024, 1, 15, 8, 0, 0),
            estimated_time=datetime(2024, 1, 15, 7, 58, 0),
        )

        print_departure(departure)
        captured = capsys.readouterr()

        assert "Delay: -2 min (early)" in captured.out

    def test_print_departure_on_time(self, capsys):
        """Test printing departure that is on time."""
        departure = Departure(
            line_id="84",
            planned_time=datetime(2024, 1, 15, 8, 0, 0),
            estimated_time=datetime(2024, 1, 15, 8, 0, 0),
        )

        print_departure(departure)
        captured = capsys.readouterr()

        assert "Delay: On time" in captured.out
