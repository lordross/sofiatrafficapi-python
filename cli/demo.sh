#!/bin/bash
# Quick test script for Sofia CLI tool
# This demonstrates all available commands

set -e

CLI="python3 cli/sofia_cli.py"

echo "========================================"
echo "Sofia Traffic CLI - Quick Demo"
echo "========================================"
echo

echo "1. Show main help"
echo "$ $CLI --help"
$CLI --help
echo
echo "Press Enter to continue..."
read

echo
echo "2. Show command-specific help"
echo "$ $CLI search-stops --help"
$CLI search-stops --help
echo
echo "Press Enter to continue..."
read

echo
echo "3. Test search-stops command"
echo "$ $CLI search-stops 'Централна' --limit 3"
$CLI search-stops "Централна" --limit 3 || echo "Note: Requires real GTFS data"
echo
echo "Press Enter to continue..."
read

echo
echo "4. Test cache-info command"
echo "$ $CLI cache-info"
$CLI cache-info || echo "Note: Requires real GTFS data"
echo

echo
echo "========================================"
echo "Demo Complete!"
echo "========================================"
echo
echo "Available commands:"
echo "  - search-stops: Find stops by name"
echo "  - get-stop: Get stop details"
echo "  - search-routes: Find routes by name/number"
echo "  - routes-for-stop: List all routes at a stop"
echo "  - departures: Get upcoming departures"
echo "  - arrivals: Get arrivals for routes"
echo "  - trip-time: Calculate travel time"
echo "  - cache-info: Show cache status"
echo
echo "For full documentation, see cli/README.md"
