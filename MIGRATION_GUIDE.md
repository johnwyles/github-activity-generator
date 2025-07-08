# Migration Guide: From contribute.py to New CLI Structure

This guide helps you migrate from the old `contribute.py` script to the new modular CLI structure.

## Overview of Changes

The GitHub Activity Generator has been refactored from a single monolithic script (`contribute.py`) into a modular package structure with clear separation of concerns.

### Old Structure
```
contribute.py  # Single file with all functionality
```

### New Structure
```
src/github_activity_generator/
├── __init__.py         # Package initialization
├── cli.py              # CLI argument parsing and entry point
├── core.py             # Main logic orchestration (ActivityGenerator)
├── git_ops.py          # Git operations
├── config_loader.py    # Configuration management
├── validators.py       # Input validation
├── progress.py         # Progress tracking
├── dry_run.py          # Dry-run mode
├── logger.py           # Logging configuration
├── utils.py            # Utility functions
├── constants.py        # Application constants
└── exceptions.py       # Custom exceptions
```

## Command-Line Interface Changes

### Basic Usage (No Changes)
```bash
# Old
python contribute.py

# New
github-activity-generator
# or
python -m github_activity_generator.cli
```

### Argument Names (Mostly Unchanged)
The command-line arguments remain largely the same:

| Old Argument | New Argument | Description |
|--------------|--------------|-------------|
| `-sd, --start_date` | `-sd, --start-date` | Start date (note the hyphen) |
| `-ed, --end_date` | `-ed, --end-date` | End date (note the hyphen) |
| `-mc, --max_commits` | `-mc, --max-commits` | Max commits per day |
| `-fr, --frequency` | `-fr, --frequency` | Frequency percentage |
| `-nw, --no_weekends` | `-nw, --no-weekends` | Skip weekends |
| `-nh, --no_holidays` | `-nh, --no-holidays` | Skip holidays |
| `-ch, --country_holidays` | `-ch, --country-holidays` | Holiday country |
| `-r, --repository` | `-r, --repository` | Repository URL |
| `-un, --user_name` | `-un, --user-name` | Git user name |
| `-ue, --user_email` | `-ue, --user-email` | Git user email |

### New Features
The new structure adds several features:

1. **Configuration Files**
   ```bash
   github-activity-generator --config config.yaml
   ```

2. **Dry Run Mode**
   ```bash
   github-activity-generator --dry-run
   ```

3. **Enhanced Progress Display**
   ```bash
   github-activity-generator --no-progress  # Disable progress bar
   ```

4. **Logging Options**
   ```bash
   github-activity-generator --verbose --log-file activity.log
   ```

## Configuration Files

The new structure supports YAML configuration files:

```yaml
# config.yaml
date_range:
  start_date: "365_days_ago"
  end_date: "today"

commit_behavior:
  max_commits_per_day: 10
  frequency_percentage: 80
  skip_weekends: false
  skip_holidays: false
  holiday_country: "US"

git_settings:
  user_name: "Your Name"
  user_email: "your.email@example.com"
  repository_url: "git@github.com:user/repo.git"

output:
  show_progress: true
  verbose: false
  dry_run: false
```

## Programmatic Usage

### Old Way
```python
import contribute

# Limited programmatic access
contribute.main([
    "--start-date", "2024-01-01",
    "--end-date", "2024-12-31"
])
```

### New Way
```python
from github_activity_generator import ActivityGenerator, Config

# Create configuration
config = Config()
config.date_range.start_date = "2024-01-01"
config.date_range.end_date = "2024-12-31"
config.commit_behavior.max_commits_per_day = 5

# Generate activity
generator = ActivityGenerator(config)
generator.generate()
```

## Key Improvements

1. **Modularity**: Each component can be imported and used independently
2. **Type Safety**: Full type hints throughout the codebase
3. **Better Error Handling**: Custom exceptions with detailed error messages
4. **Dry Run Mode**: Preview what will be generated without making changes
5. **Configuration Files**: Store and reuse configurations
6. **Better Testing**: Modular structure enables unit testing
7. **Progress Tracking**: Rich progress bars and detailed logging
8. **Validation**: Comprehensive input validation with helpful error messages

## Extending the New Structure

The modular design makes it easy to extend functionality:

```python
from github_activity_generator.git_ops import GitOperations
from github_activity_generator.core import ActivityGenerator

# Custom git operations
class CustomGitOps(GitOperations):
    def create_commit(self, directory, date, message, file_path=None):
        # Custom commit logic
        super().create_commit(directory, date, message, file_path)
        # Additional operations

# Custom activity generator
class CustomActivityGenerator(ActivityGenerator):
    def _generate_commit_message(self, date):
        # Custom commit messages
        return f"feat: Custom commit on {date}"
```

## Installation

The new structure is properly packaged:

```bash
# Install from source
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Backwards Compatibility

For temporary backwards compatibility, you can create a wrapper script:

```python
#!/usr/bin/env python3
# contribute.py - Backwards compatibility wrapper

import sys
from github_activity_generator.cli import main

if __name__ == "__main__":
    # Map old argument names to new ones
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ["--start_date", "--end_date", "--max_commits", 
                   "--no_weekends", "--no_holidays", "--country_holidays",
                   "--user_name", "--user_email"]:
            args[i] = arg.replace("_", "-")
    
    sys.exit(main(args))
```

## Summary

The new modular structure provides better maintainability, extensibility, and usability while preserving the core functionality of the original script. The migration is straightforward, with most command-line arguments remaining the same (just using hyphens instead of underscores).