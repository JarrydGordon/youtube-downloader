# Testing Guide for YouTube Downloader

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run With Coverage
```bash
pytest tests/ --cov=youtube_downloader --cov-report=term-missing
```

## Test Organization

```
tests/
├── conftest.py                  # Shared fixtures and test utilities
├── test_config.py              # Configuration module tests
├── test_base_gui.py            # Base GUI class tests
├── test_audio_downloader.py    # Audio downloader tests
├── test_video_downloader.py    # Video downloader tests
├── test_integration.py         # Integration/workflow tests
└── test_error_handling.py      # Error scenarios and edge cases
```

## Running Specific Tests

### By File
```bash
pytest tests/test_config.py -v
pytest tests/test_audio_downloader.py -v
pytest tests/test_integration.py -v
```

### By Test Class
```bash
pytest tests/test_config.py::TestConfig -v
pytest tests/test_base_gui.py::TestBaseGUI -v
```

### By Test Name
```bash
pytest tests/test_config.py::TestConfig::test_platform_detection -v
pytest tests/test_base_gui.py::TestBaseGUI::test_validate_url_valid_youtube -v
```

### By Pattern
```bash
pytest tests/ -k "url_validation" -v
pytest tests/ -k "download" -v
pytest tests/ -k "error" -v
```

## Coverage Reports

### Terminal Report
```bash
pytest tests/ --cov=youtube_downloader --cov-report=term-missing
```

### HTML Report
```bash
pytest tests/ --cov=youtube_downloader --cov-report=html
# Open htmlcov/index.html in browser
```

### XML Report (for CI/CD)
```bash
pytest tests/ --cov=youtube_downloader --cov-report=xml
```

### Multiple Reports
```bash
pytest tests/ --cov=youtube_downloader --cov-report=term-missing --cov-report=html --cov-report=xml
```

## Test Markers

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Debugging Tests

### Show Print Statements
```bash
pytest tests/ -v -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Drop to PDB on Failure
```bash
pytest tests/ --pdb
```

### Show Full Traceback
```bash
pytest tests/ --tb=long
```

### Show Only Failed Tests
```bash
pytest tests/ --tb=short --no-header -q
```

## Parallel Testing

### Run Tests in Parallel (requires pytest-xdist)
```bash
pytest tests/ -n auto
```

### Run Tests on 4 Cores
```bash
pytest tests/ -n 4
```

## Continuous Integration

### Generate Reports for CI
```bash
pytest tests/ \
  --cov=youtube_downloader \
  --cov-report=xml \
  --cov-report=html \
  --junit-xml=test-results.xml \
  -v
```

## Common Testing Scenarios

### Test Configuration Changes
```bash
pytest tests/test_config.py -v
```

### Test Download Functionality
```bash
pytest tests/test_audio_downloader.py tests/test_video_downloader.py -v
```

### Test Error Handling
```bash
pytest tests/test_error_handling.py -v
```

### Test Integration Workflows
```bash
pytest tests/test_integration.py -v
```

### Quick Validation (Fast Tests Only)
```bash
pytest tests/test_config.py tests/test_base_gui.py -v
```

## Writing New Tests

### Example Test Structure
```python
import pytest
from unittest.mock import MagicMock, patch

class TestMyFeature:
    """Test cases for my feature."""
    
    @pytest.fixture
    def my_fixture(self):
        """Create fixture for tests."""
        return MagicMock()
    
    def test_my_feature(self, my_fixture):
        """Test my feature works correctly."""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_feature.do_something()
        
        # Assert
        assert actual == expected
    
    @pytest.mark.parametrize("input,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_with_parameters(self, input, expected):
        """Test with multiple parameter sets."""
        assert process(input) == expected
```

### Using Shared Fixtures
```python
def test_with_shared_fixture(mock_tk_root, temp_dir):
    """Test using shared fixtures from conftest.py."""
    # mock_tk_root and temp_dir are automatically provided
    assert mock_tk_root is not None
    assert temp_dir.exists()
```

## Test Coverage Goals

- **Overall Coverage**: Aim for 70%+ code coverage
- **Critical Paths**: 100% coverage for download and validation logic
- **Error Handling**: All error scenarios should be tested
- **Edge Cases**: Test boundary conditions and unusual inputs

## Troubleshooting

### Tests Fail Due to Missing tkinter
- Ensure conftest.py properly mocks tkinter for headless environments
- Tests should run without requiring a display

### Tests Fail Due to Missing Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Coverage Reports Not Generated
- Ensure pytest-cov is installed: `pip install pytest-cov`
- Check pytest.ini configuration

### Slow Test Execution
- Run in parallel: `pytest -n auto`
- Skip slow tests: `pytest -m "not slow"`

## Best Practices

1. **Run tests before committing**
   ```bash
   pytest tests/ --cov=youtube_downloader
   ```

2. **Check coverage before PR**
   ```bash
   pytest tests/ --cov=youtube_downloader --cov-report=html
   ```

3. **Fix failing tests immediately**
   - Don't commit with failing tests
   - Investigate and fix or update tests

4. **Write tests for new features**
   - Add tests in appropriate test file
   - Use shared fixtures when possible
   - Follow existing patterns

5. **Update tests when changing functionality**
   - Ensure tests reflect new behavior
   - Update docstrings
   - Maintain coverage levels

## Resources

- pytest documentation: https://docs.pytest.org/
- pytest-cov documentation: https://pytest-cov.readthedocs.io/
- unittest.mock guide: https://docs.python.org/3/library/unittest.mock.html
