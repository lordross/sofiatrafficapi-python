# AI Agents for Sofia Traffic API Client

This directory contains specialized AI agent configurations for working on the Sofia Traffic API Client project.

## Agent Files

Each agent has a dedicated file with specific instructions, responsibilities, and workflows:

- [**planning-agent.md**](planning-agent.md) - Research and create implementation plans
- [**implementation-agent.md**](implementation-agent.md) - Execute code changes and features
- [**testing-agent.md**](testing-agent.md) - Create and maintain test suites
- [**documentation-agent.md**](documentation-agent.md) - Maintain project documentation
- [**cicd-agent.md**](cicd-agent.md) - Manage CI/CD pipelines
- [**code-review-agent.md**](code-review-agent.md) - Review code quality and standards
- [**integration-agent.md**](integration-agent.md) - Ensure Home Assistant compatibility

## Quick Reference

### When to Use Each Agent

| Task | Agent |
|------|-------|
| Planning new feature | Planning Agent |
| Implementing code | Implementation Agent |
| Writing tests | Testing Agent |
| Updating docs | Documentation Agent |
| Fixing CI/CD | CI/CD Agent |
| Code review | Code Review Agent |
| HA compatibility | Integration Agent |

### Typical Workflow

1. **Planning Phase** → Planning Agent creates detailed plan
2. **Implementation Phase** → Implementation + Testing + Documentation Agents work together
3. **Review Phase** → Code Review + Integration Agents validate changes
4. **Release Phase** → CI/CD + Documentation Agents handle release

## Agent Communication

Agents coordinate through:
- **Commit messages** - Clear, descriptive commits
- **Code comments** - Explain complex logic
- **Test descriptions** - Document what's being tested
- **Documentation** - Explain architectural decisions

## Project Context

All agents share knowledge of:
- **Architecture**: Dual-client design (SofiaClient + SofiaNativeClient)
- **Data flow**: Static GTFS caching → Real-time merging
- **Standards**: uv + ruff + mypy + pytest
- **Compatibility**: EfaClient interface for Home Assistant

## Usage Guidelines

### For Individual Tasks
Use a single specialized agent:
```
User: "Add method to calculate trip duration"
→ Implementation Agent (after plan approved)
```

### For Complex Features
Use multiple agents in sequence:
```
User: "Add filtering by transport type"
1. Planning Agent → Creates implementation plan
2. Implementation Agent → Writes code
3. Testing Agent → Adds tests
4. Documentation Agent → Updates docs
5. Code Review Agent → Reviews changes
6. Integration Agent → Validates HA compatibility
```

### For Maintenance
Use appropriate agent based on issue:
```
CI pipeline failing → CI/CD Agent
Missing docstrings → Documentation Agent
Low test coverage → Testing Agent
```

## Success Metrics

Across all agents:
- **Code Quality**: ruff ✓, mypy ✓, >80% coverage
- **Compatibility**: EfaClient interface maintained
- **Documentation**: All public APIs documented
- **CI/CD**: All workflows pass on Python 3.10-3.12
- **Integration**: Works with ha-departures component

## See Also

- [../copilot-instructions.md](../copilot-instructions.md) - AI coding assistant guidance
- [../agents.md](../agents.md) - Complete agent system overview
- [../../CONTRIBUTING.md](../../CONTRIBUTING.md) - Development guidelines
