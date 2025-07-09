"""Tests for commit behavior patterns."""

from datetime import datetime, timedelta

from github_activity_generator.behaviors import (
    ConsistentBehavior,
    HobbyistBehavior,
    IntenseBehavior,
    IrregularBehavior,
    OpenSourceBehavior,
    RegularBehavior,
    get_behavior,
)


class TestBehaviorFactory:
    """Test behavior factory function."""

    def test_get_behavior_consistent(self):
        """Test getting consistent behavior."""
        behavior = get_behavior("consistent", max_commits=10, frequency=80)
        assert isinstance(behavior, ConsistentBehavior)
        assert behavior.max_commits == 10
        assert behavior.frequency == 80

    def test_get_behavior_regular(self):
        """Test getting regular behavior."""
        behavior = get_behavior("regular")
        assert isinstance(behavior, RegularBehavior)

    def test_get_behavior_intense(self):
        """Test getting intense behavior."""
        behavior = get_behavior("intense")
        assert isinstance(behavior, IntenseBehavior)

    def test_get_behavior_hobbyist(self):
        """Test getting hobbyist behavior."""
        behavior = get_behavior("hobbyist")
        assert isinstance(behavior, HobbyistBehavior)

    def test_get_behavior_opensource(self):
        """Test getting opensource behavior."""
        behavior = get_behavior("opensource")
        assert isinstance(behavior, OpenSourceBehavior)

    def test_get_behavior_irregular(self):
        """Test getting irregular behavior."""
        behavior = get_behavior("irregular")
        assert isinstance(behavior, IrregularBehavior)

    def test_get_behavior_invalid_defaults_to_consistent(self):
        """Test invalid behavior defaults to consistent."""
        behavior = get_behavior("invalid")
        assert isinstance(behavior, ConsistentBehavior)


class TestConsistentBehavior:
    """Test consistent behavior pattern."""

    def test_consistent_respects_frequency(self):
        """Test that consistent behavior respects frequency."""
        behavior = ConsistentBehavior(max_commits=5, frequency=100)
        date = datetime(2024, 1, 1)
        context = {}

        # With 100% frequency, should always get commits
        commits = behavior.get_commits_for_day(date, context)
        assert 1 <= commits <= 5

    def test_consistent_zero_frequency(self):
        """Test consistent behavior with 0% frequency."""
        behavior = ConsistentBehavior(max_commits=5, frequency=0)
        date = datetime(2024, 1, 1)
        context = {}

        # With 0% frequency, should always get 0
        commits = behavior.get_commits_for_day(date, context)
        assert commits == 0


class TestRegularBehavior:
    """Test regular (9-to-5) behavior pattern."""

    def test_regular_weekday_commits(self):
        """Test regular behavior on weekdays."""
        behavior = RegularBehavior(max_commits=15)
        # Monday
        date = datetime(2024, 1, 8)
        context = {
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 12, 31),
        }

        # Should get commits on weekday
        commits = behavior.get_commits_for_day(date, context)
        assert 3 <= commits <= 12

    def test_regular_weekend_mostly_zero(self):
        """Test regular behavior rarely commits on weekends."""
        behavior = RegularBehavior()
        # Saturday
        date = datetime(2024, 1, 6)
        context = {
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 12, 31),
        }

        # Count weekend commits over many samples
        weekend_commits = 0
        for _ in range(100):
            commits = behavior.get_commits_for_day(date, context)
            if commits > 0:
                weekend_commits += 1

        # Should be rare (around 5%)
        assert weekend_commits < 15


class TestIntenseBehavior:
    """Test intense (startup) behavior pattern."""

    def test_intense_burst_pattern(self):
        """Test intense behavior has burst patterns."""
        behavior = IntenseBehavior(max_commits=40)
        start = datetime(2024, 1, 1)
        context = {"start_date": start, "end_date": datetime(2024, 1, 31)}

        # Check first 12 days for pattern
        commits_per_day = []
        for i in range(12):
            date = start + timedelta(days=i)
            commits = behavior.get_commits_for_day(date, context)
            commits_per_day.append(commits)

        # Should have high activity in first 5 days
        assert max(commits_per_day[:5]) >= 15
        # Should have low activity in days 5-7
        assert min(commits_per_day[5:8]) <= 3


class TestHobbyistBehavior:
    """Test hobbyist behavior pattern."""

    def test_hobbyist_prefers_weekends(self):
        """Test hobbyist is more active on weekends."""
        behavior = HobbyistBehavior()
        context = {}

        # Test weekend (Saturday)
        weekend = datetime(2024, 1, 6)
        # Test weekday (Monday)
        weekday = datetime(2024, 1, 8)

        # Count commits over many samples
        weekend_activity = 0
        weekday_activity = 0

        for _ in range(100):
            if behavior.get_commits_for_day(weekend, context) > 0:
                weekend_activity += 1
            if behavior.get_commits_for_day(weekday, context) > 0:
                weekday_activity += 1

        # Weekends should be more active
        assert weekend_activity > weekday_activity

    def test_hobbyist_winter_more_active(self):
        """Test hobbyist is more active in winter."""
        behavior = HobbyistBehavior()
        context = {}

        # Winter date (January)
        winter = datetime(2024, 1, 6)  # Saturday
        # Summer date (July)
        summer = datetime(2024, 7, 6)  # Saturday

        # Count activity
        winter_activity = 0
        summer_activity = 0

        for _ in range(100):
            if behavior.get_commits_for_day(winter, context) > 0:
                winter_activity += 1
            if behavior.get_commits_for_day(summer, context) > 0:
                summer_activity += 1

        # Winter should be more active
        assert winter_activity > summer_activity


class TestOpenSourceBehavior:
    """Test open source contributor behavior."""

    def test_opensource_hacktoberfest(self):
        """Test increased activity during Hacktoberfest."""
        behavior = OpenSourceBehavior()
        context = {}

        # October date
        october = datetime(2024, 10, 15)
        # Non-October date
        january = datetime(2024, 1, 15)

        # Count activity
        october_activity = 0
        january_activity = 0

        for _ in range(100):
            if behavior.get_commits_for_day(october, context) > 0:
                october_activity += 1
            if behavior.get_commits_for_day(january, context) > 0:
                january_activity += 1

        # October should be more active (at least 20% more)
        assert october_activity > january_activity * 1.2


class TestIrregularBehavior:
    """Test irregular (contractor) behavior."""

    def test_irregular_has_project_periods(self):
        """Test irregular behavior has distinct project periods."""
        behavior = IrregularBehavior()
        start = datetime(2024, 1, 1)
        end = datetime(2024, 3, 31)
        context = {"start_date": start, "end_date": end}

        # Generate activity for 3 months
        active_days = 0
        inactive_days = 0

        current = start
        while current <= end:
            commits = behavior.get_commits_for_day(current, context)
            if commits > 0:
                active_days += 1
            else:
                inactive_days += 1
            current += timedelta(days=1)

        # Should have both active and inactive periods
        assert active_days > 0
        assert inactive_days > 0
        # Should have significant inactive time (at least 15% of total)
        total_days = active_days + inactive_days
        assert inactive_days >= total_days * 0.15
