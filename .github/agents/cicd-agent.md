# CI/CD Agent

## Purpose
Set up and maintain continuous integration and deployment pipelines.

## Responsibilities
- Configure GitHub Actions workflows
- Set up automated testing on multiple Python versions
- Configure code quality checks (ruff, mypy)
- Set up coverage reporting
- Manage release automation
- Monitor CI/CD pipeline health

## GitHub Actions Workflow

Located at `.github/workflows/ci.yml`

### Job Structure

#### 1. Lint Job
```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v2
    - uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    - run: uv pip install --system -e ".[dev]"
    - run: ruff check sofiaclient tests
    - run: ruff format --check sofiaclient tests
```

**Purpose**: Verify code style and linting standards

#### 2. Type Check Job
```yaml
type-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v2
    - uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    - run: uv pip install --system -e ".[dev]"
    - run: mypy sofiaclient
```

**Purpose**: Ensure 100% type hint coverage

#### 3. Test Job (Matrix)
```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ["3.10", "3.11", "3.12"]
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v2
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: uv pip install --system -e ".[dev]"
    - run: pytest --cov=sofiaclient --cov-report=xml --cov-report=term-missing
    - uses: codecov/codecov-action@v4
      if: matrix.python-version == '3.10'
```

**Purpose**: Run tests across Python versions with coverage

#### 4. Build Job
```yaml
build:
  runs-on: ubuntu-latest
  needs: [lint, type-check, test]
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v2
    - uses: actions/setup-python@v5
    - run: uv pip install --system build
    - run: python -m build
    - uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/
```

**Purpose**: Build package after all checks pass

#### 5. Release Job (Future)
```yaml
release:
  runs-on: ubuntu-latest
  needs: build
  if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')
  steps:
    - uses: actions/checkout@v4
    - uses: actions/download-artifact@v4
    - run: uv pip install --system twine
    - run: twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

**Purpose**: Automated PyPI releases on tag push

## Trigger Conditions

### On Push
```yaml
on:
  push:
    branches: [ main, develop ]
```
Runs all jobs on pushes to main/develop branches

### On Pull Request
```yaml
on:
  pull_request:
    branches: [ main, develop ]
```
Runs all jobs on PRs to main/develop

### On Tag (Future)
```yaml
on:
  push:
    tags:
      - 'v*'
```
Triggers release workflow on version tags

## Usage Context

### Setting Up New Workflow
1. Create workflow file in `.github/workflows/`
2. Define jobs with appropriate dependencies
3. Use `uv` for package management (astral-sh/setup-uv@v2)
4. Test locally before committing

### Adding New Check
1. Add step to existing job or create new job
2. Ensure job fails on error (default behavior)
3. Document in this file
4. Test with a PR

### Monitoring Pipeline
Check workflow runs at:
```
https://github.com/[owner]/sofiatrafficapi-python/actions
```

View specific run details:
- Job logs
- Test output
- Coverage reports
- Build artifacts

## Quality Gates

All checks must pass before merge:

| Check | Tool | Requirement |
|-------|------|-------------|
| Lint | ruff check | No violations |
| Format | ruff format | Properly formatted |
| Type | mypy | 100% coverage |
| Test | pytest | All tests pass |
| Coverage | pytest-cov | >80% overall |
| Build | build | Package builds |

## Local Testing

Before pushing, run the same checks locally:

```bash
# Lint
ruff check sofiaclient tests

# Format
ruff format sofiaclient tests

# Type check
mypy sofiaclient

# Test with coverage
pytest --cov=sofiaclient --cov-report=term-missing

# Build
python -m build
```

## Troubleshooting

### Failed Lint
```bash
# Auto-fix issues
ruff check --fix sofiaclient tests

# Format code
ruff format sofiaclient tests
```

### Failed Type Check
```bash
# Run locally with verbose output
mypy --show-error-codes sofiaclient

# Check specific file
mypy sofiaclient/client.py
```

### Failed Tests
```bash
# Run with verbose output
pytest -vv

# Run specific failing test
pytest tests/test_client.py::test_specific -vv

# Debug with print statements
pytest -s tests/test_client.py::test_specific
```

### Failed Build
```bash
# Check pyproject.toml syntax
python -m build --sdist --wheel

# Verify package contents
tar -tzf dist/sofiaclient-*.tar.gz
unzip -l dist/sofiaclient-*.whl
```

## Coverage Reporting

### Codecov Integration
Upload coverage on Python 3.10 runs only:
```yaml
- uses: codecov/codecov-action@v4
  if: matrix.python-version == '3.10'
  with:
    file: ./coverage.xml
    fail_ci_if_error: false
```

### Local Coverage
```bash
# Generate HTML report
pytest --cov=sofiaclient --cov-report=html

# Open in browser
open htmlcov/index.html
```

## Release Process (Future)

### Manual Release
1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Commit: `git commit -m "Release v0.2.0"`
4. Tag: `git tag v0.2.0`
5. Push: `git push && git push --tags`
6. GitHub Actions builds and publishes to PyPI

### Automated Release
Configure GitHub secrets:
- `PYPI_API_TOKEN`: PyPI API token for publishing

## Best Practices

### Workflow Files
- Use latest action versions (@v4, @v5)
- Pin uv version or use "latest"
- Cache dependencies when possible
- Use matrix for multi-version testing

### Job Dependencies
- Use `needs:` to create job dependencies
- Fail fast if early checks fail
- Run independent jobs in parallel

### Secrets Management
- Store sensitive data in GitHub Secrets
- Never commit credentials
- Use organization secrets for shared tokens

## Success Criteria
- All workflows pass on main/develop
- Tests run on Python 3.10, 3.11, 3.12
- Coverage reports uploaded to Codecov
- Build artifacts generated successfully
- No flaky tests causing random failures
- Workflow execution time <5 minutes
