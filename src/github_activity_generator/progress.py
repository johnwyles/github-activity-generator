"""Progress bar implementation for GitHub Activity Generator."""

import sys
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from tqdm import tqdm
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from .logger import get_logger

logger = get_logger(__name__)


class ProgressTracker:
    """Track progress of commit generation."""
    
    def __init__(self, show_progress: bool = True, verbose: bool = False):
        """Initialize progress tracker.
        
        Args:
            show_progress: Whether to show progress bar
            verbose: Whether to show verbose output
        """
        self.show_progress = show_progress
        self.verbose = verbose
        self.console = Console()
        self._progress: Optional[Progress] = None
        self._task_id: Optional[TaskID] = None
        self._total_commits = 0
        self._current_commits = 0
    
    @contextmanager
    def track_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> Generator[None, None, None]:
        """Track progress through date range.
        
        Args:
            start_date: Start date
            end_date: End date
        """
        if not self.show_progress:
            yield
            return
        
        total_days = (end_date - start_date).days + 1
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            self._progress = progress
            self._task_id = progress.add_task(
                f"Generating commits from {start_date.date()} to {end_date.date()}",
                total=total_days,
            )
            
            try:
                yield
            finally:
                self._progress = None
                self._task_id = None
    
    def update_date(self, current_date: datetime, commits_made: int = 0) -> None:
        """Update progress for current date.
        
        Args:
            current_date: Current date being processed
            commits_made: Number of commits made on this date
        """
        self._current_commits += commits_made
        
        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id,
                advance=1,
                description=f"Processing {current_date.date()} "
                f"({self._current_commits} commits total)",
            )
        elif self.verbose:
            self.console.print(
                f"[cyan]Processing {current_date.date()}[/cyan] - "
                f"{commits_made} commits"
            )
    
    def log_skip(self, date: datetime, reason: str) -> None:
        """Log that a date was skipped.
        
        Args:
            date: Date that was skipped
            reason: Reason for skipping
        """
        if self.verbose:
            self.console.print(
                f"[yellow]Skipping {date.date()}[/yellow] - {reason}"
            )
        logger.debug(f"Skipped {date.date()}: {reason}")
    
    def log_commit(self, date: datetime, commit_number: int, total: int) -> None:
        """Log a single commit.
        
        Args:
            date: Date of commit
            commit_number: Current commit number
            total: Total commits for this date
        """
        if self.verbose:
            self.console.print(
                f"  [green]✓[/green] Commit {commit_number}/{total} "
                f"at {date.strftime('%Y-%m-%d %H:%M')}"
            )
        logger.debug(f"Created commit {commit_number}/{total} for {date}")
    
    def complete(self, total_commits: int, total_days: int) -> None:
        """Show completion message.
        
        Args:
            total_commits: Total number of commits created
            total_days: Total number of days processed
        """
        self.console.print(
            f"\n[bold green]✅ Successfully generated {total_commits} commits "
            f"across {total_days} days![/bold green]"
        )


class SimpleProgressBar:
    """Simple progress bar for environments without rich support."""
    
    def __init__(self, total: int, description: str = "Progress"):
        """Initialize simple progress bar.
        
        Args:
            total: Total number of items
            description: Description to show
        """
        self.total = total
        self.description = description
        self.current = 0
        self._bar = None
        
        if sys.stdout.isatty():
            self._bar = tqdm(
                total=total,
                desc=description,
                unit="days",
                leave=True,
            )
    
    def update(self, n: int = 1) -> None:
        """Update progress.
        
        Args:
            n: Number of items to advance
        """
        self.current += n
        if self._bar:
            self._bar.update(n)
    
    def close(self) -> None:
        """Close progress bar."""
        if self._bar:
            self._bar.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


@contextmanager
def progress_context(
    total: int,
    description: str = "Processing",
    show_progress: bool = True,
    use_simple: bool = False,
) -> Generator[SimpleProgressBar, None, None]:
    """Create a progress context.
    
    Args:
        total: Total number of items
        description: Description to show
        show_progress: Whether to show progress
        use_simple: Use simple progress bar instead of rich
        
    Yields:
        Progress bar instance
    """
    if not show_progress:
        # Dummy progress bar that does nothing
        class DummyProgress:
            def update(self, n=1): pass
            def close(self): pass
        
        yield DummyProgress()
        return
    
    if use_simple or not sys.stdout.isatty():
        bar = SimpleProgressBar(total, description)
    else:
        # Use rich progress bar
        bar = SimpleProgressBar(total, description)  # For now, always use simple
    
    try:
        yield bar
    finally:
        bar.close()


def format_time_remaining(seconds: float) -> str:
    """Format time remaining in human-readable format.
    
    Args:
        seconds: Number of seconds remaining
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"