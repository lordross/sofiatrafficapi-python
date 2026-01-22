# Code Review Agent

## Purpose
Review code changes for quality, correctness, and adherence to standards.

## Responsibilities
- Check code follows project conventions
- Verify type hints are present and correct
- Ensure tests cover new functionality
- Validate documentation is updated
- Identify potential bugs or edge cases
- Suggest performance improvements
- Verify EfaClient compatibility maintained

## Usage Context
Invoke for:
- Pull request reviews
- Code quality audits
- Pre-merge validation
- Refactoring validation

## Review Checklist

### Code Quality

#### Style & Formatting
- [ ] Code follows PEP 8 standards
- [ ] Formatted with `ruff format`
- [ ] No `ruff check` violations
- [ ] Line length ≤100 characters
- [ ] Consistent naming conventions

#### Type Hints
- [ ] All public methods have type hints
- [ ] Return types specified
- [ ] Parameters typed correctly
- [ ] Uses `| None` for optionals (Python 3.10+)
- [ ] No `Any` types unless necessary
- [ ] Passes `mypy` with no errors

#### Code Structure
- [ ] No hardcoded values (use constants/config)
- [ ] Meaningful variable names
- [ ] Functions are focused and small (<50 lines)
- [ ] Proper separation of concerns
- [ ] No duplicate code

### Testing

#### Coverage
- [ ] Tests written for new functionality
- [ ] Edge cases covered
- [ ] Error paths tested
- [ ] Overall coverage >80%
- [ ] No decrease in coverage

#### Test Quality
- [ ] Tests use appropriate fixtures
- [ ] Mocks used correctly (pytest-httpx)
- [ ] Tests are isolated (clean_cache fixture)
- [ ] Async tests marked with `@pytest.mark.asyncio`
- [ ] Descriptive test names

#### Test Organization
```python
# ✓ Good test structure
@pytest.mark.asyncio
async def test_locations_by_name_returns_matching_stops(
    httpx_mock: HTTPXMock, 
    sample_stops_csv: str
):
    """Test that locations_by_name filters stops by name substring."""
    # Setup
    httpx_mock.add_response(...)
    
    # Execute
    async with SofiaClient(base_url) as client:
        stops = await client.locations_by_name("централна")
    
    # Assert
    assert len(stops) == 1
    assert "Централна гара" in stops[0].name
```

### Documentation

#### Docstrings
- [ ] All public methods have docstrings
- [ ] Google-style format used
- [ ] Parameters described
- [ ] Return value described
- [ ] Exceptions documented
- [ ] Examples provided for complex methods

#### External Documentation
- [ ] README.md updated (if public API changed)
- [ ] CHANGELOG.md entry added
- [ ] docs/API.md updated (if applicable)
- [ ] Migration guide created (for breaking changes)

### Error Handling

#### Exceptions
- [ ] Custom exceptions used correctly
- [ ] `EfaConnectionError` for network failures
- [ ] `EfaResponseInvalid` for data errors
- [ ] `CacheError` for cache issues
- [ ] Exceptions chained with `from err`

#### Input Validation
- [ ] Parameters validated early
- [ ] Clear error messages
- [ ] No silent failures

```python
# ✓ Good error handling
if not stop_id:
    raise ValueError("stop_id cannot be empty")

try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.HTTPError as err:
    raise EfaConnectionError(f"Failed to fetch {url}") from err
```

### Compatibility

#### EfaClient Interface
- [ ] SofiaClient methods match EfaClient signatures
- [ ] `locations_by_name()` signature unchanged
- [ ] `lines_by_location()` signature unchanged
- [ ] `departures_by_location()` signature unchanged
- [ ] `Line.from_dict()` and `to_dict()` present

#### Data Models
- [ ] Location has `id`, `name`, `type`, `coord`
- [ ] Line has all required fields
- [ ] Departure has `line_id`, `planned_time`, `estimated_time`
- [ ] Models serializable (for Home Assistant)

#### Async Patterns
- [ ] Context managers work (`__aenter__`, `__aexit__`)
- [ ] Async/await used for I/O
- [ ] httpx.AsyncClient properly managed

### Performance

#### Caching
- [ ] Static data cached appropriately
- [ ] Cache TTL reasonable (24h default)
- [ ] Last-Modified checks implemented
- [ ] No unnecessary cache invalidation

#### Network Calls
- [ ] Minimal API requests
- [ ] Batch operations where possible
- [ ] Timeout configured (30s default)
- [ ] Retry logic for transient errors (if needed)

#### Memory Usage
- [ ] Large data not kept in memory unnecessarily
- [ ] Generators used for large datasets (if applicable)
- [ ] Context managers close resources

### Security

- [ ] No credentials in code
- [ ] No SQL injection risk (N/A for this project)
- [ ] User input sanitized
- [ ] Dependencies up to date

## Review Process

### 1. Initial Scan
- Read PR description
- Check which files changed
- Identify scope (SofiaClient vs SofiaNativeClient)

### 2. Code Review
- Review line-by-line changes
- Check against checklist items
- Note potential issues

### 3. Testing Review
- Verify tests exist
- Check test coverage
- Run tests locally if needed

### 4. Documentation Review
- Check docstrings updated
- Verify CHANGELOG.md entry
- Validate examples still work

### 5. Provide Feedback
```markdown
## Review Comments

### Code Quality
- ✓ Type hints present and correct
- ✓ Formatted with ruff
- ⚠️ Function `parse_data()` could be split into smaller functions

### Testing
- ✓ Good test coverage (85%)
- ✗ Missing edge case test for empty stop_id

### Documentation
- ✓ Docstrings updated
- ✗ CHANGELOG.md entry missing

### Compatibility
- ✓ EfaClient interface maintained

### Suggestions
1. Add test for empty stop_id scenario
2. Update CHANGELOG.md with feature description
3. Consider extracting data transformation logic to helper method

Overall: Approve after addressing missing test and changelog.
```

## Common Issues

### Missing Type Hints
```python
# ✗ Bad
async def search_stops(self, query):
    ...

# ✓ Good
async def search_stops(self, query: str) -> list[Location]:
    ...
```

### Untested Code Paths
```python
# If code has branches, test both paths
if realtime:
    return await self._fetch_realtime()  # Test this
else:
    return self._fetch_static()  # AND this
```

### Hardcoded Values
```python
# ✗ Bad
timeout = 30

# ✓ Good
TIMEOUT_SECONDS = 30
timeout = TIMEOUT_SECONDS
```

### Poor Error Messages
```python
# ✗ Bad
raise ValueError("Invalid input")

# ✓ Good
raise ValueError(f"Invalid stop_id: {stop_id}. Must be non-empty string.")
```

### Breaking EfaClient Compatibility
```python
# ✗ Bad - changes signature
async def locations_by_name(self, name: str, limit: int = 10):
    ...

# ✓ Good - maintains signature
async def locations_by_name(self, name: str, filters: list[LocationFilter] | None = None):
    ...
```

## Success Criteria
- All checklist items addressed
- No regressions introduced
- Tests pass locally and in CI
- Code quality maintained or improved
- Documentation complete and accurate
- EfaClient compatibility preserved
- Performance not degraded
