"""Tests for SofiaClient (EfaClient compatible)."""

import pytest
from pytest_httpx import HTTPXMock

from sofiaclient import SofiaClient, LocationFilter
from sofiaclient.exceptions import EfaConnectionError

# Allow unused mocks since GTFSStaticParser may cache data
pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)


@pytest.mark.asyncio
async def test_client_context_manager(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test async context manager."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        assert client._http_client is not None
        assert client._static_parser is not None
    
    # Client should be closed after exiting context
    assert client._http_client is None


@pytest.mark.asyncio
async def test_locations_by_name(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test searching locations by name."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Search for "гара"
        locations = await client.locations_by_name("гара", filters=[LocationFilter.STOPS])
        
        assert len(locations) == 1
        assert locations[0].id == "1001"
        assert locations[0].name == "Централна гара"
        assert locations[0].type == "stop"


@pytest.mark.asyncio
async def test_locations_by_name_case_insensitive(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test case-insensitive search."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        locations = await client.locations_by_name("ндк")
        
        assert len(locations) == 1
        assert "НДК" in locations[0].name


@pytest.mark.asyncio
async def test_lines_by_location(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting lines for a location."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Get lines for stop 1003 (НДК)
        lines = await client.lines_by_location("1003")
        
        assert len(lines) >= 2
        route_ids = [line.id for line in lines]
        assert "84" in route_ids
        assert "1" in route_ids
        
        # Check line properties
        line_84 = next(l for l in lines if l.id == "84")
        assert line_84.name == "84"
        assert line_84.number == "84"


@pytest.mark.asyncio
async def test_departures_by_location_without_realtime(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test getting departures without real-time data."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Get departures for stop 1002
        departures = await client.departures_by_location("1002", realtime=False)
        
        # Should have at least 2 departures (from both directions of route 84)
        assert len(departures) >= 2
        
        # All should have line_id and planned_time
        for dep in departures:
            assert dep.line_id is not None
            assert dep.planned_time is not None
            assert dep.estimated_time is None  # No real-time data


@pytest.mark.asyncio
async def test_departures_with_time_filter(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test departures with time filter."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Filter to show only departures after 09:00
        departures = await client.departures_by_location("1002", arg_date="09:00", realtime=False)
        
        # Should have at least the 09:05 departure
        assert len(departures) >= 1
        
        # All departures should be after filter time
        from datetime import time as dt_time
        filter_time = dt_time(9, 0)
        for dep in departures:
            if dep.planned_time:
                assert dep.planned_time.time() >= filter_time


@pytest.mark.asyncio
async def test_connection_error(httpx_mock: HTTPXMock):
    """Test handling of connection errors when loading static data."""
    # Mock network error on static data load (no cache exists)
    httpx_mock.add_exception(
        Exception("Network error"),
        url="https://gtfs.sofiatraffic.bg/api/v1/static"
    )
    
    # Should raise error when trying to initialize client  
    client = SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/")
    with pytest.raises(EfaConnectionError):
        await client.__aenter__()


@pytest.mark.asyncio
async def test_client_with_trailing_slash(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test client handles URL with trailing slash."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    # URL with trailing slash
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        locations = await client.locations_by_name("гара")
        assert len(locations) == 1
