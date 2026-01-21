# Sofia Traffic API Client - GitHub Copilot Instructions

## Project Overview

**sofiaclient** is a Python module that provides a clean interface to Sofia's public transportation GTFS (General Transit Feed Specification) data. It wraps real-time and static transit data from Sofia Traffic's APIs and provides **EfaClient compatibility** for Home Assistant integration.

## Architecture

### Core Components

```
sofiaclient/
├── __init__.py              # Public API exports
├── client.py                # SofiaClient (EfaClient compatible)
├── native_client.py         # SofiaNativeClient (extended features)
├── models.py                # Data models (Location, Line, Departure, etc.)
├── enums.py                 # Enums (TransportType, LocationFilter, etc.)
├── exceptions.py            # Custom exceptions
├── gtfs_parser.py           # GTFS static data parsing
├── realtime_parser.py       # GTFS Realtime protobuf parsing
├── cache.py                 # Static data caching with TTL
└── py.typed                 # PEP 561 marker for type hints
```

### API Endpoints

| Purpose | URL | Format |
|---------|-----|--------|
| Service Alerts | `{base_url}/alerts` | GTFS Realtime Protobuf |
| Trip Updates | `{base_url}/trip` | GTFS Realtime Protobuf |
| Vehicle Positions | `{base_url}/vehicle-positions` | GTFS Realtime Protobuf |
| Static Data | `{base_url}/static` | ZIP archive (GTFS) |

**Base URL:** `https://gtfs.sofiatraffic.bg/api/v1/`

## Coding Standards

### Tools in Use

- **Package Manager:** `uv` - Fast Python package installer
- **Type Checking:** `mypy` - Static type checker  
- **Formatting:** `ruff` - Fast Python linter and formatter
- **Testing:** `pytest` with `pytest-asyncio`, `pytest-httpx`
- **CI/CD:** GitHub Actions

### Code Style

- Follow PEP 8 standards (enforced by ruff)
- Use type hints for ALL public methods and functions
- Async/await patterns for network requests
- Comprehensive docstrings (Google style)
- Line length: 100 characters

### Public Interface Design

The library exposes two APIs:

1. **SofiaClient** - EfaClient-compatible for Home Assistant
2. **SofiaNativeClient** - Extended Sofia-specific features

#### EfaClient Compatible Usage

```python
from sofiaclient import SofiaClient, LocationFilter

async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Search stops by name
    stops = await client.locations_by_name("университет", filters=[LocationFilter.STOPS])
    
    # Get departures for a stop
    departures = await client.departures_by_location(
        stops[0].id,
        arg_date="14:30",
        realtime=True
    )
    
    for dep in departures:
        print(f"{dep.line_id}: {dep.planned_time} (delay: {dep.delay_minutes}min)")
```

#### Native Extended API

```python
from sofiaclient import SofiaNativeClient

async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Search routes by name
    routes = await client.search_routes("84")
    
    # Calculate trip time between stops
    trip_time = await client.calculate_trip_time(
        start_stop_id="123",
        end_stop_id="456",
        route_id="route_84"
    )
    
    print(f"Scheduled: {trip_time.scheduled_duration_str}")
    print(f"Real-time: {trip_time.realtime_duration_str}")
    print(f"Delay: {trip_time.delay_minutes} minutes")
```

## Development Guidelines

### When Adding Features

1. **Define clear type hints** for parameters and return values
2. **Add corresponding tests** in `tests/` directory  
3. **Update docstrings** with usage examples
4. **Handle API errors** gracefully with custom exceptions
5. **Cache static data** to minimize API calls

### When Working with GTFS Data

- Use `gtfs-realtime-bindings` for protobuf parsing
- Parse static GTFS once and cache (stops.txt, routes.txt, trips.txt, stop_times.txt)
- Merge real-time updates with static schedules
- Calculate delays by comparing TripUpdate times with static schedule

### Testing Approach

- **Mock external API calls** in tests using `pytest-httpx`
- **Provide sample GTFS data fixtures** in `tests/conftest.py`
- **Test edge cases:** no data, network errors, malformed responses
- **Ensure type checking passes** with `mypy`
- **Aim for >80% coverage**

### Error Handling

Custom exceptions:
- `SofiaClientError` - Base exception
- `EfaConnectionError` - Connection failures (EfaClient compatible)
- `EfaResponseInvalid` - Invalid responses (EfaClient compatible)
- `DataParseError` - GTFS parsing errors
- `CacheError` - Cache operation failures

**Best Practices:**
- Validate user inputs (stop_ids, time filters)
- Log warnings for data inconsistencies
- Provide meaningful error messages
- Always handle network timeouts

## Common Patterns

### Making API Requests

```python
import httpx
from google.transit import gtfs_realtime_pb2

async def fetch_realtime_feed(url: str) -> gtfs_realtime_pb2.FeedMessage:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
```

### Parsing Static GTFS

```python
import zipfile
import csv
from io import TextIOWrapper

def parse_stops(zip_path: str) -> dict[str, Location]:
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open('stops.txt') as f:
            reader = csv.DictReader(TextIOWrapper(f, 'utf-8'))
            return {
                row['stop_id']: Location.from_gtfs(
                    row['stop_id'],
                    row['stop_name'],
                    float(row['stop_lat']),
                    float(row['stop_lon'])
                )
                for row in reader
            }
```

### Caching with TTL

```python
from pathlib import Path
from datetime import datetime, timedelta

class GTFSCache:
    async def get_static_data(self, url: str) -> Path:
        cache_path = self.get_cache_path(url)
        
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age < self.ttl:
                # Check remote Last-Modified
                if not await self._remote_file_changed(cache_path):
                    return cache_path
        
        return await self._download_static_gtfs(url, cache_path)
```

## CI/CD Expectations

The GitHub Actions workflow runs:

1. **Lint:** `ruff check` for code quality
2. **Format:** `ruff format --check` for style consistency
3. **Type Check:** `mypy` for type safety
4. **Test:** `pytest` with coverage on Python 3.10, 3.11, 3.12
5. **Build:** Package building with `build`

All checks must pass before merging.

## Key Considerations

### Performance
- Cache static data with TTL and Last-Modified checking
- Minimize API requests (reuse parsed data)
- Use async/await for concurrent operations

### Reliability
- Handle network failures gracefully
- Implement retry logic for transient errors
- Validate all external data

### User Experience
- Simple, intuitive API
- Clear error messages
- Comprehensive documentation

### Maintainability
- Well-typed code (100% type coverage)
- Comprehensive tests (>80% coverage)
- Clear documentation and examples

## EfaClient Compatibility

The client must be a **drop-in replacement** for `apyefa.EfaClient` used in the Home Assistant `ha-departures` component.

### Required Interface

```python
class SofiaClient:
    def __init__(self, url: str): ...
    async def __aenter__(self): ...
    async def __aexit__(self, ...): ...
    
    async def locations_by_name(
        self, name: str, filters: list[LocationFilter] | None = None
    ) -> list[Location]: ...
    
    async def lines_by_location(
        self, location_id: str, req_types: list[LineRequestType] | None = None,
        show_trains_explicit: bool = False
    ) -> list[Line]: ...
    
    async def departures_by_location(
        self, location_id: str, arg_date: str | None = None, realtime: bool = False
    ) -> list[Departure]: ...
```

### Data Model Compatibility

Must provide:
- `Location` with `id`, `name`, `type`, `coord`
- `Line` with `id`, `name`, `number`, `product`, `destination`, `from_dict()`, `to_dict()`
- `Departure` with `line_id`, `planned_time`, `estimated_time`
- `TransportType` enum
- `EfaConnectionError` and `EfaResponseInvalid` exceptions

## Quick Reference

### Run Tests
```bash
pytest
pytest --cov=sofiaclient
```

### Code Quality
```bash
ruff check sofiaclient tests
ruff format sofiaclient tests
mypy sofiaclient
```

### Install for Development
```bash
uv pip install -e ".[dev]"
```

### Build Package
```bash
python -m build
```

## Resources

- GTFS Specification: https://gtfs.org/
- GTFS Realtime: https://gtfs.org/documentation/realtime/proto/
- gtfs-realtime-bindings: https://github.com/MobilityData/gtfs-realtime-bindings
- Home Assistant Component: https://github.com/alex-jung/ha-departures
