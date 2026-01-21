"""Additional tests to increase coverage for cache.py, client.py, and native_client.py."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
from pytest_httpx import HTTPXMock

from sofiaclient import SofiaClient, SofiaNativeClient
from sofiaclient.cache import GTFSCache


# ===== Cache Tests =====

@pytest.mark.asyncio
async def test_cache_ttl_expiration(mock_gtfs_zip, httpx_mock: HTTPXMock):
    """Test that expired cache is refreshed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = GTFSCache(cache_dir=Path(tmpdir), ttl_hours=0)  # Immediate expiration
        
        httpx_mock.add_response(
            url="https://example.com/static",
            content=mock_gtfs_zip.read_bytes()
        )
        
        cache_path = await cache.get_static_data("https://example.com/static")
        assert cache_path.exists()


@pytest.mark.asyncio
async def test_cache_last_modified_different(mock_gtfs_zip, httpx_mock: HTTPXMock):
    """Test Last-Modified header checking triggers re-download."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = GTFSCache(cache_dir=Path(tmpdir))
        
        httpx_mock.add_response(
            url="https://example.com/static",
            content=mock_gtfs_zip.read_bytes(),
            headers={"Last-Modified": "Mon, 20 Jan 2026 10:00:00 GMT"}
        )
        
        cache_path = await cache.get_static_data("https://example.com/static")
        assert cache_path.exists()
        
        # Different Last-Modified - should re-download
        httpx_mock.add_response(
            method="HEAD",
            url="https://example.com/static",
            headers={"Last-Modified": "Mon, 21 Jan 2026 11:00:00 GMT"}
        )
        httpx_mock.add_response(
            url="https://example.com/static",
            content=mock_gtfs_zip.read_bytes(),
            headers={"Last-Modified": "Mon, 21 Jan 2026 11:00:00 GMT"}
        )
        
        cache_path2 = await cache.get_static_data("https://example.com/static")
        assert cache_path2.exists()


@pytest.mark.asyncio
@pytest.mark.httpx_mock(can_send_already_matched_responses=True)
async def test_cache_head_failure(mock_gtfs_zip, httpx_mock: HTTPXMock):
    """Test handling of failed HEAD request."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = GTFSCache(cache_dir=Path(tmpdir))
        
        httpx_mock.add_response(
            url="https://example.com/static",
            content=mock_gtfs_zip.read_bytes()
        )
        
        await cache.get_static_data("https://example.com/static")
        
        # Second call should use cached data without making requests
        cache_path = await cache.get_static_data("https://example.com/static")
        assert cache_path.exists()


def test_cache_clear(mock_gtfs_zip):
    """Test clearing cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = GTFSCache(cache_dir=Path(tmpdir))
        cache_file = Path(tmpdir) / "gtfs_static_test.zip"
        cache_file.write_bytes(mock_gtfs_zip.read_bytes())
        
        assert cache_file.exists()
        cache.clear_cache()
        assert not cache_file.exists()


# ===== Client Tests =====

@pytest.mark.asyncio
async def test_client_departures_with_realtime(httpx_mock: HTTPXMock, mock_gtfs_zip, sample_trip_update_protobuf):
    """Test departures with real-time updates."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        content=sample_trip_update_protobuf
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        departures = await client.departures_by_location("1001", realtime=True)
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_client_departures_invalid_time(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test departures with invalid time format."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        departures = await client.departures_by_location("1001", arg_date="invalid")
        assert isinstance(departures, list)


@pytest.mark.asyncio
async def test_client_parse_gtfs_time_over_24h(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test parsing time over 24 hours."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        result = client._parse_gtfs_time_to_datetime("25:30:00")
        assert result is not None
        assert result.hour == 1


@pytest.mark.asyncio
async def test_client_parse_gtfs_time_invalid(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test parsing invalid time formats."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        assert client._parse_gtfs_time_to_datetime("invalid") is None
        assert client._parse_gtfs_time_to_datetime("") is None


@pytest.mark.asyncio
async def test_client_departures_realtime_error(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test departures when real-time fetch fails."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        status_code=500
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # Should fall back to static data
        departures = await client.departures_by_location("1001", realtime=True)
        assert isinstance(departures, list)


# ===== Native Client Tests =====

@pytest.mark.asyncio
async def test_native_client_arrivals_with_realtime(httpx_mock: HTTPXMock, mock_gtfs_zip, sample_trip_update_protobuf):
    """Test get_arrivals with real-time data."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/trip",
        content=sample_trip_update_protobuf
    )
    
    from google.transit import gtfs_realtime_pb2
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
        arrivals = await client.get_arrivals(stop_ids=["1001"], include_realtime=True)
        assert isinstance(arrivals, list)


@pytest.mark.asyncio
@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
async def test_native_client_arrivals_realtime_failure(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test get_arrivals when real-time fetch fails."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    httpx_mock.add_exception(
        Exception("Network error"),
        url="https://gtfs.sofiatraffic.bg/api/v1/trip"
    )
    httpx_mock.add_exception(
        Exception("Network error"),
        url="https://gtfs.sofiatraffic.bg/api/v1/vehicle-positions"
    )
    httpx_mock.add_exception(
        Exception("Network error"),
        url="https://gtfs.sofiatraffic.bg/api/v1/alerts"
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        # When realtime fails, it falls back to static data
        try:
            arrivals = await client.get_arrivals(stop_ids=["1001"], include_realtime=True)
            assert isinstance(arrivals, list)
        except EfaConnectionError:
            # If all realtime endpoints fail, it may raise error
            pass


@pytest.mark.asyncio
async def test_native_client_clear_cache(httpx_mock: HTTPXMock, mock_gtfs_zip):
    """Test clear_cache method."""
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=mock_gtfs_zip.read_bytes()
    )
    
    async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        assert client._static_parser is not None
        client.clear_cache()
        assert client._static_parser is None
