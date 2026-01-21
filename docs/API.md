# Sofia Traffic API Client - API Reference

## SofiaClient (EfaClient Compatible)

Drop-in replacement for `apyefa.EfaClient` for Home Assistant integration.

### Constructor

```python
SofiaClient(url: str)
```

**Parameters:**
- `url`: Base API URL (e.g., `https://gtfs.sofiatraffic.bg/api/v1/`)

**Usage:**
```python
async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Use client
    ...
```

### Methods

#### `locations_by_name`

Search for stops by name.

```python
async def locations_by_name(
    self,
    name: str,
    filters: list[LocationFilter] | None = None
) -> list[Location]
```

**Parameters:**
- `name`: Search query (substring match, case-insensitive)
- `filters`: Optional list of filters (only `LocationFilter.STOPS` supported)

**Returns:** List of `Location` objects

**Example:**
```python
stops = await client.locations_by_name("университет", filters=[LocationFilter.STOPS])
for stop in stops:
    print(f"{stop.id}: {stop.name}")
```

#### `lines_by_location`

Get all routes serving a specific stop.

```python
async def lines_by_location(
    self,
    location_id: str,
    req_types: list[LineRequestType] | None = None,
    show_trains_explicit: bool = False
) -> list[Line]
```

**Parameters:**
- `location_id`: Stop ID
- `req_types`: Request types (compatibility parameter, not used)
- `show_trains_explicit`: Show trains flag (compatibility parameter, not used)

**Returns:** List of `Line` objects

**Example:**
```python
lines = await client.lines_by_location("1001")
for line in lines:
    print(f"{line.number}: {line.description}")
```

#### `departures_by_location`

Get departures for a specific stop.

```python
async def departures_by_location(
    self,
    location_id: str,
    arg_date: str | None = None,
    realtime: bool = False
) -> list[Departure]
```

**Parameters:**
- `location_id`: Stop ID
- `arg_date`: Time filter in "HH:MM" format (shows departures after this time)
- `realtime`: Include real-time delay information

**Returns:** List of `Departure` objects sorted by planned time

**Example:**
```python
departures = await client.departures_by_location(
    "1001",
    arg_date="14:30",
    realtime=True
)
for dep in departures:
    delay = dep.delay_minutes or 0
    print(f"{dep.line_id}: {dep.planned_time} (delay: {delay} min)")
```

---

## SofiaNativeClient

Extended client with Sofia-specific features.

### Constructor

```python
SofiaNativeClient(url: str, cache_ttl_hours: int = 24)
```

**Parameters:**
- `url`: Base API URL
- `cache_ttl_hours`: Cache time-to-live in hours (default: 24)

### Methods

#### `search_stops`

Search for stops by name.

```python
async def search_stops(self, query: str) -> list[Location]
```

**Example:**
```python
stops = await client.search_stops("централна")
```

#### `get_stop`

Get stop by ID.

```python
async def get_stop(self, stop_id: str) -> Location | None
```

#### `search_routes`

Search for routes by name or number.

```python
async def search_routes(self, query: str) -> list[dict[str, Any]]
```

**Example:**
```python
routes = await client.search_routes("84")
for route in routes:
    print(f"{route['route_id']}: {route['route_long_name']}")
```

#### `get_arrivals`

Get arrivals for multiple stops with time filtering.

```python
async def get_arrivals(
    self,
    stop_ids: list[str],
    time_offset_minutes: int | None = None,
    include_realtime: bool = True
) -> list[StopArrival]
```

**Parameters:**
- `stop_ids`: List of stop IDs to query
- `time_offset_minutes`: Only show arrivals within this many minutes (None = all)
- `include_realtime`: Include real-time delay information

**Returns:** List of `StopArrival` objects sorted by arrival time

**Example:**
```python
# Get arrivals for next 30 minutes
arrivals = await client.get_arrivals(
    stop_ids=["1001", "1002"],
    time_offset_minutes=30,
    include_realtime=True
)

for arrival in arrivals:
    print(f"{arrival.route_name} to {arrival.headsign}")
    print(f"  Scheduled: {arrival.scheduled_time}")
    if arrival.estimated_time:
        print(f"  Estimated: {arrival.estimated_time}")
    if arrival.delay_minutes:
        print(f"  Delay: {arrival.delay_minutes} min")
    if arrival.alerts:
        print(f"  Alerts: {', '.join(arrival.alerts)}")
```

#### `calculate_trip_time`

Calculate trip time between two stops on a route.

```python
async def calculate_trip_time(
    self,
    start_stop_id: str,
    end_stop_id: str,
    route_id: str
) -> TripTime | None
```

**Parameters:**
- `start_stop_id`: Starting stop ID
- `end_stop_id`: Ending stop ID
- `route_id`: Route ID

**Returns:** `TripTime` object or None if route not found

**Example:**
```python
trip_time = await client.calculate_trip_time(
    start_stop_id="1001",
    end_stop_id="1003",
    route_id="84"
)

if trip_time:
    print(f"Scheduled: {trip_time.scheduled_duration_str}")
    if trip_time.realtime_duration_str:
        print(f"Real-time: {trip_time.realtime_duration_str}")
    if trip_time.delay_minutes:
        print(f"Delay: {trip_time.delay_minutes} min")
```

#### `get_cache_info`

Get information about cached data.

```python
def get_cache_info(self) -> dict[str, Any]
```

#### `clear_cache`

Clear all cached data.

```python
def clear_cache(self) -> None
```

---

## Data Models

### Location

Represents a transit stop.

**Attributes:**
- `id: str` - Stop ID
- `name: str` - Stop name
- `type: str` - Location type (always "stop")
- `coord: tuple[float, float] | None` - Coordinates (latitude, longitude)

### Line

Represents a transit line/route.

**Attributes:**
- `id: str` - Route ID
- `name: str` - Route name
- `number: str` - Route number
- `product: TransportType` - Transport type
- `description: str` - Route description
- `destination: Destination` - Final destination

### Departure

Represents a departure from a stop.

**Attributes:**
- `line_id: str` - Route ID
- `planned_time: datetime | None` - Scheduled time
- `estimated_time: datetime | None` - Real-time estimated time

**Properties:**
- `delay_minutes: int | None` - Delay in minutes

### StopArrival

Extended arrival information.

**Attributes:**
- `stop_id: str`
- `stop_name: str`
- `route_id: str`
- `route_name: str`
- `vehicle_id: str | None`
- `scheduled_time: datetime`
- `estimated_time: datetime | None`
- `delay_minutes: int | None`
- `trip_id: str`
- `headsign: str | None`
- `alerts: list[str]`

### TripTime

Trip time between two stops.

**Attributes:**
- `start_stop_id: str`
- `end_stop_id: str`
- `route_id: str`
- `scheduled_duration: int` - Duration in minutes
- `realtime_duration: int | None` - Real-time duration in minutes
- `delay_minutes: int | None` - Delay in minutes

**Properties:**
- `scheduled_duration_str: str` - Formatted duration (e.g., "1h 15m")
- `realtime_duration_str: str | None` - Formatted real-time duration

---

## Enums

### TransportType

```python
class TransportType(Enum):
    TRAM = 0
    SUBWAY = 1
    TRAIN = 2
    CITY_BUS = 3
    REGIONAL_BUS = 4
    EXPRESS_BUS = 5
    AERIAL_LIFT = 6
    FUNICULAR = 7
    TROLLEYBUS = 11
    MONORAIL = 12
```

### LocationFilter

```python
class LocationFilter(Enum):
    STOPS = "stops"
```

### LineRequestType

```python
class LineRequestType(Enum):
    DEPARTURE_MONITOR = "departure_monitor"
```

---

## Exceptions

### SofiaClientError

Base exception for all Sofia client errors.

### EfaConnectionError

Raised when connection to API fails. Compatible with EfaClient.

### EfaResponseInvalid

Raised when API response is invalid or cannot be parsed. Compatible with EfaClient.

### DataParseError

Raised when GTFS data parsing fails.

### CacheError

Raised when cache operations fail.

---

## Examples

### Basic Stop Search and Departures

```python
from sofiaclient import SofiaClient, LocationFilter

async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Search for stops
    stops = await client.locations_by_name("университет", filters=[LocationFilter.STOPS])
    
    if stops:
        stop = stops[0]
        print(f"Found: {stop.name} ({stop.id})")
        
        # Get departures
        departures = await client.departures_by_location(
            stop.id,
            arg_date="14:00",
            realtime=True
        )
        
        for dep in departures[:5]:  # Show first 5
            delay = f" +{dep.delay_minutes}min" if dep.delay_minutes else ""
            print(f"{dep.line_id}: {dep.planned_time.strftime('%H:%M')}{delay}")
```

### Trip Planning with Native Client

```python
from sofiaclient import SofiaNativeClient

async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Find route
    routes = await client.search_routes("84")
    route = routes[0]
    
    # Calculate trip time
    trip = await client.calculate_trip_time(
        start_stop_id="1001",
        end_stop_id="1003",
        route_id=route["route_id"]
    )
    
    if trip:
        print(f"Trip on route {trip.route_id}")
        print(f"Scheduled: {trip.scheduled_duration_str}")
        if trip.realtime_duration_str:
            print(f"Real-time: {trip.realtime_duration_str}")
```

### Monitor Multiple Stops

```python
async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Monitor arrivals at multiple stops
    arrivals = await client.get_arrivals(
        stop_ids=["1001", "1002", "1003"],
        time_offset_minutes=30,
        include_realtime=True
    )
    
    for arrival in arrivals:
        print(f"\n{arrival.stop_name}")
        print(f"  Route {arrival.route_name} → {arrival.headsign}")
        print(f"  {arrival.scheduled_time.strftime('%H:%M')}", end="")
        
        if arrival.delay_minutes:
            print(f" (delay: {arrival.delay_minutes}min)", end="")
        print()
        
        if arrival.alerts:
            for alert in arrival.alerts:
                print(f"  ⚠️  {alert}")
```
