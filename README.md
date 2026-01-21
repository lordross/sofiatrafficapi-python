# Sofia Traffic API Client

A Python client library for accessing Sofia's public transportation GTFS data with real-time updates.

## Features

- **EfaClient Compatible**: Drop-in replacement for `apyefa.EfaClient` for Home Assistant integration
- **Real-time Data**: Access to vehicle positions, trip updates, and service alerts
- **Static GTFS Data**: Complete access to stops, routes, and schedules
- **Smart Caching**: On-demand caching with TTL for optimal performance
- **Type Safe**: Fully typed with mypy support
- **Async/Await**: Built with asyncio for efficient I/O operations

## Installation

```bash
uv pip install sofiaclient
```

## Quick Start

### EfaClient Compatible Usage (Home Assistant)

```python
from sofiaclient import SofiaClient, LocationFilter

async with SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # Search for stops
    stops = await client.locations_by_name("университет", filters=[LocationFilter.STOPS])
    
    # Get departures for a stop
    departures = await client.departures_by_location(
        stops[0].id,
        arg_date="14:30",
        realtime=True
    )
    
    for dep in departures:
        print(f"{dep.line_id}: {dep.planned_time} (delay: {dep.estimated_time})")
```

### Native Extended API

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
    
    print(f"Scheduled: {trip_time.scheduled_duration}")
    print(f"Real-time: {trip_time.realtime_duration}")
    print(f"Delay: {trip_time.delay_minutes} minutes")
```

## Command-Line Tool

A CLI tool is included for testing and manual interaction:

```bash
# Show help
python3 cli/sofia_cli.py --help

# Search for stops
python3 cli/sofia_cli.py search-stops "Централна"

# Get departures with real-time data
python3 cli/sofia_cli.py departures 1001 --realtime --limit 10

# Calculate trip time
python3 cli/sofia_cli.py trip-time 1001 1003 84 --realtime
```

See [`cli/README.md`](cli/README.md) for complete CLI documentation and examples.

## Requirements

- Python 3.10+
- httpx
- gtfs-realtime-bindings
- protobuf

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy sofiaclient

# Linting and formatting
ruff check sofiaclient
ruff format sofiaclient
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Created by Rosen Nedyalkov for Sofia's public transportation system.
