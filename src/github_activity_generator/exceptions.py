"""Custom exceptions for GitHub Activity Generator."""

from typing import Optional, Dict, Any


class GitHubActivityError(Exception):
    """Base exception for GitHub Activity Generator."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize exception.
        
        Args:
            message: Error message
            details: Optional details dictionary
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(GitHubActivityError):
    """Error in configuration."""
    
    pass


class ValidationError(GitHubActivityError):
    """Error in input validation."""
    
    pass


class GitOperationError(GitHubActivityError):
    """Error during git operations."""
    
    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        output: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize git operation error.
        
        Args:
            message: Error message
            command: Git command that failed
            exit_code: Exit code from git command
            output: Output from git command
            details: Additional details
        """
        details = details or {}
        if command:
            details["command"] = command
        if exit_code is not None:
            details["exit_code"] = exit_code
        if output:
            details["output"] = output
        
        super().__init__(message, details)


# Alias for backward compatibility
GitError = GitOperationError


class DateRangeError(GitHubActivityError):
    """Error with date range."""
    
    pass


class FileSystemError(GitHubActivityError):
    """Error with file system operations."""
    
    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize file system error.
        
        Args:
            message: Error message
            path: Path involved in the error
            operation: Operation that failed
            details: Additional details
        """
        details = details or {}
        if path:
            details["path"] = path
        if operation:
            details["operation"] = operation
        
        super().__init__(message, details)


class DependencyError(GitHubActivityError):
    """Error with external dependencies."""
    
    def __init__(
        self,
        message: str,
        dependency: Optional[str] = None,
        version_required: Optional[str] = None,
        version_found: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize dependency error.
        
        Args:
            message: Error message
            dependency: Name of the dependency
            version_required: Required version
            version_found: Found version
            details: Additional details
        """
        details = details or {}
        if dependency:
            details["dependency"] = dependency
        if version_required:
            details["version_required"] = version_required
        if version_found:
            details["version_found"] = version_found
        
        super().__init__(message, details)


class PermissionError(GitHubActivityError):
    """Error with permissions."""
    
    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize permission error.
        
        Args:
            message: Error message
            path: Path with permission issue
            operation: Operation that was denied
            details: Additional details
        """
        details = details or {}
        if path:
            details["path"] = path
        if operation:
            details["operation"] = operation
        
        super().__init__(message, details)


class NetworkError(GitHubActivityError):
    """Error with network operations."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize network error.
        
        Args:
            message: Error message
            url: URL that failed
            status_code: HTTP status code
            details: Additional details
        """
        details = details or {}
        if url:
            details["url"] = url
        if status_code is not None:
            details["status_code"] = status_code
        
        super().__init__(message, details)


class UserCancelledError(GitHubActivityError):
    """User cancelled the operation."""
    
    def __init__(self, message: str = "Operation cancelled by user"):
        """Initialize user cancelled error."""
        super().__init__(message)


def format_error_message(error: Exception, verbose: bool = False) -> str:
    """Format an error message for display.
    
    Args:
        error: Exception to format
        verbose: Whether to include detailed information
        
    Returns:
        Formatted error message
    """
    if isinstance(error, GitHubActivityError):
        message = str(error)
        
        if verbose and isinstance(error, GitOperationError):
            if error.details.get("output"):
                message += f"\n\nGit output:\n{error.details['output']}"
        
        return message
    
    # Generic exception
    if verbose:
        return f"{type(error).__name__}: {error}"
    
    return str(error)


def is_recoverable_error(error: Exception) -> bool:
    """Check if an error is recoverable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if the error might be recoverable
    """
    # Configuration and validation errors are not recoverable
    if isinstance(error, (ConfigurationError, ValidationError)):
        return False
    
    # Permission and dependency errors are not recoverable
    if isinstance(error, (PermissionError, DependencyError)):
        return False
    
    # User cancelled is not recoverable
    if isinstance(error, UserCancelledError):
        return False
    
    # Network errors might be recoverable (retry)
    if isinstance(error, NetworkError):
        return True
    
    # Some git errors might be recoverable
    if isinstance(error, GitOperationError):
        # Check for specific recoverable conditions
        exit_code = error.details.get("exit_code")
        if exit_code == 128:  # Git configuration error
            return False
        return True
    
    # Default to not recoverable
    return False