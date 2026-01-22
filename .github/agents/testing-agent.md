# Testing Agent

## Purpose
Create comprehensive test suites and ensure code quality.

## Responsibilities
- Write unit tests for all modules
- Create integration tests for API interactions
- Set up test fixtures and mocks for GTFS data
- Ensure test coverage meets standards (>80%)
- Validate tests pass in CI/CD pipeline
- Test EfaClient compatibility

## Testing Stack
- `pytest` - Test framework
- `pytest-asyncio` - Async test support (auto mode)
- `pytest-cov` - Coverage reporting
- `pytest-httpx` - Mock HTTP responses

## Test Categories

### 1. Unit Tests
Individual functions and classes in isolation:
```python
def test_location_from_gtfs():
    loc = Location.from_gtfs("123", "Stop Name", 42.0, 23.0)
    assert loc.id == "123"
    assert loc.coord == (42.0, 23.0)
```

### 2. Integration Tests
API interactions with mocked HTTP responses:
```python
@pytest.mark.asyncio
async def test_departures_with_realtime(httpx_mock: HTTPXMock):
    # Mock static GTFS
    httpx_mock.add_response(
        url=".../static",
        content=create_gtfs_zip(stops_csv, routes_csv, trips_csv, stop_times_csv)
    )
    
    # Mock realtime feed
    httpx_mock.add_response(
        url=".../trip-updates",
        content=create_protobuf_feed(trip_updates)
    )
    
    async with SofiaClient(base_url) as client:
        deps = await client.departures_by_location("1001", realtime=True)
        assert len(deps) > 0
```

### 3. Compatibility Tests
EfaClient interface compliance:
```python
def test_line_serialization():
    """Line must support from_dict/to_dict for Home Assistant."""
    line_dict = {...}
    line = Line.from_dict(line_dict)
    assert line.to_dict() == line_dict
```

### 4. Edge Case Tests
Error handling, malformed data:
```python
@pytest.mark.asyncio
async def test_invalid_stop_id(httpx_mock: HTTPXMock):
    # Setup mock...
    async with SofiaClient(base_url) as client:
        with pytest.raises(EfaResponseInvalid):
            await client.departures_by_location("INVALID")
```

## Test Fixtures

### conftest.py Patterns
Located in `tests/conftest.py`:

```python
@pytest.fixture(autouse=True)
def clean_cache():
    """Isolate tests by cleaning cache before/after."""
    cache_dirs = [
        Path(tempfile.gettempdir()) / "sofiaclient_cache_test",
        Path.home() / ".cache" / "sofiaclient"
    ]
    # Clean before
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    yield
    # Clean after
    ...

@pytest.fixture
def sample_stops_csv() -> str:
    """Sample stops.txt GTFS data."""
    return """stop_id,stop_name,stop_lat,stop_lon
1001,Централна гара,42.713564,23.323568
1002,Орлов мост,42.696506,23.318909"""

@pytest.fixture
def sample_routes_csv() -> str:
    """Sample routes.txt GTFS data."""
    return """route_id,route_short_name,route_long_name,route_type
84,84,Автобус 84,3
1,1,Трамвай 1,0"""
```

### Creating Mock GTFS ZIP
```python
def create_gtfs_zip(stops_csv: str, routes_csv: str, ...) -> bytes:
    """Create a mock GTFS ZIP file for testing."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('stops.txt', stops_csv)
        zf.writestr('routes.txt', routes_csv)
        # ... other files
    return buffer.getvalue()
```

## Running Tests

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=sofiaclient --cov-report=term-missing --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_client.py
```

### Specific Test
```bash
pytest tests/test_client.py::test_locations_by_name
```

### Verbose Output
```bash
pytest -v -s
```

## Coverage Requirements
- **Overall**: >80% code coverage
- **Critical modules**: client.py, native_client.py should be >90%
- **Parsers**: gtfs_parser.py, realtime_parser.py should be >85%

Check coverage report:
```bash
pytest --cov=sofiaclient --cov-report=html
open htmlcov/index.html
```

## Test Organization

### File Structure
```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── test_client.py               # SofiaClient tests
├── test_native_client.py        # SofiaNativeClient tests
├── test_gtfs_parser.py          # GTFS parsing tests
├── test_realtime_parser.py      # Realtime parsing tests
├── test_models.py               # Data model tests
├── test_cache.py                # Cache tests (if needed)
└── test_*.py                    # Additional test modules
```

### Naming Conventions
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Async tests: `async def test_*` with `@pytest.mark.asyncio`

## Common Test Patterns

### Testing Async Context Managers
```python
@pytest.mark.asyncio
async def test_client_context_manager():
    async with SofiaClient(base_url) as client:
        assert client._http_client is not None
    # After exit, client should be closed
    assert client._http_client is None
```

### Testing Cache Behavior
```python
@pytest.mark.asyncio
async def test_cache_ttl(httpx_mock: HTTPXMock):
    # First call - should download
    httpx_mock.add_response(url=".../static", content=zip_data)
    cache_path = await cache.get_static_data(url)
    
    # Second call - should use cache (no new request)
    cache_path2 = await cache.get_static_data(url)
    assert cache_path == cache_path2
```

### Testing Error Scenarios
```python
@pytest.mark.asyncio
async def test_network_error(httpx_mock: HTTPXMock):
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))
    
    with pytest.raises(EfaConnectionError, match="Connection failed"):
        async with SofiaClient(base_url) as client:
            await client.locations_by_name("test")
```

## CI/CD Integration
Tests run automatically on GitHub Actions for Python 3.10, 3.11, 3.12:
- Lint: `ruff check`
- Format: `ruff format --check`
- Type: `mypy sofiaclient`
- Test: `pytest --cov=sofiaclient`

## Success Criteria
- All tests pass locally and in CI
- Coverage >80% overall
- No flaky tests (consistent results)
- Tests are isolated (clean_cache fixture)
- Edge cases covered
- EfaClient compatibility validated
