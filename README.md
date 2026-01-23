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
python cli/sofia_cli.py --help

# Search for stops
python cli/sofia_cli.py search-stops "Орлов мост"

# Get departures with real-time data (table format)
python cli/sofia_cli.py departures A1289 --realtime --limit 10

# Query multiple stops at once (A1289, TB1289, TM1289)
python cli/sofia_cli.py departures --real-stop-id 1289 --realtime

# Get arrivals for a route
python cli/sofia_cli.py arrivals A57 --stop-ids A1289 --realtime

# View raw real-time data
python cli/sofia_cli.py realtime trip --limit 10
```

See [`cli/README.md`](cli/README.md) for complete CLI documentation and examples.

## TUI Application

An interactive terminal UI is also available:

```bash
# Run the TUI
python utils/tui/app.py

# Or as a module
python -m utils.tui
```

Features:
- Real-time departures display with auto-refresh (1 minute)
- Table format with Line, Direction, Scheduled, Estimated, Deviation, Live columns
- Keyboard shortcuts: `q` quit, `r` refresh

Requires: `pip install textual`

## Requirements

- Python 3.10+
- httpx
- gtfs-realtime-bindings
- protobuf
- textual (optional, for TUI application)

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
