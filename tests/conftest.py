"""Shared pytest fixtures and configuration for all tests."""

import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator, List, Tuple
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    """Mock subprocess.Popen for git commands."""
    with patch("contribute.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_git_commands() -> Generator[MagicMock, None, None]:
    """Mock all git command executions."""
    with patch("contribute.run") as mock_run:
        yield mock_run


@pytest.fixture
def sample_date_range() -> Tuple[datetime, datetime]:
    """Provide a sample date range for testing."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date


@pytest.fixture
def sample_args() -> List[str]:
    """Provide sample command line arguments."""
    return [
        "--start_date", "2024-01-01",
        "--end_date", "2024-01-07",
        "--max_commits", "5",
        "--frequency", "100",
        "--no_weekends",
        "--no_holidays",
        "--country_holidays", "US"
    ]


@pytest.fixture
def mock_holidays() -> Generator[MagicMock, None, None]:
    """Mock the holidays module."""
    with patch("contribute.holidays") as mock_holidays_module:
        mock_us_holidays = MagicMock()
        mock_us_holidays.__contains__ = lambda self, date: date.day == 1  # Jan 1 is a holiday
        mock_holidays_module.__dict__ = {"US": lambda: mock_us_holidays}
        yield mock_holidays_module


@pytest.fixture(autouse=True)
def change_test_dir(temp_dir: Path, monkeypatch) -> None:
    """Automatically change to temp directory for each test."""
    monkeypatch.chdir(temp_dir)


@pytest.fixture
def git_config() -> Generator[None, None, None]:
    """Set up and tear down git config for tests."""
    # Save current git config
    original_name = os.environ.get("GIT_AUTHOR_NAME")
    original_email = os.environ.get("GIT_AUTHOR_EMAIL")
    
    # Set test git config
    os.environ["GIT_AUTHOR_NAME"] = "Test User"
    os.environ["GIT_AUTHOR_EMAIL"] = "test@example.com"
    os.environ["GIT_COMMITTER_NAME"] = "Test User"
    os.environ["GIT_COMMITTER_EMAIL"] = "test@example.com"
    
    yield
    
    # Restore original config
    if original_name:
        os.environ["GIT_AUTHOR_NAME"] = original_name
    else:
        os.environ.pop("GIT_AUTHOR_NAME", None)
        
    if original_email:
        os.environ["GIT_AUTHOR_EMAIL"] = original_email
    else:
        os.environ.pop("GIT_AUTHOR_EMAIL", None)
        
    os.environ.pop("GIT_COMMITTER_NAME", None)
    os.environ.pop("GIT_COMMITTER_EMAIL", None)


@pytest.fixture
def mock_input() -> Generator[MagicMock, None, None]:
    """Mock user input for interactive prompts."""
    with patch("builtins.input") as mock_input_func:
        mock_input_func.return_value = "y"
        yield mock_input_func