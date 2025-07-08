"""Utility functions for GitHub Activity Generator."""

import ctypes
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

from .constants import (
    DATE_FORMAT,
    DAYS_IN_MONTH,
    DAYS_IN_WEEK,
    DAYS_IN_YEAR,
    ENV_FORCE_COLOR,
    ENV_NO_COLOR,
    GIT_URL_SUFFIX,
    HASH_LENGTH,
    HTTPS_URL_PREFIX,
    KILOBYTE,
    MIN_FILE_PARTS,
    MIN_URL_PARTS,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    SSH_URL_PREFIX,
    Colors,
)
from .exceptions import DependencyError, FileSystemError
from .logger import get_logger

logger = get_logger(__name__)


def check_git_installed() -> Tuple[bool, Optional[str]]:
    """Check if git is installed and available.

    Returns:
        Tuple of (is_installed, version)
    """
    try:
        # Git is expected to be in PATH - this is standard practice
        # S607: Using 'git' without full path is safe and portable
        result = subprocess.run(
            ["git", "--version"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip()
        return True, version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def get_git_version() -> Optional[str]:
    """Get git version string.

    Returns:
        Git version or None if not available
    """
    _, version = check_git_installed()
    if version:
        # Extract version number from "git version 2.34.1"
        parts = version.split()
        if len(parts) >= MIN_URL_PARTS:
            return parts[2]
    return None


def ensure_git_available() -> None:
    """Ensure git is available, raise error if not.

    Raises:
        DependencyError: If git is not available
    """
    is_installed, version = check_git_installed()
    if not is_installed:
        error_msg = (
            "Git is not installed or not in PATH. "
            "Please install Git from https://git-scm.com/"
        )
        raise DependencyError(error_msg, dependency="git")
    logger.debug(f"Git is available: {version}")


def parse_repository_url(url: str) -> Tuple[str, str, str]:
    """Parse repository URL to extract components.

    Args:
        url: Repository URL

    Returns:
        Tuple of (host, owner, repo_name)

    Example:
        >>> parse_repository_url("git@github.com:user/repo.git")
        ("github.com", "user", "repo")
    """
    url = url.strip()

    if url.startswith(SSH_URL_PREFIX):
        # SSH format: git@github.com:user/repo.git
        parts = url.split(":")
        if len(parts) != MIN_FILE_PARTS:
            return "", "", ""

        host = parts[0].split("@")[1]
        path = parts[1]
    elif url.startswith(HTTPS_URL_PREFIX) or url.startswith("http://"):
        # HTTPS format: https://github.com/user/repo.git
        without_protocol = url.split("://", 1)[1]
        parts = without_protocol.split("/", 1)
        if len(parts) != MIN_FILE_PARTS:
            return "", "", ""

        host = parts[0]
        path = parts[1]
    else:
        return "", "", ""

    # Remove .git suffix
    if path.endswith(GIT_URL_SUFFIX):
        path = path[:-4]

    # Split owner/repo
    path_parts = path.split("/")
    if len(path_parts) >= MIN_FILE_PARTS:
        owner = path_parts[-2]
        repo_name = path_parts[-1]
    else:
        owner = ""
        repo_name = path_parts[0] if path_parts else ""

    return host, owner, repo_name


def extract_repo_name_from_url(url: str) -> str:
    """Extract repository name from URL.

    Args:
        url: Repository URL

    Returns:
        Repository name
    """
    _, _, repo_name = parse_repository_url(url)
    return repo_name


def format_date(date: datetime) -> str:
    """Format date for display.

    Args:
        date: Date to format

    Returns:
        Formatted date string
    """
    return date.strftime(DATE_FORMAT)


def format_datetime(date: datetime) -> str:
    """Format datetime for display.

    Args:
        date: Datetime to format

    Returns:
        Formatted datetime string
    """
    return date.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds:.2f}s"
    if seconds < SECONDS_PER_MINUTE:
        return f"{int(seconds)}s"
    if seconds < SECONDS_PER_HOUR:
        minutes = int(seconds / SECONDS_PER_MINUTE)
        remaining_seconds = int(seconds % SECONDS_PER_MINUTE)
        if remaining_seconds:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    hours = int(seconds / SECONDS_PER_HOUR)
    remaining_minutes = int((seconds % SECONDS_PER_HOUR) / SECONDS_PER_MINUTE)
    if remaining_minutes:
        return f"{hours}h {remaining_minutes}m"
    return f"{hours}h"


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Pluralize a word based on count.

    Args:
        count: Number of items
        singular: Singular form
        plural: Plural form (defaults to singular + 's')

    Returns:
        Appropriate form with count
    """
    if plural is None:
        plural = singular + "s"

    word = singular if count == 1 else plural
    return f"{count} {word}"


def create_directory(path: Union[str, Path], exist_ok: bool = True) -> Path:
    """Create directory with proper error handling.

    Args:
        path: Directory path
        exist_ok: Whether it's OK if directory exists

    Returns:
        Path object

    Raises:
        FileSystemError: If directory creation fails
    """
    path = Path(path)

    try:
        path.mkdir(parents=True, exist_ok=exist_ok)
        return path
    except FileExistsError:
        if not exist_ok:
            error_msg = f"Directory already exists: {path}"
            raise FileSystemError(
                error_msg,
                path=str(path),
                operation="create",
            ) from None
        return path
    except PermissionError as e:
        error_msg = f"Permission denied creating directory: {path}"
        raise FileSystemError(
            error_msg,
            path=str(path),
            operation="create",
        ) from e
    except Exception as e:
        error_msg = f"Failed to create directory: {path}"
        raise FileSystemError(
            error_msg,
            path=str(path),
            operation="create",
        ) from e


def remove_directory(path: Union[str, Path], ignore_errors: bool = False) -> None:
    """Remove directory and all contents.

    Args:
        path: Directory path
        ignore_errors: Whether to ignore errors

    Raises:
        FileSystemError: If removal fails and ignore_errors is False
    """
    path = Path(path)

    if not path.exists():
        return

    try:
        shutil.rmtree(path)
    except Exception as e:
        if not ignore_errors:
            error_msg = f"Failed to remove directory: {path}"
            raise FileSystemError(
                error_msg,
                path=str(path),
                operation="remove",
            ) from e
        logger.warning(f"Failed to remove directory {path}: {e}")


def get_platform_info() -> dict:
    """Get platform information.

    Returns:
        Dictionary with platform details
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def supports_color() -> bool:  # noqa: PLR0911
    """Check if terminal supports color output.

    Returns:
        True if color is supported
    """
    # Check environment variables
    if os.environ.get(ENV_NO_COLOR):
        return False
    if os.environ.get(ENV_FORCE_COLOR):
        return True

    # Check if stdout is a TTY
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False

    # Check platform
    if platform.system() == "Windows":
        # Windows 10+ supports ANSI colors
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False

    # Unix-like systems generally support color
    return True


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Colorize text for terminal output.

    Args:
        text: Text to colorize
        color: Color name from Colors class
        bold: Whether to make text bold

    Returns:
        Colorized text or original if color not supported
    """
    if not supports_color():
        return text

    color_code = getattr(Colors, color.upper(), "")
    if not color_code:
        return text

    if bold:
        return f"{Colors.BOLD}{color_code}{text}{Colors.RESET}"

    return f"{color_code}{text}{Colors.RESET}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe use.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove control characters
    filename = "".join(char for char in filename if ord(char) >= HASH_LENGTH)

    # Trim whitespace
    filename = filename.strip()

    # Ensure not empty
    if not filename:
        filename = "unnamed"

    return filename


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return text[:max_length]

    return text[: max_length - len(suffix)] + suffix


def get_date_range_description(start_date: datetime, end_date: datetime) -> str:
    """Get human-readable description of date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Description string
    """
    days = (end_date - start_date).days + 1

    if days == 1:
        return f"1 day ({format_date(start_date)})"
    if days <= DAYS_IN_WEEK:
        return f"{days} days ({format_date(start_date)} to {format_date(end_date)})"
    if days <= DAYS_IN_MONTH:
        weeks = days / DAYS_IN_WEEK
        return (
            f"{weeks:.1f} weeks ({format_date(start_date)} to {format_date(end_date)})"
        )
    if days <= DAYS_IN_YEAR:
        months = days / DAYS_IN_MONTH
        return (
            f"{months:.1f} months "
            f"({format_date(start_date)} to {format_date(end_date)})"
        )
    years = days / DAYS_IN_YEAR
    return f"{years:.1f} years ({format_date(start_date)} to {format_date(end_date)})"


def parse_size(size_str: str) -> int:
    """Parse size string to bytes.

    Args:
        size_str: Size string (e.g., "10MB", "1.5GB")

    Returns:
        Size in bytes

    Raises:
        ValueError: If format is invalid
    """
    size_str = size_str.strip().upper()

    units = {
        "B": 1,
        "KB": KILOBYTE,
        "MB": KILOBYTE**2,
        "GB": KILOBYTE**3,
        "TB": KILOBYTE**4,
    }

    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            number_str = size_str[: -len(unit)].strip()
            try:
                return int(float(number_str) * multiplier)
            except ValueError as err:
                error_msg = f"Invalid size format: {size_str}"
                raise ValueError(error_msg) from err

    # Try parsing as plain number (bytes)
    try:
        return int(size_str)
    except ValueError as err:
        error_msg = f"Invalid size format: {size_str}"
        raise ValueError(error_msg) from err


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < KILOBYTE:
        return f"{size_bytes}B"
    if size_bytes < KILOBYTE**2:
        return f"{size_bytes / KILOBYTE:.1f}KB"
    if size_bytes < KILOBYTE**3:
        return f"{size_bytes / KILOBYTE ** 2:.1f}MB"
    if size_bytes < KILOBYTE**4:
        return f"{size_bytes / KILOBYTE ** 3:.1f}GB"
    return f"{size_bytes / 1024 ** 4:.1f}TB"
