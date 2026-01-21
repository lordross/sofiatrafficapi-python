"""Shared test fixtures and utilities."""

import pytest
import shutil
import tempfile
from pathlib import Path


@pytest.fixture(scope="function", autouse=True)
def clean_cache():
    """Clean test cache directory before each test."""
    # Clean both the temp cache and the default home cache
    cache_dirs = [
        Path(tempfile.gettempdir()) / "sofiaclient_cache_test",
        Path.home() / ".cache" / "sofiaclient"
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    
    yield
    
    # Cleanup after test
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)


@pytest.fixture
def sample_stops_csv() -> str:
    """Sample stops.txt GTFS data."""
    return """stop_id,stop_name,stop_lat,stop_lon
1001,Централна гара,42.713564,23.323568
1002,Орлов мост,42.696506,23.318909
1003,НДК,42.684788,23.316872
1004,Софийски университет,42.696225,23.328735
"""


@pytest.fixture
def sample_routes_csv() -> str:
    """Sample routes.txt GTFS data."""
    return """route_id,route_short_name,route_long_name,route_type
84,84,Автобус 84,3
1,1,Трамвай 1,0
M2,M2,Метро линия 2,1
"""


@pytest.fixture
def sample_trips_csv() -> str:
    """Sample trips.txt GTFS data."""
    return """trip_id,route_id,trip_headsign,direction_id
trip_84_1,84,Лъвов мост,0
trip_84_2,84,Централна гара,1
trip_1_1,1,Княжево,0
"""


@pytest.fixture
def sample_stop_times_csv() -> str:
    """Sample stop_times.txt GTFS data."""
    return """trip_id,stop_id,stop_sequence,arrival_time,departure_time
trip_84_1,1001,1,08:00:00,08:00:00
trip_84_1,1002,2,08:05:00,08:05:00
trip_84_1,1003,3,08:10:00,08:10:00
trip_84_2,1003,1,09:00:00,09:00:00
trip_84_2,1002,2,09:05:00,09:05:00
trip_84_2,1001,3,09:10:00,09:10:00
trip_1_1,1004,1,10:00:00,10:00:00
trip_1_1,1003,2,10:15:00,10:15:00
"""


@pytest.fixture
def mock_gtfs_zip(tmp_path, sample_stops_csv, sample_routes_csv, sample_trips_csv, sample_stop_times_csv):
    """Create a mock GTFS ZIP file."""
    import zipfile
    
    zip_path = tmp_path / "gtfs.zip"
    
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("stops.txt", sample_stops_csv)
        zf.writestr("routes.txt", sample_routes_csv)
        zf.writestr("trips.txt", sample_trips_csv)
        zf.writestr("stop_times.txt", sample_stop_times_csv)
    
    return zip_path


@pytest.fixture
def sample_trip_update_protobuf() -> bytes:
    """Sample TripUpdate protobuf data."""
    from google.transit import gtfs_realtime_pb2
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 1234567890
    
    entity = feed.entity.add()
    entity.id = "1"
    
    trip_update = entity.trip_update
    trip_update.trip.trip_id = "trip_84_1"
    trip_update.trip.route_id = "84"
    
    stu = trip_update.stop_time_update.add()
    stu.stop_id = "1002"
    stu.stop_sequence = 2
    stu.arrival.delay = 120  # 2 minutes delay
    stu.departure.delay = 120
    
    return feed.SerializeToString()


@pytest.fixture
def sample_vehicle_position_protobuf() -> bytes:
    """Sample VehiclePosition protobuf data."""
    from google.transit import gtfs_realtime_pb2
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 1234567890
    
    entity = feed.entity.add()
    entity.id = "vehicle_1"
    
    vehicle = entity.vehicle
    vehicle.vehicle.id = "BUS_123"
    vehicle.trip.trip_id = "trip_84_1"
    vehicle.trip.route_id = "84"
    vehicle.position.latitude = 42.696506
    vehicle.position.longitude = 23.318909
    vehicle.timestamp = 1234567890
    
    return feed.SerializeToString()


@pytest.fixture
def sample_service_alert_protobuf() -> bytes:
    """Sample ServiceAlert protobuf data."""
    from google.transit import gtfs_realtime_pb2
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 1234567890
    
    entity = feed.entity.add()
    entity.id = "alert_1"
    
    alert = entity.alert
    
    # Add header text
    header = alert.header_text.translation.add()
    header.text = "Service disruption on route 84"
    
    # Add description
    desc = alert.description_text.translation.add()
    desc.text = "Delays expected due to traffic"
    
    # Add informed entity
    informed = alert.informed_entity.add()
    informed.route_id = "84"
    
    return feed.SerializeToString()
