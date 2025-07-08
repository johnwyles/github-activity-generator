"""GitHub Activity Generator - Generate realistic GitHub activity"""

from .cli import main, run
from .config_loader import Config, load_config
from .constants import APP_NAME, APP_VERSION
from .core import ActivityGenerator
from .exceptions import (
    ConfigurationError,
    GitError,
    GitHubActivityError,
    ValidationError,
)

__version__ = APP_VERSION
__author__ = "John Wyles"
__email__ = "john@johnwyles.com"

__all__ = [
    "APP_NAME",
    "ActivityGenerator",
    "Config",
    "ConfigurationError",
    "GitError",
    "GitHubActivityError",
    "ValidationError",
    "__version__",
    "load_config",
    "main",
    "run",
]
