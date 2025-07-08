"""Tests for command line argument parsing."""

from datetime import datetime, timedelta
from typing import List

import pytest

from github_activity_generator.cli import create_parser


class TestArgumentParsing:
    """Test argument parsing functionality."""

    def test_default_arguments(self):
        """Test parsing with no arguments uses defaults."""
        parser = create_parser()
        args = parser.parse_args([])
        
        assert args.country_holidays is None
        assert args.no_holidays is False
        assert args.no_weekends is False
        assert args.max_commits is None  # Default handled by Config
        assert args.frequency is None  # Default handled by Config
        assert args.repository is None
        assert args.user_name is None
        assert args.user_email is None
        
        # Default dates are handled by Config class
        assert args.end_date is None
        assert args.start_date is None

    def test_all_arguments_provided(self):
        """Test parsing when all arguments are provided."""
        parser = create_parser()
        sample_args = [
            "--start-date", "2024-01-01",
            "--end-date", "2024-01-07",
            "--max-commits", "5",
            "--frequency", "100",
            "--no-weekends",
            "--no-holidays",
            "--country-holidays", "US"
        ]
        args = parser.parse_args(sample_args)
        
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
        
        parser = create_parser()
        for repo_url, expected in test_cases:
            args = parser.parse_args(["-r", repo_url])
            assert args.repository == expected

    def test_user_config_arguments(self):
        """Test user name and email arguments."""
        parser = create_parser()
        args = parser.parse_args([
            "--user-name", "Test User",
            "--user-email", "test@example.com"
        ])
        
        assert args.user_name == "Test User"
        assert args.user_email == "test@example.com"

    def test_max_commits_boundaries(self):
        """Test max_commits argument boundaries."""
        # Test valid values
        parser = create_parser()
        for value in [1, 5, 10, 15, 20]:
            args = parser.parse_args(["--max-commits", str(value)])
            assert args.max_commits == value

    def test_frequency_boundaries(self):
        """Test frequency argument boundaries."""
        # Test valid values
        parser = create_parser()
        for value in [0, 25, 50, 75, 100]:
            args = parser.parse_args(["--frequency", str(value)])
            assert args.frequency == value

    def test_date_format_arguments(self):
        """Test various date format arguments."""
        test_dates = [
            "2024-01-01",
            "2023-12-31",
            "2024-06-15",
        ]
        
        parser = create_parser()
        for date_str in test_dates:
            args = parser.parse_args(["--start-date", date_str])
            assert args.start_date == date_str
            
            args = parser.parse_args(["--end-date", date_str])
            assert args.end_date == date_str

    def test_country_holidays_argument(self):
        """Test country holidays argument."""
        countries = ["US", "UK", "CA", "AU", "DE", "FR"]
        
        parser = create_parser()
        for country in countries:
            args = parser.parse_args(["--country-holidays", country])
            assert args.country_holidays == country

    def test_boolean_flags(self):
        """Test boolean flag arguments."""
        # Test no_weekends flag
        parser = create_parser()
        args = parser.parse_args(["--no-weekends"])
        assert args.no_weekends is True
        
        args = parser.parse_args([])
        assert args.no_weekends is False
        
        # Test no_holidays flag
        args = parser.parse_args(["--no-holidays"])
        assert args.no_holidays is True
        
        args = parser.parse_args([])
        assert args.no_holidays is False

    def test_short_form_arguments(self):
        """Test short form of arguments."""
        parser = create_parser()
        args = parser.parse_args([
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
        parser = create_parser()
        args = parser.parse_args(["--no-weekends", "--no-holidays"])
        assert args.no_weekends is True
        assert args.no_holidays is True
        
        # Test custom dates with frequency
        args = parser.parse_args([
            "--start-date", "2024-01-01",
            "--end-date", "2024-01-31",
            "--frequency", "50"
        ])
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-01-31"
        assert args.frequency == 50