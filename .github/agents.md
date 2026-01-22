# AI Agents Configuration for sofiaclient Project

This document defines the roles and responsibilities of AI agents working on the Sofia Traffic API client project.

---

## Planning Agent

### Purpose
Research and create detailed implementation plans for features and changes.

### Responsibilities
- Analyze requirements and existing codebase
- Research GTFS specifications and best practices
- Create actionable, step-by-step plans
- Identify potential issues and edge cases
- Suggest alternative approaches when applicable
- Validate compatibility with EfaClient interface

### Usage Context
Invoke for:
- Feature planning and architecture decisions
- API design and interface changes
- Refactoring plans
- Integration strategies (e.g., Home Assistant compatibility)

### Deliverables
- Detailed implementation plans with numbered steps
- Architecture diagrams (text-based)
- API design specifications
- Risk assessment and mitigation strategies

---

## Implementation Agent

### Purpose
Execute planned changes and implement features in the codebase.

### Responsibilities
- Implement features according to approved plans
- Write clean, typed, tested Python code
- Follow project coding standards (ruff, mypy, uv)
- Create or update tests for new functionality
- Update documentation and docstrings
- Maintain EfaClient compatibility

### Constraints
- Must use `uv` for dependency management
- All code must pass `mypy` type checking
- Code must be formatted with `ruff`
- Tests must be written using `pytest`
- Maintain >80% test coverage

### Usage Context
Invoke after planning phase is approved for:
- Feature implementation
- Bug fixes
- Code refactoring
- Performance optimizations

---

## Testing Agent

### Purpose
Create comprehensive test suites and ensure code quality.

### Responsibilities
- Write unit tests for all modules
- Create integration tests for API interactions
- Set up test fixtures and mocks for GTFS data
- Ensure test coverage meets standards (>80%)
- Validate tests pass in CI/CD pipeline
- Test EfaClient compatibility

### Testing Stack
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-httpx` - Mock HTTP responses

### Test Categories
1. **Unit Tests:** Individual functions and classes
2. **Integration Tests:** API interactions with mocked responses
3. **Compatibility Tests:** EfaClient interface compliance
4. **Edge Case Tests:** Error handling, malformed data

### Usage Context
Invoke for:
- Test creation for new features
- Coverage improvement
- Test debugging and fixes
- Regression test development

---

## Documentation Agent

### Purpose
Maintain comprehensive project documentation.

### Responsibilities
- Write and update README.md
- Create API documentation (docs/API.md)
- Write usage examples and tutorials
- Document architecture decisions
- Maintain CHANGELOG.md
- Create migration guides (e.g., from EfaClient)

### Documentation Standards
- Clear, concise language
- Practical code examples
- Type hints in all examples
- Links to GTFS specification when relevant
- Keep documentation synchronized with code

### Documentation Structure
```
README.md              - Quick start, installation
docs/API.md           - Complete API reference
CONTRIBUTING.md       - Development guidelines
CHANGELOG.md          - Version history
copilot-instructions.md - GitHub Copilot guide
agents.md             - This file
```

### Usage Context
Invoke for:
- Documentation updates after feature changes
- Usage examples and tutorials
- API reference updates
- Migration guides

---

## CI/CD Agent

### Purpose
Set up and maintain continuous integration and deployment pipelines.

### Responsibilities
- Configure GitHub Actions workflows
- Set up automated testing on multiple Python versions
- Configure code quality checks (ruff, mypy)
- Set up coverage reporting
- Manage release automation
- Monitor CI/CD pipeline health

### GitHub Actions Jobs

#### 1. Lint
```yaml
- ruff check sofiaclient tests
- ruff format --check sofiaclient tests
```

#### 2. Type Check
```yaml
- mypy sofiaclient
```

#### 3. Test
```yaml
- pytest --cov=sofiaclient
- Run on Python 3.10, 3.11, 3.12
```

#### 4. Build
```yaml
- python -m build
- Upload artifacts
```

#### 5. Release (Future)
```yaml
- Automated version bumping
- PyPI publishing
```

### Usage Context
Invoke for:
- CI/CD setup and configuration
- Workflow debugging and optimization
- Deployment configuration
- Adding new quality checks

---

## Code Review Agent

### Purpose
Review code changes for quality, correctness, and adherence to standards.

### Responsibilities
- Check code follows project conventions
- Verify type hints are present and correct
- Ensure tests cover new functionality
- Validate documentation is updated
- Identify potential bugs or edge cases
- Suggest performance improvements
- Verify EfaClient compatibility maintained

### Review Checklist

#### Code Quality
- [ ] Code follows PEP 8 and ruff standards
- [ ] Type hints present and correct
- [ ] No hardcoded values
- [ ] Meaningful variable names
- [ ] Functions are focused and small

#### Testing
- [ ] Tests written and passing
- [ ] Edge cases covered
- [ ] Mocks used appropriately
- [ ] Coverage maintained >80%

#### Documentation
- [ ] Docstrings updated (Google style)
- [ ] API changes documented
- [ ] Examples provided for new features
- [ ] CHANGELOG.md updated

#### Error Handling
- [ ] Exceptions handled appropriately
- [ ] Custom exceptions used correctly
- [ ] Error messages are clear
- [ ] Network failures handled gracefully

#### Compatibility
- [ ] EfaClient interface maintained
- [ ] Data models match requirements
- [ ] Async/await used correctly

### Usage Context
Invoke for:
- Pull request reviews
- Code quality audits
- Pre-merge validation
- Refactoring validation

---

## Integration Agent

### Purpose
Ensure Sofia client integrates correctly with external systems, particularly Home Assistant.

### Responsibilities
- Test EfaClient compatibility
- Validate data model compatibility
- Test with ha-departures component
- Identify integration issues
- Document integration procedures

### Integration Testing
1. **Interface Compliance:** Verify all EfaClient methods present
2. **Data Model Match:** Ensure Location, Line, Departure match expected structure
3. **Exception Compatibility:** Test EfaConnectionError, EfaResponseInvalid
4. **Async Context Manager:** Validate __aenter__ and __aexit__
5. **Real Usage Simulation:** Test with Home Assistant-like workflows

### Usage Context
Invoke for:
- Pre-release compatibility checks
- Integration testing
- Home Assistant component validation
- API contract verification

---

## Usage Guidelines

### Workflow

1. **Planning Phase**
   - Planning Agent creates implementation plan
   - Code Review Agent validates plan
   - User approves plan

2. **Implementation Phase**
   - Implementation Agent executes plan
   - Testing Agent writes tests
   - Documentation Agent updates docs
   - CI/CD Agent ensures pipeline passes

3. **Review Phase**
   - Code Review Agent reviews changes
   - Integration Agent tests compatibility
   - User approves changes

4. **Release Phase**
   - CI/CD Agent manages release
   - Documentation Agent updates changelog

### Agent Invocation

```python
# Example: Planning a new feature
# User: "I need to add filtering by transport type"
# -> Invoke Planning Agent

# Planning Agent delivers plan
# User: "Proceed with implementation"
# -> Invoke Implementation Agent + Testing Agent + Documentation Agent

# Implementation complete
# -> Invoke Code Review Agent + Integration Agent

# Review passed
# -> Invoke CI/CD Agent for release
```

### Best Practices

1. **Always start with planning** for non-trivial changes
2. **Test alongside implementation**, not after
3. **Document as you go**, not at the end
4. **Review before merging**, always
5. **Maintain compatibility**, test thoroughly

---

## Agent Communication

Agents should communicate context through:
- Clear commit messages
- Inline code comments for complex logic
- Test descriptions that explain what's being tested
- Documentation that explains why decisions were made

---

## Success Metrics

- **Code Quality:** ruff and mypy pass, >80% coverage
- **Compatibility:** All EfaClient interface tests pass
- **Documentation:** All public APIs documented with examples
- **CI/CD:** All workflows pass on all supported Python versions
- **Integration:** Works with ha-departures component

---

## Maintenance

This agent configuration should be reviewed and updated:
- When adding new features that change workflow
- When project standards change
- When new tools are adopted
- After major refactoring
- Based on lessons learned during development
