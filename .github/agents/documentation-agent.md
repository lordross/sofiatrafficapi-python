# Documentation Agent

## Purpose
Maintain comprehensive project documentation.

## Responsibilities
- Write and update README.md
- Create API documentation (docs/API.md)
- Write usage examples and tutorials
- Document architecture decisions
- Maintain CHANGELOG.md
- Create migration guides (e.g., from EfaClient)

## Documentation Standards
- Clear, concise language
- Practical code examples with type hints
- Links to GTFS specification when relevant
- Keep documentation synchronized with code
- Use Google-style docstrings in Python code

## Documentation Structure

### Root Level
```
README.md              - Quick start, installation, basic usage
CONTRIBUTING.md        - Development guidelines, setup, workflow
CHANGELOG.md          - Version history with dates
LICENSE               - MIT license
```

### .github/
```
.github/
├── copilot-instructions.md  - AI agent guidance
├── agents.md               - Agent role definitions
└── agents/                 - Individual agent files
    ├── planning-agent.md
    ├── implementation-agent.md
    ├── testing-agent.md
    ├── documentation-agent.md
    ├── cicd-agent.md
    ├── code-review-agent.md
    └── integration-agent.md
```

### docs/
```
docs/
├── API.md              - Complete API reference
├── TRIP_TIME_DEMO.md   - Trip time calculation examples
└── [future guides]     - Additional tutorials
```

### cli/
```
cli/
├── README.md          - CLI usage guide
├── USAGE.md          - Detailed CLI examples
└── QUICK_REFERENCE.md - Command cheat sheet
```

## Usage Context
Invoke for:
- Documentation updates after feature changes
- Usage examples and tutorials
- API reference updates
- Migration guides
- Architecture decision records

## Documentation Patterns

### Docstrings (Google Style)
```python
async def locations_by_name(
    self, name: str, filters: list[LocationFilter] | None = None
) -> list[Location]:
    """
    Search for locations (stops) by name.
    
    Args:
        name: Search query (substring match, case-insensitive)
        filters: Optional filters (only STOPS supported)
        
    Returns:
        List of matching Location objects
        
    Raises:
        EfaConnectionError: If network request fails
        EfaResponseInvalid: If response data is malformed
        
    Example:
        >>> async with SofiaClient(base_url) as client:
        ...     stops = await client.locations_by_name("университет")
        ...     print(f"Found {len(stops)} stops")
    """
```

### README.md Structure
1. **Title & Description**: What the project does
2. **Features**: Key capabilities (bulleted)
3. **Installation**: Using `uv pip install`
4. **Quick Start**: Basic usage examples
5. **API Overview**: Brief intro to both clients
6. **CLI Tool**: Reference to cli/README.md
7. **Development**: Link to CONTRIBUTING.md
8. **License**: Link to LICENSE

### API Documentation (docs/API.md)
For each public class/method:
```markdown
## SofiaClient

### `locations_by_name(name, filters=None)`

Search for stops by name.

**Parameters:**
- `name` (str): Search query
- `filters` (list[LocationFilter] | None): Optional filters

**Returns:** `list[Location]`

**Raises:**
- `EfaConnectionError`: Network failure
- `EfaResponseInvalid`: Invalid response

**Example:**
```python
async with SofiaClient(base_url) as client:
    stops = await client.locations_by_name("централна гара")
    for stop in stops:
        print(f"{stop.id}: {stop.name}")
```
```

### CHANGELOG.md Format
Follow Keep a Changelog standard:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior Y

### Fixed
- Bug fix Z

## [0.1.0] - 2026-01-21

### Added
- Initial release
- SofiaClient with EfaClient compatibility
- SofiaNativeClient with extended features
```

### Code Examples
Always include:
- **Type hints**: Show proper typing
- **Context managers**: Use `async with`
- **Error handling**: Show try/except where relevant
- **Real data**: Use actual Sofia stop names when possible

```python
# ✓ Good example
from sofiaclient import SofiaClient, LocationFilter

async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Search for stops
    stops = await client.locations_by_name(
        "университет",
        filters=[LocationFilter.STOPS]
    )
    
    # Get departures
    if stops:
        departures = await client.departures_by_location(
            stops[0].id,
            realtime=True
        )
        for dep in departures:
            delay = f" (+{dep.delay_minutes}min)" if dep.delay_minutes else ""
            print(f"{dep.line_id}: {dep.planned_time}{delay}")
```

## Update Workflow

### After Feature Implementation
1. Update relevant docstrings
2. Add example to README.md (if major feature)
3. Update docs/API.md with new methods/classes
4. Add entry to CHANGELOG.md (Unreleased section)
5. Update __init__.py __all__ if needed

### Before Release
1. Move Unreleased changes to versioned section in CHANGELOG.md
2. Verify all examples still work
3. Check links are not broken
4. Update version in pyproject.toml and __init__.py

### For Breaking Changes
1. Document migration path in CHANGELOG.md
2. Create migration guide in docs/ if complex
3. Update all examples
4. Consider deprecation warnings

## GTFS Documentation Links

When documenting GTFS-related features, link to:
- **Static GTFS**: https://gtfs.org/schedule/reference/
  - stops.txt: https://gtfs.org/schedule/reference/#stopstxt
  - routes.txt: https://gtfs.org/schedule/reference/#routestxt
  - trips.txt: https://gtfs.org/schedule/reference/#tripstxt
  - stop_times.txt: https://gtfs.org/schedule/reference/#stop_timestxt

- **GTFS Realtime**: https://gtfs.org/realtime/reference/
  - TripUpdate: https://gtfs.org/realtime/reference/#message-tripupdate
  - VehiclePosition: https://gtfs.org/realtime/reference/#message-vehicleposition
  - Alert: https://gtfs.org/realtime/reference/#message-alert

- **Protobuf**: https://github.com/MobilityData/gtfs-realtime-bindings

## Success Criteria
- All public APIs documented with examples
- Documentation synced with code
- Examples use proper type hints
- CHANGELOG.md updated for all changes
- No broken links
- Clear migration guides for breaking changes
- README.md provides quick start path
