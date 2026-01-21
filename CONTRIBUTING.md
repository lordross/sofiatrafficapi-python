# Contributing to Sofia Traffic API Client

Thank you for your interest in contributing to the Sofia Traffic API Client!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sofiatrafficapi-python.git
   cd sofiatrafficapi-python
   ```

2. **Install uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sofiaclient

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::test_locations_by_name
```

### Code Quality

```bash
# Lint code
ruff check sofiaclient tests

# Format code
ruff format sofiaclient tests

# Type check
mypy sofiaclient
```

### Running All Checks

```bash
# Run all quality checks
ruff check sofiaclient tests && \
ruff format --check sofiaclient tests && \
mypy sofiaclient && \
pytest
```

## Coding Standards

### Style Guide

- Follow PEP 8 standards (enforced by ruff)
- Use type hints for all public methods and functions
- Write comprehensive docstrings (Google style)
- Keep functions focused and small
- Use meaningful variable names

### Type Hints

Always use type hints:

```python
def search_stops(self, query: str) -> list[Location]:
    """Search for stops by name."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_trip_time(
    self, start_stop_id: str, end_stop_id: str, route_id: str
) -> TripTime | None:
    """
    Calculate trip time between two stops on a route.
    
    Args:
        start_stop_id: Starting stop ID
        end_stop_id: Ending stop ID
        route_id: Route ID (line ID)
        
    Returns:
        TripTime object with scheduled and real-time durations, or None if not found
    """
    ...
```

### Testing

- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for common test data
- Mock external API calls with pytest-httpx
- Test both success and error cases

### Error Handling

- Use custom exceptions from `sofiaclient.exceptions`
- Provide meaningful error messages
- Handle network failures gracefully
- Log warnings for data inconsistencies

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the style guide
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   ruff check sofiaclient tests
   ruff format sofiaclient tests
   mypy sofiaclient
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

### Review Checklist

- [ ] Code follows style guide
- [ ] Type hints present and correct
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] API changes documented

## Reporting Issues

### Bug Reports

Include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version)
- Error messages or logs

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed API (if applicable)
- Alternative solutions considered

## Questions?

Feel free to open an issue for questions or discussions.

Thank you for contributing! 🚀
