#!/usr/bin/env python3
"""
Sofia Traffic API Command Line Tool

A CLI tool for testing and interacting with the Sofia Traffic API.
"""

import argparse
import asyncio
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from sofiaclient import SofiaClient, SofiaNativeClient, TransportType


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_location(location) -> None:
    """Print location details."""
    print(f"  Stop ID: {location.id}")
    print(f"  Name: {location.name}")
    if location.coord:
        lat, lon = location.coord
        print(f"  Coordinates: {lat}, {lon}")
    print()


def print_line(line) -> None:
    """Print line (route) details."""
    print(f"  Route ID: {line.id}")
    print(f"  Name: {line.name}")
    print(f"  Type: {line.product}")
    if hasattr(line, 'route_type') and line.route_type is not None:
        print(f"  GTFS Route Type: {line.route_type}")
    print()


def print_route(route: dict) -> None:
    """Print route dict details from GTFS data."""
    print(f"  Route ID: {route.get('route_id', 'N/A')}")
    print(f"  Short Name: {route.get('route_short_name', 'N/A')}")
    print(f"  Long Name: {route.get('route_long_name', 'N/A')}")
    print(f"  Type: {route.get('route_type', 'N/A')}")
    if route.get('route_color'):
        print(f"  Color: #{route.get('route_color')}")
    print()


def print_departure(departure) -> None:
    """Print departure details."""
    sofia_tz = ZoneInfo("Europe/Sofia")
    
    print(f"  Line: {departure.line_id}")
    planned_str = departure.planned_time.strftime("%H:%M:%S") if departure.planned_time else "N/A"
    print(f"  Scheduled: {planned_str}")
    
    if departure.estimated_time:
        # Convert estimated time to Sofia timezone if it's in UTC or other TZ
        est_time = departure.estimated_time
        if est_time.tzinfo is not None:
            # Convert to Sofia local time
            est_time = est_time.astimezone(sofia_tz)
        
        estimated_str = est_time.strftime("%H:%M:%S")
        print(f"  Estimated: {estimated_str}")
        
        # Show delay if available
        delay = departure.delay_minutes
        if delay is not None:
            if delay > 0:
                print(f"  Delay: +{delay} minutes")
            elif delay < 0:
                print(f"  Early: {abs(delay)} minutes")
            else:
                print(f"  Status: On time")
    else:
        # No real-time data available
        print(f"  Status: No real-time data")
    print()


def print_arrival(arrival) -> None:
    """Print arrival details."""
    sofia_tz = ZoneInfo("Europe/Sofia")
    
    print(f"  Stop ID: {arrival.stop_id}")
    print(f"  Stop Name: {arrival.stop_name}")
    print(f"  Route: {arrival.route_id} - {arrival.route_name}")
    
    scheduled_str = arrival.scheduled_time.strftime("%H:%M:%S") if arrival.scheduled_time else "N/A"
    print(f"  Scheduled: {scheduled_str}")
    
    if arrival.estimated_time:
        # Convert estimated time to Sofia timezone if it's in UTC or other TZ
        est_time = arrival.estimated_time
        if est_time.tzinfo is not None:
            # Convert to Sofia local time
            est_time = est_time.astimezone(sofia_tz)
        
        estimated_str = est_time.strftime("%H:%M:%S")
        print(f"  Estimated: {estimated_str}")
        
        # Show delay if available
        if arrival.delay_minutes is not None:
            if arrival.delay_minutes > 0:
                print(f"  Delay: +{arrival.delay_minutes} minutes")
            elif arrival.delay_minutes < 0:
                print(f"  Early: {abs(arrival.delay_minutes)} minutes")
            else:
                print(f"  Status: On time")
    else:
        # No real-time data available
        print(f"  Status: No real-time data")
    
    if arrival.alerts:
        print(f"  Alerts: {len(arrival.alerts)}")
        for alert in arrival.alerts:
            print(f"    - {alert}")
    print()


def print_trip_time(trip_time, start_stop=None, end_stop=None, next_departure=None, next_arrival=None, departure_obj=None) -> None:
    """Print trip time details."""
    if start_stop:
        print(f"  From: {start_stop.name} ({trip_time.start_stop_id})")
    else:
        print(f"  From: {trip_time.start_stop_id}")
    
    if end_stop:
        print(f"  To: {end_stop.name} ({trip_time.end_stop_id})")
    else:
        print(f"  To: {trip_time.end_stop_id}")
    
    print(f"  Route: {trip_time.route_id}")
    print(f"  Scheduled Duration: {trip_time.scheduled_duration_str}")
    
    if trip_time.realtime_duration is not None:
        print(f"  Realtime Duration: {trip_time.realtime_duration_str}")
    
    if trip_time.delay_minutes is not None:
        if trip_time.delay_minutes > 0:
            print(f"  Route Delay: +{trip_time.delay_minutes} minutes")
        elif trip_time.delay_minutes < 0:
            print(f"  Route Early: {abs(trip_time.delay_minutes)} minutes")
    
    if next_departure:
        print(f"  Next Departure: {next_departure.strftime('%H:%M:%S')}")
        
        # Show departure delay status
        if departure_obj:
            delay = departure_obj.delay_minutes
            if delay is not None:
                if delay > 0:
                    print(f"  Departure Delay: +{delay} minutes")
                elif delay < 0:
                    print(f"  Departure Early: {abs(delay)} minutes")
                else:
                    print(f"  Departure Status: On time")
    
    if next_arrival:
        print(f"  Estimated Arrival: {next_arrival.strftime('%H:%M:%S')}")
    
    print()


async def cmd_search_stops(args) -> None:
    """Search for stops by name."""
    print_header(f"Searching stops: '{args.query}'")
    
    async with SofiaNativeClient(args.base_url) as client:
        stops = await client.search_stops(args.query)
        
        if not stops:
            print("  No stops found.")
            return
        
        # Limit results
        stops = stops[:args.limit]
        
        print(f"Found {len(stops)} stop(s):\n")
        for stop in stops:
            print_location(stop)


async def cmd_get_stop(args) -> None:
    """Get details for a specific stop."""
    print_header(f"Stop Details: {args.stop_id}")
    
    async with SofiaNativeClient(args.base_url) as client:
        stop = await client.get_stop(args.stop_id)
        
        if not stop:
            print(f"  Stop '{args.stop_id}' not found.")
            return
        
        print_location(stop)


async def cmd_search_routes(args) -> None:
    """Search for routes by name or number."""
    print_header(f"Searching routes: '{args.query}'")
    
    async with SofiaNativeClient(args.base_url) as client:
        routes = await client.search_routes(args.query)
        
        if not routes:
            print("  No routes found.")
            return
        
        # Limit results
        routes = routes[:args.limit]
        
        print(f"Found {len(routes)} route(s):\n")
        for route in routes:
            print_route(route)


async def cmd_routes_for_stop(args) -> None:
    """Get all routes that service a stop."""
    print_header(f"Routes for Stop: {args.stop_id}")
    
    async with SofiaNativeClient(args.base_url) as client:
        routes = await client.get_routes_for_stop(args.stop_id)
        
        if not routes:
            print(f"  No routes found for stop '{args.stop_id}'.")
            return
        
        print(f"Found {len(routes)} route(s):\n")
        for route in routes:
            print_line(route)


async def cmd_departures(args) -> None:
    """Get departures from a stop."""
    print_header(f"Departures from Stop: {args.stop_id}")
    
    async with SofiaClient(args.base_url) as client:
        departures = await client.departures_by_location(
            args.stop_id,
            arg_date=args.time,
            realtime=args.realtime
        )
        
        if not departures:
            print(f"  No departures found for stop '{args.stop_id}'.")
            return
        
        # Limit results
        departures = departures[:args.limit]
        
        print(f"Found {len(departures)} departure(s):\n")
        for departure in departures:
            print_departure(departure)


async def cmd_arrivals(args) -> None:
    """Get arrivals at specific stops."""
    print_header(f"Arrivals for Stop(s): {', '.join(args.stop_ids)}")
    
    async with SofiaNativeClient(args.base_url) as client:
        arrivals = await client.get_arrivals(
            stop_ids=args.stop_ids,
            time_offset_minutes=args.time,
            include_realtime=args.realtime
        )
        
        if not arrivals:
            print("  No arrivals found.")
            return
        
        # Limit results
        arrivals = arrivals[:args.limit]
        
        print(f"Found {len(arrivals)} arrival(s):\n")
        for arrival in arrivals:
            print_arrival(arrival)


async def cmd_trip_time(args) -> None:
    """Calculate trip time between two stops on a route."""
    print_header(f"Trip Time: {args.start_stop} → {args.end_stop} on Route {args.route}")
    
    # Sofia timezone (Europe/Sofia)
    sofia_tz = ZoneInfo("Europe/Sofia")
    now = datetime.now(sofia_tz)
    
    async with SofiaNativeClient(args.base_url) as client:
        # Get stop names
        start_stop = await client.get_stop(args.start_stop)
        end_stop = await client.get_stop(args.end_stop)
        
        trip_time = await client.calculate_trip_time(
            start_stop_id=args.start_stop,
            end_stop_id=args.end_stop,
            route_id=args.route,
            include_realtime=args.realtime
        )
        
        if not trip_time:
            print("  Trip time could not be calculated.")
            print("  Make sure the stops are on the specified route.")
            return
        
        # Get next departure to calculate arrival time
        next_departure = None
        next_arrival = None
        next_departure_obj = None
        try:
            # Need to use SofiaClient for departures_by_location
            from sofiaclient import SofiaClient
            async with SofiaClient(args.base_url) as efa_client:
                # Pass current time as filter to get future departures
                current_time_str = now.strftime("%H:%M")
                departures = await efa_client.departures_by_location(
                    location_id=args.start_stop,
                    arg_date=current_time_str,
                    realtime=args.realtime
                )
                # Find next departure for this route
                for dep in departures:
                    if dep.line_id == args.route and dep.planned_time:
                        # Use estimated time if available and makes sense, otherwise use planned
                        departure_time = dep.planned_time
                        
                        if dep.estimated_time:
                            # Convert estimated time to Sofia timezone if it's in UTC or other TZ
                            est_time = dep.estimated_time
                            if est_time.tzinfo is not None:
                                # Convert to Sofia time
                                est_time = est_time.astimezone(sofia_tz)
                            else:
                                # Assume it's Sofia time if naive
                                est_time = est_time.replace(tzinfo=sofia_tz)
                            
                            # Only use estimated if it's in the future
                            if est_time > now:
                                departure_time = est_time
                        
                        # Make timezone-aware if naive
                        if departure_time.tzinfo is None:
                            departure_time = departure_time.replace(tzinfo=sofia_tz)
                        
                        next_departure = departure_time
                        next_departure_obj = dep  # Store the departure object for delay info
                        # Calculate arrival
                        duration_minutes = trip_time.realtime_duration if trip_time.realtime_duration is not None else trip_time.scheduled_duration
                        next_arrival = next_departure + timedelta(minutes=duration_minutes)
                        break
        except Exception as e:
            # Continue without arrival time if we can't fetch it
            pass
        
        print_trip_time(trip_time, start_stop, end_stop, next_departure, next_arrival, next_departure_obj)


async def cmd_cache_info(args) -> None:
    """Display cache information."""
    print_header("Cache Information")
    
    async with SofiaNativeClient(args.base_url) as client:
        info = client.get_cache_info()
        
        print(f"  Cache Directory: {info['cache_dir']}")
        print(f"  Number of Files: {info['num_files']}")
        print(f"  Total Size: {info['total_size_mb']} MB ({info['total_size_bytes']} bytes)")
        
        print()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Sofia Traffic API Command Line Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for stops
  %(prog)s search-stops "Централна"
  %(prog)s search-stops "NDK" --limit 5
  
  # Get stop details
  %(prog)s get-stop 1001
  
  # Search for routes
  %(prog)s search-routes "84"
  %(prog)s search-routes "трамвай" --type TRAM
  
  # Get routes for a stop
  %(prog)s routes-for-stop 1001
  
  # Get departures
  %(prog)s departures 1001
  %(prog)s departures 1001 --time "09:00" --realtime
  %(prog)s departures 1001 --limit 10
  
  # Get arrivals
  %(prog)s arrivals 84 --stop-ids 1001 1002
  %(prog)s arrivals 84 285 --realtime
  
  # Calculate trip time
  %(prog)s trip-time A1139 A6753 A99
  %(prog)s trip-time A1139 A6753 A99 --realtime
  %(prog)s trip-time A1139 A6753 A99 --no-realtime
  
  # Cache information
  %(prog)s cache-info
  
Transport Types: TRAM, SUBWAY, TRAIN, CITY_BUS, INTERCITY_BUS, TROLLEYBUS
        """
    )
    
    parser.add_argument(
        "--base-url",
        default="https://gtfs.sofiatraffic.bg/api/v1/",
        help="Base URL for Sofia Traffic API (default: %(default)s)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search stops
    search_stops = subparsers.add_parser(
        "search-stops",
        help="Search for stops by name"
    )
    search_stops.add_argument("query", help="Search query (substring match)")
    search_stops.add_argument("--limit", type=int, default=20, help="Maximum results (default: 20)")
    
    # Get stop
    get_stop = subparsers.add_parser(
        "get-stop",
        help="Get details for a specific stop"
    )
    get_stop.add_argument("stop_id", help="Stop ID")
    
    # Search routes
    search_routes = subparsers.add_parser(
        "search-routes",
        help="Search for routes by name or number"
    )
    search_routes.add_argument("query", help="Search query")
    search_routes.add_argument("--limit", type=int, default=20, help="Maximum results (default: 20)")
    
    # Routes for stop
    routes_for_stop = subparsers.add_parser(
        "routes-for-stop",
        help="Get all routes that service a stop"
    )
    routes_for_stop.add_argument("stop_id", help="Stop ID")
    
    # Departures
    departures = subparsers.add_parser(
        "departures",
        help="Get departures from a stop"
    )
    departures.add_argument("stop_id", help="Stop ID")
    departures.add_argument("--time", help="Filter departures after this time (HH:MM)")
    departures.add_argument("--realtime", action="store_true", help="Include real-time delay information")
    departures.add_argument("--limit", type=int, default=20, help="Maximum results (default: 20)")
    
    # Arrivals
    arrivals = subparsers.add_parser(
        "arrivals",
        help="Get arrivals at specific stops"
    )
    arrivals.add_argument("stop_ids", nargs="+", help="Stop ID(s)")
    arrivals.add_argument("--time", type=int, help="Time window in minutes (e.g., 30 for next 30 minutes)")
    arrivals.add_argument("--realtime", action="store_true", help="Include real-time information")
    arrivals.add_argument("--limit", type=int, default=20, help="Maximum results (default: 20)")
    
    # Trip time
    trip_time = subparsers.add_parser(
        "trip-time",
        help="Calculate trip time between two stops on a route"
    )
    trip_time.add_argument("start_stop", help="Start stop ID")
    trip_time.add_argument("end_stop", help="End stop ID")
    trip_time.add_argument("route", help="Route ID")
    trip_time.add_argument("--realtime", action="store_true", default=True, help="Include real-time delays (default: True)")
    trip_time.add_argument("--no-realtime", dest="realtime", action="store_false", help="Use only scheduled times")
    
    # Cache info
    subparsers.add_parser(
        "cache-info",
        help="Display cache information"
    )
    
    return parser


async def main() -> None:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Route to appropriate command handler
        if args.command == "search-stops":
            await cmd_search_stops(args)
        elif args.command == "get-stop":
            await cmd_get_stop(args)
        elif args.command == "search-routes":
            await cmd_search_routes(args)
        elif args.command == "routes-for-stop":
            await cmd_routes_for_stop(args)
        elif args.command == "departures":
            await cmd_departures(args)
        elif args.command == "arrivals":
            await cmd_arrivals(args)
        elif args.command == "trip-time":
            await cmd_trip_time(args)
        elif args.command == "cache-info":
            await cmd_cache_info(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
