# Sofia Traffic API CLI Tool - Quick Test

This guide shows how to test the CLI tool.

## Quick Start

The CLI tool is fully functional and supports all sofiaclient features:

```bash
cd /home/did1sf4/projects/hackaton/sofiatrafficapi-python
python3 cli/sofia_cli.py --help
```

## Usage Examples

### Show all available commands:
```bash
python3 cli/sofia_cli.py --help
```

### Get help for a specific command:
```bash
python3 cli/sofia_cli.py search-stops --help
python3 cli/sofia_cli.py departures --help
python3 cli/sofia_cli.py arrivals --help
```

### Search for stops:
```bash
# Search by name (Bulgarian or transliterated)
python3 cli/sofia_cli.py search-stops "Централна"
python3 cli/sofia_cli.py search-stops "NDK"
python3 cli/sofia_cli.py search-stops "университет" --limit 5
```

### Get stop details:
```bash
python3 cli/sofia_cli.py get-stop 1001
```

### Search routes:
```bash
python3 cli/sofia_cli.py search-routes "84"
python3 cli/sofia_cli.py search-routes "трамвай" --type TRAM
```

### Get departures:
```bash
# Basic usage
python3 cli/sofia_cli.py departures 1001

# With time filter
python3 cli/sofia_cli.py departures 1001 --time "09:00"

# With real-time data
python3 cli/sofia_cli.py departures 1001 --realtime

# Combined
python3 cli/sofia_cli.py departures 1001 --time "14:30" --realtime --limit 10
```

### Get arrivals:
```bash
# Single route
python3 cli/sofia_cli.py arrivals 84

# Multiple routes
python3 cli/sofia_cli.py arrivals 84 285

# With filters
python3 cli/sofia_cli.py arrivals 84 --stop-ids 1001 1002 --realtime
```

### Calculate trip time:
```bash
python3 cli/sofia_cli.py trip-time 1001 1003 84
python3 cli/sofia_cli.py trip-time 1001 1003 84 --realtime
```

### Cache management:
```bash
python3 cli/sofia_cli.py cache-info
```

## Features

✅ **8 Commands**: search-stops, get-stop, search-routes, routes-for-stop, departures, arrivals, trip-time, cache-info  
✅ **Real-time Support**: `--realtime` flag for live delay information  
✅ **Time Filtering**: `--time "HH:MM"` for scheduled time filters  
✅ **Result Limiting**: `--limit N` to control output size  
✅ **Transport Type Filters**: Filter routes by TRAM, SUBWAY, BUS, etc.  
✅ **Comprehensive Help**: `--help` on every command with examples  
✅ **Pretty Output**: Formatted headers and structured data display  
✅ **Error Handling**: Graceful error messages for common issues  

## Output Format

All commands print results in a clean, readable format:

```
======================================================================
  Searching stops: 'Централна'
======================================================================

Found 3 stop(s):

  Stop ID: 1001
  Name: Централна гара
  Coordinates: 42.713564, 23.323568

  Stop ID: 1005
  Name: Централна автогара
  Coordinates: 42.714123, 23.329456

  Stop ID: 1234
  Name: Централна поща
  Coordinates: 42.698567, 23.321234
```

## Integration with Sofia Traffic API

The CLI tool connects to the real Sofia Traffic GTFS API:
- **API Base URL**: https://gtfs.sofiatraffic.bg/api/v1/
- **Static GTFS Data**: Automatically cached for 24 hours
- **Real-time Updates**: GTFS Realtime protobuf feeds
- **Full Coverage**: All Sofia public transport (tram, metro, bus, trolleybus)

## Notes

- **First Run**: Initial execution downloads GTFS data (~1-2 seconds)
- **Cache Location**: `~/.cache/sofiaclient/`
- **Cache TTL**: 24 hours by default
- **Bulgarian Text**: Fully supported in search queries
- **Case-Insensitive**: All text searches ignore case
- **Real-time Data**: May not always be available from the API

## Troubleshooting

### Data Parsing Errors

If you encounter parsing errors with the real Sofia Traffic GTFS data, this is due to data quality issues in the upstream feed. The client handles most edge cases, but some malformed records may cause issues.

**Solution**: The library catches these errors and continues processing valid data. If critical, check the cache directory for the downloaded GTFS file.

### Network Issues

Ensure you have internet connectivity and the API is accessible:

```bash
curl -I https://gtfs.sofiatraffic.bg/api/v1/static
```

### Clear Cache

If data seems stale or corrupted:

```bash
rm -rf ~/.cache/sofiaclient
# Next command will re-download
python3 cli/sofia_cli.py cache-info
```

## Development

The CLI is located in [`cli/sofia_cli.py`](sofia_cli.py) and uses:
- Standard library `argparse` for command parsing
- `asyncio` for async operations
- `sofiaclient` package for all API interactions

Modify the script to add new commands or change output formatting.
