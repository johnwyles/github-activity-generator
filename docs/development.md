# Development Guide

This guide provides detailed information for developers working on GitHub Activity Generator.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Testing Strategy](#testing-strategy)
- [Debugging Tips](#debugging-tips)
- [Performance Considerations](#performance-considerations)
- [Release Process](#release-process)

## Architecture Overview

### High-Level Design

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI Interface │────▶│  Core Generator  │────▶│ Git Operations  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Config Loader   │     │  Date Logic      │     │ File System     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Component Responsibilities

- **CLI Interface**: Parses arguments, validates input
- **Core Generator**: Orchestrates the generation process
- **Git Operations**: Handles all git commands
- **Config Loader**: Loads and merges configuration
- **Date Logic**: Handles date calculations, weekends, holidays
- **File System**: Manages directories and files

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git 2.25 or higher
- Virtual environment tool (venv, virtualenv, or conda)
- Make (optional but recommended)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/github-activity-generator.git
cd github-activity-generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
make install-dev
# or manually:
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Verify setup
make test
```

### IDE Configuration

#### VS Code

```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm

1. Set Project Interpreter to your virtual environment
2. Enable Black formatter: Settings → Tools → Black
3. Configure pytest: Settings → Tools → Python Integrated Tools → Testing → pytest
4. Enable type checking: Settings → Editor → Inspections → Python → Type checker

## Code Structure

### Project Layout

```
github-activity-generator/
├── src/
│   └── github_activity_generator/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # CLI argument parsing
│       ├── core.py              # Core generation logic
│       ├── git_ops.py           # Git operations
│       ├── date_utils.py        # Date calculations
│       ├── config_loader.py     # Configuration handling
│       ├── validators.py        # Input validation
│       ├── progress.py          # Progress bar implementation
│       ├── dry_run.py           # Dry-run mode
│       ├── constants.py         # Shared constants
│       ├── exceptions.py        # Custom exceptions
│       ├── logger.py            # Logging configuration
│       └── utils.py             # Utility functions
├── tests/                       # Test suite
├── docs/                        # Documentation
├── scripts/                     # Development scripts
└── contribute.py               # Legacy entry point
```

### Module Descriptions

#### cli.py
```python
"""Command-line interface handling."""

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    
def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    
def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments."""
```

#### core.py
```python
"""Core generation logic."""

class ActivityGenerator:
    """Main class for generating GitHub activity."""
    
    def __init__(self, config: Config):
        """Initialize with configuration."""
        
    def generate(self) -> None:
        """Generate commits for date range."""
        
    def _should_commit_on_date(self, date: datetime) -> bool:
        """Determine if commits should be made on date."""
```

#### git_ops.py
```python
"""Git operations wrapper."""

class GitOperations:
    """Handle all git commands."""
    
    def init_repository(self) -> None:
        """Initialize git repository."""
        
    def add_and_commit(self, message: str, date: datetime) -> None:
        """Add changes and create commit."""
        
    def push_to_remote(self, url: str) -> None:
        """Push commits to remote repository."""
```

## Testing Strategy

### Test Organization

```
tests/
├── unit/                    # Unit tests
│   ├── test_cli.py
│   ├── test_core.py
│   ├── test_date_utils.py
│   └── test_validators.py
├── integration/            # Integration tests
│   ├── test_git_workflow.py
│   └── test_config_loading.py
├── e2e/                    # End-to-end tests
│   └── test_full_workflow.py
└── fixtures/               # Test data
    ├── configs/
    └── data/
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/test_date_utils.py
import pytest
from datetime import datetime
from github_activity_generator.date_utils import is_weekend, is_holiday

class TestDateUtils:
    """Test date utility functions."""
    
    @pytest.mark.parametrize("date,expected", [
        (datetime(2024, 1, 1), False),   # Monday
        (datetime(2024, 1, 6), True),    # Saturday
        (datetime(2024, 1, 7), True),    # Sunday
    ])
    def test_is_weekend(self, date, expected):
        """Test weekend detection."""
        assert is_weekend(date) == expected
    
    def test_is_holiday_us(self):
        """Test US holiday detection."""
        # New Year's Day
        assert is_holiday(datetime(2024, 1, 1), "US") is True
        # Regular day
        assert is_holiday(datetime(2024, 1, 2), "US") is False
```

#### Integration Test Example

```python
# tests/integration/test_git_workflow.py
import pytest
from pathlib import Path
from github_activity_generator.git_ops import GitOperations

class TestGitWorkflow:
    """Test git operation workflows."""
    
    def test_full_git_workflow(self, tmp_path):
        """Test complete git workflow."""
        git_ops = GitOperations(tmp_path)
        
        # Initialize repository
        git_ops.init_repository()
        assert (tmp_path / ".git").exists()
        
        # Create commit
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        git_ops.add_and_commit(
            "Test commit",
            datetime(2024, 1, 1)
        )
        
        # Verify commit exists
        commits = git_ops.get_commits()
        assert len(commits) == 1
        assert commits[0].message == "Test commit"
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_cli.py

# Run specific test
pytest tests/unit/test_cli.py::TestCLI::test_parse_args

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only unit tests
pytest tests/unit

# Run with verbose output
pytest -vv

# Run tests matching pattern
pytest -k "test_weekend"
```

## Debugging Tips

### Debug Logging

```python
# Enable debug logging in code
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Starting function with args: %s", args)
    # ... code ...
    logger.debug("Result: %s", result)
```

### Interactive Debugging

```python
# Using ipdb
import ipdb

def problematic_function():
    # ... code ...
    ipdb.set_trace()  # Debugger will stop here
    # ... more code ...
```

```bash
# Run with ipdb on exception
python -m ipdb contribute.py --config config.yaml
```

### Git Command Debugging

```bash
# See actual git commands being run
export GIT_TRACE=1
python contribute.py --verbose

# Debug git operations
export GIT_CURL_VERBOSE=1
export GIT_TRACE_PACKET=1
```

### Memory Profiling

```python
# Profile memory usage
from memory_profiler import profile

@profile
def memory_intensive_function():
    # ... code ...
```

```bash
# Run with memory profiling
python -m memory_profiler contribute.py
```

## Performance Considerations

### Optimization Guidelines

1. **Batch Operations**: Group git operations to reduce overhead
2. **Lazy Loading**: Load configuration and modules only when needed
3. **Generator Functions**: Use generators for large date ranges
4. **Caching**: Cache holiday calculations and date operations

### Performance Testing

```python
# tests/performance/test_large_ranges.py
import pytest
import time

@pytest.mark.performance
def test_large_date_range_performance():
    """Test performance with large date range."""
    start_time = time.time()
    
    # Generate 5 years of activity
    generator = ActivityGenerator(config)
    generator.generate()
    
    elapsed = time.time() - start_time
    assert elapsed < 60  # Should complete in under 1 minute
```

### Profiling

```bash
# Profile with cProfile
python -m cProfile -s cumulative contribute.py > profile.txt

# Use line_profiler for detailed analysis
kernprof -l -v contribute.py

# Profile specific functions
@profile
def slow_function():
    # ... code ...
```

## Release Process

### Version Bumping

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md

# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 2.1.0"

# Create tag
git tag -a v2.1.0 -m "Release version 2.1.0"
```

### Building Distribution

```bash
# Clean previous builds
make clean

# Build distribution
make build

# Check distribution
twine check dist/*
```

### Testing Release

```bash
# Test in fresh virtual environment
python -m venv test-release
source test-release/bin/activate

# Install from built distribution
pip install dist/github_activity_generator-2.1.0-py3-none-any.whl

# Run smoke tests
github-activity --help
github-activity --dry_run --start_date 2024-01-01 --end_date 2024-01-07
```

### Publishing

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install -i https://test.pypi.org/simple/ github-activity-generator

# Upload to PyPI
twine upload dist/*
```

### Post-Release

1. Create GitHub release with changelog
2. Update documentation if needed
3. Announce release
4. Monitor for issues

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          pip install build twine
          python -m build
          twine upload dist/*
```

## Code Quality Metrics

### Maintaining Quality

```bash
# Run all quality checks
make check

# Individual checks
make lint       # Linting
make type-check # Type checking
make security   # Security scan
make test       # Tests with coverage
```

### Quality Goals

- Test coverage: 90%+
- Type coverage: 100%
- Linting: 0 errors, 0 warnings
- Security: No high/critical issues
- Documentation: All public APIs documented