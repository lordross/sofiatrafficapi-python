#!/bin/bash

# Demo script for trip-time command with real Sofia traffic data
# This script demonstrates the trip-time calculation functionality

echo "======================================================================"
echo "  Sofia Traffic API - Trip Time Demo"
echo "======================================================================"
echo ""
echo "NOTE: The Sofia Traffic GTFS static data may not contain complete"
echo "      stop_times.txt information needed for trip time calculations."
echo "      This demo shows the CLI functionality even if calculations fail."
echo ""

cd cli

echo "1. Finding available stops..."
echo "   Searching for stops near 'НАЦИОНАЛЕН ДВОРЕЦ НА КУЛТУРАТА' (NDK)"
./sofia_cli.py search-stops "национален" --limit 2
echo ""

echo "2. Finding available routes..."
echo "   Searching for route 97"
./sofia_cli.py search-routes "97" --limit 3
echo ""

echo "3. Searching for stops along a route..."
echo "   Finding 'централ' stops"
./sofia_cli.py search-stops "централ" --limit 3
echo ""

echo "4. DEMO: Calculate trip time (SCHEDULED only)"
echo "   Attempting with example stops from the data"
echo "   Command: ./sofia_cli.py trip-time A1139 A6753 A264 --no-realtime"
echo ""
./sofia_cli.py trip-time A1139 A6753 A264 --no-realtime
echo ""

echo "5. DEMO: Calculate trip time (with REALTIME data)"
echo "   Same stops but with real-time delays included"
echo "   Command: ./sofia_cli.py trip-time A1139 A6753 A264 --realtime"
echo ""
./sofia_cli.py trip-time A1139 A6753 A264 --realtime
echo ""

echo "======================================================================"
echo "  Note About Results"
echo "======================================================================"
echo ""
echo "If you see 'Trip time could not be calculated', this means:"
echo "  - The GTFS static data lacks complete stop_times.txt information"
echo "  - The stops are not connected by the specified route"
echo "  - The route doesn't have schedule data"
echo ""
echo "The Sofia Traffic API provides real-time vehicle positions and alerts,"
echo "but the static schedule data (stop_times.txt) may be incomplete or"
echo "not published. This is common for some transit agencies."
echo ""
echo "======================================================================"
echo "  Testing with Mock Data"
echo "======================================================================"
echo ""
echo "To see the trip-time feature working correctly, run the test suite:"
echo "  cd .. && python3 -m pytest tests/test_native_client.py::test_calculate_trip_time -v"
echo ""
echo "The tests use complete mock GTFS data that includes full stop_times"
echo "information, demonstrating the functionality when proper data is available."
echo ""
echo "======================================================================"
echo "  Usage Examples"
echo "======================================================================"
echo ""
echo "  # Scheduled time only:"
echo "  ./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE> --no-realtime"
echo ""
echo "  # With real-time delays (default):"
echo "  ./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE>"
echo "  ./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE> --realtime"
echo ""

