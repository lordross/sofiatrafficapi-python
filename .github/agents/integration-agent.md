# Integration Agent

## Purpose
Ensure Sofia client integrates correctly with external systems, particularly Home Assistant.

## Responsibilities
- Test EfaClient compatibility
- Validate data model compatibility
- Test with ha-departures component (when possible)
- Identify integration issues
- Document integration procedures

## Usage Context
Invoke for:
- Pre-release compatibility checks
- Integration testing
- Home Assistant component validation
- API contract verification

## Integration Testing

### 1. Interface Compliance

Verify all required EfaClient methods are present and compatible:

```python
import inspect
from sofiaclient import SofiaClient

# Check method signatures
assert hasattr(SofiaClient, 'locations_by_name')
assert hasattr(SofiaClient, 'lines_by_location')
assert hasattr(SofiaClient, 'departures_by_location')

# Check async context manager
assert hasattr(SofiaClient, '__aenter__')
assert hasattr(SofiaClient, '__aexit__')

# Verify method signatures
sig = inspect.signature(SofiaClient.locations_by_name)
params = list(sig.parameters.keys())
assert 'name' in params
assert 'filters' in params
```

### 2. Data Model Match

Ensure Location, Line, Departure match Home Assistant expectations:

```python
from sofiaclient import Location, Line, Departure, Destination, TransportType

# Location must have these attributes
location = Location(id="123", name="Test Stop", coord=(42.0, 23.0))
assert hasattr(location, 'id')
assert hasattr(location, 'name')
assert hasattr(location, 'type')
assert hasattr(location, 'coord')

# Line must support serialization
destination = Destination(id="456", name="End Stop")
line = Line(
    id="1",
    name="Line 1",
    number="1",
    product=TransportType.TRAM,
    description="Tram Line 1",
    destination=destination
)
line_dict = line.to_dict()
line_restored = Line.from_dict(line_dict)
assert line.id == line_restored.id

# Departure must have time fields
departure = Departure(
    line_id="1",
    planned_time="14:30",
    estimated_time="14:32"
)
assert hasattr(departure, 'line_id')
assert hasattr(departure, 'planned_time')
assert hasattr(departure, 'estimated_time')
```

### 3. Exception Compatibility

Test that correct exceptions are raised:

```python
from sofiaclient.exceptions import EfaConnectionError, EfaResponseInvalid
import httpx
import pytest

@pytest.mark.asyncio
async def test_connection_error():
    """Test network errors raise EfaConnectionError."""
    with pytest.raises(EfaConnectionError):
        async with SofiaClient("https://invalid.url") as client:
            await client.locations_by_name("test")

@pytest.mark.asyncio  
async def test_invalid_response():
    """Test invalid data raises EfaResponseInvalid."""
    # Mock invalid response scenario
    ...
    with pytest.raises(EfaResponseInvalid):
        await client.departures_by_location("INVALID_ID")
```

### 4. Async Context Manager

Validate proper resource management:

```python
@pytest.mark.asyncio
async def test_context_manager():
    """Test client properly enters and exits context."""
    client = SofiaClient(base_url)
    
    # Before entering context
    assert client._http_client is None
    
    # Enter context
    async with client as c:
        assert c._http_client is not None
        assert c is client
    
    # After exiting context
    # Note: Implementation may keep client open, verify actual behavior
```

### 5. Real Usage Simulation

Simulate Home Assistant ha-departures workflow:

```python
@pytest.mark.asyncio
async def test_ha_departures_workflow(httpx_mock: HTTPXMock):
    """Simulate typical Home Assistant usage pattern."""
    # Mock API responses
    httpx_mock.add_response(
        url=f"{base_url}/static",
        content=create_gtfs_zip(stops_csv, routes_csv, trips_csv, stop_times_csv)
    )
    httpx_mock.add_response(
        url=f"{base_url}/trip-updates",
        content=create_trip_update_feed()
    )
    
    async with SofiaClient(base_url) as client:
        # Step 1: Find stop
        stops = await client.locations_by_name("Централна гара")
        assert len(stops) > 0
        stop = stops[0]
        
        # Step 2: Get lines at stop
        lines = await client.lines_by_location(stop.id)
        assert len(lines) > 0
        
        # Step 3: Get departures with real-time
        departures = await client.departures_by_location(
            stop.id,
            realtime=True
        )
        assert len(departures) > 0
        
        # Step 4: Verify data structure matches HA expectations
        for dep in departures[:5]:
            assert isinstance(dep.line_id, str)
            assert isinstance(dep.planned_time, str)
            # estimated_time can be None if no real-time data
            if dep.estimated_time:
                assert isinstance(dep.estimated_time, str)
```

## Integration Scenarios

### Scenario 1: Initial Setup
User configures ha-departures component with Sofia Transit:
```yaml
sensor:
  - platform: departures
    name: "Sofia Central Station"
    client_type: "sofiaclient.SofiaClient"
    api_url: "https://gtfs.sofiatraffic.bg/api/v1/"
    stop_id: "1001"
```

**Test**: Verify client initializes and fetches data

### Scenario 2: Real-time Updates
HA polls for departures every 60 seconds:
```python
# Verify rapid successive calls use cache
async with SofiaClient(base_url) as client:
    deps1 = await client.departures_by_location("1001", realtime=True)
    # Immediate second call should use cached static data
    deps2 = await client.departures_by_location("1001", realtime=True)
```

**Test**: Verify cache reduces API calls

### Scenario 3: Network Failure
Sofia Traffic API is temporarily unavailable:
```python
# Verify graceful degradation
with pytest.raises(EfaConnectionError):
    async with SofiaClient(base_url) as client:
        await client.departures_by_location("1001")
```

**Test**: Verify appropriate error raised (not generic Exception)

### Scenario 4: Invalid Stop ID
User configures non-existent stop:
```python
async with SofiaClient(base_url) as client:
    departures = await client.departures_by_location("999999")
    # Should return empty list or raise EfaResponseInvalid
    assert isinstance(departures, list)
```

**Test**: Verify handling of invalid input

## Home Assistant Integration Points

### ha-departures Component Requirements

The component expects:

1. **Async context manager**:
   ```python
   async with ClientClass(url) as client:
       ...
   ```

2. **locations_by_name** for stop search:
   ```python
   stops = await client.locations_by_name("search term")
   ```

3. **departures_by_location** for live data:
   ```python
   deps = await client.departures_by_location(
       location_id="123",
       arg_date="14:30",  # Optional time filter
       realtime=True      # Enable real-time data
   )
   ```

4. **Data model serialization**:
   ```python
   # Line must support dict conversion for state storage
   line_dict = line.to_dict()
   line = Line.from_dict(line_dict)
   ```

### Testing Without Home Assistant

Create standalone integration test script:

```python
# test_ha_integration.py
import asyncio
from sofiaclient import SofiaClient

async def main():
    base_url = "https://gtfs.sofiatraffic.bg/api/v1/"
    
    async with SofiaClient(base_url) as client:
        # Test 1: Search stops
        print("Searching for stops...")
        stops = await client.locations_by_name("университет")
        print(f"Found {len(stops)} stops")
        
        if stops:
            stop = stops[0]
            print(f"\nUsing stop: {stop.name} ({stop.id})")
            
            # Test 2: Get lines
            print("\nFetching lines...")
            lines = await client.lines_by_location(stop.id)
            print(f"Found {len(lines)} lines")
            
            # Test 3: Get departures
            print("\nFetching departures...")
            deps = await client.departures_by_location(
                stop.id,
                realtime=True
            )
            print(f"Found {len(deps)} departures")
            
            # Display first 5 departures
            for dep in deps[:5]:
                delay = ""
                if dep.delay_minutes:
                    delay = f" (+{dep.delay_minutes}min)"
                print(f"  {dep.line_id}: {dep.planned_time}{delay}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run with:
```bash
python test_ha_integration.py
```

## Compatibility Matrix

| Feature | EfaClient | SofiaClient | Status |
|---------|-----------|-------------|--------|
| locations_by_name | ✓ | ✓ | Compatible |
| lines_by_location | ✓ | ✓ | Compatible |
| departures_by_location | ✓ | ✓ | Compatible |
| Location model | ✓ | ✓ | Compatible |
| Line.to_dict() | ✓ | ✓ | Compatible |
| Line.from_dict() | ✓ | ✓ | Compatible |
| Departure model | ✓ | ✓ | Compatible |
| EfaConnectionError | ✓ | ✓ | Compatible |
| EfaResponseInvalid | ✓ | ✓ | Compatible |
| Async context manager | ✓ | ✓ | Compatible |

## Pre-Release Checklist

Before releasing new version:

- [ ] Run all integration tests
- [ ] Verify EfaClient interface unchanged
- [ ] Test with real Sofia Traffic API
- [ ] Validate data model serialization
- [ ] Check exception handling
- [ ] Test context manager lifecycle
- [ ] Verify cache behavior
- [ ] Test with multiple Python versions (3.10, 3.11, 3.12)
- [ ] Run ha-departures simulation
- [ ] Document any breaking changes

## Success Criteria
- All EfaClient interface tests pass
- Data models serialize correctly
- Proper exceptions raised
- Context manager works as expected
- Cache reduces API calls
- Works with real Sofia Traffic API
- No regressions from previous version
- Compatible with Python 3.10+
