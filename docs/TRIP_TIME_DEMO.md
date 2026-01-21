# Trip Time CLI Demo Guide

This guide demonstrates how to use the `trip-time` command with real Sofia traffic data.

## Overview

The `trip-time` command calculates travel time between two stops on a specific route. It supports both:
- **Scheduled time** (static GTFS data)
- **Real-time estimates** (with live delay information)

## Usage

```bash
./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE> [OPTIONS]
```

### Options

- `--realtime` - Include real-time delays (default: enabled)
- `--no-realtime` - Use only scheduled times (no real-time data)

## Examples

### 1. Using Default (Real-time Enabled)

```bash
# Calculate trip time with real-time delays
./sofia_cli.py trip-time A1139 A6753 A99
```

### 2. Scheduled Time Only

```bash
# Calculate using only static schedule data
./sofia_cli.py trip-time A1139 A6753 A99 --no-realtime
```

### 3. Explicitly Enable Real-time

```bash
# Same as default, but explicit
./sofia_cli.py trip-time A1139 A6753 A99 --realtime
```

## Finding Valid Stop IDs and Routes

### Step 1: Search for Stops

```bash
# Find stops by name
./sofia_cli.py search-stops "национален" --limit 5
```

Example output:
```
Stop ID: A1139
Name: НАЦИОНАЛЕН ДВОРЕЦ НА КУЛТУРАТА
Coordinates: 42.68593215942383, 23.319372177124023
```

### Step 2: Search for Routes

```bash
# Find routes by number
./sofia_cli.py search-routes "97" --limit 5
```

Example output:
```
Route ID: A264
Short Name: 97
Long Name: ХОТЕЛ АМБАСАДОР - МЕТРОСТАНЦИЯ Г. М. ДИМИТРОВ - ХОТЕЛ АМБАСАДОР
Type: 3
```

### Step 3: Check Arrivals at a Stop

```bash
# See what routes service a stop
./sofia_cli.py arrivals A1139 --time 60 --limit 5
```

## Understanding the Output

When a trip time is calculated successfully, you'll see:

```
======================================================================
  Trip Time: A1139 → A6753 on Route A99
======================================================================

  From: A1139
  To: A6753
  Route: A99
  Scheduled Duration: 15 minutes
  Estimated Duration: 18 minutes (with real-time delays)
  Delay: 180 seconds (3 minutes)
```

### Output Fields

- **From/To**: Stop IDs
- **Route**: Route ID
- **Scheduled Duration**: Time based on static schedule
- **Estimated Duration**: Time including real-time delays (only with `--realtime`)
- **Delay**: Additional delay in seconds (only with `--realtime`)

## Common Issues

### "Trip time could not be calculated"

This message appears when:
1. One or both stop IDs don't exist in the GTFS data
2. The route doesn't connect these stops
3. No schedule information exists for this route

**Solution**: Use valid stop and route IDs from the Sofia traffic API.

### No Real-time Data

If real-time data is unavailable, the command will:
- Still calculate scheduled time
- Not show estimated duration or delay fields
- Work the same as `--no-realtime`

## Demo Script

Run the included demo script to see all features:

```bash
./demo_trip_time.sh
```

This script will:
1. Search for available stops
2. Search for available routes
3. Demonstrate scheduled-only calculation
4. Demonstrate real-time calculation
5. Show example usage patterns

## API Usage

You can also use the Python API directly:

```python
from sofiaclient import SofiaNativeClient

async with SofiaNativeClient("https://gtfs.sofiatraffic.bg/api/v1/") as client:
    # With real-time data
    trip_time = await client.calculate_trip_time(
        start_stop_id="A1139",
        end_stop_id="A6753",
        route_id="A99",
        include_realtime=True  # Default
    )
    
    # Scheduled only
    trip_time_scheduled = await client.calculate_trip_time(
        start_stop_id="A1139",
        end_stop_id="A6753",
        route_id="A99",
        include_realtime=False
    )
    
    if trip_time:
        print(f"Scheduled: {trip_time.scheduled_duration} minutes")
        if trip_time.realtime_duration:
            print(f"Real-time: {trip_time.realtime_duration} minutes")
            print(f"Delay: {trip_time.delay_minutes} minutes")
```

## Valid Sofia Traffic Stop IDs

Examples of real stop IDs in the system:
- `A1139` - НАЦИОНАЛЕН ДВОРЕЦ НА КУЛТУРАТА (NDK)
- `A6753` - ЦЕНТРАЛНИ ХАЛИ
- `A2335` - ЦЕНТРАЛНИ ХАЛИ
- `TM2336` - ЦЕНТРАЛНИ ХАЛИ
- `TB1139` - НАЦИОНАЛЕН ДВОРЕЦ НА КУЛТУРАТА

## Valid Sofia Traffic Route IDs

Examples of real route IDs:
- `A99` - Route 84
- `A264` - Route 97
- `A220` - Route 184
- `TB26` - Route 184 (Trolleybus)
- `TB25` - Route 84 (Trolleybus)

## Notes

- Real-time data depends on live feed availability from Sofia Traffic API
- Scheduled times come from the static GTFS data
- Some routes may not have complete schedule information
- Trip time calculations require valid route topology data in `stop_times.txt`
