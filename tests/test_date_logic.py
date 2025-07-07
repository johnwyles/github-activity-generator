"""Tests for date logic including weekends and holidays."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

import contribute


class TestDateLogic:
    """Test date-related functionality."""

    def test_not_weekend_logic(self):
        """Test weekend detection logic."""
        # Create args with no_weekends = True
        args = contribute.arguments(["--no_weekends"])
        
        # Test weekdays (should return True)
        weekday_dates = [
            datetime(2024, 1, 1),   # Monday
            datetime(2024, 1, 2),   # Tuesday
            datetime(2024, 1, 3),   # Wednesday
            datetime(2024, 1, 4),   # Thursday
            datetime(2024, 1, 5),   # Friday
        ]
        
        for date in weekday_dates:
            assert contribute.not_weekend(args, date) is True
        
        # Test weekends (should return False when no_weekends is True)
        weekend_dates = [
            datetime(2024, 1, 6),   # Saturday
            datetime(2024, 1, 7),   # Sunday
        ]
        
        for date in weekend_dates:
            assert contribute.not_weekend(args, date) is False

    def test_not_weekend_disabled(self):
        """Test weekend logic when no_weekends is False."""
        args = contribute.arguments([])  # no_weekends defaults to False
        
        # All days should return True when no_weekends is False
        all_dates = [
            datetime(2024, 1, 1),   # Monday
            datetime(2024, 1, 2),   # Tuesday
            datetime(2024, 1, 3),   # Wednesday
            datetime(2024, 1, 4),   # Thursday
            datetime(2024, 1, 5),   # Friday
            datetime(2024, 1, 6),   # Saturday
            datetime(2024, 1, 7),   # Sunday
        ]
        
        for date in all_dates:
            assert contribute.not_weekend(args, date) is True

    def test_not_holiday_logic(self, mock_holidays):
        """Test holiday detection logic."""
        args = contribute.arguments(["--no_holidays"])
        
        # January 1st is mocked as a holiday
        new_years = datetime(2024, 1, 1)
        assert contribute.not_holiday(args, new_years, "US") is False
        
        # Other dates should not be holidays
        regular_day = datetime(2024, 1, 2)
        assert contribute.not_holiday(args, regular_day, "US") is True

    def test_not_holiday_disabled(self, mock_holidays):
        """Test holiday logic when no_holidays is False."""
        args = contribute.arguments([])  # no_holidays defaults to False
        
        # All days should return True when no_holidays is False
        new_years = datetime(2024, 1, 1)
        regular_day = datetime(2024, 1, 2)
        
        assert contribute.not_holiday(args, new_years, "US") is True
        assert contribute.not_holiday(args, regular_day, "US") is True

    def test_different_country_holidays(self):
        """Test holiday detection for different countries."""
        with patch("contribute.holidays") as mock_holidays_module:
            # Mock different holiday calendars
            mock_us_holidays = MagicMock()
            mock_uk_holidays = MagicMock()
            mock_ca_holidays = MagicMock()
            
            # US has Jan 1 as holiday
            mock_us_holidays.__contains__ = lambda self, date: date.day == 1 and date.month == 1
            # UK has Jan 2 as holiday
            mock_uk_holidays.__contains__ = lambda self, date: date.day == 2 and date.month == 1
            # Canada has both Jan 1 and Jan 2
            mock_ca_holidays.__contains__ = lambda self, date: date.day in [1, 2] and date.month == 1
            
            mock_holidays_module.__dict__ = {
                "US": lambda: mock_us_holidays,
                "UK": lambda: mock_uk_holidays,
                "CA": lambda: mock_ca_holidays,
            }
            
            args = contribute.arguments(["--no_holidays"])
            
            jan_1 = datetime(2024, 1, 1)
            jan_2 = datetime(2024, 1, 2)
            
            # Test US holidays
            assert contribute.not_holiday(args, jan_1, "US") is False
            assert contribute.not_holiday(args, jan_2, "US") is True
            
            # Test UK holidays
            assert contribute.not_holiday(args, jan_1, "UK") is True
            assert contribute.not_holiday(args, jan_2, "UK") is False
            
            # Test Canadian holidays
            assert contribute.not_holiday(args, jan_1, "CA") is False
            assert contribute.not_holiday(args, jan_2, "CA") is False

    def test_date_range_iteration(self):
        """Test iteration through date ranges."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 7)
        
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)
        
        assert len(dates) == 7
        assert dates[0] == start_date
        assert dates[-1] == end_date

    def test_leap_year_handling(self):
        """Test handling of leap years."""
        # 2024 is a leap year
        feb_28_2024 = datetime(2024, 2, 28)
        feb_29_2024 = datetime(2024, 2, 29)
        mar_1_2024 = datetime(2024, 3, 1)
        
        # Test that Feb 29 exists in leap year
        assert (mar_1_2024 - feb_28_2024).days == 2
        
        # Test weekend detection on leap day
        args = contribute.arguments(["--no_weekends"])
        # Feb 29, 2024 is a Thursday
        assert contribute.not_weekend(args, feb_29_2024) is True

    def test_year_boundary_dates(self):
        """Test dates around year boundaries."""
        args = contribute.arguments(["--no_weekends", "--no_holidays"])
        
        # Test end of year
        dec_31_2023 = datetime(2023, 12, 31)  # Sunday
        jan_1_2024 = datetime(2024, 1, 1)     # Monday
        
        # Dec 31, 2023 is Sunday (weekend)
        assert contribute.not_weekend(args, dec_31_2023) is False
        # Jan 1, 2024 is Monday (weekday)
        assert contribute.not_weekend(args, jan_1_2024) is True

    def test_contributions_per_day(self):
        """Test random contributions per day generation."""
        test_cases = [
            (1, 1, 1),      # min=max=1
            (5, 1, 5),      # typical case
            (10, 1, 10),    # default max
            (20, 1, 20),    # maximum allowed
            (25, 1, 20),    # over maximum (should cap at 20)
            (0, 1, 1),      # below minimum (should be at least 1)
        ]
        
        for max_commits, expected_min, expected_max in test_cases:
            args = contribute.arguments(["--max_commits", str(max_commits)])
            
            # Test multiple times to ensure randomness stays within bounds
            for _ in range(100):
                commits = contribute.contributions_per_day(args)
                assert expected_min <= commits <= expected_max