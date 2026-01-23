# CLI Tool Quick Reference

## Installation

No additional installation needed if sofiaclient is installed:
```bash
pip install -e .
```

For TUI application:
```bash
pip install textual
```

## Basic Usage

```bash
python cli/sofia_cli.py <command> [options]
```

## Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `search-stops` | Find stops by name | `search-stops "Централна"` |
| `get-stop` | Get stop details | `get-stop A1289` |
| `search-routes` | Find routes by name/number | `search-routes "84"` |
| `routes-for-stop` | Routes serving a stop | `routes-for-stop A1289` |
| `departures` | Upcoming departures | `departures A1289 --realtime` |
| `arrivals` | Route arrivals | `arrivals A57 --stop-ids A1289` |
| `trip-time` | Calculate travel time | `trip-time A1001 A1003 A57` |
| `cache-info` | Show cache status | `cache-info` |
| `realtime` | Raw real-time data | `realtime trip --limit 10` |

## Common Options

- `--help` - Show help for any command
- `--limit N` - Limit results to N items (default: 20)
- `--realtime` - Include real-time delay information
- `--time "HH:MM"` - Filter by time
- `--type TYPE` - Filter by transport type (TRAM, SUBWAY, etc.)
- `--real-stop-id N` - Query stops with A, TB, TM prefixes

## Quick Examples

### Search and Navigate
```bash
# Find a stop
python cli/sofia_cli.py search-stops "Орлов мост"

# Get its routes
python cli/sofia_cli.py routes-for-stop A1289

# Check departures
python cli/sofia_cli.py departures A1289 --realtime --limit 10

# Query multiple stops at once (A1289, TB1289, TM1289)
python cli/sofia_cli.py departures --real-stop-id 1289 --realtime
```

### Route Planning
```bash
# Find a route (note: returns route ID, not name)
python cli/sofia_cli.py search-routes "94"
# Output: Route ID: A57, Name: 94

# Check arrivals (use route ID)
python cli/sofia_cli.py arrivals A57 --stop-ids A1289 --realtime

# Calculate trip time
python cli/sofia_cli.py trip-time A1001 A1003 A57
```

### Real-time Data
```bash
# Trip updates (delays)
python cli/sofia_cli.py realtime trip --limit 10

# Vehicle positions
python cli/sofia_cli.py realtime vehicle --limit 10

# Export to CSV
python cli/sofia_cli.py realtime trip --csv
```

### With Filters
```bash
# Trams only
python cli/sofia_cli.py search-routes "трамвай" --type TRAM

# After specific time
python cli/sofia_cli.py departures A1289 --time "09:00"

# Metro departures
python cli/sofia_cli.py departures M7 --limit 10
```

## TUI Application

Interactive terminal interface:
```bash
python utils/tui/app.py
# Or: python -m utils.tui
```

**Keyboard shortcuts:** `q` quit, `r` refresh, `d` departures tab

## Stop ID Prefixes

| Prefix | Transport Type |
|--------|---------------|
| `A` | Bus |
| `TB` | Trolleybus |
| `TM` | Tram |
| `M` | Metro |

## Transport Types

- `TRAM` - Tram lines
- `SUBWAY` - Metro lines
- `TRAIN` - Train services
- `CITY_BUS` - City bus routes
- `INTERCITY_BUS` - Intercity buses
- `TROLLEYBUS` - Trolleybus lines

## Output Format

Departures and arrivals display as tables:

```
  Line            Direction        Scheduled  Estimated  Deviation  Live
  ----------------------------------------------------------------------
  94 (CITY_BUS)   СТУДЕНТСКИ ГРАД  17:06      17:08      +2 min     ✓
  84 (CITY_BUS)   УЛ. ГЕН. ГУРКО   17:08      -          -          ✗
```

- **Live column:** ✓ = real-time data available, ✗ = scheduled only

## Files

- **cli/sofia_cli.py** - Main CLI tool
- **cli/README.md** - Complete documentation
- **cli/USAGE.md** - Usage guide
- **cli/QUICK_REFERENCE.md** - This file
- **cli/demo.sh** - Interactive demo script
- **utils/tui/app.py** - TUI application

## Troubleshooting

**Command not found**: Use `python` or `python3`

**Module not found**: Install package with `pip install -e .`

**No results**: Check internet connection and API accessibility

**Route not found**: Use route ID (e.g., A57) not route name (e.g., 94)

## Documentation

- Full CLI documentation: [cli/README.md](README.md)
- Usage guide: [cli/USAGE.md](USAGE.md)
- API documentation: [docs/API.md](../docs/API.md)
- Main README: [README.md](../README.md)
