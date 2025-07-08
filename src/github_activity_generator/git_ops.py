"""Git operations for GitHub Activity Generator."""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .dry_run import DryRunSimulator
from .exceptions import GitOperationError
from .logger import get_logger
from .utils import ensure_git_available, format_datetime

logger = get_logger(__name__)


class GitOperations:
    """Handle git operations for the activity generator."""

    def __init__(
        self, dry_run: bool = False, verbose: bool = False, dry_run_simulator=None
    ):
        """Initialize GitOperations.

        Args:
            dry_run: Whether to simulate operations without executing
            verbose: Whether to show verbose output
            dry_run_simulator: Optional shared DryRunSimulator instance
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.dry_run_simulator = dry_run_simulator or (
            DryRunSimulator(verbose) if dry_run else None
        )

        # Ensure git is available
        if not dry_run:
            ensure_git_available()

    def init_repository(self, directory: Path, branch: str = "main") -> None:
        """Initialize a new git repository.

        Args:
            directory: Directory to initialize repository in
            branch: Initial branch name
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would initialize git repository in {directory}")
            return

        # Change to directory
        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            # Initialize repository
            self._run_git_command(["init", "-b", branch])
            logger.info(f"Initialized git repository with branch '{branch}'")

        finally:
            os.chdir(original_dir)

    def configure_user(
        self, directory: Path, name: Optional[str] = None, email: Optional[str] = None
    ) -> None:
        """Configure git user for repository.

        Args:
            directory: Repository directory
            name: User name
            email: User email
        """
        if not name and not email:
            return

        if self.dry_run:
            if name:
                logger.info(f"[DRY RUN] Would set user.name to '{name}'")
            if email:
                logger.info(f"[DRY RUN] Would set user.email to '{email}'")
            return

        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            if name:
                self._run_git_command(["config", "user.name", name])
                logger.info(f"Set user.name to '{name}'")

            if email:
                self._run_git_command(["config", "user.email", email])
                logger.info(f"Set user.email to '{email}'")

        finally:
            os.chdir(original_dir)

    def create_commit(
        self,
        directory: Path,
        date: datetime,
        message: str,
        file_path: Optional[Path] = None,
    ) -> None:
        """Create a commit with specific date.

        Args:
            directory: Repository directory
            date: Commit date
            message: Commit message
            file_path: Optional file to modify (defaults to README.md)
        """
        if self.dry_run:
            self.dry_run_simulator.simulate_commit(date, message)
            return

        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            # Default to README.md
            if file_path is None:
                file_path = Path("README.md")

            # Append to file
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"{message}\n\n")

            # Stage changes
            self._run_git_command(["add", str(file_path)])

            # Create commit with specific date
            self._run_git_command(
                [
                    "commit",
                    "-m",
                    message,
                    "--date",
                    date.strftime("%Y-%m-%d %H:%M:%S"),
                    "--no-gpg-sign",
                ]
            )

            if self.verbose:
                logger.debug(f"Created commit: {message} at {format_datetime(date)}")

        finally:
            os.chdir(original_dir)

    def add_remote(self, directory: Path, name: str, url: str) -> None:
        """Add a remote repository.

        Args:
            directory: Repository directory
            name: Remote name (usually 'origin')
            url: Remote URL
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would add remote '{name}' -> {url}")
            return

        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            self._run_git_command(["remote", "add", name, url])
            logger.info(f"Added remote '{name}' -> {url}")

        finally:
            os.chdir(original_dir)

    def push(
        self,
        directory: Path,
        remote: str = "origin",
        branch: str = "main",
        force: bool = False,
    ) -> None:
        """Push commits to remote repository.

        Args:
            directory: Repository directory
            remote: Remote name
            branch: Branch name
            force: Whether to force push
        """
        if self.dry_run:
            force_msg = " (force)" if force else ""
            logger.info(f"[DRY RUN] Would push to {remote}/{branch}{force_msg}")
            return

        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            cmd = ["push", "-u", remote, branch]
            if force:
                cmd.insert(1, "--force")

            self._run_git_command(cmd)
            logger.info(f"Pushed to {remote}/{branch}")

        finally:
            os.chdir(original_dir)

    def rename_branch(self, directory: Path, old_name: str, new_name: str) -> None:
        """Rename a branch.

        Args:
            directory: Repository directory
            old_name: Current branch name
            new_name: New branch name
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename branch '{old_name}' to '{new_name}'")
            return

        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            self._run_git_command(["branch", "-m", old_name, new_name])
            logger.info(f"Renamed branch '{old_name}' to '{new_name}'")

        finally:
            os.chdir(original_dir)

    def get_current_branch(self, directory: Path) -> Optional[str]:
        """Get current branch name.

        Args:
            directory: Repository directory

        Returns:
            Current branch name or None
        """
        if self.dry_run:
            return "main"

        original_dir = os.getcwd()
        try:
            os.chdir(directory)

            result = self._run_git_command(
                ["rev-parse", "--abbrev-ref", "HEAD"], capture_output=True
            )
            return result.stdout.strip() if result else None

        finally:
            os.chdir(original_dir)

    def _run_git_command(
        self, args: List[str], capture_output: bool = False
    ) -> Optional[subprocess.CompletedProcess]:
        """Run a git command.

        Args:
            args: Git command arguments
            capture_output: Whether to capture output

        Returns:
            Completed process if capture_output is True

        Raises:
            GitError: If git command fails
        """
        cmd = ["git", *args]

        if self.verbose and not capture_output:
            logger.debug(f"Running: {' '.join(cmd)}")

        try:
            if capture_output:
                return subprocess.run(  # noqa: S603
                    cmd, capture_output=True, text=True, check=True
                )
            subprocess.run(cmd, check=True)  # noqa: S603
            return None

        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {' '.join(cmd)}"
            if e.stderr:
                error_msg += f"\nError: {e.stderr}"
            raise GitOperationError(error_msg, command=" ".join(cmd)) from e
        except FileNotFoundError as e:
            error_msg = "Git executable not found. Please ensure git is installed."
            raise GitOperationError(
                error_msg,
                command=" ".join(cmd),
            ) from e
