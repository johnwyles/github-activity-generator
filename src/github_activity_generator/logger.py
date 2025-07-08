"""Logging configuration for GitHub Activity Generator."""

import contextlib
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.logging import RichHandler

# Global console instance
console = Console(stderr=True)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    verbose: bool = False,
    use_rich: bool = True,
) -> None:
    """Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        verbose: Whether to enable verbose output
        use_rich: Whether to use rich formatting for console output
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # If verbose, use DEBUG level
    if verbose:
        numeric_level = logging.DEBUG

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    if use_rich and sys.stderr.isatty():
        console_handler = RichHandler(
            console=console,
            show_time=False,
            show_path=verbose,
            rich_tracebacks=True,
            tracebacks_show_locals=verbose,
        )
        console_handler.setLevel(numeric_level)

        # Use simpler format for rich handler
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
    else:
        # Fallback to standard console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(numeric_level)

        # Standard format
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if not verbose:
            console_format = "%(levelname)s: %(message)s"

        console_formatter = logging.Formatter(console_format)
        console_handler.setFormatter(console_formatter)

    root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            # Create log directory if needed
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file

            # Detailed format for file
            file_format = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
            )
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)

            root_logger.addHandler(file_handler)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not create log file: {e}[/yellow]")

    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.debug(
        f"Logging configured: level={level}, verbose={verbose}, log_file={log_file}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_section(logger: logging.Logger, title: str, width: int = 60) -> None:
    """Log a section header.

    Args:
        logger: Logger to use
        title: Section title
        width: Width of the section header
    """
    separator = "=" * width
    logger.info(separator)
    logger.info(f"{title:^{width}}")
    logger.info(separator)


def log_subsection(logger: logging.Logger, title: str, width: int = 60) -> None:
    """Log a subsection header.

    Args:
        logger: Logger to use
        title: Subsection title
        width: Width of the subsection header
    """
    separator = "-" * width
    logger.info(separator)
    logger.info(f"{title:^{width}}")
    logger.info(separator)


def log_key_value(
    logger: logging.Logger, key: str, value: Any, indent: int = 2
) -> None:
    """Log a key-value pair.

    Args:
        logger: Logger to use
        key: Key name
        value: Value to log
        indent: Number of spaces to indent
    """
    indent_str = " " * indent
    logger.info(f"{indent_str}{key}: {value}")


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Exception,
    context: Optional[dict] = None,
) -> None:
    """Log an error with additional context.

    Args:
        logger: Logger to use
        message: Error message
        error: Exception instance
        context: Optional context dictionary
    """
    logger.error(f"{message}: {type(error).__name__}: {error}")

    if context:
        logger.error("Context:")
        for key, value in context.items():
            logger.error(f"  {key}: {value}")

    # Log stack trace at debug level
    logger.debug("Stack trace:", exc_info=error)


def get_log_file_path(name: str = "github-activity-generator") -> str:
    """Get default log file path.

    Args:
        name: Base name for log file

    Returns:
        Log file path
    """
    # Use user's home directory for logs
    log_dir = Path.home() / ".local" / "share" / "github-activity-generator" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{name}_{timestamp}.log"

    return str(log_file)


def cleanup_old_logs(log_dir: Path, keep_days: int = 7) -> None:
    """Clean up old log files.

    Args:
        log_dir: Directory containing log files
        keep_days: Number of days to keep logs
    """
    if not log_dir.exists():
        return

    cutoff_time = datetime.now(timezone.utc).timestamp() - (keep_days * 24 * 60 * 60)

    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            with contextlib.suppress(Exception):
                log_file.unlink()  # Ignore errors when cleaning up


# Convenience functions for module-level logging
def debug(message: str, *args, **kwargs) -> None:
    """Log a debug message."""
    logger = get_logger("github_activity_generator")
    logger.debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """Log an info message."""
    logger = get_logger("github_activity_generator")
    logger.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """Log a warning message."""
    logger = get_logger("github_activity_generator")
    logger.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs) -> None:
    """Log an error message."""
    logger = get_logger("github_activity_generator")
    logger.error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs) -> None:
    """Log a critical message."""
    logger = get_logger("github_activity_generator")
    logger.critical(message, *args, **kwargs)
