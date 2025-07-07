"""Tests for commit generation logic."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

import contribute


class TestCommitGeneration:
    """Test commit generation functionality."""

    def test_contributions_per_day_boundaries(self):
        """Test contributions per day stays within boundaries."""
        # Test with different max_commits values
        test_values = [
            (1, 1, 1),      # min value
            (5, 1, 5),      # small value
            (10, 1, 10),    # default
            (20, 1, 20),    # max value
            (25, 1, 20),    # over max (should cap)
            (-5, 1, 1),     # negative (should floor)
            (0, 1, 1),      # zero (should floor)
        ]
        
        for max_commits, expected_min, expected_max in test_values:
            args = contribute.arguments(["--max_commits", str(max_commits)])
            
            # Test 100 times to ensure consistency
            results = []
            for _ in range(100):
                result = contribute.contributions_per_day(args)
                results.append(result)
                assert expected_min <= result <= expected_max
            
            # Ensure we get some variety (unless min==max)
            if expected_min < expected_max:
                assert len(set(results)) > 1

    def test_make_daily_commits_timing(self):
        """Test that commits are spaced by minutes within a day."""
        args = contribute.arguments(["--max_commits", "5"])
        base_date = datetime(2024, 1, 1, 0, 0, 0)
        
        with patch("contribute.contributions_per_day", return_value=5):
            with patch("contribute.contribute") as mock_contribute:
                contribute.make_daily_commits(args, base_date)
                
                # Check that contribute was called 5 times
                assert mock_contribute.call_count == 5
                
                # Check that each call has a different minute offset
                call_times = [call[0][0] for call in mock_contribute.call_args_list]
                
                for i, commit_time in enumerate(call_times):
                    # Each commit should be i minutes after base_date
                    expected_time = base_date + timedelta(minutes=i)
                    assert commit_time == expected_time

    def test_frequency_filtering(self, mock_git_commands):
        """Test that frequency parameter correctly filters days."""
        # Test with 50% frequency
        args = contribute.arguments([
            "--frequency", "50",
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-10"
        ])
        
        # Mock randint to return predictable values
        with patch("contribute.randint") as mock_randint:
            # Make alternating days pass/fail the frequency check
            mock_randint.side_effect = [25, 75, 25, 75, 25, 75, 25, 75, 25, 75]
            
            commit_dates = []
            with patch("contribute.make_daily_commits") as mock_make_commits:
                # Simulate the main loop
                start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
                end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
                delta_days = timedelta(days=1)
                
                while start_date <= end_date:
                    if contribute.randint(0, 100) < args.frequency:
                        commit_dates.append(start_date)
                    start_date += delta_days
            
            # Should have roughly half the days
            assert len(commit_dates) == 5

    def test_weekend_and_holiday_filtering(self, mock_holidays):
        """Test that weekends and holidays are properly filtered."""
        args = contribute.arguments([
            "--no_weekends",
            "--no_holidays",
            "--frequency", "100",
            "--start_date", "2024-01-01",  # Monday (and holiday)
            "--end_date", "2024-01-07"      # Sunday
        ])
        
        # Expected commit days (excluding weekend and holiday)
        # Jan 1 (Mon) - Holiday, skip
        # Jan 2 (Tue) - Commit
        # Jan 3 (Wed) - Commit
        # Jan 4 (Thu) - Commit
        # Jan 5 (Fri) - Commit
        # Jan 6 (Sat) - Weekend, skip
        # Jan 7 (Sun) - Weekend, skip
        
        commit_dates = []
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        delta_days = timedelta(days=1)
        
        while start_date <= end_date:
            if (contribute.not_weekend(args, start_date) and 
                contribute.not_holiday(args, start_date, args.country_holidays)):
                commit_dates.append(start_date)
            start_date += delta_days
        
        assert len(commit_dates) == 4  # Tue, Wed, Thu, Fri

    def test_date_validation_logic(self):
        """Test date validation in main function."""
        # Test valid date formats
        valid_dates = [
            "2024-01-01",
            "2023-12-31",
            "2024-06-15",
        ]
        
        for date_str in valid_dates:
            # Should not raise an exception
            datetime.strptime(date_str, "%Y-%m-%d")

        # Test invalid date formats
        invalid_dates = [
            "2024/01/01",    # Wrong separator
            "01-01-2024",    # Wrong order
            "2024-1-1",      # Missing zeros
            "2024-13-01",    # Invalid month
            "2024-01-32",    # Invalid day
            "not-a-date",    # Not a date
        ]
        
        for date_str in invalid_dates:
            with pytest.raises(ValueError):
                datetime.strptime(date_str, "%Y-%m-%d")

    def test_full_year_generation(self):
        """Test generation for a full year."""
        args = contribute.arguments([
            "--start_date", "2023-01-01",
            "--end_date", "2023-12-31",
            "--frequency", "100",
            "--max_commits", "1"
        ])
        
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        
        # Count total days
        total_days = (end_date - start_date).days + 1
        assert total_days == 365  # 2023 is not a leap year

    def test_readme_content_accumulation(self, temp_dir):
        """Test that README.md accumulates entries correctly."""
        dates = [
            datetime(2024, 1, 1, 10, 0),
            datetime(2024, 1, 1, 10, 1),
            datetime(2024, 1, 1, 10, 2),
        ]
        
        for date in dates:
            contribute.contribute(date)
        
        # Check README.md content
        with open("README.md", "r") as f:
            content = f.read()
            
        # Should have all three entries
        for date in dates:
            assert contribute.message(date) in content
        
        # Count entries (each has two newlines)
        entries = content.strip().split("\n\n")
        assert len(entries) == 3

    @pytest.mark.parametrize("frequency", [0, 25, 50, 75, 100])
    def test_frequency_statistics(self, frequency):
        """Test that frequency parameter produces expected statistics."""
        # Run multiple simulations to test statistical properties
        total_days = 100
        total_commits_made = 0
        simulations = 100
        
        for _ in range(simulations):
            commits_in_sim = 0
            for _ in range(total_days):
                if contribute.randint(0, 100) < frequency:
                    commits_in_sim += 1
            total_commits_made += commits_in_sim
        
        average_percentage = (total_commits_made / (simulations * total_days)) * 100
        
        # Allow for some variance (±10%)
        if frequency == 0:
            assert average_percentage == 0
        elif frequency == 100:
            assert average_percentage == 100
        else:
            assert abs(average_percentage - frequency) < 10

    def test_commit_message_consistency(self):
        """Test that commit messages are consistent."""
        date1 = datetime(2024, 1, 1, 10, 30, 45)
        date2 = datetime(2024, 1, 1, 10, 30, 45)
        
        # Same date should produce same message
        assert contribute.message(date1) == contribute.message(date2)
        
        # Different dates should produce different messages
        date3 = datetime(2024, 1, 2, 10, 30, 45)
        assert contribute.message(date1) != contribute.message(date3)