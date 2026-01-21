# Sofia Traffic API Python Module - Refined Requirements
**Date:** 2026-01-21  
**Project:** sofiaclient  
**Status:** Approved for Implementation

---

## Project Overview

Create a standalone Python module named **sofiaclient** that wraps GTFS (General Transit Feed Specification) data for Sofia city's public transportation system. The module provides **EfaClient compatibility** for Home Assistant integration and extended Sofia-specific features.

---

## API Endpoints

The Sofia Traffic system provides the following GTFS endpoints:

### Real-time Data (GTFS Realtime Protocol Buffers)
1. **Alerts**: `https://gtfs.sofiatraffic.bg/api/v1/alerts`
   - Service alerts and notifications
   
2. **Trip Updates**: `https://gtfs.sofiatraffic.bg/api/v1/trip`
   - Real-time trip schedule updates
   
3. **Vehicle Positions**: `https://gtfs.sofiatraffic.bg/api/v1/vehicle-positions`
   - Current vehicle locations and status

### Static Data
4. **Static GTFS**: `https://gtfs.sofiatraffic.bg/api/v1/static`
   - Archive file containing stops, routes, schedules, etc.

### Configuration
- **Base URL:** `https://gtfs.sofiatraffic.bg/api/v1/` ✅
- **URL Usage:** Passed to constructor as base, methods append specific paths

### Reference Documentation
- GTFS Realtime specification: https://gtfs.org/documentation/realtime/proto/
- Recommended library: `gtfs-realtime-bindings` (https://github.com/MobilityData/gtfs-realtime-bindings)

---

## Core Requirements

### 1. Well-Defined Public Interface
The library must expose a clean, intuitive API for end users with **EfaClient compatibility** for Home Assistant integration.

### 2. Vehicle Arrival Information
**Primary Use Case**: Get information about when vehicles will arrive at a given stop

Required information per arrival:
- Vehicle identification  
- Scheduled arrival time
- Real-time delay information (in minutes)
- Detour or service alert information

**Display Requirements**:
- Provide both scheduled time AND delay separately
- Combine real-time updates with static schedule data

### 3. Stop Selection
- Users must be able to select multiple stops they're interested in
- Support searching for stops by partial name matching (substring search)
  - Example: searching "университет" returns all stops containing this substring

### 4. Time Filtering
- Filter results by time offset from current time
- Example: "Show arrivals in the next 30 minutes"  
- Configurable time window for user convenience
- **Time Format:** Combine "HH:MM" string with current date ✅

### 5. Route Creation & Trip Time Calculation
- Create a route based on start stop and end stop
- Calculate travel time between start and end stops using real-time data
- **Constraints**:
  - Trip must be done with ONE vehicle only (no transfers)
  - User selects line via `route_id` from static GTFS data
  - Calculate both scheduled and real-time trip duration

---

## Use Case Scenarios

As an API developer, the following workflows must be supported:

1. **Search Stop by Name**
   - Input: Stop name (partial match, e.g., "университет")
   - Output: List of matching stops with `stop_id` and `stop_name`

2. **Get Arrivals for a Stop**
   - Input: `stop_id`
   - Output: List of vehicles arriving at the stop with:
     - Scheduled arrival time
     - Real-time arrival time (if available)
     - Vehicle/route identification
     - Delay in minutes

3. **Calculate Trip Time Between Stops**
   - Input: `start_stop_id`, `end_stop_id`, `route_id`
   - Output: Trip duration showing:
     - Scheduled time between stops
     - Real-time adjusted time (based on current delays)
     - Time difference/delay

4. **Search Route by Name**
   - Input: Route name or number (e.g., "84", "метро")
   - Output: List of matching routes with `route_id` and `route_name`

---

## Integration Requirements

### Target System
[GitHub - alex-jung/ha-departures](https://github.com/alex-jung/ha-departures) - Home Assistant custom component for public transport departure times

**Integration Method:** Manual replacement of EfaClient by human developer

### Drop-in Replacement for EfaClient

The sofiaclient must implement a **compatibility layer** that matches the EfaClient interface:

#### Required Interface

```python
class SofiaClient:
    """Drop-in replacement for EfaClient"""
    
    def __init__(self, url: str):
        """
        Initialize client with API base URL
        
        Args:
            url: Base URL (https://gtfs.sofiatraffic.bg/api/v1/)
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        pass
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
    
    async def locations_by_name(
        self, 
        name: str, 
        filters: list[LocationFilter] | None = None
    ) -> list[Location]:
        """Search stops by name substring"""
        pass
    
    async def lines_by_location(
        self,
        location_id: str,
        req_types: list[LineRequestType] | None = None,
        show_trains_explicit: bool = False
    ) -> list[Line]:
        """Get all lines/routes serving a stop"""
        pass
    
    async def departures_by_location(
        self,
        location_id: str,
        arg_date: str | None = None,  # "HH:MM" format
        realtime: bool = False
    ) -> list[Departure]:
        """
        Get departures for a stop with optional real-time data
        
        Args:
            location_id: stop_id from GTFS
            arg_date: Time filter in "HH:MM" format (combined with current date)
            realtime: Include real-time delay information
        """
        pass
```

#### Required Data Models

```python
@dataclass
class Location:
    id: str                      # stop_id from GTFS
    name: str                    # stop_name from GTFS
    type: str                    # "stop"
    coord: tuple[float, float] | None  # (lat, lon)

@dataclass
class Line:
    id: str                      # route_id from GTFS (no year component) ✅
    name: str                    # route_short_name or route_long_name
    number: str                  # route_short_name
    product: TransportType       # Mapped from route_type
    description: str             # route_long_name
    destination: Destination     # Final stop of route
    
    @classmethod
    def from_dict(cls, data: dict) -> Line: ...
    
    def to_dict(self) -> dict: ...

@dataclass
class Destination:
    id: str                      # stop_id of final stop
    name: str                    # stop_name of final stop
    type: str                    # "stop"

@dataclass
class Departure:
    line_id: str                 # route_id from GTFS
    planned_time: datetime | None      # Scheduled time
    estimated_time: datetime | None    # Real-time time (with delays)
```

#### Required Enums

```python
class TransportType(Enum):
    """Map from GTFS route_type - Sofia has all standard types ✅"""
    TRAM = 0          # GTFS route_type 0
    SUBWAY = 1        # GTFS route_type 1
    TRAIN = 2         # GTFS route_type 2
    CITY_BUS = 3      # GTFS route_type 3
    REGIONAL_BUS = 4
    EXPRESS_BUS = 5
    # Additional types as found in Sofia GTFS

class LocationFilter(Enum):
    STOPS = "stops"   # Filter to only stops

class LineRequestType(Enum):
    DEPARTURE_MONITOR = "departure_monitor"
```

#### Required Exceptions

```python
class EfaConnectionError(Exception):
    """Raised when API connection fails"""
    pass

class EfaResponseInvalid(Exception):
    """Raised when API response is invalid"""
    pass
```

---

## Technical Stack

### Package Management
- **uv**: Modern, fast Python package manager

### Core Dependencies
- `gtfs-realtime-bindings`: Parse GTFS Realtime protobuf data
- `httpx`: Async HTTP client for API requests
- `protobuf`: Protocol buffer support

### Code Quality Tools
- **mypy**: Type checking and static analysis (replacing ty)
- **ruff**: Code formatting and linting

### Testing
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `pytest-httpx`: Mock HTTP responses

### CI/CD
- **GitHub Actions**: Automated workflows

---

## Project Architecture

```
sofiaclient/
├── __init__.py              # Public API exports
├── client.py                # SofiaClient class (EfaClient compatible)
├── native_client.py         # Native Sofia-specific extended API
├── models.py                # Data models (Location, Line, Departure, etc.)
├── gtfs_parser.py           # GTFS static data parsing
├── realtime_parser.py       # GTFS Realtime protobuf parsing
├── cache.py                 # Static data caching layer with TTL
├── exceptions.py            # Custom exceptions
└── enums.py                 # Enums (TransportType, LocationFilter, etc.)
```

**Two API Layers:** ✅
1. **Compatibility Layer** (`SofiaClient`): Drop-in replacement for EfaClient
2. **Native Layer** (`SofiaNativeClient`): Extended Sofia-specific features (route creation, trip time calculation)

---

## Confirmed Design Decisions

### 1. URL Configuration ✅
- Base URL: `https://gtfs.sofiatraffic.bg/api/v1/`
- Endpoints constructed by appending: `alerts`, `trip`, `vehicle-positions`, `static`
- URL passed to constructor as base, methods append specific paths

### 2. Line ID Format ✅
- Use GTFS `route_id` directly as `Line.id`
- No year component appending needed
- Direct mapping from static GTFS data

### 3. Transport Types ✅
- Sofia GTFS contains all standard EFA transport types
- Map GTFS `route_type` integers to `TransportType` enum
- Verify exact types during implementation from static data

### 4. Time Format Handling ✅
- Input: `arg_date` as "HH:MM" string (e.g., "14:30")
- Implementation: Combine with current date to create datetime
- Approach: 
  ```python
  from datetime import datetime, time
  
  time_obj = datetime.strptime(arg_date, "%H:%M").time()
  filter_datetime = datetime.combine(datetime.now().date(), time_obj)
  ```
- Filter departures >= filter_datetime

### 5. Caching Strategy ✅
- **On-demand with TTL** approach
- Check downloaded static GTFS file's last modified time
- Implementation:
  1. Download static GTFS on first request
  2. Cache file locally with timestamp
  3. On subsequent requests, check file modification time:
     - If `Last-Modified` header differs, re-download
     - Otherwise, use cached file
  4. Optional: Configurable TTL (e.g., 24 hours) as fallback

```python
class GTFSCache:
    def __init__(self, cache_dir: Path | None = None, ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
    
    async def get_static_data(self, url: str) -> Path:
        """Get static GTFS, refresh if needed based on Last-Modified"""
        cached_file = self.get_cache_path(url)
        
        if cached_file.exists():
            # Check if cache is still valid
            age = datetime.now() - datetime.fromtimestamp(cached_file.stat().st_mtime)
            if age < self.ttl:
                # Check remote Last-Modified
                if not await self._remote_file_changed(cached_file):
                    return cached_file
        
        # Download fresh data
        return await self._download_static_gtfs(cached_file)
```

### 6. Dual API Design ✅
- **SofiaClient**: EfaClient drop-in replacement (HA compatibility)
- **SofiaNativeClient**: Full Sofia-specific features
- Shared internal components (parsers, cache, models)

---

## Implementation Status

### Completed ✅

#### Phase 1: Core Infrastructure
- [x] Project structure setup with uv
- [x] Data models (Location, Line, Departure, TripTime, StopArrival)
- [x] Exception classes (EfaConnectionError, EfaResponseInvalid, etc.)
- [x] Enum definitions (TransportType, LocationFilter, LineRequestType)

#### Phase 2: GTFS Parsing
- [x] Static GTFS parser (stops, routes, trips, stop_times)
- [x] GTFS Realtime parser (TripUpdates, VehiclePositions, ServiceAlerts)
- [x] Caching layer with TTL and Last-Modified checking

#### Phase 3: EfaClient Compatibility Layer
- [x] SofiaClient class with async context manager
- [x] `locations_by_name()` - search stops
- [x] `lines_by_location()` - get routes for stop
- [x] `departures_by_location()` - get departures with real-time

#### Phase 4: Native Extended API
- [x] SofiaNativeClient class
- [x] Route search by name
- [x] Trip time calculation between stops
- [x] Enhanced filtering and time offset features

#### Phase 5: Testing & Documentation
- [x] Unit tests for all components
- [x] Integration tests with mocked API responses
- [x] EfaClient compatibility tests
- [x] Documentation and usage examples (README, API.md)
- [x] copilot-instructions.md
- [x] agents.md

#### Phase 6: CI/CD
- [x] GitHub Actions workflow
- [x] Linting (ruff), type checking (mypy), testing (pytest)
- [x] Coverage reporting
- [x] Multi-version testing (Python 3.10, 3.11, 3.12)

---

## API Endpoints Mapping

| Purpose | URL | Format |
|---------|-----|--------|
| Service Alerts | `{base_url}/alerts` | GTFS Realtime Protobuf |
| Trip Updates | `{base_url}/trip` | GTFS Realtime Protobuf |
| Vehicle Positions | `{base_url}/vehicle-positions` | GTFS Realtime Protobuf |
| Static Data | `{base_url}/static` | ZIP archive (GTFS) |

Where `base_url = https://gtfs.sofiatraffic.bg/api/v1/`

---

## Data Flow Example

**Use Case**: Get departures for a stop with delays

```
1. User calls: client.departures_by_location("stop_123", arg_date="14:30", realtime=True)

2. Load static GTFS (cached):
   - Parse stops.txt → Find stop "stop_123"
   - Parse routes.txt → Get all routes
   - Parse trips.txt → Get trips serving this stop
   - Parse stop_times.txt → Get scheduled times

3. Fetch real-time TripUpdates:
   - GET {base_url}/trip
   - Parse protobuf FeedMessage
   - Extract StopTimeUpdates for "stop_123"

4. Merge data:
   - For each scheduled departure after 14:30:
     - Get planned_time from stop_times.txt
     - Find matching TripUpdate
     - Calculate estimated_time = planned_time + delay
     - Get route_id for line_id

5. Return list[Departure] with both planned and estimated times
```

---

## Success Criteria

✅ EfaClient-compatible interface for ha-departures integration  
✅ All EfaClient methods implemented with correct signatures  
✅ Native extended API for Sofia-specific features  
✅ Accurate trip time calculation with real-time delays  
✅ On-demand caching with Last-Modified checking  
✅ Time filtering using "HH:MM" format combined with current date  
✅ GTFS route_id used directly as line identifier  
✅ Comprehensive test coverage including compatibility tests  
✅ Type-safe code passing mypy checks  
✅ Formatted code passing ruff checks  
✅ Automated CI/CD pipeline  
✅ Documentation with migration guide from EfaClient  

---

## Next Steps

1. **Testing with Real Data**
   - Test with actual Sofia Traffic API endpoints
   - Validate data parsing with real GTFS data
   - Verify real-time updates work correctly

2. **Home Assistant Integration**
   - Test as drop-in replacement in ha-departures component
   - Validate all use cases work correctly
   - Create migration guide for users

3. **Performance Optimization**
   - Profile code for bottlenecks
   - Optimize GTFS parsing if needed
   - Tune cache settings

4. **PyPI Publishing**
   - Prepare package for PyPI
   - Set up automated releases
   - Create version tags

---

**Implementation Status:** ✅ COMPLETE  
**Ready for Testing:** YES  
**Ready for Integration:** YES

