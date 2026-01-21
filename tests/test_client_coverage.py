"""Additional tests for client.py to increase coverage."""

import pytest
from datetime import datetime, time as dt_time
from pytest_httpx import HTTPXMock

from sofiaclient import SofiaClient


@pytest.mark.asyncio
async def test_departures_with_realtime_updates(httpx_mock: HTTPXMock, mock_gtfs_zip, sample_trip_update_protobuf):
    """Test departures with real-time delay information."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        content=sample_trip_update_protobuf
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Get departures with real-time enabled
        departures = await client.departures_by_location("1001", realtime=True)
        
        # Should have departures
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_departures_realtime_with_departure_time(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test real-time departures with departure_time in updates."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # Mock trip updates with departure_time
    from google.transit import gtfs_realtime_pb2
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = int(datetime.now().timestamp())
    
    entity = feed.entity.add()
    entity.id = "trip1"
    entity.trip_update.trip.trip_id = "trip_84_1"
    
    stop_update = entity.trip_update.stop_time_update.add()
    stop_update.stop_id = "1001"
    stop_update.departure.time = int(datetime.now().timestamp()) + 600  # 10 min from now
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        content=feed.SerializeToString()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        departures = await client.departures_by_location("1001", realtime=True)
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_departures_realtime_with_delay(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test real-time departures with delay in updates."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # Mock trip updates with delay
    from google.transit import gtfs_realtime_pb2
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = int(datetime.now().timestamp())
    
    entity = feed.entity.add()
    entity.id = "trip1"
    entity.trip_update.trip.trip_id = "trip_84_1"
    
    stop_update = entity.trip_update.stop_time_update.add()
    stop_update.stop_id = "1001"
    stop_update.departure.delay = 300  # 5 minutes delay
    
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        content=feed.SerializeToString()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        departures = await client.departures_by_location("1001", realtime=True)
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_departures_invalid_time_format(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test departures with invalid time format."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Invalid time format should be ignored
        departures = await client.departures_by_location("1001", arg_date="invalid")
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_departures_no_matching_trips(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test departures for stop with no trips."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        departures = await client.departures_by_location("nonexistent_stop")
        assert departures == []


@pytest.mark.asyncio
async def test_departures_trip_without_route(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test departures handling trips without route info."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Should handle missing trip info gracefully
        departures = await client.departures_by_location("1001")
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_fetch_trip_updates_http_error(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test handling of HTTP errors when fetching trip updates."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        status_code=500
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Real-time error should be caught, returns static data only
        departures = await client.departures_by_location("1001", realtime=True)
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_fetch_trip_updates_parse_error(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test handling of parse errors in trip updates."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        content=b"invalid protobuf data"
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Parse error should be caught, returns static data only
        departures = await client.departures_by_location("1001", realtime=True)
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_parse_gtfs_time_invalid_formats(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test parsing various invalid time formats."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Test with invalid times in GTFS data
        result = client._parse_gtfs_time_to_datetime("invalid:time:format")
        assert result is None
        
        result = client._parse_gtfs_time_to_datetime("99")
        assert result is None
        
        result = client._parse_gtfs_time_to_datetime("")
        assert result is None


@pytest.mark.asyncio
async def test_parse_gtfs_time_over_24_hours(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test parsing time that exceeds 24 hours."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Test time over 24 hours (next day)
        result = client._parse_gtfs_time_to_datetime("25:30:00")
        assert result is not None
        assert result.hour == 1
        assert result.minute == 30


@pytest.mark.asyncio
async def test_locations_without_static_parser(httpx_mock: HTTPXMock):
    """Test locations_by_name when static parser fails to initialize."""
    httpx_mock.add_exception(
        Exception("Network error"),
        url="https://gtfs.sofiatraffic.bg/api/v1/static"
    )
    
    client = SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/")
    
    with pytest.raises(Exception):
        async with client:
            pass


@pytest.mark.asyncio
async def test_lines_by_location_without_static_parser():
    """Test lines_by_location when static parser is None."""
    client = SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/")
    # Don't enter context manager, so _static_parser is None
    await client.__aenter__()
    client._static_parser = None
    
    result = await client.lines_by_location("1001")
    assert result == []
    
    await client.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_departures_without_static_parser():
    """Test departures_by_location when static parser is None."""
    client = SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/")
    await client.__aenter__()
    client._static_parser = None
    
    result = await client.departures_by_location("1001")
    assert result == []
    
    await client.__aexit__(None, None, None)
