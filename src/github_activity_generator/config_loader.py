"""Configuration loading and management for GitHub Activity Generator."""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from .exceptions import ConfigurationError
from .validators import (
    validate_country_code,
    validate_frequency,
    validate_max_commits,
    validate_repository_url,
)


@dataclass
class DateRangeConfig:
    """Configuration for date range."""

    start_date: str = field(default_factory=lambda: "365_days_ago")
    end_date: str = field(default_factory=lambda: "today")

    def resolve_dates(self) -> tuple[datetime, datetime]:
        """Resolve date strings to datetime objects."""
        start = self._resolve_date(self.start_date)
        end = self._resolve_date(self.end_date)

        if start > end:
            error_msg = f"Start date ({start}) cannot be after end date ({end})"
            raise ConfigurationError(error_msg)

        return start, end

    @staticmethod
    def _resolve_date(date_str: str) -> datetime:
        """Resolve a date string to datetime object."""
        date_str = date_str.strip().lower()

        # Handle special values
        if date_str == "today":
            return datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        if date_str == "yesterday":
            return (datetime.now(timezone.utc) - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        if date_str.endswith("_days_ago"):
            try:
                days = int(date_str.split("_")[0])
                return (datetime.now(timezone.utc) - timedelta(days=days)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            except (ValueError, IndexError) as err:
                error_msg = (
                    f"Invalid relative date format: {date_str}. "
                    "Use format like '30_days_ago'"
                )
                raise ConfigurationError(error_msg) from err
        else:
            # Try to parse as YYYY-MM-DD
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError as err:
                error_msg = (
                    f"Invalid date format: {date_str}. "
                    "Use YYYY-MM-DD or special values like 'today', '30_days_ago'"
                )
                raise ConfigurationError(error_msg) from err


@dataclass
class CommitBehaviorConfig:
    """Configuration for commit behavior."""

    max_commits_per_day: int = 10
    frequency_percentage: int = 80
    skip_weekends: bool = False
    skip_holidays: bool = False
    holiday_country: str = "US"
    behavior: str = "consistent"

    def __post_init__(self):
        """Validate configuration after initialization."""
        validate_max_commits(self.max_commits_per_day)
        validate_frequency(self.frequency_percentage)
        if self.skip_holidays:
            validate_country_code(self.holiday_country)
        # Validate behavior choice
        valid_behaviors = [
            "consistent",
            "regular",
            "intense",
            "hobbyist",
            "opensource",
            "irregular",
        ]
        if self.behavior not in valid_behaviors:
            error_msg = f"Invalid behavior: {self.behavior}. Must be one of: {', '.join(valid_behaviors)}"
            raise ConfigurationError(error_msg)


@dataclass
class GitSettingsConfig:
    """Configuration for git settings."""

    user_name: Optional[str] = None
    user_email: Optional[str] = None
    repository_url: Optional[str] = None
    repo_dir: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.repository_url:
            validate_repository_url(self.repository_url)


@dataclass
class OutputConfig:
    """Configuration for output options."""

    show_progress: bool = True
    verbose: bool = False
    dry_run: bool = False


@dataclass
class Config:
    """Complete configuration for GitHub Activity Generator."""

    date_range: DateRangeConfig = field(default_factory=DateRangeConfig)
    commit_behavior: CommitBehaviorConfig = field(default_factory=CommitBehaviorConfig)
    git_settings: GitSettingsConfig = field(default_factory=GitSettingsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        return cls(
            date_range=DateRangeConfig(**data.get("date_range", {})),
            commit_behavior=CommitBehaviorConfig(**data.get("commit_behavior", {})),
            git_settings=GitSettingsConfig(**data.get("git_settings", {})),
            output=OutputConfig(**data.get("output", {})),
        )

    def merge_with_args(self, args: Any) -> None:  # noqa: C901, PLR0912
        """Merge command-line arguments into configuration."""
        # Date range
        if hasattr(args, "start_date") and args.start_date:
            self.date_range.start_date = args.start_date
        if hasattr(args, "end_date") and args.end_date:
            self.date_range.end_date = args.end_date

        # Commit behavior
        if hasattr(args, "behavior") and args.behavior:
            self.commit_behavior.behavior = args.behavior
        if hasattr(args, "max_commits") and args.max_commits is not None:
            self.commit_behavior.max_commits_per_day = args.max_commits
        if hasattr(args, "frequency") and args.frequency is not None:
            self.commit_behavior.frequency_percentage = args.frequency
        if hasattr(args, "no_weekends"):
            self.commit_behavior.skip_weekends = args.no_weekends
        if hasattr(args, "no_holidays"):
            self.commit_behavior.skip_holidays = args.no_holidays
        if hasattr(args, "country_holidays") and args.country_holidays:
            self.commit_behavior.holiday_country = args.country_holidays

        # Git settings
        if hasattr(args, "user_name") and args.user_name:
            self.git_settings.user_name = args.user_name
        if hasattr(args, "user_email") and args.user_email:
            self.git_settings.user_email = args.user_email
        if hasattr(args, "repository") and args.repository:
            self.git_settings.repository_url = args.repository
        if hasattr(args, "repo_dir") and args.repo_dir:
            self.git_settings.repo_dir = args.repo_dir

        # Output
        if hasattr(args, "no_progress"):
            self.output.show_progress = not args.no_progress
        if hasattr(args, "verbose"):
            self.output.verbose = args.verbose
        if hasattr(args, "dry_run"):
            self.output.dry_run = args.dry_run


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from file.

    Args:
        config_path: Path to configuration file. If None, looks for config.yaml
                    in current directory.

    Returns:
        Loaded configuration

    Raises:
        ConfigurationError: If configuration is invalid
    """
    if config_path is None:
        # Look for default config file
        default_paths = [
            Path("config.yaml"),
            Path("config.yml"),
            Path(".github-activity.yaml"),
            Path(".github-activity.yml"),
        ]

        for path in default_paths:
            if path.exists():
                config_path = path
                break
        else:
            # No config file found, return defaults
            return Config()

    config_path = Path(config_path)

    if not config_path.exists():
        error_msg = f"Configuration file not found: {config_path}"
        raise ConfigurationError(error_msg)

    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        error_msg = f"Invalid YAML in {config_path}: {e}"
        raise ConfigurationError(error_msg) from e
    except Exception as e:
        error_msg = f"Error reading {config_path}: {e}"
        raise ConfigurationError(error_msg) from e

    if not isinstance(data, dict):
        error_msg = (
            f"Configuration file must contain a YAML dictionary, got {type(data)}"
        )
        raise ConfigurationError(error_msg)

    # Substitute environment variables
    data = _substitute_env_vars(data)

    try:
        return Config.from_dict(data)
    except Exception as e:
        error_msg = f"Invalid configuration: {e}"
        raise ConfigurationError(error_msg) from e


def _substitute_env_vars(data: Any) -> Any:
    """Recursively substitute environment variables in configuration."""
    if isinstance(data, dict):
        return {k: _substitute_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_substitute_env_vars(item) for item in data]
    if isinstance(data, str):
        # Replace ${VAR_NAME} with environment variable value
        def replacer(match):
            var_name = match.group(1)
            value = os.environ.get(var_name)
            if value is None:
                error_msg = f"Environment variable not set: {var_name}"
                raise ConfigurationError(error_msg)
            return value

        return re.sub(r"\$\{([^}]+)\}", replacer, data)
    return data


def save_config(config: Config, path: Union[str, Path]) -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save
        path: Path to save configuration to
    """
    path = Path(path)

    data = {
        "date_range": {
            "start_date": config.date_range.start_date,
            "end_date": config.date_range.end_date,
        },
        "commit_behavior": {
            "max_commits_per_day": config.commit_behavior.max_commits_per_day,
            "frequency_percentage": config.commit_behavior.frequency_percentage,
            "skip_weekends": config.commit_behavior.skip_weekends,
            "skip_holidays": config.commit_behavior.skip_holidays,
            "holiday_country": config.commit_behavior.holiday_country,
        },
        "git_settings": {
            "user_name": config.git_settings.user_name,
            "user_email": config.git_settings.user_email,
            "repository_url": config.git_settings.repository_url,
        },
        "output": {
            "show_progress": config.output.show_progress,
            "verbose": config.output.verbose,
            "dry_run": config.output.dry_run,
        },
    }

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
