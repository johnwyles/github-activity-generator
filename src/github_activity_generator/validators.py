"""Input validation functions for GitHub Activity Generator."""

import re
from datetime import datetime
from typing import Any, List, Optional, Union

import holidays

from .exceptions import ValidationError


def validate_date_string(date_str: str) -> str:
    """Validate date string format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Validated date string
        
    Raises:
        ValidationError: If date string is invalid
    """
    if not isinstance(date_str, str):
        raise ValidationError(f"Date must be a string, got {type(date_str)}")
    
    date_str = date_str.strip()
    
    # Check for special values
    special_values = ["today", "yesterday"]
    if date_str.lower() in special_values:
        return date_str.lower()
    
    # Check for relative date format
    if date_str.lower().endswith("_days_ago"):
        try:
            days = int(date_str.split("_")[0])
            if days < 0:
                raise ValidationError(
                    f"Days ago must be positive, got {days}"
                )
            return date_str.lower()
        except (ValueError, IndexError):
            raise ValidationError(
                f"Invalid relative date format: {date_str}. "
                "Use format like '30_days_ago'"
            )
    
    # Check for YYYY-MM-DD format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValidationError(
            f"Invalid date format: {date_str}. "
            "Use YYYY-MM-DD or special values like 'today', '30_days_ago'"
        )


def validate_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """Validate date range.
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        Tuple of validated date strings
        
    Raises:
        ValidationError: If date range is invalid
    """
    start_date = validate_date_string(start_date)
    end_date = validate_date_string(end_date)
    
    # Can't validate actual date comparison for relative dates
    # That will be done when dates are resolved
    
    return start_date, end_date


def validate_max_commits(value: Any) -> int:
    """Validate max commits value.
    
    Args:
        value: Value to validate
        
    Returns:
        Validated integer value
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"max_commits must be an integer, got {type(value).__name__}"
        )
    
    if value < 1:
        raise ValidationError(
            f"max_commits must be at least 1, got {value}"
        )
    
    if value > 20:
        raise ValidationError(
            f"max_commits must be at most 20, got {value}"
        )
    
    return value


def validate_frequency(value: Any) -> int:
    """Validate frequency percentage.
    
    Args:
        value: Value to validate
        
    Returns:
        Validated integer value
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"frequency must be an integer, got {type(value).__name__}"
        )
    
    if value < 0:
        raise ValidationError(
            f"frequency must be at least 0, got {value}"
        )
    
    if value > 100:
        raise ValidationError(
            f"frequency must be at most 100, got {value}"
        )
    
    return value


def validate_country_code(country: str) -> str:
    """Validate country code for holidays.
    
    Args:
        country: Country code to validate
        
    Returns:
        Validated country code
        
    Raises:
        ValidationError: If country code is invalid
    """
    if not isinstance(country, str):
        raise ValidationError(
            f"country_holidays must be a string, got {type(country).__name__}"
        )
    
    country = country.strip().upper()
    
    # Check if country is supported by holidays library
    if country not in holidays.__dict__:
        # Get list of supported countries
        supported = sorted([
            name for name in dir(holidays)
            if not name.startswith("_") and len(name) == 2
        ])
        
        raise ValidationError(
            f"Country '{country}' is not supported. "
            f"Supported countries: {', '.join(supported[:10])}... "
            "See https://python-holidays.readthedocs.io for full list."
        )
    
    return country


def validate_repository_url(url: str) -> str:
    """Validate git repository URL.
    
    Args:
        url: Repository URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError(
            f"repository_url must be a string, got {type(url).__name__}"
        )
    
    url = url.strip()
    
    if not url:
        raise ValidationError("repository_url cannot be empty")
    
    # SSH URL pattern
    ssh_pattern = r'^[\w\-]+@[\w\.\-]+:[\w\-\./]+\.git$'
    
    # HTTPS URL pattern
    https_pattern = r'^https?://[\w\.\-]+/[\w\-\./]+\.git$'
    
    if not (re.match(ssh_pattern, url) or re.match(https_pattern, url)):
        raise ValidationError(
            f"Invalid repository URL: {url}. "
            "Expected format: "
            "git@github.com:user/repo.git or "
            "https://github.com/user/repo.git"
        )
    
    return url


def validate_git_user_config(
    name: Optional[str], email: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    """Validate git user configuration.
    
    Args:
        name: User name
        email: User email
        
    Returns:
        Tuple of validated name and email
        
    Raises:
        ValidationError: If configuration is invalid
    """
    if name is not None:
        if not isinstance(name, str):
            raise ValidationError(
                f"user_name must be a string, got {type(name).__name__}"
            )
        name = name.strip()
        if not name:
            name = None
    
    if email is not None:
        if not isinstance(email, str):
            raise ValidationError(
                f"user_email must be a string, got {type(email).__name__}"
            )
        email = email.strip()
        if not email:
            email = None
        elif "@" not in email:
            raise ValidationError(
                f"Invalid email format: {email}"
            )
    
    return name, email


def validate_boolean(value: Any, field_name: str) -> bool:
    """Validate boolean value.
    
    Args:
        value: Value to validate
        field_name: Name of field being validated
        
    Returns:
        Boolean value
        
    Raises:
        ValidationError: If value is not boolean
    """
    if not isinstance(value, bool):
        raise ValidationError(
            f"{field_name} must be a boolean, got {type(value).__name__}"
        )
    
    return value


def validate_directory_path(path: str) -> str:
    """Validate directory path.
    
    Args:
        path: Directory path to validate
        
    Returns:
        Validated path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not isinstance(path, str):
        raise ValidationError(
            f"Directory path must be a string, got {type(path).__name__}"
        )
    
    path = path.strip()
    
    if not path:
        raise ValidationError("Directory path cannot be empty")
    
    # Check for invalid characters
    invalid_chars = ["<", ">", "|", "?", "*", "\0"]
    for char in invalid_chars:
        if char in path:
            raise ValidationError(
                f"Directory path contains invalid character: {char}"
            )
    
    return path


def validate_file_path(path: str) -> str:
    """Validate file path.
    
    Args:
        path: File path to validate
        
    Returns:
        Validated path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not isinstance(path, str):
        raise ValidationError(
            f"File path must be a string, got {type(path).__name__}"
        )
    
    path = path.strip()
    
    if not path:
        raise ValidationError("File path cannot be empty")
    
    # Check for invalid characters
    invalid_chars = ["<", ">", "|", "?", "*", "\0"]
    for char in invalid_chars:
        if char in path:
            raise ValidationError(
                f"File path contains invalid character: {char}"
            )
    
    return path


def validate_positive_integer(value: Any, field_name: str, max_value: Optional[int] = None) -> int:
    """Validate positive integer value.
    
    Args:
        value: Value to validate
        field_name: Name of field being validated
        max_value: Optional maximum value
        
    Returns:
        Validated integer
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"{field_name} must be an integer, got {type(value).__name__}"
        )
    
    if value <= 0:
        raise ValidationError(
            f"{field_name} must be positive, got {value}"
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field_name} must be at most {max_value}, got {value}"
        )
    
    return value