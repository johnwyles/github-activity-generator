# Configuration Guide

This guide covers all configuration options for GitHub Activity Generator.

## Configuration Methods

GitHub Activity Generator can be configured in three ways (in order of precedence):

1. **Command-line arguments** - Highest priority
2. **Configuration file** - Medium priority
3. **Default values** - Lowest priority

## Configuration File Format

Configuration files use YAML format. Create a file named `config.yaml` or specify a custom path with `--config`.

### Complete Configuration Example

```yaml
# config.yaml - Complete configuration example
date_range:
  # Start date for commit generation
  # Format: YYYY-MM-DD or special values
  # Special values: "today", "yesterday", "N_days_ago" (e.g., "365_days_ago")
  start_date: "365_days_ago"
  
  # End date for commit generation
  # Format: YYYY-MM-DD or special values
  # Special values: "today", "yesterday", "N_days_ago"
  end_date: "today"

commit_behavior:
  # Maximum number of commits to create per day (1-20)
  max_commits_per_day: 10
  
  # Percentage chance of creating commits on any given day (0-100)
  frequency_percentage: 80
  
  # Skip weekends (Saturday and Sunday)
  skip_weekends: false
  
  # Skip holidays based on country calendar
  skip_holidays: false
  
  # Country code for holiday calendar (e.g., US, UK, CA, AU, DE, FR, JP, CN)
  # See: https://python-holidays.readthedocs.io/en/latest/#available-countries
  holiday_country: "US"

git_settings:
  # Git user name (overrides global git config)
  # Set to null to use global git config
  user_name: "Your Name"
  
  # Git user email (overrides global git config)
  # Set to null to use global git config
  user_email: "your.email@example.com"
  
  # Remote repository URL (SSH or HTTPS)
  # Examples:
  # - git@github.com:username/repo.git
  # - https://github.com/username/repo.git
  # Set to null to create local repository only
  repository_url: null

output:
  # Show progress bar during commit generation
  show_progress: true
  
  # Enable verbose output for debugging
  verbose: false
  
  # Dry run mode - preview changes without making commits
  dry_run: false
```

### Minimal Configuration Example

```yaml
# config-minimal.yaml - Minimal configuration
date_range:
  start_date: "2023-01-01"
  end_date: "2023-12-31"

commit_behavior:
  max_commits_per_day: 5
  frequency_percentage: 70
```

## Configuration Options Reference

### Date Range Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `date_range.start_date` | string | 365 days ago | Start date for commits |
| `date_range.end_date` | string | today | End date for commits |

**Date Format Examples:**
- Specific date: `"2023-01-01"`
- Relative dates: `"today"`, `"yesterday"`, `"7_days_ago"`, `"30_days_ago"`

### Commit Behavior Options

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `commit_behavior.max_commits_per_day` | integer | 10 | 1-20 | Maximum commits per day |
| `commit_behavior.frequency_percentage` | integer | 80 | 0-100 | Percentage of days with commits |
| `commit_behavior.skip_weekends` | boolean | false | - | Skip Saturday and Sunday |
| `commit_behavior.skip_holidays` | boolean | false | - | Skip country holidays |
| `commit_behavior.holiday_country` | string | "US" | - | Country code for holidays |

### Git Settings Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `git_settings.user_name` | string/null | null | Git user name override |
| `git_settings.user_email` | string/null | null | Git user email override |
| `git_settings.repository_url` | string/null | null | Remote repository URL |

### Output Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output.show_progress` | boolean | true | Display progress bar |
| `output.verbose` | boolean | false | Enable debug output |
| `output.dry_run` | boolean | false | Preview without commits |

## Environment Variables

Some options can also be set via environment variables:

```bash
# Set default configuration file path
export GITHUB_ACTIVITY_CONFIG="/path/to/config.yaml"

# Override specific settings
export GITHUB_ACTIVITY_MAX_COMMITS=15
export GITHUB_ACTIVITY_FREQUENCY=90
```

## Configuration Profiles

Create multiple configuration files for different scenarios:

### Work Projects Profile

```yaml
# config-work.yaml
date_range:
  start_date: "90_days_ago"
  end_date: "today"

commit_behavior:
  max_commits_per_day: 8
  frequency_percentage: 95
  skip_weekends: true
  skip_holidays: true

git_settings:
  user_name: "Your Work Name"
  user_email: "you@company.com"
```

### Personal Projects Profile

```yaml
# config-personal.yaml
date_range:
  start_date: "365_days_ago"
  end_date: "today"

commit_behavior:
  max_commits_per_day: 5
  frequency_percentage: 60
  skip_weekends: false
  skip_holidays: false

git_settings:
  user_name: "Your Name"
  user_email: "personal@email.com"
```

### Test Repository Profile

```yaml
# config-test.yaml
date_range:
  start_date: "7_days_ago"
  end_date: "today"

commit_behavior:
  max_commits_per_day: 20
  frequency_percentage: 100
  
output:
  verbose: true
  dry_run: true  # Always dry run for testing
```

## Using Configuration Files

### Basic Usage

```bash
# Use default config.yaml in current directory
python contribute.py --config config.yaml

# Use specific configuration file
python contribute.py --config /path/to/config-work.yaml

# Override configuration file values
python contribute.py --config config.yaml --max_commits 5 --frequency 50
```

### Multiple Configurations

```bash
# Generate work activity
python contribute.py --config profiles/work.yaml

# Generate personal activity  
python contribute.py --config profiles/personal.yaml

# Test configuration
python contribute.py --config profiles/test.yaml
```

## Validation

The tool validates all configuration values:

- **Dates**: Must be valid YYYY-MM-DD format or recognized special values
- **Integers**: Must be within specified ranges
- **Booleans**: Must be true/false (or yes/no in YAML)
- **URLs**: Must be valid git repository URLs

Invalid values will produce clear error messages:

```
Error: max_commits_per_day must be between 1 and 20 (got: 25)
Error: frequency_percentage must be between 0 and 100 (got: 150)
Error: Invalid date format for start_date: "2023/01/01" (use YYYY-MM-DD)
```

## Best Practices

1. **Version Control**: Keep configuration files in version control
2. **Sensitive Data**: Don't commit files with personal emails or tokens
3. **Comments**: Document your configuration with comments
4. **Profiles**: Use different files for different scenarios
5. **Validation**: Test configuration with `--dry_run` first

## Troubleshooting

### Configuration Not Loading

```bash
# Check if file exists and is readable
ls -la config.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Use verbose mode to see what's loaded
python contribute.py --config config.yaml --verbose
```

### Unexpected Behavior

```bash
# See final configuration after merging
python contribute.py --config config.yaml --show-config

# Test with dry run
python contribute.py --config config.yaml --dry_run
```