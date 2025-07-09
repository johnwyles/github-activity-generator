"""Core logic for GitHub Activity Generator."""

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple

import holidays

from .behaviors import get_behavior
from .config_loader import Config
from .constants import MIN_CONTRIBUTION_DAYS, Colors
from .dry_run import DryRunSimulator, display_dry_run_report
from .exceptions import GitOperationError, ValidationError
from .git_ops import GitOperations
from .logger import get_logger
from .progress import ProgressTracker
from .utils import (
    create_directory,
    extract_repo_name_from_url,
    format_date,
    format_datetime,
    pluralize,
)

logger = get_logger(__name__)


class ActivityGenerator:
    """Main class for generating GitHub activity."""

    def __init__(self, config: Config):
        """Initialize activity generator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.dry_run_simulator = (
            DryRunSimulator(verbose=config.output.verbose)
            if config.output.dry_run
            else None
        )
        self.git_ops = GitOperations(
            dry_run=config.output.dry_run,
            verbose=config.output.verbose,
            dry_run_simulator=self.dry_run_simulator,
        )
        self.progress = ProgressTracker(
            show_progress=config.output.show_progress, verbose=config.output.verbose
        )

        # Initialize behavior pattern
        self.behavior = get_behavior(
            config.commit_behavior.behavior,
            config.commit_behavior.max_commits_per_day,
            config.commit_behavior.frequency_percentage,
        )

        # Get holiday calendar if needed
        self.holidays = None
        if config.commit_behavior.skip_holidays:
            try:
                holiday_class = getattr(
                    holidays, config.commit_behavior.holiday_country
                )
                self.holidays = holiday_class()
            except AttributeError:
                logger.warning(
                    f"Country '{config.commit_behavior.holiday_country}' not supported "
                    "for holidays. Skipping holiday detection."
                )

    def generate(self) -> None:
        """Generate GitHub activity based on configuration."""
        try:
            # Resolve dates
            start_date, end_date = self.config.date_range.resolve_dates()

            # Validate date range
            self._validate_date_range(start_date, end_date)

            # Create repository directory
            repo_dir = self._setup_repository()

            # Generate commits
            total_commits = self._generate_commits(repo_dir, start_date, end_date)

            # Handle remote repository if configured
            if (
                self.config.git_settings.repository_url
                and not self.config.output.dry_run
            ):
                self._setup_remote(repo_dir)

            # Show completion message or dry-run report
            if self.config.output.dry_run:
                report = self.dry_run_simulator.generate_report(start_date, end_date)
                display_dry_run_report(report)
            else:
                self._show_completion_message(total_commits, start_date, end_date)

        except (GitOperationError, ValidationError) as e:
            logger.error(f"Error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("\nOperation cancelled by user")
            sys.exit(130)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.debug("Full traceback:", exc_info=True)
            sys.exit(1)

    def _validate_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """Validate and confirm date range with user.

        Args:
            start_date: Start date
            end_date: End date
        """
        current_date = datetime.now(timezone.utc)

        # Check if start date is in the future
        if start_date > current_date:
            logger.warning(
                f"{Colors.BLUE}Start date ({format_date(start_date)}) "
                f"is in the future.{Colors.RESET}"
            )
            if not self._confirm_action("Continue anyway?"):
                sys.exit(0)

        # Check if end date is in the future
        if end_date > current_date:
            logger.warning(
                f"{Colors.BLUE}End date ({format_date(end_date)}) "
                f"is in the future.{Colors.RESET}"
            )
            if not self._confirm_action("Continue anyway?"):
                sys.exit(0)

        # Show date range summary
        total_days = (end_date - start_date).days + 1
        logger.info(
            f"Will generate commits from "
            f"{format_date(start_date)} "
            f"to {format_date(end_date)} "
            f"({total_days} days)"
        )

    def _confirm_action(self, prompt: str) -> bool:
        """Ask user for confirmation.

        Args:
            prompt: Prompt message

        Returns:
            True if user confirms
        """
        if self.config.output.dry_run:
            return True  # Always continue in dry-run mode

        response = input(f"{Colors.BLUE}{prompt} [y/N]: {Colors.RESET}").strip().lower()
        return response == "y"

    def _setup_repository(self) -> Path:
        """Set up the repository directory.

        Returns:
            Path to repository directory
        """
        # Use specified repo_dir if provided
        if self.config.git_settings.repo_dir:
            repo_dir = Path(self.config.git_settings.repo_dir).expanduser().resolve()

            if repo_dir.exists():
                # Check if it's a git repository
                if not (repo_dir / ".git").exists():
                    if self.config.output.dry_run:
                        logger.info(
                            f"[DRY RUN] Would initialize git repository in existing directory: {repo_dir}"
                        )
                    elif self._confirm_action(
                        f"Directory '{repo_dir}' exists but is not a git repository. "
                        "Initialize it as a git repository?"
                    ):
                        self.git_ops.init_repository(repo_dir)
                        logger.info(f"Initialized git repository in: {repo_dir}")
                    else:
                        logger.error("Cannot proceed without a git repository")
                        sys.exit(1)
                else:
                    logger.info(f"Using existing git repository: {repo_dir}")
            # Directory doesn't exist
            elif self.config.output.dry_run:
                logger.info(
                    f"[DRY RUN] Would create directory and initialize git repository: {repo_dir}"
                )
            elif self._confirm_action(
                f"Directory '{repo_dir}' does not exist. Create it?"
            ):
                create_directory(repo_dir)
                logger.info(f"Created repository directory: {repo_dir}")
                self.git_ops.init_repository(repo_dir)
                logger.info(f"Initialized git repository in: {repo_dir}")
            else:
                logger.error("Cannot proceed without repository directory")
                sys.exit(1)
        else:
            # Generate a new directory name
            if self.config.git_settings.repository_url:
                dir_name = extract_repo_name_from_url(
                    self.config.git_settings.repository_url
                )
                if not dir_name:
                    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
                    dir_name = f"repository-{timestamp}"
            else:
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
                dir_name = f"repository-{timestamp}"

            repo_dir = Path(dir_name)

            # Create or use existing directory
            if repo_dir.exists():
                logger.info(f"Using existing directory: {repo_dir}")
            else:
                create_directory(repo_dir)
                logger.info(f"Created repository directory: {repo_dir}")

            # Initialize git repository
            self.git_ops.init_repository(repo_dir)

        # Configure git user if specified
        self.git_ops.configure_user(
            repo_dir,
            name=self.config.git_settings.user_name,
            email=self.config.git_settings.user_email,
        )

        return repo_dir

    def _generate_commits(
        self, repo_dir: Path, start_date: datetime, end_date: datetime
    ) -> int:
        """Generate commits for the date range.

        Args:
            repo_dir: Repository directory
            start_date: Start date
            end_date: End date

        Returns:
            Total number of commits created
        """
        total_commits = 0
        current_date = start_date
        delta = timedelta(days=1)

        # Create context for behavior
        context = {
            "start_date": start_date,
            "end_date": end_date,
        }

        with self.progress.track_date_range(start_date, end_date):
            while current_date <= end_date:
                # For non-consistent behaviors, let behavior decide
                if self.config.commit_behavior.behavior != "consistent":
                    # Get commits from behavior pattern
                    num_commits = self.behavior.get_commits_for_day(
                        current_date, context
                    )

                    # Check additional restrictions (holidays)
                    if num_commits > 0 and self.config.commit_behavior.skip_holidays:
                        if self.holidays and current_date.date() in self.holidays:
                            self.progress.log_skip(
                                current_date,
                                f"holiday ({self.holidays.get(current_date.date())})",
                            )
                            self.progress.update_date(current_date, 0)
                            current_date += delta
                            continue
                else:
                    # Original behavior for consistent pattern
                    should_commit, skip_reason = self._should_commit_on_date(
                        current_date
                    )
                    if should_commit:
                        num_commits = self._get_commits_for_day()
                    else:
                        self.progress.log_skip(current_date, skip_reason)
                        self.progress.update_date(current_date, 0)
                        current_date += delta
                        continue

                # Make commits if any
                if num_commits > 0:
                    for i in range(num_commits):
                        commit_time = current_date + timedelta(minutes=i)
                        message = self._generate_commit_message(commit_time)

                        self.git_ops.create_commit(repo_dir, commit_time, message)

                        self.progress.log_commit(commit_time, i + 1, num_commits)
                        total_commits += 1

                    self.progress.update_date(current_date, num_commits)
                else:
                    self.progress.update_date(current_date, 0)

                current_date += delta

        return total_commits

    def _should_commit_on_date(self, date: datetime) -> Tuple[bool, str]:
        """Check if commits should be made on a given date.

        Args:
            date: Date to check

        Returns:
            Tuple of (should_commit, skip_reason)
        """
        # Check weekend
        if (
            self.config.commit_behavior.skip_weekends
            and date.weekday() >= MIN_CONTRIBUTION_DAYS
        ):
            return False, "weekend"

        # Check holiday
        if (
            self.config.commit_behavior.skip_holidays
            and self.holidays
            and date.date() in self.holidays
        ):
            return False, f"holiday ({self.holidays.get(date.date())})"

        # Check frequency
        if (
            random.randint(1, 100)  # noqa: S311
            > self.config.commit_behavior.frequency_percentage
        ):
            return False, "frequency"

        return True, ""

    def _get_commits_for_day(self) -> int:
        """Get random number of commits for a day.

        Returns:
            Number of commits to make
        """
        max_commits = self.config.commit_behavior.max_commits_per_day
        return random.randint(1, max_commits)  # noqa: S311

    def _generate_commit_message(self, date: datetime) -> str:
        """Generate commit message for a given date.

        Args:
            date: Commit date

        Returns:
            Commit message
        """
        return f"Contribution: {format_datetime(date)}"

    def _setup_remote(self, repo_dir: Path) -> None:
        """Set up remote repository.

        Args:
            repo_dir: Repository directory
        """
        url = self.config.git_settings.repository_url

        logger.info(f"Setting up remote repository: {url}")

        # Ensure we're on main branch
        current_branch = self.git_ops.get_current_branch(repo_dir)
        if current_branch and current_branch != "main":
            self.git_ops.rename_branch(repo_dir, current_branch, "main")

        # Add remote
        self.git_ops.add_remote(repo_dir, "origin", url)

        # Push to remote
        logger.info("Pushing commits to remote repository...")
        self.git_ops.push(repo_dir, "origin", "main")

    def _show_completion_message(
        self, total_commits: int, start_date: datetime, end_date: datetime
    ) -> None:
        """Show completion message.

        Args:
            total_commits: Total number of commits created
            start_date: Start date
            end_date: End date
        """
        total_days = (end_date - start_date).days + 1

        self.progress.complete(total_commits, total_days)

        logger.info("\nRepository generation completed successfully!")
        logger.info(
            f"Created {total_commits} "
            f"{pluralize(total_commits, 'commit')} "
            f"over {total_days} "
            f"{pluralize(total_days, 'day')}"
        )
