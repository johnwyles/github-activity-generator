"""GitHub Activity Generator - Generate realistic GitHub activity"""

from .cli import main, run
from .config_loader import Config, load_config
from .constants import APP_NAME, APP_VERSION
from .core import ActivityGenerator
from .exceptions import GitHubActivityError, ConfigurationError, ValidationError, GitError

__version__ = APP_VERSION
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "main",
    "run", 
    "Config",
    "load_config",
    "ActivityGenerator",
    "GitHubActivityError",
    "ConfigurationError",
    "ValidationError",
    "GitError",
    "__version__",
]