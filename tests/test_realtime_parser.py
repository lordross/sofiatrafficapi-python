"""Tests for GTFS Realtime parser."""

import pytest
from datetime import datetime

from sofiaclient.realtime_parser import GTFSRealtimeParser


def test_parse_trip_updates(sample_trip_update_protobuf):
    """Test parsing TripUpdate feed."""
    parser = GTFSRealtimeParser()
    updates = parser.parse_trip_updates(sample_trip_update_protobuf)
    
    # Should have updates for stop 1002
    assert "1002" in updates
    assert len(updates["1002"]) == 1
    
    update = updates["1002"][0]
    assert update["trip_id"] == "trip_84_1"
    assert update["route_id"] == "84"
    assert update["stop_id"] == "1002"
    assert update["arrival_delay"] == 120  # 2 minutes in seconds
    assert update["departure_delay"] == 120


def test_parse_vehicle_positions(sample_vehicle_position_protobuf):
    """Test parsing VehiclePosition feed."""
    parser = GTFSRealtimeParser()
    positions = parser.parse_vehicle_positions(sample_vehicle_position_protobuf)
    
    # Should have position for vehicle BUS_123
    assert "BUS_123" in positions
    
    pos = positions["BUS_123"]
    assert pos["vehicle_id"] == "BUS_123"
    assert pos["trip_id"] == "trip_84_1"
    assert pos["route_id"] == "84"
    assert abs(pos["latitude"] - 42.696506) < 0.0001
    assert abs(pos["longitude"] - 23.318909) < 0.0001


def test_parse_service_alerts(sample_service_alert_protobuf):
    """Test parsing ServiceAlert feed."""
    parser = GTFSRealtimeParser()
    alerts = parser.parse_service_alerts(sample_service_alert_protobuf)
    
    # Should have alerts for route 84
    assert "routes" in alerts
    assert "84" in alerts["routes"]
    assert len(alerts["routes"]["84"]) == 1
    
    alert = alerts["routes"]["84"][0]
    assert alert["header"] == "Service disruption on route 84"
    assert alert["description"] == "Delays expected due to traffic"


def test_parse_empty_feed():
    """Test parsing empty feed."""
    from google.transit import gtfs_realtime_pb2
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 1234567890
    
    parser = GTFSRealtimeParser()
    
    updates = parser.parse_trip_updates(feed.SerializeToString())
    assert len(updates) == 0
    
    positions = parser.parse_vehicle_positions(feed.SerializeToString())
    assert len(positions) == 0
    
    alerts = parser.parse_service_alerts(feed.SerializeToString())
    assert len(alerts["routes"]) == 0
    assert len(alerts["stops"]) == 0


def test_parse_invalid_protobuf():
    """Test parsing invalid protobuf data."""
    from sofiaclient.exceptions import DataParseError
    
    parser = GTFSRealtimeParser()
    
    with pytest.raises(DataParseError):
        parser.parse_trip_updates(b"invalid data")
    
    with pytest.raises(DataParseError):
        parser.parse_vehicle_positions(b"invalid data")
    
    with pytest.raises(DataParseError):
        parser.parse_service_alerts(b"invalid data")
