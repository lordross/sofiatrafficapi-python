"""Enums for Sofia Traffic API client."""

from enum import Enum


class TransportType(Enum):
    """Transport types mapped from GTFS route_type."""

    TRAM = 0  # Tram, Streetcar, Light rail
    SUBWAY = 1  # Subway, Metro
    TRAIN = 2  # Rail
    CITY_BUS = 3  # Bus
    REGIONAL_BUS = 4  # Ferry (mapped as regional bus)
    EXPRESS_BUS = 5  # Cable tram (mapped as express bus)
    AERIAL_LIFT = 6  # Aerial lift, suspended cable car
    FUNICULAR = 7  # Funicular
    TROLLEYBUS = 11  # Trolleybus
    MONORAIL = 12  # Monorail


class LocationFilter(Enum):
    """Filter for location searches."""

    STOPS = "stops"


class LineRequestType(Enum):
    """Type of line request for EfaClient compatibility."""

    DEPARTURE_MONITOR = "departure_monitor"
