"""Constants for GitHub Activity Generator."""

from pathlib import Path

# Version info
APP_NAME = "GitHub Activity Generator"
APP_VERSION = "2.0.0"
VERSION = APP_VERSION  # Backward compatibility
GITHUB_URL = "https://github.com/johnwyles/github-activity-generator"
DOCS_URL = "https://github-activity-generator.readthedocs.io"

# Limits
MIN_COMMITS_PER_DAY = 1
MAX_COMMITS_PER_DAY = 20
DEFAULT_MAX_COMMITS = 10

MIN_FREQUENCY = 0
MAX_FREQUENCY = 100
DEFAULT_FREQUENCY = 80

# Time constants (in seconds)
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600

# Date/Time constants
DAYS_IN_WEEK = 7
DAYS_IN_MONTH = 30
DAYS_IN_YEAR = 365

# File/Data constants
MIN_FILE_PARTS = 2
MIN_URL_PARTS = 3
HASH_LENGTH = 32
KILOBYTE = 1024

# Git constants
GIT_ERROR_CODE = 128

# Display constants
MIN_DISPLAY_ITEMS = 3
MIN_CONTRIBUTION_DAYS = 5

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
COMMIT_DATE_FORMAT = '"%Y-%m-%d %H:%M:%S"'

# Special date values
SPECIAL_DATES = ["today", "yesterday"]
RELATIVE_DATE_SUFFIX = "_days_ago"

# Default values
DEFAULT_START_DATE = "365_days_ago"
DEFAULT_END_DATE = "today"
DEFAULT_COUNTRY = "US"
DEFAULT_BRANCH = "main"

# Git settings
GIT_COMMAND_TIMEOUT = 30  # seconds
GIT_INIT_BRANCH_FLAG = "-b"  # for git init -b main

# File patterns
README_FILENAME = "README.md"
CONFIG_FILENAMES = [
    "config.yaml",
    "config.yml",
    ".github-activity.yaml",
    ".github-activity.yml",
]

# Directory patterns
DEFAULT_REPO_PREFIX = "repository-"
LOG_DIR_NAME = "logs"
CACHE_DIR_NAME = ".cache"

# Repository URL patterns
SSH_URL_PREFIX = "git@"
HTTPS_URL_PREFIX = "https://"
GIT_URL_SUFFIX = ".git"

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USER_CANCELLED = 2
EXIT_VALIDATION_ERROR = 3
EXIT_CONFIGURATION_ERROR = 4
EXIT_GIT_ERROR = 5


# Colors for terminal output (ANSI codes)
class Colors:
    """Terminal color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


# Emoji constants
class Emoji:
    """Unicode emoji for output."""

    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"  # noqa: RUF001
    ROCKET = "🚀"
    CALENDAR = "📅"
    CLOCK = "🕐"
    FOLDER = "📁"
    FILE = "📄"
    GIT = "🔧"
    COMMIT = "💾"
    PUSH = "⬆️"
    SPARKLES = "✨"
    FIRE = "🔥"
    BUG = "🐛"
    WRENCH = "🔧"
    MEMO = "📝"
    PACKAGE = "📦"
    QUESTION = "❓"
    EXCLAMATION = "❗"
    CHECK = "✓"
    CROSS = "✗"
    HOURGLASS = "⌛"
    MAGNIFYING_GLASS = "🔍"
    KEY = "🔑"
    LOCK = "🔒"
    UNLOCK = "🔓"
    COMPUTER = "💻"
    CHART = "📊"


# Environment variable names
ENV_PREFIX = "GITHUB_ACTIVITY_"
ENV_CONFIG_FILE = f"{ENV_PREFIX}CONFIG"
ENV_LOG_LEVEL = f"{ENV_PREFIX}LOG_LEVEL"
ENV_LOG_FILE = f"{ENV_PREFIX}LOG_FILE"
ENV_DEBUG = f"{ENV_PREFIX}DEBUG"
ENV_NO_COLOR = "NO_COLOR"
ENV_FORCE_COLOR = "FORCE_COLOR"

# Commit messages
COMMIT_MESSAGE_PREFIX = "Contribution:"
DEFAULT_COMMIT_MESSAGE_FORMAT = "{prefix} {date}"

# Progress messages
PROGRESS_INITIALIZING = "Initializing repository..."
PROGRESS_GENERATING = "Generating commits..."
PROGRESS_PUSHING = "Pushing to remote repository..."
PROGRESS_COMPLETE = "Generation complete!"

# Error messages
ERROR_GIT_NOT_FOUND = "Git is not installed or not in PATH"
ERROR_INVALID_DATE_FORMAT = "Invalid date format. Use YYYY-MM-DD"
ERROR_START_AFTER_END = "Start date cannot be after end date"
ERROR_FUTURE_DATE = "Date is in the future"
ERROR_UNSUPPORTED_COUNTRY = "Unsupported country code for holidays"
ERROR_INVALID_REPOSITORY_URL = "Invalid repository URL format"
ERROR_DIRECTORY_EXISTS = "Directory already exists"
ERROR_PERMISSION_DENIED = "Permission denied"
ERROR_NETWORK_ERROR = "Network error occurred"

# Success messages
SUCCESS_REPOSITORY_CREATED = "Repository created successfully"
SUCCESS_COMMITS_GENERATED = "Commits generated successfully"
SUCCESS_PUSHED_TO_REMOTE = "Pushed to remote repository successfully"

# Warning messages
WARNING_NO_CONFIG_FILE = "No configuration file found, using defaults"
WARNING_FUTURE_DATE = "Warning: Date is in the future"
WARNING_EXISTING_DIRECTORY = "Using existing directory"
WARNING_NO_COMMITS_GENERATED = "No commits were generated"

# Help text snippets
HELP_DATE_FORMAT = (
    "Date format: YYYY-MM-DD or special values like 'today', '30_days_ago'"
)
HELP_REPOSITORY_FORMAT = "Repository URL format: git@github.com:user/repo.git or https://github.com/user/repo.git"
HELP_COUNTRY_LIST = (
    "For supported countries, see: https://python-holidays.readthedocs.io"
)

# Paths
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "github-activity-generator"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "github-activity-generator"
DEFAULT_LOG_DIR = (
    Path.home() / ".local" / "share" / "github-activity-generator" / "logs"
)
