# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of Sofia Traffic API client
- EfaClient-compatible interface for Home Assistant integration
- Native extended API with Sofia-specific features
- GTFS static data parser (stops, routes, trips, stop_times)
- GTFS Realtime parser (TripUpdates, VehiclePositions, ServiceAlerts)
- Smart caching with TTL and Last-Modified checking
- Data models: Location, Line, Destination, Departure, TripTime, StopArrival
- Exception classes compatible with EfaClient
- Comprehensive test suite with pytest
- Type hints and mypy support
- CI/CD pipeline with GitHub Actions
- Documentation and usage examples

### Features
- Search stops by name (substring, case-insensitive)
- Get all routes serving a stop
- Get departures with real-time delay information
- Calculate trip time between two stops on a route
- Search routes by name or number
- Service alerts and detour information
- Vehicle position tracking

## [0.1.0] - 2026-01-21

### Added
- Initial project structure
- Core functionality implementation
- Test suite
- Documentation

[Unreleased]: https://github.com/yourusername/sofiaclient/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/sofiaclient/releases/tag/v0.1.0
