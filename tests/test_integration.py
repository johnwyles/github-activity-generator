"""Integration tests for the GitHub Activity Generator."""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from github_activity_generator.cli import main
from github_activity_generator.config_loader import Config
from github_activity_generator.constants import (
    DAYS_IN_WEEK,
    DEFAULT_FREQUENCY,
    DEFAULT_MAX_COMMITS,
)


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_dir)

        # Windows-specific handling for .git directories
        if platform.system() == "Windows":
            # Try Windows rmdir to force remove git directories
            # S602, S607: Using shell=True is needed for Windows rmdir command
            # S110: Ignoring errors is intentional for test cleanup
            try:
                subprocess.run(
                    ["rmdir", "/s", "/q", temp_dir],
                    shell=True,
                    check=False,
                )
            except Exception:
                pass  # Ignore cleanup errors on Windows
        else:
            shutil.rmtree(temp_dir)

    def test_dry_run_execution(self, temp_dir):
        """Test dry run execution."""
        # Run with dry-run flag
        exit_code = main(
            [
                "--dry-run",
                "--start-date",
                "2_days_ago",
                "--end-date",
                "today",
                "--max-commits",
                "3",
                "--frequency",
                "100",
            ]
        )

        assert exit_code == 0
        # In dry run, no repository should be created
        repos = list(Path(temp_dir).glob("repository-*"))
        assert len(repos) == 1  # Directory created but no commits

    def test_actual_generation(self, temp_dir):
        """Test actual commit generation."""
        # Run actual generation with git config
        exit_code = main(
            [
                "--start-date",
                "1_days_ago",
                "--end-date",
                "today",
                "--max-commits",
                "2",
                "--frequency",
                "100",
                "--no-progress",
                "--user-name",
                "Test User",
                "--user-email",
                "test@example.com",
            ]
        )

        assert exit_code == 0

        # Check repository was created
        repos = list(Path(temp_dir).glob("repository-*"))
        assert len(repos) == 1

        # Check git repository exists
        repo_dir = repos[0]
        assert (repo_dir / ".git").exists()
        assert (repo_dir / "README.md").exists()

    def test_config_loading(self):
        """Test configuration loading and defaults."""
        config = Config()

        # Test defaults
        assert config.commit_behavior.max_commits_per_day == DEFAULT_MAX_COMMITS
        assert config.commit_behavior.frequency_percentage == DEFAULT_FREQUENCY
        assert config.commit_behavior.skip_weekends is False
        assert config.commit_behavior.skip_holidays is False
        assert config.commit_behavior.holiday_country == "US"

    def test_date_range_parsing(self):
        """Test date range parsing."""
        config = Config()

        # Test special values
        config.date_range.start_date = "7_days_ago"
        config.date_range.end_date = "today"

        start, end = config.date_range.resolve_dates()
        assert start < end
        assert (end - start).days == DAYS_IN_WEEK

    def test_no_arguments_shows_help(self, capsys, monkeypatch, temp_dir):
        """Test that running without arguments shows help."""
        # Mock sys.argv to simulate no arguments
        monkeypatch.setattr(sys, "argv", ["generate.py"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "GitHub Activity Generator" in captured.out
        assert "USAGE:" in captured.out
        assert "COMMON EXAMPLES:" in captured.out
