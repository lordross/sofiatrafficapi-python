"""Sofia Traffic API Client - GTFS wrapper for Sofia city traffic data."""

from sofiaclient.client import SofiaClient
from sofiaclient.enums import LocationFilter, LineRequestType, TransportType
from sofiaclient.exceptions import EfaConnectionError, EfaResponseInvalid, SofiaClientError
from sofiaclient.models import Departure, Destination, Line, Location
from sofiaclient.native_client import SofiaNativeClient

__version__ = "0.1.0"

__all__ = [
    # Main clients
    "SofiaClient",
    "SofiaNativeClient",
    # Models
    "Location",
    "Line",
    "Destination",
    "Departure",
    # Enums
    "TransportType",
    "LocationFilter",
    "LineRequestType",
    # Exceptions
    "SofiaClientError",
    "EfaConnectionError",
    "EfaResponseInvalid",
]
