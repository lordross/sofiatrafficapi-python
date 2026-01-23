# Sofia Traffic API CLI Tool

A command-line interface for testing and interacting with the Sofia Traffic API.

## Installation

No additional installation required if you have the `sofiaclient` package installed:

```bash
# From the project root
pip install -e .
```

## Usage

Make the CLI executable (Linux/Mac):

```bash
chmod +x cli/sofia_cli.py
```

Run the tool:

```bash
# Show help
python cli/sofia_cli.py --help

# Or if executable
./cli/sofia_cli.py --help
```

## Available Commands

### Search Stops

Search for stops (stations) by name:

```bash
# Search for stops containing "Централна"
python cli/sofia_cli.py search-stops "Централна"

# Limit results
python cli/sofia_cli.py search-stops "NDK" --limit 5

# Case-insensitive search
python cli/sofia_cli.py search-stops "university"
```

### Get Stop Details

Get detailed information about a specific stop:

```bash
python cli/sofia_cli.py get-stop A1289
```

### Search Routes

Search for routes (lines) by name or number:

```bash
# Search by route number
python cli/sofia_cli.py search-routes "84"

# Search with transport type filter
python cli/sofia_cli.py search-routes "трамвай" --type TRAM

# Available transport types: TRAM, SUBWAY, TRAIN, CITY_BUS, INTERCITY_BUS, TROLLEYBUS
python cli/sofia_cli.py search-routes "метро" --type SUBWAY
```

### Routes for Stop

Get all routes that service a specific stop:

```bash
python cli/sofia_cli.py routes-for-stop A1289
```

### Get Departures

Get upcoming departures from a stop. Results are displayed in a table format with columns: Line, Direction, Scheduled, Estimated, Deviation, and Live indicator.

```bash
# Basic departures (from current time)
python cli/sofia_cli.py departures A1289

# Filter by time (show departures after 09:00)
python cli/sofia_cli.py departures A1289 --time "09:00"

# Include real-time delay information
python cli/sofia_cli.py departures A1289 --realtime

# Limit results
python cli/sofia_cli.py departures A1289 --limit 10

# Combined options
python cli/sofia_cli.py departures A1289 --time "14:30" --realtime --limit 5
```

#### Multi-Stop Query with --real-stop-id

Query multiple stops at once using a numeric stop ID. The CLI will automatically search for stops with A, TB, and TM prefixes and display all results in a single table:

```bash
# Query stops A1289, TB1289, TM1289 at once
python cli/sofia_cli.py departures --real-stop-id 1289 --realtime --limit 15
```

Output example:
```
Stops found: ПЛ. ОРЛОВ МОСТ (A1289), ПЛ. ОРЛОВ МОСТ (TB1289)

Found 10 departure(s):

  Stop            Line            Direction          Scheduled  Estimated  Deviation  Live
  ----------------------------------------------------------------------------------------
  ПЛ. ОРЛОВ МОСТ  94 (CITY_BUS)   СТУДЕНТСКИ ГРАД    17:06      17:08      +2 min     ✓
  ПЛ. ОРЛОВ МОСТ  84 (CITY_BUS)   УЛ. ГЕН. ГУРКО     17:08      17:12      +4 min     ✓
```

### Get Arrivals

Get arrivals at stops for specific routes. Results are displayed in a table format.

**Note:** The arrivals command uses route IDs (not route names). Use `search-routes` to find route IDs first.

```bash
# Find route ID first
python cli/sofia_cli.py search-routes "94"
# Output: Route ID: A57, Name: 94

# Arrivals for one route (using route ID)
python cli/sofia_cli.py arrivals A57

# Arrivals for multiple routes
python cli/sofia_cli.py arrivals A57 A84 A72

# Filter by specific stops
python cli/sofia_cli.py arrivals A57 --stop-ids A1289 A1290

# Filter by time
python cli/sofia_cli.py arrivals A57 --time "10:00"

# Include real-time information
python cli/sofia_cli.py arrivals A57 --realtime

# Combined options
python cli/sofia_cli.py arrivals A57 --stop-ids A1289 --time "09:00" --realtime --limit 15
```

Output example:
```
  Route  Direction        Stop            Scheduled  Estimated  Deviation  Live
  -----------------------------------------------------------------------------
  94     СТУДЕНТСКИ ГРАД  ПЛ. ОРЛОВ МОСТ  17:34      17:41      +7 min     ✓
  94     СТУДЕНТСКИ ГРАД  ПЛ. ОРЛОВ МОСТ  17:40      17:47      +7 min     ✓
```

### Calculate Trip Time

Calculate travel time between two stops on a specific route:

```bash
# Basic trip time
python cli/sofia_cli.py trip-time A1001 A1003 A57

# With real-time delay information
python cli/sofia_cli.py trip-time A1001 A1003 A57 --realtime
```

### Cache Information

Display information about the cached GTFS data:

```bash
python cli/sofia_cli.py cache-info
```

### Real-time Data

Display raw real-time data from the GTFS-RT feeds:

```bash
# Trip updates (delays)
python cli/sofia_cli.py realtime trip --limit 10

# Vehicle positions
python cli/sofia_cli.py realtime vehicle --limit 10

# Service alerts
python cli/sofia_cli.py realtime alerts --limit 10

# Export to CSV
python cli/sofia_cli.py realtime trip --csv
python cli/sofia_cli.py realtime vehicle --csv
python cli/sofia_cli.py realtime alerts --csv
```

## TUI Application

A terminal user interface (TUI) application is available for interactive use:

```bash
# Run the TUI
python utils/tui/app.py

# Or as a module
python -m utils.tui
```

### TUI Features

- **Departures Tab**: View departures from any stop
- **Auto-refresh**: Automatically updates every 1 minute
- **Real-time data**: Shows live departure information
- **Table display**: Clean tabular format with columns for Line, Direction, Scheduled, Estimated, Deviation, and Live indicator

### TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh |
| `d` | Focus departures tab |

### TUI Requirements

The TUI requires the `textual` library:

```bash
pip install textual
```

## Output Format

### Table Format

Departures and arrivals are displayed in a table format:

```
  Line            Direction        Scheduled  Estimated  Deviation  Live
  ----------------------------------------------------------------------
  94 (CITY_BUS)   СТУДЕНТСКИ ГРАД  17:06      17:08      +2 min     ✓
  84 (CITY_BUS)   УЛ. ГЕН. ГУРКО   17:08      -          -          ✗
```

- **Line**: Route number and transport type
- **Direction**: Final destination (headsign)
- **Scheduled**: Planned departure/arrival time
- **Estimated**: Real-time estimated time (if available)
- **Deviation**: Delay status (+X min, -X min, On time)
- **Live**: ✓ if real-time data available, ✗ if not

## Custom API URL

You can specify a custom API base URL:

```bash
python cli/sofia_cli.py --base-url "http://localhost:8000/api/v1/" search-stops "Централна"
```

## Examples

### Complete Workflow Example

```bash
# 1. Search for a stop
python cli/sofia_cli.py search-stops "Орлов мост"
# Output: Stop ID: A1289, Name: ПЛ. ОРЛОВ МОСТ

# 2. Get all routes for that stop
python cli/sofia_cli.py routes-for-stop A1289
# Output: Route A57 (94), Route A84 (84), etc.

# 3. Get upcoming departures with real-time info
python cli/sofia_cli.py departures A1289 --realtime --limit 10

# 4. Or query all nearby stops at once
python cli/sofia_cli.py departures --real-stop-id 1289 --realtime --limit 10
```

### Metro Example

```bash
# Search for metro station
python cli/sofia_cli.py search-stops "Сердика"
# Output: Stop ID: M7, Name: СЕРДИКА

# Get metro departures
python cli/sofia_cli.py departures M7 --limit 10

# Get arrivals for metro line M1
python cli/sofia_cli.py arrivals M1 --stop-ids M7 --limit 10
```

### Bus Route Planning Example

```bash
# Find bus routes
python cli/sofia_cli.py search-routes "94" --type CITY_BUS

# Get arrivals for specific bus routes
python cli/sofia_cli.py arrivals A57 --realtime --limit 20
```

## Error Handling

The tool handles common errors gracefully:

- Network connectivity issues
- Invalid stop/route IDs
- Malformed API responses
- Cache errors

Error messages are printed to stderr and the tool exits with code 1.

## Tips

1. **Use quotes** for search queries with spaces: `"Централна гара"`
2. **Bulgarian text** works in search queries
3. **Case-insensitive** search is automatic
4. **Real-time data** may not always be available - the tool falls back to scheduled times
5. **Cache** is automatically managed - first run downloads GTFS data (~1-2 seconds)
6. **Stop IDs** use prefixes: A (bus), TB (trolleybus), TM (tram), M (metro)
7. **Route IDs** are different from route names - use `search-routes` to find them
8. **--real-stop-id** allows querying multiple stop prefixes at once

## Troubleshooting

### Command not found

Make sure you're running from the correct directory or use the full path:

```bash
python /path/to/sofiatrafficapi-python/cli/sofia_cli.py --help
```

### Module not found

Install the package in development mode:

```bash
cd /path/to/sofiatrafficapi-python
pip install -e .
```

### No data returned

Check your internet connection and verify the API is accessible:

```bash
curl https://gtfs.sofiatraffic.bg/api/v1/static
```

### Cache issues

Clear the cache manually:

```bash
rm -rf ~/.cache/sofiaclient
```

Then run any command to rebuild the cache.

## Development

To modify the CLI tool, edit `cli/sofia_cli.py`. The tool uses:

- `argparse` for command-line parsing
- `asyncio` for async/await operations
- `sofiaclient` package for API interactions

All output goes to stdout, errors to stderr.
