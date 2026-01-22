# Sofia Traffic API Client - AI Agent Instructions

## Project Overview

**sofiaclient** is a Python GTFS wrapper for Sofia's public transportation API. It provides two interfaces:

1. **SofiaClient** - EfaClient-compatible for Home Assistant `ha-departures` component
2. **SofiaNativeClient** - Extended Sofia-specific features (trip time calculation, route search)

## Architecture

### Dual-Client Design

Two client classes share the same backend (cache, parsers):

```
sofiaclient/
├── client.py           # SofiaClient (EfaClient interface: locations_by_name, departures_by_location)
├── native_client.py    # SofiaNativeClient (calculate_trip_time, search_routes, get_stop_arrivals)
├── gtfs_parser.py      # Parses static GTFS ZIP (stops.txt, routes.txt, trips.txt, stop_times.txt)
├── realtime_parser.py  # Merges protobuf feeds (TripUpdate, VehiclePosition) with static schedules
├── cache.py            # Downloads/caches static GTFS with TTL + Last-Modified checks
├── models.py           # Location, Line, Departure, TripTime, StopArrival
└── exceptions.py       # EfaConnectionError, EfaResponseInvalid (HA-compatible)
```

### Data Flow

```
API Request → _ensure_static_data_loaded() → GTFSCache → GTFSStaticParser
                                                ↓
                                          Parse once, reuse
                                                ↓
                          GTFSRealtimeParser.fetch_realtime_updates()
                                                ↓
                          Merge static + realtime → Return results
```

**GTFS Endpoints:** `{base_url}/static` (ZIP), `{base_url}/trip-updates` (protobuf), `{base_url}/vehicle-positions` (protobuf)

## Development Toolchain

**Critical:** Use `uv` for all package operations (NOT pip/pip3):

```bash
# Install project in editable mode
uv pip install -e ".[dev]"

# Quality checks (run before committing)
ruff check sofiaclient tests      # Linting
ruff format sofiaclient tests     # Auto-format
mypy sofiaclient                  # Type checking (must pass 100%)

# Testing
pytest                            # Run all tests
pytest --cov=sofiaclient          # With coverage (target: >80%)
pytest tests/test_client.py::test_locations_by_name  # Single test
```

**CI Pipeline (`.github/workflows/ci.yml`):** Tests run on Python 3.10, 3.11, 3.12 with separate lint/typecheck/test jobs.

## Project-Specific Patterns

### 1. GTFS Static Data Lazy Loading

Both clients defer loading until first API call via `_ensure_static_data_loaded()`:

```python
# In client.py and native_client.py
async def _ensure_static_data_loaded(self) -> None:
    if self._static_parser is not None:
        return  # Already loaded
    
    static_url = f"{self.base_url}/static"
    cache_path = await self._cache.get_static_data(static_url)  # Handles TTL + Last-Modified
    self._static_parser = GTFSStaticParser(cache_path)
    self._static_parser.parse()  # Parses all GTFS files into memory
```

**Why:** Avoids downloading 2MB ZIP on import, only when needed.

### 2. Cache TTL with Remote Modified Check

`GTFSCache` (cache.py) implements dual-validation:

```python
# Age-based TTL (default 24h)
if age > self.ttl:
    return False

# Last-Modified header check (even if within TTL)
remote_modified = await self._get_remote_last_modified(url)
if remote_modified and remote_modified > local_modified:
    return False  # Redownload
```

Cache location: `~/.cache/sofiaclient/gtfs_static_{md5(url)}.zip`

### 3. EfaClient Interface Constraints

`SofiaClient` MUST maintain exact method signatures for Home Assistant compatibility:

```python
# Required methods (see client.py lines 60-250)
async def locations_by_name(name: str, filters: list[LocationFilter] | None = None) -> list[Location]
async def lines_by_location(location_id: str, req_types: list[LineRequestType] | None = None, show_trains_explicit: bool = False) -> list[Line]
async def departures_by_location(location_id: str, arg_date: str | None = None, realtime: bool = False) -> list[Departure]

# Required exceptions (exceptions.py)
EfaConnectionError(SofiaClientError)  # Network/API failures
EfaResponseInvalid(SofiaClientError)  # Malformed data
```

**Critical:** `Line` model MUST have `from_dict()` and `to_dict()` for HA serialization.

### 4. Realtime Update Merging

`GTFSRealtimeParser.fetch_realtime_updates()` (realtime_parser.py):

```python
# Trip updates (delays, cancellations)
feed = await self._fetch_protobuf_feed(f"{base_url}/trip-updates")
for entity in feed.entity:
    if entity.HasField("trip_update"):
        trip_id = entity.trip_update.trip.trip_id
        # Map to route_id via static data, calculate delays
```

**Key:** Real-time delays are computed by comparing `StopTimeUpdate.arrival.time` to static `stop_times.txt` schedules.

### 5. Test Fixtures with Mock GTFS Data

`tests/conftest.py` provides CSV fixtures mimicking GTFS structure:

```python
@pytest.fixture
def sample_stops_csv() -> str:
    return """stop_id,stop_name,stop_lat,stop_lon
1001,Централна гара,42.713564,23.323568"""

# Tests use pytest-httpx to mock API responses:
@pytest.mark.asyncio
async def test_client(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=".../static", content=create_zip(stops_csv, routes_csv))
```

**Important:** Use `clean_cache` autouse fixture to isolate tests.

## Common Workflows

### Adding a New Client Method

1. **Determine client:** EfaClient-compatible → `client.py`, Sofia-specific → `native_client.py`
2. **Add method with full type hints** (mypy strict mode)
3. **Create test in `tests/test_*.py`** with mocked HTTP responses
4. **Update `__all__` in `__init__.py`** if exposing new models/enums
5. **Run quality checks:** `ruff format && mypy && pytest --cov`

### Debugging Cache Issues

```bash
# Inspect cache
ls -lh ~/.cache/sofiaclient/
cat ~/.cache/sofiaclient/gtfs_static_*.meta  # Check Last-Modified metadata

# Force cache refresh
rm ~/.cache/sofiaclient/gtfs_static_*.zip
```

### CLI Testing (Real API)

```bash
# Interactive exploration (see cli/sofia_cli.py)
python3 cli/sofia_cli.py search-stops "университет"
python3 cli/sofia_cli.py departures 1001 --realtime --limit 5
python3 cli/sofia_cli.py trip-time 1001 1003 84 --realtime
```

## Type Hints Standards

**All public methods MUST have return types and parameter types:**

```python
# ✓ Correct
async def search_stops(self, query: str) -> list[Location]:
    ...

# ✗ Wrong (mypy error)
async def search_stops(self, query):
    ...
```

**Use `| None` for optionals (Python 3.10+ union syntax):**

```python
destination: Destination | None = None
```

## Error Handling

**Use custom exceptions (not generic `Exception`):**

```python
# Network errors
raise EfaConnectionError(f"Failed to fetch {url}: {err}") from err

# Data parsing errors
raise EfaResponseInvalid(f"Invalid stop_id: {stop_id}")

# Cache errors
raise CacheError(f"Cannot write to {cache_path}") from err
```

**Validate inputs early:**

```python
if not stop_id:
    raise ValueError("stop_id cannot be empty")
```

## Resources

- GTFS Spec: https://gtfs.org/ (stops.txt, routes.txt, trips.txt, stop_times.txt)
- GTFS Realtime: https://gtfs.org/documentation/realtime/proto/ (TripUpdate, VehiclePosition)
- gtfs-realtime-bindings: https://github.com/MobilityData/gtfs-realtime-bindings
- Home Assistant ha-departures: https://github.com/alex-jung/ha-departures
