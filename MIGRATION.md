# Migration Guide: From contribute.py to Modern Structure

This guide helps you migrate from the original `contribute.py` script to the new modular structure.

## What Changed?

The project has been restructured from a single script (`contribute.py`) to a professional Python package with:

- ✅ Modular architecture with separated concerns
- ✅ Configuration file support (YAML)
- ✅ Better error handling and validation
- ✅ Progress bars and dry-run mode
- ✅ Comprehensive test suite
- ✅ Type hints throughout

## Quick Start

### Old Way
```bash
python contribute.py --start_date 2024-01-01 --end_date 2024-12-31
```

### New Way
```bash
# Option 1: Use the new script directly
python github_activity_generator.py --start_date 2024-01-01 --end_date 2024-12-31

# Option 2: Install and use as a package
pip install -e .
github-activity-generator --start_date 2024-01-01 --end_date 2024-12-31
```

## Command Line Arguments

All arguments from `contribute.py` are supported with the same names:

| Original Argument | Still Works? | Notes |
|------------------|--------------|-------|
| `--start_date` / `-sd` | ✅ Yes | Same format: YYYY-MM-DD |
| `--end_date` / `-ed` | ✅ Yes | Same format: YYYY-MM-DD |
| `--max_commits` / `-mc` | ✅ Yes | Range: 1-20 |
| `--frequency` / `-fr` | ✅ Yes | Range: 0-100 |
| `--no_weekends` / `-nw` | ✅ Yes | |
| `--no_holidays` / `-nh` | ✅ Yes | |
| `--country_holidays` / `-ch` | ✅ Yes | |
| `--repository` / `-r` | ✅ Yes | |
| `--user_name` / `-un` | ✅ Yes | |
| `--user_email` / `-ue` | ✅ Yes | |

## New Features

### 1. Configuration Files

Instead of long command lines, use a configuration file:

```yaml
# config.yaml
date_range:
  start_date: "2024-01-01"
  end_date: "2024-12-31"

commit_behavior:
  max_commits_per_day: 10
  frequency_percentage: 80
  skip_weekends: true
  skip_holidays: true
  holiday_country: "US"

git_settings:
  user_name: "Your Name"
  user_email: "your.email@example.com"
```

Use it:
```bash
github-activity-generator --config config.yaml
```

### 2. Dry Run Mode

Preview what will happen without making commits:

```bash
github-activity-generator --dry_run
```

### 3. Progress Bars

See real-time progress (enabled by default):

```bash
github-activity-generator  # Progress bar shown
github-activity-generator --no_progress  # Disable progress bar
```

### 4. Better Error Messages

The new version provides clearer error messages:

```bash
# Old error:
🔴 Date format is incorrect. Please use YYYY-MM-DD format.

# New error:
Error: Invalid date format: 2024/01/01. Use YYYY-MM-DD or special values like 'today', '30_days_ago'
```

## Using the Original Script

The original `contribute.py` has been preserved as `contribute.py.legacy`:

```bash
# If you need the exact original behavior
python contribute.py.legacy [arguments]
```

## Programmatic Usage

The new structure allows importing and using the generator in your Python code:

```python
from github_activity_generator import ActivityGenerator, load_config

# Load configuration
config = load_config("config.yaml")

# Create and run generator
generator = ActivityGenerator(config)
generator.generate()
```

## Environment Variables

You can now use environment variables in configuration files:

```yaml
git_settings:
  user_name: ${GIT_USER_NAME}
  user_email: ${GIT_USER_EMAIL}
```

## Troubleshooting

### Import Errors

If you get import errors, install the package:

```bash
pip install -e .
```

### Missing Dependencies

Install all dependencies:

```bash
pip install -r requirements.txt
```

### Configuration Not Found

The tool looks for configuration files in this order:
1. Specified with `--config`
2. `config.yaml` in current directory
3. `config.yml` in current directory
4. `.github-activity.yaml` in current directory
5. `.github-activity.yml` in current directory

## Getting Help

```bash
# Show help
github-activity-generator --help

# Enable verbose output for debugging
github-activity-generator --verbose

# Check version
github-activity-generator --version
```

## Reporting Issues

Please report any migration issues at:
https://github.com/yourusername/github-activity-generator/issues