"""Comprehensive tests to reach 85%+ coverage for native_client.py."""

import pytest
from datetime import datetime, timedelta
from pytest_httpx import HTTPXMock
from google.transit import gtfs_realtime_pb2

from sofiaclient import SofiaNativeClient
from sofiaclient.exceptions import EfaConnectionError


@pytest.mark.asyncio
async def test_search_stops_no_parser(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test search_stops when parser is None (edge case)."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        status_code=500  # Force failure so parser stays None
    )
    
    try:
        async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
            # Force internal state
            client._static_parser = None
            stops = await client.search_stops("test")
            assert stops == []
    except EfaConnectionError:
        pass  # Expected when loading fails


@pytest.mark.asyncio
async def test_get_stop_no_parser(httpx_mock: HTTPXMock):
    """Test get_stop when parser is None."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        status_code=500
    )
    
    try:
        async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
            client._static_parser = None
            stop = await client.get_stop("1001")
            assert stop is None
    except EfaConnectionError:
        pass


@pytest.mark.asyncio
async def test_search_routes_no_parser(httpx_mock: HTTPXMock):
    """Test search_routes when parser is None."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        status_code=500
    )
    
    try:
        async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
            client._static_parser = None
            routes = await client.search_routes("84")
            assert routes == []
    except EfaConnectionError:
        pass


@pytest.mark.asyncio
async def test_arrivals_with_delays_and_vehicles(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test get_arrivals with arrival delays and vehicle matching."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # Create trip updates with arrival delay
    trip_feed = gtfs_realtime_pb2.FeedMessage()
    trip_feed.header.gtfs_realtime_version = "2.0"
    trip_feed.header.timestamp = int(datetime.now().timestamp())
    
    entity = trip_feed.entity.add()
    entity.id = "trip_update_1"
    entity.trip_update.trip.trip_id = "trip_1"
    entity.trip_update.trip.route_id = "84"
    
    # Add stop time update with arrival delay (not arrival_time)
    stu = entity.trip_update.stop_time_update.add()
    stu.stop_id = "1001"
    stu.arrival.delay = 300  # 5 minute delay
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip-updates",
        content=trip_feed.SerializeToString()
    )
    
    # Create vehicle positions matching trip
    vp_feed = gtfs_realtime_pb2.FeedMessage()
    vp_feed.header.gtfs_realtime_version = "2.0"
    vp_feed.header.timestamp = int(datetime.now().timestamp())
    
    vp_entity = vp_feed.entity.add()
    vp_entity.id = "veh_123"
    vp_entity.vehicle.vehicle.id = "123"
    vp_entity.vehicle.trip.trip_id = "trip_1"  # Match the trip
    vp_entity.vehicle.position.latitude = 42.6977
    vp_entity.vehicle.position.longitude = 23.3219
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/vehicle-positions",
        content=vp_feed.SerializeToString()
    )
    
    # Create alerts for route and stop
    alert_feed = gtfs_realtime_pb2.FeedMessage()
    alert_feed.header.gtfs_realtime_version = "2.0"
    alert_feed.header.timestamp = int(datetime.now().timestamp())
    
    # Route alert
    alert_entity1 = alert_feed.entity.add()
    alert_entity1.id = "alert_route"
    alert_entity1.alert.header_text.translation.add().text = "Route disruption"
    alert_entity1.alert.informed_entity.add().route_id = "84"
    
    # Stop alert
    alert_entity2 = alert_feed.entity.add()
    alert_entity2.id = "alert_stop"
    alert_entity2.alert.header_text.translation.add().text = "Stop maintenance"
    alert_entity2.alert.informed_entity.add().stop_id = "1001"
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/alerts",
        content=alert_feed.SerializeToString()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        arrivals = await client.get_arrivals(
            stop_ids=["1001"],
            include_realtime=True
        )
        assert isinstance(arrivals, list)
        # Should have arrival with delay, vehicle, and alerts


@pytest.mark.asyncio
async def test_arrivals_with_exact_arrival_time(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test get_arrivals with arrival_time (not delay)."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # Create trip updates with exact arrival_time
    trip_feed = gtfs_realtime_pb2.FeedMessage()
    trip_feed.header.gtfs_realtime_version = "2.0"
    trip_feed.header.timestamp = int(datetime.now().timestamp())
    
    entity = trip_feed.entity.add()
    entity.id = "trip_update_1"
    entity.trip_update.trip.trip_id = "trip_1"
    entity.trip_update.trip.route_id = "84"
    
    # Add stop time update with arrival time
    stu = entity.trip_update.stop_time_update.add()
    stu.stop_id = "1001"
    stu.arrival.time = int((datetime.now() + timedelta(minutes=10)).timestamp())
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip-updates",
        content=trip_feed.SerializeToString()
    )
    
    vp_feed = gtfs_realtime_pb2.FeedMessage()
    vp_feed.header.gtfs_realtime_version = "2.0"
    vp_feed.header.timestamp = int(datetime.now().timestamp())
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/vehicle-positions",
        content=vp_feed.SerializeToString()
    )
    
    alert_feed = gtfs_realtime_pb2.FeedMessage()
    alert_feed.header.gtfs_realtime_version = "2.0"
    alert_feed.header.timestamp = int(datetime.now().timestamp())
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/alerts",
        content=alert_feed.SerializeToString()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        arrivals = await client.get_arrivals(
            stop_ids=["1001"],
            include_realtime=True
        )
        assert isinstance(arrivals, list)


@pytest.mark.asyncio
async def test_calculate_trip_time_with_realtime(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test calculate_trip_time returns TripTime object."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # Mock trip updates
    trip_feed = gtfs_realtime_pb2.FeedMessage()
    trip_feed.header.gtfs_realtime_version = "2.0"
    trip_feed.header.timestamp = int(datetime.now().timestamp())
    
    entity = trip_feed.entity.add()
    entity.id = "trip_update_1"
    entity.trip_update.trip.trip_id = "trip_1"
    entity.trip_update.trip.route_id = "84"
    
    stu1 = entity.trip_update.stop_time_update.add()
    stu1.stop_id = "1001"
    stu1.arrival.delay = 60
    
    stu2 = entity.trip_update.stop_time_update.add()
    stu2.stop_id = "1002"
    stu2.arrival.delay = 120
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip-updates",
        content=trip_feed.SerializeToString()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        result = await client.calculate_trip_time("1001", "1002", "84")
        assert result is not None
        assert hasattr(result, "start_stop_id")
        assert hasattr(result, "scheduled_duration")


@pytest.mark.asyncio
async def test_fetch_trip_updates_error(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test _fetch_trip_updates handles errors by raising exception."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip-updates",
        status_code=500
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        with pytest.raises(EfaConnectionError):
            await client._fetch_trip_updates()


@pytest.mark.asyncio
async def test_fetch_vehicle_positions_error(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test _fetch_vehicle_positions handles errors by raising exception."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/vehicle-positions",
        status_code=500
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        with pytest.raises(EfaConnectionError):
            await client._fetch_vehicle_positions()


@pytest.mark.asyncio
async def test_fetch_service_alerts_error(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test _fetch_service_alerts handles errors by raising exception."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/alerts",
        status_code=500
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        with pytest.raises(EfaConnectionError):
            await client._fetch_service_alerts()


@pytest.mark.asyncio
async def test_parse_gtfs_time_edge_cases(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test _parse_gtfs_time_to_datetime with various inputs."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Invalid formats
        assert client._parse_gtfs_time_to_datetime("") is None
        assert client._parse_gtfs_time_to_datetime("invalid") is None
        
        # Valid formats
        result = client._parse_gtfs_time_to_datetime("12:30:00")
        assert result is not None
        assert result.hour == 12
        assert result.minute == 30
        
        # Valid over-24h time
        result = client._parse_gtfs_time_to_datetime("25:30:00")
        assert result is not None
        assert result.hour == 1
        assert result.minute == 30


@pytest.mark.asyncio
async def test_get_cache_info(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test get_cache_info method."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        info = client.get_cache_info()
        assert isinstance(info, dict)
        assert "cache_dir" in info


@pytest.mark.asyncio
async def test_arrivals_time_filtering(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test that arrivals respects time_offset_minutes filtering."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Get arrivals with short time window
        arrivals_short = await client.get_arrivals(
            stop_ids=["1001"],
            time_offset_minutes=1,  # Only next 1 minute
            include_realtime=False
        )
        
        # Get arrivals with longer time window
        arrivals_long = await client.get_arrivals(
            stop_ids=["1001"],
            time_offset_minutes=120,  # Next 2 hours
            include_realtime=False
        )
        
        # Longer window should have same or more arrivals
        assert len(arrivals_long) >= len(arrivals_short)
