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
python cli/sofia_cli.py get-stop 1001
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
python cli/sofia_cli.py routes-for-stop 1001
```

### Get Departures

Get upcoming departures from a stop:

```bash
# Basic departures
python cli/sofia_cli.py departures 1001

# Filter by time (show departures after 09:00)
python cli/sofia_cli.py departures 1001 --time "09:00"

# Include real-time delay information
python cli/sofia_cli.py departures 1001 --realtime

# Limit results
python cli/sofia_cli.py departures 1001 --limit 10

# Combined options
python cli/sofia_cli.py departures 1001 --time "14:30" --realtime --limit 5
```

### Get Arrivals

Get arrivals at stops for specific routes:

```bash
# Arrivals for one route
python cli/sofia_cli.py arrivals 84

# Arrivals for multiple routes
python cli/sofia_cli.py arrivals 84 285 120

# Filter by specific stops
python cli/sofia_cli.py arrivals 84 --stop-ids 1001 1002 1003

# Filter by time
python cli/sofia_cli.py arrivals 84 --time "10:00"

# Include real-time information
python cli/sofia_cli.py arrivals 84 --realtime

# Combined options
python cli/sofia_cli.py arrivals 84 285 --stop-ids 1001 1002 --time "09:00" --realtime --limit 15
```

### Calculate Trip Time

Calculate travel time between two stops on a specific route:

```bash
# Basic trip time
python cli/sofia_cli.py trip-time 1001 1003 84

# With real-time delay information
python cli/sofia_cli.py trip-time 1001 1003 84 --realtime
```

### Cache Information

Display information about the cached GTFS data:

```bash
python cli/sofia_cli.py cache-info
```

## Custom API URL

You can specify a custom API base URL:

```bash
python cli/sofia_cli.py --base-url "http://localhost:8000/api/v1/" search-stops "Централна"
```

## Examples

### Complete Workflow Example

```bash
# 1. Search for a stop
python cli/sofia_cli.py search-stops "Централна гара"
# Output: Stop ID: 1001, Name: Централна гара

# 2. Get all routes for that stop
python cli/sofia_cli.py routes-for-stop 1001
# Output: Route 84, Route 285, etc.

# 3. Get upcoming departures with real-time info
python cli/sofia_cli.py departures 1001 --realtime --limit 5

# 4. Find destination stop
python cli/sofia_cli.py search-stops "НДК"
# Output: Stop ID: 1003, Name: НДК

# 5. Calculate trip time
python cli/sofia_cli.py trip-time 1001 1003 84 --realtime
```

### Bus Route Planning Example

```bash
# Find bus routes
python cli/sofia_cli.py search-routes "автобус" --type CITY_BUS --limit 10

# Get arrivals for specific bus routes
python cli/sofia_cli.py arrivals 213 305 --realtime --limit 20
```

### Tram Schedule Example

```bash
# Find tram routes
python cli/sofia_cli.py search-routes "трамвай" --type TRAM

# Get tram departures from a stop
python cli/sofia_cli.py departures 1002 --time "08:00" --realtime
```

## Output Format

All commands print results in a human-readable format with clear headers and formatting:

- **Headers**: `=====` separators with command title
- **Sections**: Empty lines between results
- **Details**: Indented information with labels

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
6. **Stop IDs and Route IDs** are preserved from the official Sofia Traffic GTFS feed

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
