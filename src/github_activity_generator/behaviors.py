"""Commit behavior patterns for GitHub Activity Generator."""

import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict

from .constants import MIN_CONTRIBUTION_DAYS


class CommitBehavior(ABC):
    """Base class for commit behavior patterns."""

    def __init__(self, max_commits: int = 10, frequency: int = 80):
        """Initialize behavior with base parameters.

        Args:
            max_commits: Maximum commits per day
            frequency: Base frequency percentage
        """
        self.max_commits = max_commits
        self.frequency = frequency
        self._vacation_days = set()
        self._sick_days = set()

    @abstractmethod
    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Get number of commits for a specific day.

        Args:
            date: The date to get commits for
            context: Additional context (start_date, end_date, etc.)

        Returns:
            Number of commits to make
        """
        pass

    def _is_weekend(self, date: datetime) -> bool:
        """Check if date is a weekend."""
        return date.weekday() >= MIN_CONTRIBUTION_DAYS

    def _should_skip_by_frequency(self) -> bool:
        """Check if should skip based on frequency."""
        return random.randint(1, 100) > self.frequency


class ConsistentBehavior(CommitBehavior):
    """Original consistent random behavior."""

    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Standard random commits based on frequency."""
        # date and context are required by base class but not used here
        _ = (date, context)
        if self._should_skip_by_frequency():
            return 0
        return random.randint(1, self.max_commits)


class RegularBehavior(CommitBehavior):
    """9-to-5 professional developer pattern."""

    def __init__(self, max_commits: int = 10, frequency: int = 80):
        super().__init__(max_commits, frequency)
        self._setup_time_off()

    def _setup_time_off(self):
        """Setup vacation and sick days for the year."""
        # This will be populated when we have the date range
        pass

    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Get commits for a regular developer."""
        # Initialize time off if not done
        if not self._vacation_days and "start_date" in context:
            self._generate_time_off(context["start_date"], context["end_date"])

        # Check if on vacation
        if date.date() in self._vacation_days:
            return 0

        # Check if sick
        if date.date() in self._sick_days:
            return 0

        # Rare weekend work (5% chance)
        if self._is_weekend(date):
            if random.random() < 0.05:
                return random.randint(1, min(3, self.max_commits))
            return 0

        # Regular workday
        min_commits = min(3, self.max_commits)
        max_commits = min(12, self.max_commits)
        return random.randint(min_commits, max_commits)

    def _generate_time_off(self, start_date: datetime, end_date: datetime):
        """Generate vacation and sick days for the period."""
        total_days = (end_date - start_date).days
        year_fraction = min(total_days / 365, 1.0)

        # 2-3 weeks vacation
        vacation_days = int(random.randint(10, 15) * year_fraction)
        # Generate vacation blocks
        days_allocated = 0
        while days_allocated < vacation_days:
            # Start vacation on random Monday
            vacation_start = start_date + timedelta(
                days=random.randint(0, total_days - 14)
            )
            # Adjust to Monday
            days_to_monday = (7 - vacation_start.weekday()) % 7
            vacation_start += timedelta(days=days_to_monday)

            # Vacation length (5-10 days)
            min_vacation = min(5, vacation_days - days_allocated)
            max_vacation = min(10, vacation_days - days_allocated)
            vacation_length = (
                random.randint(min_vacation, max_vacation)
                if min_vacation <= max_vacation
                else min_vacation
            )

            for i in range(vacation_length):
                vacation_date = vacation_start + timedelta(days=i)
                if start_date <= vacation_date <= end_date:
                    self._vacation_days.add(vacation_date.date())
                    days_allocated += 1

        # 8-10 sick days scattered
        sick_days = int(random.randint(8, 10) * year_fraction)
        for _ in range(sick_days):
            sick_date = start_date + timedelta(days=random.randint(0, total_days))
            # Sick days often come in 1-3 day blocks
            sick_length = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            for i in range(sick_length):
                sick_day = sick_date + timedelta(days=i)
                if start_date <= sick_day <= end_date and not self._is_weekend(
                    sick_day
                ):
                    self._sick_days.add(sick_day.date())


class IntenseBehavior(CommitBehavior):
    """Startup/crunch mode with burst patterns."""

    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Get commits for intense burst pattern."""
        # Calculate cycle position (12-day cycles)
        days_since_start = (date - context.get("start_date", date)).days
        cycle_day = days_since_start % 12

        if cycle_day < 5:  # Crunch time (days 0-4)
            min_crunch = min(15, self.max_commits)
            max_crunch = min(30, self.max_commits)
            if min_crunch == max_crunch:
                base = min_crunch
            else:
                base = random.randint(min_crunch, max_crunch)
            # Even more on some days
            if random.random() < 0.2 and self.max_commits > 30:
                base += random.randint(5, 10)
            return min(base, self.max_commits)

        if cycle_day < 8:  # Recovery (days 5-7)
            return random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]

        # Normal pace (days 8-11)
        if self._is_weekend(date) and random.random() < 0.3:
            return 0
        return random.randint(3, min(10, self.max_commits))


class HobbyistBehavior(CommitBehavior):
    """Side project developer - evenings and weekends."""

    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Get commits for hobbyist pattern."""
        # More active in winter months (Oct-Mar)
        month = date.month
        is_winter = month >= 10 or month <= 3

        # Base activity rate
        if self._is_weekend(date):
            # Weekends are prime time
            if random.random() < (0.7 if is_winter else 0.5):
                min_val = min(5, self.max_commits)
                max_val = min(15, self.max_commits)
                return (
                    random.randint(min_val, max_val) if min_val < max_val else min_val
                )
        # Weekday evenings - less likely
        elif random.random() < (0.3 if is_winter else 0.2):
            return random.randint(1, min(5, self.max_commits))

        return 0


class OpenSourceBehavior(CommitBehavior):
    """Open source contributor pattern."""

    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Get commits for open source contributor."""
        # Check for Hacktoberfest (October)
        if date.month == 10:
            # Much more active
            if random.random() < 0.8:
                min_val = min(3, self.max_commits)
                max_val = min(15, self.max_commits)
                return (
                    random.randint(min_val, max_val) if min_val < max_val else min_val
                )

        # Conference/hackathon simulation (5% chance of burst)
        if random.random() < 0.05:
            min_val = min(15, self.max_commits)
            max_val = min(25, self.max_commits)
            return random.randint(min_val, max_val) if min_val < max_val else min_val

        # Regular contribution pattern - steady but not daily
        if random.random() < 0.5:  # 50% of days active
            min_val = min(2, self.max_commits)
            max_val = min(8, self.max_commits)
            return random.randint(min_val, max_val) if min_val < max_val else min_val

        return 0


class IrregularBehavior(CommitBehavior):
    """Contractor/freelancer with project-based work."""

    def __init__(self, max_commits: int = 10, frequency: int = 80):
        super().__init__(max_commits, frequency)
        self._project_periods = []

    def get_commits_for_day(self, date: datetime, context: Dict) -> int:
        """Get commits for irregular pattern."""
        # Initialize project periods if not done
        if not self._project_periods and "start_date" in context:
            self._generate_project_periods(context["start_date"], context["end_date"])

        # Check if in a project period
        for start, end in self._project_periods:
            if start <= date.date() <= end:
                # Active project - lots of commits
                min_val = min(8, self.max_commits)
                max_val = min(25, self.max_commits)
                return (
                    random.randint(min_val, max_val) if min_val < max_val else min_val
                )

        # Between projects
        return 0

    def _generate_project_periods(self, start_date: datetime, end_date: datetime):
        """Generate project periods."""
        current = start_date
        total_days = (end_date - start_date).days

        while current < end_date:
            # Gap between projects (1-3 weeks)
            gap_days = random.randint(7, 21)
            current += timedelta(days=gap_days)

            if current >= end_date:
                break

            # Project duration (2-8 weeks)
            project_days = random.randint(14, 56)
            project_end = current + timedelta(days=project_days)

            project_end = min(project_end, end_date)

            self._project_periods.append((current.date(), project_end.date()))
            current = project_end


def get_behavior(
    behavior_type: str, max_commits: int = 10, frequency: int = 80
) -> CommitBehavior:
    """Factory function to get behavior instance.

    Args:
        behavior_type: Type of behavior
        max_commits: Maximum commits per day
        frequency: Base frequency percentage

    Returns:
        CommitBehavior instance
    """
    behaviors = {
        "consistent": ConsistentBehavior,
        "regular": RegularBehavior,
        "intense": IntenseBehavior,
        "hobbyist": HobbyistBehavior,
        "opensource": OpenSourceBehavior,
        "irregular": IrregularBehavior,
    }

    behavior_class = behaviors.get(behavior_type, ConsistentBehavior)
    return behavior_class(max_commits, frequency)
