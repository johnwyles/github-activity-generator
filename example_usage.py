#!/usr/bin/env python3
"""Example of how to use the new modular structure."""

import sys
from pathlib import Path

# Add src to path for demonstration
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Example 1: Using the CLI programmatically
print("Example 1: Using CLI programmatically")
print("=" * 50)
try:
    from github_activity_generator.cli import main  # noqa: F401
    # This would run the CLI with arguments
    # main(["--dry-run", "--start-date", "2024-01-01", "--end-date", "2024-01-31"])
    print("CLI module imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")

# Example 2: Using the core components directly
print("\n\nExample 2: Using core components directly")
print("=" * 50)
try:
    from github_activity_generator.config_loader import Config
    from github_activity_generator.core import ActivityGenerator  # noqa: F401

    # Create a configuration
    config = Config()

    # Modify configuration as needed
    config.date_range.start_date = "30_days_ago"
    config.date_range.end_date = "today"
    config.commit_behavior.max_commits_per_day = 5
    config.commit_behavior.frequency_percentage = 70
    config.output.dry_run = True  # For demonstration

    print("Configuration created:")
    print(
        f"  Date range: {config.date_range.start_date} "
        f"to {config.date_range.end_date}"
    )
    print(f"  Max commits: {config.commit_behavior.max_commits_per_day}")
    print(f"  Frequency: {config.commit_behavior.frequency_percentage}%")
    print(f"  Dry run: {config.output.dry_run}")

    # Create generator
    # generator = ActivityGenerator(config)
    # generator.generate()

    print("\nCore components imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")

# Example 3: Using git operations directly
print("\n\nExample 3: Using git operations directly")
print("=" * 50)
try:
    from github_activity_generator.git_ops import GitOperations

    # Create git operations handler
    git_ops = GitOperations(dry_run=True, verbose=True)

    print("GitOperations created in dry-run mode")

    # Example operations (in dry-run mode)
    # repo_dir = Path("test-repo")
    # git_ops.init_repository(repo_dir)
    # git_ops.configure_user(repo_dir, name="Test User", email="test@example.com")

    print("Git operations module imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")

# Example 4: Configuration from file
print("\n\nExample 4: Loading configuration from file")
print("=" * 50)
try:
    from github_activity_generator.config_loader import load_config, save_config  # noqa: F401

    # Create example config file
    example_config = Config()
    example_config.date_range.start_date = "2024-01-01"
    example_config.date_range.end_date = "2024-12-31"
    example_config.commit_behavior.skip_weekends = True
    example_config.commit_behavior.skip_holidays = True
    example_config.commit_behavior.holiday_country = "US"

    # Save to file
    config_path = Path("example_config.yaml")
    # save_config(example_config, config_path)
    # print(f"Example config saved to {config_path}")

    # Load from file
    # loaded_config = load_config(config_path)
    # print(f"Config loaded from {config_path}")

    print("Config loader module imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")

print("\n\nModule structure overview:")
print("=" * 50)
print("""
The new structure provides:

1. CLI Interface (cli.py):
   - Command-line argument parsing
   - Entry point for the application
   - Can be used programmatically via main()

2. Core Logic (core.py):
   - ActivityGenerator class
   - Main orchestration of the generation process
   - Handles date ranges, commit creation, and remote setup

3. Git Operations (git_ops.py):
   - GitOperations class
   - All git-related commands
   - Supports dry-run mode
   - Clean separation of git logic

4. Configuration (config_loader.py):
   - Config dataclasses
   - YAML file loading/saving
   - Environment variable substitution
   - Command-line argument merging

5. Other modules:
   - validators.py: Input validation
   - progress.py: Progress tracking
   - dry_run.py: Dry-run simulation
   - logger.py: Logging configuration
   - utils.py: Utility functions
   - constants.py: Application constants
   - exceptions.py: Custom exceptions

This modular structure allows for:
- Easy testing of individual components
- Reusability of modules in other projects
- Clear separation of concerns
- Better maintainability
""")
