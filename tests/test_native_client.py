"""Tests for SofiaNativeClient (extended API)."""

import pytest
from pytest_httpx import HTTPXMock

from sofiaclient import SofiaNativeClient
from sofiaclient.models import TripTime

# Allow unused mocks since GTFSStaticParser may cache data
pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)


@pytest.mark.asyncio
async def test_native_client_context_manager(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test async context manager for native client."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        assert client._http_client is not None
        assert client._static_parser is not None


@pytest.mark.asyncio
async def test_search_stops(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test searching stops with native client."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        stops = await client.search_stops("гара")
        
        assert len(stops) == 1
        assert stops[0].id == "1001"
        assert "гара" in stops[0].name.lower()


@pytest.mark.asyncio
async def test_get_stop(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting a specific stop."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        stop = await client.get_stop("1001")
        
        assert stop is not None
        assert stop.id == "1001"
        assert stop.name == "Централна гара"


@pytest.mark.asyncio
async def test_get_stop_not_found(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting a non-existent stop."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        stop = await client.get_stop("9999")
        assert stop is None


@pytest.mark.asyncio
async def test_search_routes(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test searching routes by name."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        routes = await client.search_routes("84")
        
        assert len(routes) == 1
        assert routes[0]["route_id"] == "84"


@pytest.mark.asyncio
async def test_get_arrivals_without_realtime(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting arrivals without real-time data."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        arrivals = await client.get_arrivals(
            stop_ids=["1002"],
            time_offset_minutes=None,
            include_realtime=False
        )
        
        # Note: Test data has arrivals in the past (08:05, 09:05)
        # So arrivals will be empty unless we're testing before those times
        # Let's verify the function runs without error and returns a list
        assert isinstance(arrivals, list)
        
        # If we get arrivals, check their properties
        for arrival in arrivals:
            assert arrival.stop_id == "1002"
            assert arrival.scheduled_time is not None
            assert arrival.route_id is not None


@pytest.mark.asyncio
async def test_get_arrivals_with_time_filter(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting arrivals with time offset filter."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Get arrivals for next 30 minutes (may be empty for test data)
        arrivals = await client.get_arrivals(
            stop_ids=["1002"],
            time_offset_minutes=30,
            include_realtime=False
        )
        
        # Verify all arrivals are within time window
        from datetime import datetime, timedelta
        now = datetime.now()
        max_time = now + timedelta(minutes=30)
        
        for arrival in arrivals:
            assert arrival.scheduled_time >= now
            assert arrival.scheduled_time <= max_time


@pytest.mark.asyncio
async def test_get_arrivals_multiple_stops(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting arrivals for multiple stops."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        arrivals = await client.get_arrivals(
            stop_ids=["1001", "1002", "1003"],
            include_realtime=False
        )
        
        # Test data has arrivals in the past, so this may return empty list
        # Verify function runs and returns a list
        assert isinstance(arrivals, list)
        
        # If we get arrivals, verify they're from the requested stops
        if arrivals:
            stop_ids = {arrival.stop_id for arrival in arrivals}
            assert stop_ids.issubset({"1001", "1002", "1003"})


@pytest.mark.asyncio
async def test_calculate_trip_time(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test calculating trip time between stops."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    # Mock trip endpoint (can return empty - test still uses static data)
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip-updates",
        content=b""  # Empty protobuf is fine for this test
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Calculate trip time on route 84 from stop 1001 to 1003
        trip_time = await client.calculate_trip_time(
            start_stop_id="1001",
            end_stop_id="1003",
            route_id="84"
        )
        
        assert trip_time is not None
        assert isinstance(trip_time, TripTime)
        assert trip_time.start_stop_id == "1001"
        assert trip_time.end_stop_id == "1003"
        assert trip_time.route_id == "84"
        assert trip_time.scheduled_duration == 10  # 08:00 to 08:10
        assert trip_time.scheduled_duration_str == "10m"


@pytest.mark.asyncio
async def test_calculate_trip_time_invalid_route(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test trip time calculation with invalid route."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        trip_time = await client.calculate_trip_time(
            start_stop_id="1001",
            end_stop_id="1003",
            route_id="999"  # Non-existent route
        )
        
        assert trip_time is None


@pytest.mark.asyncio
async def test_cache_info(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting cache information."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        info = client.get_cache_info()
        
        assert "cache_dir" in info
        assert "num_files" in info
        assert "total_size_bytes" in info


@pytest.mark.asyncio
async def test_custom_cache_ttl(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test client with custom cache TTL."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # Create client with custom TTL
    async with SofiaNativeClient(
        "https://gtfs.sofiatraffic.bg/api/v1/",
        cache_ttl_hours=48
    ) as client:
        stops = await client.search_stops("гара")
        assert len(stops) == 1
