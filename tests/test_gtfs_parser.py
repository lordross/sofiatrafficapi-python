"""Tests for GTFS static data parser."""

import pytest

from sofiaclient.gtfs_parser import GTFSStaticParser
from sofiaclient.enums import TransportType


def test_parse_stops(mock_gtfs_zip):
    """Test parsing stops from GTFS data."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    stops = parser.get_stops()
    
    assert len(stops) == 4
    assert "1001" in stops
    assert stops["1001"].name == "Централна гара"
    assert stops["1001"].coord == (42.713564, 23.323568)


def test_parse_routes(mock_gtfs_zip):
    """Test parsing routes from GTFS data."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    routes = parser.get_routes()
    
    assert len(routes) == 3
    assert "84" in routes
    assert routes["84"]["route_short_name"] == "84"
    assert routes["84"]["route_type"] == 3  # Bus


def test_search_stops(mock_gtfs_zip):
    """Test searching stops by name."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    # Search for "гара" (station)
    results = parser.search_stops("гара")
    assert len(results) == 1
    assert results[0].name == "Централна гара"
    
    # Search for "мост" (bridge)
    results = parser.search_stops("мост")
    assert len(results) == 1
    assert results[0].name == "Орлов мост"
    
    # Case insensitive
    results = parser.search_stops("ндк")
    assert len(results) == 1


def test_search_routes(mock_gtfs_zip):
    """Test searching routes by name."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    # Search by number
    results = parser.search_routes("84")
    assert len(results) == 1
    assert results[0]["route_id"] == "84"
    
    # Search by name
    results = parser.search_routes("метро")
    assert len(results) == 1
    assert results[0]["route_id"] == "M2"


def test_get_routes_for_stop(mock_gtfs_zip):
    """Test getting routes serving a stop."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    # Stop 1003 (НДК) is served by route 84 and route 1
    lines = parser.get_routes_for_stop("1003")
    
    assert len(lines) >= 2
    route_ids = [line.id for line in lines]
    assert "84" in route_ids
    assert "1" in route_ids
    
    # Check line properties
    line_84 = next(l for l in lines if l.id == "84")
    assert line_84.name == "84"
    assert line_84.product == TransportType.CITY_BUS


def test_get_scheduled_time_between_stops(mock_gtfs_zip):
    """Test calculating scheduled time between stops."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    # Route 84: stop 1001 -> stop 1003 should be 10 minutes
    duration = parser.get_scheduled_time_between_stops("84", "1001", "1003")
    assert duration == 10
    
    # Route 84: stop 1002 -> stop 1003 should be 5 minutes
    duration = parser.get_scheduled_time_between_stops("84", "1002", "1003")
    assert duration == 5


def test_get_scheduled_time_invalid_route(mock_gtfs_zip):
    """Test calculating time with invalid route."""
    parser = GTFSStaticParser(mock_gtfs_zip)
    parser.parse()
    
    duration = parser.get_scheduled_time_between_stops("999", "1001", "1003")
    assert duration is None


def test_parse_gtfs_time():
    """Test GTFS time parsing."""
    parser = GTFSStaticParser(None)
    
    # Normal time
    assert parser._parse_gtfs_time("08:30:00") == 8 * 60 + 30
    
    # Time after midnight (next day)
    assert parser._parse_gtfs_time("25:30:00") == 25 * 60 + 30
    
    # Invalid time
    assert parser._parse_gtfs_time("invalid") is None
