#!/bin/bash

# Demo script for trip-time command with real Sofia traffic data
# This script demonstrates the trip-time calculation functionality

echo "======================================================================"
echo "  Sofia Traffic API - Trip Time Demo"
echo "======================================================================"
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
echo "   Using example stops from the data (may not calculate if route doesn't connect them)"
echo "   Command: ./sofia_cli.py trip-time A1139 A6753 A99 --no-realtime"
./sofia_cli.py trip-time A1139 A6753 A99 --no-realtime
echo ""

echo "5. DEMO: Calculate trip time (with REALTIME data)"
echo "   Same stops but with real-time delays included"
echo "   Command: ./sofia_cli.py trip-time A1139 A6753 A99 --realtime"
./sofia_cli.py trip-time A1139 A6753 A99 --realtime
echo ""

echo "======================================================================"
echo "  Demo Complete!"
echo "======================================================================"
echo ""
echo "Usage examples:"
echo "  # Scheduled time only:"
echo "  ./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE> --no-realtime"
echo ""
echo "  # With real-time delays (default):"
echo "  ./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE>"
echo "  ./sofia_cli.py trip-time <START_STOP> <END_STOP> <ROUTE> --realtime"
echo ""
echo "Note: The trip time can only be calculated if:"
echo "  1. Both stops exist in the GTFS static data"
echo "  2. The route connects these stops"
echo "  3. There is schedule information (stop_times.txt) for this route"
echo ""
