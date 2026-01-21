"""Custom exceptions for Sofia Traffic API client."""


class SofiaClientError(Exception):
    """Base exception for Sofia client errors."""

    pass


class EfaConnectionError(SofiaClientError):
    """Raised when connection to API fails. Compatible with EfaClient."""

    pass


class EfaResponseInvalid(SofiaClientError):
    """Raised when API response is invalid or cannot be parsed. Compatible with EfaClient."""

    pass


class DataParseError(SofiaClientError):
    """Raised when GTFS data parsing fails."""

    pass


class CacheError(SofiaClientError):
    """Raised when cache operations fail."""

    pass
