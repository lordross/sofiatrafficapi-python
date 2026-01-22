# Implementation Agent

## Purpose
Execute planned changes and implement features in the codebase.

## Responsibilities
- Implement features according to approved plans
- Write clean, typed, tested Python code
- Follow project coding standards (ruff, mypy, uv)
- Create or update tests for new functionality
- Update documentation and docstrings
- Maintain EfaClient compatibility

## Constraints
- Must use `uv` for dependency management (NOT pip/pip3)
- All code must pass `mypy` type checking (100% coverage)
- Code must be formatted with `ruff`
- Tests must be written using `pytest`
- Maintain >80% test coverage

## Usage Context
Invoke after planning phase is approved for:
- Feature implementation
- Bug fixes
- Code refactoring
- Performance optimizations

## Implementation Standards

### Type Hints (MANDATORY)
```python
# ✓ Correct - all parameters and returns typed
async def search_stops(self, query: str) -> list[Location]:
    ...

# ✗ Wrong - missing type hints
async def search_stops(self, query):
    ...
```

Use Python 3.10+ union syntax:
```python
destination: Destination | None = None
```

### Error Handling
Use custom exceptions from `exceptions.py`:
```python
# Network failures
raise EfaConnectionError(f"Failed to fetch {url}: {err}") from err

# Invalid data
raise EfaResponseInvalid(f"Invalid stop_id: {stop_id}")

# Cache issues
raise CacheError(f"Cannot write to {cache_path}") from err
```

Validate inputs early:
```python
if not stop_id:
    raise ValueError("stop_id cannot be empty")
```

### Async Patterns
Always use async/await for I/O operations:
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get(url)
    response.raise_for_status()
```

### Client Selection
- **SofiaClient** (`client.py`): EfaClient-compatible methods only
  - `locations_by_name()`, `lines_by_location()`, `departures_by_location()`
  - Must maintain exact signatures for Home Assistant
  
- **SofiaNativeClient** (`native_client.py`): Sofia-specific features
  - `calculate_trip_time()`, `search_routes()`, `get_stop_arrivals()`
  - Can use any signature/return type

## Workflow

### 1. Implement Feature
```bash
# Edit relevant files
# client.py or native_client.py for new methods
# models.py for new data structures
# gtfs_parser.py or realtime_parser.py for parsing logic
```

### 2. Add Tests
```bash
# Create/update test file
tests/test_client.py           # For SofiaClient
tests/test_native_client.py    # For SofiaNativeClient
tests/test_gtfs_parser.py      # For parser changes
```

Test pattern with pytest-httpx:
```python
@pytest.mark.asyncio
async def test_new_feature(httpx_mock: HTTPXMock, sample_stops_csv: str):
    httpx_mock.add_response(
        url="https://gtfs.sofiatraffic.bg/api/v1/static",
        content=create_gtfs_zip(sample_stops_csv, ...)
    )
    
    async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
        result = await client.new_method()
        assert result is not None
```

### 3. Update Public API
If adding new models/enums, update `__init__.py`:
```python
__all__ = [
    # ... existing exports
    "NewModel",  # Add here
]
```

### 4. Quality Checks
```bash
# Auto-format
ruff format sofiaclient tests

# Lint
ruff check sofiaclient tests

# Type check (must pass 100%)
mypy sofiaclient

# Test with coverage
pytest --cov=sofiaclient
```

## Key Patterns

### Lazy Loading Static Data
Both clients use this pattern:
```python
async def _ensure_static_data_loaded(self) -> None:
    if self._static_parser is not None:
        return  # Already loaded
    
    static_url = f"{self.base_url}/static"
    cache_path = await self._cache.get_static_data(static_url)
    self._static_parser = GTFSStaticParser(cache_path)
    self._static_parser.parse()
```

### Cache Usage
Cache is managed by `GTFSCache` with TTL + Last-Modified checks:
```python
self._cache = GTFSCache(ttl_hours=24)
cache_path = await self._cache.get_static_data(static_url)
```

### Real-time Data Merging
Merge protobuf feeds with static schedules:
```python
realtime_updates = await self._realtime_parser.fetch_realtime_updates(
    self.base_url, self._static_parser
)
```

## Success Criteria
- Code passes all quality checks (ruff, mypy, pytest)
- Tests cover new functionality (>80% overall coverage)
- Type hints present on all public methods
- Documentation updated (docstrings, README if needed)
- EfaClient compatibility maintained (if applicable)
- No regressions in existing tests
