# CLI Tool Quick Reference

## Installation

No additional installation needed if sofiaclient is installed:
```bash
pip install -e .
```

## Basic Usage

```bash
python3 cli/sofia_cli.py <command> [options]
```

## Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `search-stops` | Find stops by name | `search-stops "Централна"` |
| `get-stop` | Get stop details | `get-stop 1001` |
| `search-routes` | Find routes by name/number | `search-routes "84"` |
| `routes-for-stop` | Routes serving a stop | `routes-for-stop 1001` |
| `departures` | Upcoming departures | `departures 1001 --realtime` |
| `arrivals` | Route arrivals | `arrivals 84 --stop-ids 1001` |
| `trip-time` | Calculate travel time | `trip-time 1001 1003 84` |
| `cache-info` | Show cache status | `cache-info` |

## Common Options

- `--help` - Show help for any command
- `--limit N` - Limit results to N items (default: 20)
- `--realtime` - Include real-time delay information
- `--time "HH:MM"` - Filter by time
- `--type TYPE` - Filter by transport type (TRAM, SUBWAY, etc.)

## Quick Examples

### Search and Navigate
```bash
# Find a stop
python3 cli/sofia_cli.py search-stops "университет"

# Get its routes
python3 cli/sofia_cli.py routes-for-stop 1004

# Check departures
python3 cli/sofia_cli.py departures 1004 --realtime --limit 5
```

### Route Planning
```bash
# Find a route
python3 cli/sofia_cli.py search-routes "84"

# Check where it goes
python3 cli/sofia_cli.py arrivals 84 --limit 10

# Calculate trip time
python3 cli/sofia_cli.py trip-time 1001 1003 84
```

### With Filters
```bash
# Trams only
python3 cli/sofia_cli.py search-routes "трамвай" --type TRAM

# After specific time
python3 cli/sofia_cli.py departures 1001 --time "09:00"

# Multiple routes
python3 cli/sofia_cli.py arrivals 84 285 120
```

## Transport Types

- `TRAM` - Tram lines
- `SUBWAY` - Metro lines
- `TRAIN` - Train services
- `CITY_BUS` - City bus routes
- `INTERCITY_BUS` - Intercity buses
- `TROLLEYBUS` - Trolleybus lines

## Output Format

All commands produce formatted output:

```
======================================================================
  Command Description
======================================================================

Result 1:
  Field: Value
  Field: Value

Result 2:
  Field: Value
  Field: Value
```

## Files

- **sofia_cli.py** (405 lines) - Main CLI tool
- **README.md** (270 lines) - Complete documentation
- **USAGE.md** (170 lines) - Usage guide
- **QUICK_REFERENCE.md** (this file) - Quick reference
- **demo.sh** (58 lines) - Interactive demo script

## Running the Demo

```bash
./cli/demo.sh
```

Press Enter at each step to see the next command demonstration.

## Troubleshooting

**Command not found**: Use `python3` instead of `python`

**Module not found**: Install package with `pip install -e .`

**Parsing errors**: The real GTFS data may have quality issues - this is expected

**No results**: Check internet connection and API accessibility

## Documentation

- Full documentation: [cli/README.md](README.md)
- Usage guide: [cli/USAGE.md](USAGE.md)
- API documentation: [docs/API.md](../docs/API.md)
- Main README: [README.md](../README.md)

## Development

The CLI uses:
- `argparse` for command parsing
- `asyncio` for async operations
- `sofiaclient` package for all API calls

Edit `sofia_cli.py` to add new commands or modify output formatting.
