#!/usr/bin/env python3
"""
Sofia Traffic API Command Line Tool

A CLI tool for testing and interacting with the Sofia Traffic API.
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

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
    if location.latitude and location.longitude:
        print(f"  Coordinates: {location.latitude}, {location.longitude}")
    print()


def print_line(line) -> None:
    """Print line (route) details."""
    print(f"  Route ID: {line.id}")
    print(f"  Name: {line.name}")
    print(f"  Type: {line.transport_type}")
    if line.route_type is not None:
        print(f"  GTFS Route Type: {line.route_type}")
    print()


def print_departure(departure) -> None:
    """Print departure details."""
    print(f"  Line: {departure.line_id}")
    planned_str = departure.planned_time.strftime("%H:%M:%S") if departure.planned_time else "N/A"
    print(f"  Scheduled: {planned_str}")

    if departure.estimated_time:
        estimated_str = departure.estimated_time.strftime("%H:%M:%S")
        print(f"  Estimated: {estimated_str}")

        if departure.delay_minutes is not None:
            if departure.delay_minutes > 0:
                print(f"  Delay: +{departure.delay_minutes} min")
            elif departure.delay_minutes < 0:
                print(f"  Delay: {departure.delay_minutes} min (early)")
            else:
                print(f"  Delay: On time")
    print()


def print_arrival(arrival) -> None:
    """Print arrival details."""
    print(f"  Stop ID: {arrival.stop_id}")
    print(f"  Stop Name: {arrival.stop_name}")
    print(f"  Route: {arrival.route_id} - {arrival.route_name}")

    scheduled_str = arrival.scheduled_time.strftime("%H:%M:%S") if arrival.scheduled_time else "N/A"
    print(f"  Scheduled: {scheduled_str}")

    if arrival.estimated_time:
        estimated_str = arrival.estimated_time.strftime("%H:%M:%S")
        print(f"  Estimated: {estimated_str}")

    if arrival.delay_minutes is not None:
        if arrival.delay_minutes > 0:
            print(f"  Delay: +{arrival.delay_minutes} min")
        elif arrival.delay_minutes < 0:
            print(f"  Delay: {arrival.delay_minutes} min (early)")
        else:
            print(f"  Delay: On time")

    if arrival.vehicle_id:
        print(f"  Vehicle: {arrival.vehicle_id}")

    if arrival.headsign:
        print(f"  Headsign: {arrival.headsign}")

    if arrival.alerts:
        print(f"  Alerts: {len(arrival.alerts)}")
        for alert in arrival.alerts:
            print(f"    - {alert}")
    print()


def print_trip_time(trip_time) -> None:
    """Print trip time details."""
    print(f"  From: {trip_time.start_stop_id}")
    print(f"  To: {trip_time.end_stop_id}")
    print(f"  Route: {trip_time.route_id}")
    print(f"  Scheduled Duration: {trip_time.scheduled_duration_str}")
    
    if trip_time.estimated_duration:
        print(f"  Estimated Duration: {trip_time.estimated_duration_str}")
    
    if trip_time.delay:
        print(f"  Delay: {trip_time.delay} seconds")
    print()


async def cmd_search_stops(args) -> None:
    """Search for stops by name."""
    print_header(f"Searching stops: '{args.query}'")
    
    async with SofiaNativeClient(args.base_url) as client:
        stops = await client.search_stops(args.query, limit=args.limit)
        
        if not stops:
            print("  No stops found.")
            return
        
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
        routes = await client.search_routes(
            args.query,
            transport_type=args.type,
            limit=args.limit
        )
        
        if not routes:
            print("  No routes found.")
            return
        
        print(f"Found {len(routes)} route(s):\n")
        for route in routes:
            print_line(route)


async def cmd_routes_for_stop(args) -> None:
    """Get all routes that service a stop."""
    print_header(f"Routes for Stop: {args.stop_id}")
    
    async with SofiaClient(args.base_url) as client:
        routes = await client.lines_by_location(args.stop_id)
        
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
    """Get arrivals at stops for specific routes."""
    print_header(f"Arrivals for Route(s): {', '.join(args.route_ids)}")
    
    async with SofiaNativeClient(args.base_url) as client:
        arrivals = await client.get_arrivals(
            route_ids=args.route_ids,
            stop_ids=args.stop_ids,
            after_time=args.time,
            realtime=args.realtime
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
    
    async with SofiaNativeClient(args.base_url) as client:
        trip_time = await client.calculate_trip_time(
            start_stop_id=args.start_stop,
            end_stop_id=args.end_stop,
            route_id=args.route,
            realtime=args.realtime
        )
        
        if not trip_time:
            print("  Trip time could not be calculated.")
            print("  Make sure the stops are on the specified route.")
            return
        
        print_trip_time(trip_time)


async def cmd_cache_info(args) -> None:
    """Display cache information."""
    print_header("Cache Information")

    async with SofiaNativeClient(args.base_url) as client:
        info = client.get_cache_info()

        print(f"  Cache Directory: {info['cache_dir']}")
        print(f"  Cache Exists: {info['cache_exists']}")

        if info['cache_exists']:
            last_update = datetime.fromisoformat(info['last_update'])
            print(f"  Last Update: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  TTL Hours: {info['ttl_hours']}")

        print()


def to_local_time(dt):
    """Convert datetime to local timezone."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


async def cmd_realtime(args) -> None:
    """Display raw real-time data from the API."""
    import csv
    import httpx
    from sofiaclient.realtime_parser import GTFSRealtimeParser

    print_header(f"Real-time Data: {args.feed_type}")

    base_url = args.base_url.rstrip("/")

    # Map feed type to URL endpoint
    feed_urls = {
        "trip": f"{base_url}/trip-updates",
        "vehicle": f"{base_url}/vehicle-positions",
        "alerts": f"{base_url}/alerts",
    }

    url = feed_urls.get(args.feed_type)
    if not url:
        print(f"  Unknown feed type: {args.feed_type}")
        return

    print(f"  Fetching from: {url}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.content

            parser = GTFSRealtimeParser()

            if args.feed_type == "trip":
                updates = parser.parse_trip_updates(data)
                total_updates = sum(len(v) for v in updates.values())
                print(f"  Found {total_updates} trip updates for {len(updates)} stops:\n")

                # Save to CSV if requested
                if args.csv:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"trip_updates_{timestamp}.csv"
                    with open(filename, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "stop_id", "trip_id", "route_id", "stop_sequence",
                            "arrival_delay_sec", "arrival_time",
                            "departure_delay_sec", "departure_time"
                        ])
                        for stop_id, stop_updates in updates.items():
                            for update in stop_updates:
                                writer.writerow([
                                    stop_id,
                                    update.get("trip_id", ""),
                                    update.get("route_id", ""),
                                    update.get("stop_sequence", ""),
                                    update.get("arrival_delay", ""),
                                    to_local_time(update.get("arrival_time")) or "",
                                    update.get("departure_delay", ""),
                                    to_local_time(update.get("departure_time")) or "",
                                ])
                    print(f"  Saved {total_updates} records to {filename}\n")
                else:
                    # Display to console with limit
                    count = 0
                    for stop_id, stop_updates in updates.items():
                        if args.limit and count >= args.limit:
                            print(f"\n  ... and {len(updates) - count} more stops")
                            break

                        print(f"  Stop: {stop_id}")
                        for update in stop_updates[:3]:
                            print(f"    Trip: {update['trip_id']}")
                            if update.get('route_id'):
                                print(f"    Route: {update['route_id']}")
                            if update.get('arrival_delay') is not None:
                                delay_min = update['arrival_delay'] // 60
                                print(f"    Arrival Delay: {delay_min} min ({update['arrival_delay']} sec)")
                            if update.get('departure_delay') is not None:
                                delay_min = update['departure_delay'] // 60
                                print(f"    Departure Delay: {delay_min} min ({update['departure_delay']} sec)")
                            if update.get('arrival_time'):
                                print(f"    Arrival Time: {to_local_time(update['arrival_time'])}")
                            if update.get('departure_time'):
                                print(f"    Departure Time: {to_local_time(update['departure_time'])}")
                            print()
                        if len(stop_updates) > 3:
                            print(f"    ... and {len(stop_updates) - 3} more updates for this stop\n")
                        count += 1

            elif args.feed_type == "vehicle":
                positions = parser.parse_vehicle_positions(data)
                print(f"  Found {len(positions)} vehicle positions:\n")

                # Save to CSV if requested
                if args.csv:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"vehicle_positions_{timestamp}.csv"
                    with open(filename, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "vehicle_id", "trip_id", "route_id",
                            "latitude", "longitude", "stop_id",
                            "current_stop_sequence", "timestamp"
                        ])
                        for vehicle_id, pos in positions.items():
                            writer.writerow([
                                vehicle_id,
                                pos.get("trip_id", ""),
                                pos.get("route_id", ""),
                                pos.get("latitude", ""),
                                pos.get("longitude", ""),
                                pos.get("stop_id", ""),
                                pos.get("current_stop_sequence", ""),
                                to_local_time(pos.get("timestamp")) or "",
                            ])
                    print(f"  Saved {len(positions)} records to {filename}\n")
                else:
                    # Display to console with limit
                    count = 0
                    for vehicle_id, pos in positions.items():
                        if args.limit and count >= args.limit:
                            print(f"\n  ... and {len(positions) - count} more vehicles")
                            break

                        print(f"  Vehicle: {vehicle_id}")
                        if pos.get('trip_id'):
                            print(f"    Trip: {pos['trip_id']}")
                        if pos.get('route_id'):
                            print(f"    Route: {pos['route_id']}")
                        if pos.get('latitude') and pos.get('longitude'):
                            print(f"    Position: {pos['latitude']}, {pos['longitude']}")
                        if pos.get('stop_id'):
                            print(f"    Current Stop: {pos['stop_id']}")
                        if pos.get('timestamp'):
                            print(f"    Timestamp: {to_local_time(pos['timestamp'])}")
                        print()
                        count += 1

            elif args.feed_type == "alerts":
                alerts = parser.parse_service_alerts(data)
                route_alerts = alerts.get('routes', {})
                stop_alerts = alerts.get('stops', {})

                total_alerts = sum(len(v) for v in route_alerts.values()) + sum(len(v) for v in stop_alerts.values())
                print(f"  Found {total_alerts} alerts for {len(route_alerts)} routes and {len(stop_alerts)} stops:\n")

                # Save to CSV if requested
                if args.csv:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"service_alerts_{timestamp}.csv"
                    with open(filename, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "entity_type", "entity_id", "alert_id",
                            "header", "description", "cause", "effect"
                        ])
                        for route_id, route_alert_list in route_alerts.items():
                            for alert in route_alert_list:
                                writer.writerow([
                                    "route",
                                    route_id,
                                    alert.get("alert_id", ""),
                                    alert.get("header", ""),
                                    alert.get("description", ""),
                                    alert.get("cause", ""),
                                    alert.get("effect", ""),
                                ])
                        for stop_id, stop_alert_list in stop_alerts.items():
                            for alert in stop_alert_list:
                                writer.writerow([
                                    "stop",
                                    stop_id,
                                    alert.get("alert_id", ""),
                                    alert.get("header", ""),
                                    alert.get("description", ""),
                                    alert.get("cause", ""),
                                    alert.get("effect", ""),
                                ])
                    print(f"  Saved {total_alerts} records to {filename}\n")
                else:
                    # Display to console with limit
                    count = 0
                    for route_id, route_alert_list in route_alerts.items():
                        if args.limit and count >= args.limit:
                            print(f"\n  ... and more alerts")
                            break

                        print(f"  Route: {route_id}")
                        for alert in route_alert_list:
                            if alert.get('header'):
                                print(f"    Header: {alert['header']}")
                            if alert.get('description'):
                                print(f"    Description: {alert['description'][:100]}...")
                        print()
                        count += 1

                    for stop_id, stop_alert_list in stop_alerts.items():
                        if args.limit and count >= args.limit:
                            break

                        print(f"  Stop: {stop_id}")
                        for alert in stop_alert_list:
                            if alert.get('header'):
                                print(f"    Header: {alert['header']}")
                            if alert.get('description'):
                                print(f"    Description: {alert['description'][:100]}...")
                        print()
                        count += 1

        except httpx.HTTPError as e:
            print(f"  Error fetching data: {e}")
        except Exception as e:
            print(f"  Error parsing data: {e}")


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
  %(prog)s trip-time 1001 1003 84
  %(prog)s trip-time 1001 1003 84 --realtime
  
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
    search_routes.add_argument("--type", help="Transport type filter", choices=[t.name for t in TransportType])
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
        help="Get arrivals at stops for specific routes"
    )
    arrivals.add_argument("route_ids", nargs="+", help="Route IDs")
    arrivals.add_argument("--stop-ids", nargs="+", help="Optional stop IDs to filter")
    arrivals.add_argument("--time", help="Filter arrivals after this time (HH:MM)")
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
    trip_time.add_argument("--realtime", action="store_true", help="Include real-time delay information")
    
    # Cache info
    subparsers.add_parser(
        "cache-info",
        help="Display cache information"
    )

    # Realtime data
    realtime = subparsers.add_parser(
        "realtime",
        help="Display raw real-time data from the API"
    )
    realtime.add_argument(
        "feed_type",
        choices=["trip", "vehicle", "alerts"],
        help="Type of real-time feed (trip=delays, vehicle=positions, alerts=service alerts)"
    )
    realtime.add_argument("--limit", type=int, default=10, help="Maximum items to display (default: 10)")
    realtime.add_argument("--csv", action="store_true", help="Save all data to CSV file with timestamp")

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
        elif args.command == "realtime":
            await cmd_realtime(args)
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
