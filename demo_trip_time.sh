#!/bin/bash

# Demo script for Sofia Traffic API CLI with real Sofia traffic data
# This script demonstrates all available CLI commands using actual stops and routes

echo "======================================================================"
echo "  Sofia Traffic API - Complete CLI Demo"
echo "======================================================================"
echo ""

cd cli

echo "1. SEARCH STOPS - Finding NDK (National Palace of Culture)"
echo "   Command: ./sofia_cli.py search-stops \"ндк\" --limit 3"
./sofia_cli.py search-stops "ндк" --limit 3
echo ""

echo "2. SEARCH STOPS - Finding Central Station"
echo "   Command: ./sofia_cli.py search-stops \"централна гара\" --limit 3"
./sofia_cli.py search-stops "централна гара" --limit 3
echo ""

echo "3. GET STOP DETAILS - Details for NDK stop A1135"
echo "   Command: ./sofia_cli.py get-stop A1135"
./sofia_cli.py get-stop A1135
echo ""

echo "4. SEARCH ROUTES - Finding route 97"
echo "   Command: ./sofia_cli.py search-routes \"97\" --limit 3"
./sofia_cli.py search-routes "97" --limit 3
echo ""

echo "5. SEARCH ROUTES - Finding all routes containing '9'"
echo "   Command: ./sofia_cli.py search-routes \"9\" --limit 5"
./sofia_cli.py search-routes "9" --limit 5
echo ""

echo "6. ROUTES FOR STOP - All routes serving Central Station (A1333)"
echo "   Command: ./sofia_cli.py routes-for-stop A1333"
./sofia_cli.py routes-for-stop A1333
echo ""

echo "7. DEPARTURES - Next departures from Central Station (A1333)"
echo "   Command: ./sofia_cli.py departures A1333 --limit 5"
./sofia_cli.py departures A1333 --limit 5
echo ""

echo "8. DEPARTURES WITH REALTIME - Real-time departures from A1333"
echo "   Command: ./sofia_cli.py departures A1333 --realtime --limit 5"
./sofia_cli.py departures A1333 --realtime --limit 5
echo ""

echo "9. ARRIVALS - Upcoming arrivals at NDK stops"
echo "   Command: ./sofia_cli.py arrivals A1135 TB6107 --limit 5"
./sofia_cli.py arrivals A1135 TB6107 --limit 5
echo ""

echo "10. ARRIVALS WITH REALTIME - Real-time arrivals at stops"
echo "    Command: ./sofia_cli.py arrivals A1135 TB6107 --realtime --limit 5"
./sofia_cli.py arrivals A1135 TB6107 --realtime --limit 5
echo ""

echo "11. TRIP TIME (SCHEDULED) - NDK to Central Station via Route 97"
echo "    Command: ./sofia_cli.py trip-time A1135 A1333 A264 --no-realtime"
./sofia_cli.py trip-time A1135 A1333 A264 --no-realtime
echo ""

echo "12. TRIP TIME (WITH REALTIME) - Same route with delays"
echo "    Command: ./sofia_cli.py trip-time A1135 A1333 A264 --realtime"
./sofia_cli.py trip-time A1135 A1333 A264 --realtime
echo ""

echo "13. CACHE INFO - Display cache statistics"
echo "    Command: ./sofia_cli.py cache-info"
./sofia_cli.py cache-info
echo ""

echo "======================================================================"
echo "  Demo Complete"
echo "======================================================================"
echo ""
echo "All CLI commands demonstrated with real Sofia Traffic data:"
echo "  ✓ search-stops    - Search for stops by name"
echo "  ✓ get-stop        - Get details for a specific stop"
echo "  ✓ search-routes   - Search for routes by name/number"
echo "  ✓ routes-for-stop - Get all routes serving a stop"
echo "  ✓ departures      - Get departures from a stop"
echo "  ✓ arrivals        - Get arrivals at specific stops"
echo "  ✓ trip-time       - Calculate trip time between stops"
echo "  ✓ cache-info      - Display cache information"
echo ""
echo "Note: Some operations may return no results if the GTFS static data"
echo "      lacks complete schedule information for specific stops/routes."
echo ""

