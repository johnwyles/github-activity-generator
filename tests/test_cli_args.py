"""Tests for command line argument parsing."""

from datetime import datetime, timedelta
from typing import List

import pytest

import contribute


class TestArgumentParsing:
    """Test argument parsing functionality."""

    def test_default_arguments(self):
        """Test parsing with no arguments uses defaults."""
        args = contribute.arguments([])
        
        assert args.country_holidays == "US"
        assert args.no_holidays is False
        assert args.no_weekends is False
        assert args.max_commits == 10
        assert args.frequency == 80
        assert args.repository is None
        assert args.user_name is None
        assert args.user_email is None
        
        # Check default dates
        expected_end_date = datetime.now().strftime("%Y-%m-%d")
        expected_start_date = (datetime.now() - timedelta(365)).strftime("%Y-%m-%d")
        assert args.end_date == expected_end_date
        assert args.start_date == expected_start_date

    def test_all_arguments_provided(self, sample_args: List[str]):
        """Test parsing when all arguments are provided."""
        args = contribute.arguments(sample_args)
        
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-01-07"
        assert args.max_commits == 5
        assert args.frequency == 100
        assert args.no_weekends is True
        assert args.no_holidays is True
        assert args.country_holidays == "US"

    def test_repository_argument(self):
        """Test repository URL parsing."""
        test_cases = [
            ("git@github.com:user/repo.git", "git@github.com:user/repo.git"),
            ("https://github.com/user/repo.git", "https://github.com/user/repo.git"),
            ("https://gitlab.com/user/repo.git", "https://gitlab.com/user/repo.git"),
        ]
        
        for repo_url, expected in test_cases:
            args = contribute.arguments(["-r", repo_url])
            assert args.repository == expected

    def test_user_config_arguments(self):
        """Test user name and email arguments."""
        args = contribute.arguments([
            "--user_name", "Test User",
            "--user_email", "test@example.com"
        ])
        
        assert args.user_name == "Test User"
        assert args.user_email == "test@example.com"

    def test_max_commits_boundaries(self):
        """Test max_commits argument boundaries."""
        # Test valid values
        for value in [1, 5, 10, 15, 20]:
            args = contribute.arguments(["--max_commits", str(value)])
            assert args.max_commits == value

    def test_frequency_boundaries(self):
        """Test frequency argument boundaries."""
        # Test valid values
        for value in [0, 25, 50, 75, 100]:
            args = contribute.arguments(["--frequency", str(value)])
            assert args.frequency == value

    def test_date_format_arguments(self):
        """Test various date format arguments."""
        test_dates = [
            "2024-01-01",
            "2023-12-31",
            "2024-06-15",
        ]
        
        for date_str in test_dates:
            args = contribute.arguments(["--start_date", date_str])
            assert args.start_date == date_str
            
            args = contribute.arguments(["--end_date", date_str])
            assert args.end_date == date_str

    def test_country_holidays_argument(self):
        """Test country holidays argument."""
        countries = ["US", "UK", "CA", "AU", "DE", "FR"]
        
        for country in countries:
            args = contribute.arguments(["--country_holidays", country])
            assert args.country_holidays == country

    def test_boolean_flags(self):
        """Test boolean flag arguments."""
        # Test no_weekends flag
        args = contribute.arguments(["--no_weekends"])
        assert args.no_weekends is True
        
        args = contribute.arguments([])
        assert args.no_weekends is False
        
        # Test no_holidays flag
        args = contribute.arguments(["--no_holidays"])
        assert args.no_holidays is True
        
        args = contribute.arguments([])
        assert args.no_holidays is False

    def test_short_form_arguments(self):
        """Test short form of arguments."""
        args = contribute.arguments([
            "-ch", "UK",
            "-nh",
            "-nw",
            "-mc", "15",
            "-fr", "90",
            "-r", "git@github.com:test/repo.git",
            "-un", "Short User",
            "-ue", "short@example.com",
            "-sd", "2024-01-01",
            "-ed", "2024-01-31"
        ])
        
        assert args.country_holidays == "UK"
        assert args.no_holidays is True
        assert args.no_weekends is True
        assert args.max_commits == 15
        assert args.frequency == 90
        assert args.repository == "git@github.com:test/repo.git"
        assert args.user_name == "Short User"
        assert args.user_email == "short@example.com"
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-01-31"

    def test_combined_arguments(self):
        """Test various combinations of arguments."""
        # Test weekend + holidays
        args = contribute.arguments(["--no_weekends", "--no_holidays"])
        assert args.no_weekends is True
        assert args.no_holidays is True
        
        # Test custom dates with frequency
        args = contribute.arguments([
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-31",
            "--frequency", "50"
        ])
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-01-31"
        assert args.frequency == 50