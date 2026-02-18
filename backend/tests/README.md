# MarketRadar Tests

This directory contains all tests for the MarketRadar application.

## Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_agent.py
│   ├── test_extractor.py
│   ├── test_memory.py
│   ├── test_mission_repository.py
│   └── test_mission_service.py
└── integration/             # Integration tests
    └── test_api.py
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_agent.py
```

### Run specific test
```bash
pytest tests/unit/test_agent.py::TestMarketRadarAgent::test_analyze_goal_price_research
```

### Run only unit tests
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

After running tests with coverage, view the HTML report:
```bash
open htmlcov/index.html
```

## Writing Tests

### Unit Tests
- Test individual components in isolation
- Use mocks for external dependencies
- Fast execution
- Located in `tests/unit/`

### Integration Tests
- Test component interactions
- Use real implementations where possible
- May be slower
- Located in `tests/integration/`

### Fixtures
Shared fixtures are defined in `conftest.py`:
- `mission_repository`: MissionRepository instance
- `memory`: Memory instance
- `mock_browser_engine`: Mocked BrowserEngine
- `mission_service`: MissionService instance
- `sample_mission_data`: Sample mission data
- `sample_extracted_data`: Sample extracted data

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External Dependencies**: Don't make real network calls in unit tests
5. **Test Edge Cases**: Include boundary conditions and error cases
6. **Keep Tests Fast**: Unit tests should run quickly

## Example Test

```python
def test_create_mission(mission_service):
    """Test creating a new mission."""
    result = mission_service.create_mission(
        goal="Test goal",
        headless=True,
        max_iterations=50
    )
    
    assert "mission_id" in result
    assert result["mission_id"] is not None
```
