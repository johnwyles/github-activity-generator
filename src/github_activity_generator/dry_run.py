"""Dry-run mode implementation for GitHub Activity Generator."""

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .constants import MIN_DISPLAY_ITEMS
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class DryRunCommit:
    """Represents a commit in dry-run mode."""

    date: datetime
    message: str
    day_of_week: str
    is_weekend: bool
    is_holiday: bool


@dataclass
class DryRunReport:
    """Report generated from dry-run execution."""

    start_date: datetime
    end_date: datetime
    total_days: int
    commit_days: int
    skipped_days: int
    total_commits: int
    commits_by_day: Dict[datetime, List[DryRunCommit]]
    skipped_weekends: int
    skipped_holidays: int
    skipped_frequency: int

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics from the report."""
        return {
            "Total Days": self.total_days,
            "Days with Commits": self.commit_days,
            "Skipped Days": self.skipped_days,
            "Total Commits": self.total_commits,
            "Skipped Weekends": self.skipped_weekends,
            "Skipped Holidays": self.skipped_holidays,
            "Skipped by Frequency": self.skipped_frequency,
            "Average Commits per Active Day": (
                self.total_commits // self.commit_days if self.commit_days > 0 else 0
            ),
        }

    def get_commits_by_weekday(self) -> Dict[str, int]:
        """Get commit count by day of week."""
        weekday_commits = defaultdict(int)
        for commits in self.commits_by_day.values():
            if commits:
                weekday_commits[commits[0].day_of_week] += len(commits)
        return dict(weekday_commits)


class DryRunSimulator:
    """Simulates commit generation without making actual commits."""

    def __init__(self, verbose: bool = False):
        """Initialize dry-run simulator.

        Args:
            verbose: Whether to show verbose output
        """
        self.verbose = verbose
        self.console = Console()
        self.commits: List[DryRunCommit] = []
        self.skipped_weekends = 0
        self.skipped_holidays = 0
        self.skipped_frequency = 0

    def simulate_commit(
        self,
        date: datetime,
        message: str,
        is_weekend: bool = False,
        is_holiday: bool = False,
    ) -> None:
        """Simulate creating a commit.

        Args:
            date: Commit date
            message: Commit message
            is_weekend: Whether date is a weekend
            is_holiday: Whether date is a holiday
        """
        commit = DryRunCommit(
            date=date,
            message=message,
            day_of_week=date.strftime("%A"),
            is_weekend=is_weekend,
            is_holiday=is_holiday,
        )
        self.commits.append(commit)

        if self.verbose:
            self.console.print(
                f"[green]WOULD CREATE:[/green] Commit on "
                f"{date.strftime('%Y-%m-%d %H:%M')} - {message}"
            )

    def skip_date(self, date: datetime, reason: str) -> None:
        """Record that a date was skipped.

        Args:
            date: Date that was skipped
            reason: Reason for skipping
        """
        if "weekend" in reason.lower():
            self.skipped_weekends += 1
        elif "holiday" in reason.lower():
            self.skipped_holidays += 1
        elif "frequency" in reason.lower():
            self.skipped_frequency += 1

        if self.verbose:
            self.console.print(
                f"[yellow]WOULD SKIP:[/yellow] {date.strftime('%Y-%m-%d')} - {reason}"
            )

    def generate_report(self, start_date: datetime, end_date: datetime) -> DryRunReport:
        """Generate report from simulation.

        Args:
            start_date: Start date of simulation
            end_date: End date of simulation

        Returns:
            Dry-run report
        """
        # Group commits by day
        commits_by_day: Dict[datetime, List[DryRunCommit]] = defaultdict(list)
        for commit in self.commits:
            day = commit.date.replace(hour=0, minute=0, second=0, microsecond=0)
            commits_by_day[day].append(commit)

        total_days = (end_date - start_date).days + 1
        commit_days = len(commits_by_day)
        skipped_days = total_days - commit_days

        return DryRunReport(
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            commit_days=commit_days,
            skipped_days=skipped_days,
            total_commits=len(self.commits),
            commits_by_day=dict(commits_by_day),
            skipped_weekends=self.skipped_weekends,
            skipped_holidays=self.skipped_holidays,
            skipped_frequency=self.skipped_frequency,
        )


def display_dry_run_report(
    report: DryRunReport, console: Optional[Console] = None
) -> None:
    """Display dry-run report in a formatted way.

    Args:
        report: Report to display
        console: Rich console to use (creates new if None)
    """
    if console is None:
        console = Console()

    # Header
    console.print("\n[bold cyan]🔍 DRY RUN REPORT[/bold cyan]\n")

    # Date range
    date_text = Text()
    date_text.append("Date Range: ", style="bold")
    date_text.append(
        f"{report.start_date.strftime('%Y-%m-%d')} to "
        f"{report.end_date.strftime('%Y-%m-%d')}"
    )
    console.print(Panel(date_text, title="Simulation Period", border_style="cyan"))

    # Statistics table
    stats_table = Table(
        title="Statistics", show_header=True, header_style="bold magenta"
    )
    stats_table.add_column("Metric", style="cyan", no_wrap=True)
    stats_table.add_column("Value", justify="right")

    for metric, value in report.get_statistics().items():
        stats_table.add_row(metric, str(value))

    console.print(stats_table)
    console.print()

    # Commits by weekday
    weekday_table = Table(
        title="Commits by Day of Week", show_header=True, header_style="bold magenta"
    )
    weekday_table.add_column("Day", style="cyan")
    weekday_table.add_column("Commits", justify="right")

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday_commits = report.get_commits_by_weekday()

    for day in weekday_order:
        count = weekday_commits.get(day, 0)
        weekday_table.add_row(day, str(count))

    console.print(weekday_table)
    console.print()

    # Sample commits
    if report.commits_by_day:
        console.print("[bold]Sample Commits (first 5 days with activity):[/bold]")

        sample_days = sorted(report.commits_by_day.keys())[:5]
        for day in sample_days:
            commits = report.commits_by_day[day]
            console.print(f"\n  [cyan]{day.strftime('%Y-%m-%d %A')}[/cyan]")
            # Show max 3 commits per day
            for i, commit in enumerate(commits[:MIN_DISPLAY_ITEMS]):
                console.print(
                    f"    {i+1}. {commit.date.strftime('%H:%M')} - {commit.message}"
                )
            if len(commits) > MIN_DISPLAY_ITEMS:
                remaining = len(commits) - MIN_DISPLAY_ITEMS
                console.print(f"    ... and {remaining} more commits")

    # Summary
    console.print("\n[bold green]✅ Dry run complete![/bold green]")
    console.print(
        f"Would create [bold]{report.total_commits}[/bold] commits "
        f"across [bold]{report.commit_days}[/bold] days."
    )


def save_dry_run_report(
    report: DryRunReport, filepath: str, output_format: str = "text"
) -> None:
    """Save dry-run report to file.

    Args:
        report: Report to save
        filepath: Path to save report to
        output_format: Format to save in ("text", "json", "csv")
    """
    if output_format == "json":
        data = {
            "start_date": report.start_date.isoformat(),
            "end_date": report.end_date.isoformat(),
            "statistics": report.get_statistics(),
            "commits_by_weekday": report.get_commits_by_weekday(),
            "commits": [
                {
                    "date": commit.date.isoformat(),
                    "message": commit.message,
                    "day_of_week": commit.day_of_week,
                    "is_weekend": commit.is_weekend,
                    "is_holiday": commit.is_holiday,
                }
                for commits in report.commits_by_day.values()
                for commit in commits
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    elif output_format == "csv":
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Date", "Time", "Day of Week", "Message", "Is Weekend", "Is Holiday"]
            )

            for commits in report.commits_by_day.values():
                for commit in commits:
                    writer.writerow(
                        [
                            commit.date.strftime("%Y-%m-%d"),
                            commit.date.strftime("%H:%M:%S"),
                            commit.day_of_week,
                            commit.message,
                            commit.is_weekend,
                            commit.is_holiday,
                        ]
                    )

    else:  # text format
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("DRY RUN REPORT\n")
            f.write("=" * 50 + "\n\n")

            f.write(
                f"Date Range: {report.start_date.strftime('%Y-%m-%d')} to "
                f"{report.end_date.strftime('%Y-%m-%d')}\n\n"
            )

            f.write("Statistics:\n")
            for metric, value in report.get_statistics().items():
                f.write(f"  {metric}: {value}\n")

            f.write("\nCommits by Day of Week:\n")
            for day, count in report.get_commits_by_weekday().items():
                f.write(f"  {day}: {count}\n")

            f.write(f"\nTotal commits to be created: {report.total_commits}\n")

    logger.info(f"Dry-run report saved to {filepath}")
