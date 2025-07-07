"""Command-line interface for GitHub Activity Generator."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .config_loader import Config, load_config
from .constants import APP_NAME, APP_VERSION, Colors
from .core import ActivityGenerator
from .exceptions import ConfigurationError, ValidationError
from .logger import get_logger, setup_logging
from .utils import get_platform_info

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="github-activity-generator",
        description="Generate realistic GitHub activity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate activity for the past year with default settings
  %(prog)s
  
  # Generate activity for a specific date range
  %(prog)s --start-date 2023-01-01 --end-date 2023-12-31
  
  # Generate with custom frequency and skip weekends
  %(prog)s --frequency 60 --no-weekends
  
  # Push to a remote repository
  %(prog)s --repository git@github.com:user/repo.git
  
  # Dry run to see what would be generated
  %(prog)s --dry-run
  
  # Use a configuration file
  %(prog)s --config config.yaml
"""
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}"
    )
    
    # Configuration file
    parser.add_argument(
        "-c", "--config",
        type=str,
        metavar="FILE",
        help="Configuration file (YAML format)"
    )
    
    # Date range arguments
    date_group = parser.add_argument_group("Date Range")
    date_group.add_argument(
        "-sd", "--start-date",
        type=str,
        metavar="DATE",
        help="Start date (YYYY-MM-DD or special values like 'today', '365_days_ago')"
    )
    date_group.add_argument(
        "-ed", "--end-date",
        type=str,
        metavar="DATE",
        help="End date (YYYY-MM-DD or special values like 'today', '365_days_ago')"
    )
    
    # Commit behavior arguments
    commit_group = parser.add_argument_group("Commit Behavior")
    commit_group.add_argument(
        "-mc", "--max-commits",
        type=int,
        metavar="N",
        help="Maximum commits per day (1-20, default: 10)"
    )
    commit_group.add_argument(
        "-fr", "--frequency",
        type=int,
        metavar="N",
        help="Percentage of days to commit (0-100, default: 80)"
    )
    commit_group.add_argument(
        "-nw", "--no-weekends",
        action="store_true",
        help="Skip weekends"
    )
    commit_group.add_argument(
        "-nh", "--no-holidays",
        action="store_true",
        help="Skip holidays"
    )
    commit_group.add_argument(
        "-ch", "--country-holidays",
        type=str,
        metavar="CODE",
        help="Country code for holidays (e.g., US, UK, DE)"
    )
    
    # Git settings arguments
    git_group = parser.add_argument_group("Git Settings")
    git_group.add_argument(
        "-r", "--repository",
        type=str,
        metavar="URL",
        help="Remote repository URL (SSH or HTTPS format)"
    )
    git_group.add_argument(
        "-un", "--user-name",
        type=str,
        metavar="NAME",
        help="Git user name (overrides global config)"
    )
    git_group.add_argument(
        "-ue", "--user-email",
        type=str,
        metavar="EMAIL",
        help="Git user email (overrides global config)"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    output_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    output_group.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )
    output_group.add_argument(
        "--log-file",
        type=str,
        metavar="FILE",
        help="Write logs to file"
    )
    
    # Debug options
    debug_group = parser.add_argument_group("Debug Options")
    debug_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    debug_group.add_argument(
        "--show-config",
        action="store_true",
        help="Show configuration and exit"
    )
    
    return parser


def show_configuration(config: Config) -> None:
    """Display configuration details.
    
    Args:
        config: Configuration to display
    """
    print(f"\n{Colors.BOLD}Configuration:{Colors.RESET}")
    print(f"\n{Colors.CYAN}Date Range:{Colors.RESET}")
    print(f"  Start: {config.date_range.start_date}")
    print(f"  End: {config.date_range.end_date}")
    
    print(f"\n{Colors.CYAN}Commit Behavior:{Colors.RESET}")
    print(f"  Max commits per day: {config.commit_behavior.max_commits_per_day}")
    print(f"  Frequency: {config.commit_behavior.frequency_percentage}%")
    print(f"  Skip weekends: {config.commit_behavior.skip_weekends}")
    print(f"  Skip holidays: {config.commit_behavior.skip_holidays}")
    if config.commit_behavior.skip_holidays:
        print(f"  Holiday country: {config.commit_behavior.holiday_country}")
    
    print(f"\n{Colors.CYAN}Git Settings:{Colors.RESET}")
    print(f"  User name: {config.git_settings.user_name or '(use global)'}")
    print(f"  User email: {config.git_settings.user_email or '(use global)'}")
    print(f"  Repository: {config.git_settings.repository_url or '(local only)'}")
    
    print(f"\n{Colors.CYAN}Output Options:{Colors.RESET}")
    print(f"  Show progress: {config.output.show_progress}")
    print(f"  Verbose: {config.output.verbose}")
    print(f"  Dry run: {config.output.dry_run}")
    print()


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for CLI.
    
    Args:
        args: Command-line arguments (for testing)
        
    Returns:
        Exit code
    """
    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Set up logging
    log_level = "DEBUG" if parsed_args.debug else ("INFO" if not parsed_args.verbose else "DEBUG")
    setup_logging(
        level=log_level,
        log_file=parsed_args.log_file,
        verbose=parsed_args.verbose or parsed_args.debug,
        use_rich=not parsed_args.no_progress
    )
    
    try:
        # Show header
        if not parsed_args.no_progress:
            print(f"{Colors.BOLD}{Colors.CYAN}{APP_NAME} v{APP_VERSION}{Colors.RESET}")
            if parsed_args.debug:
                platform_info = get_platform_info()
                print(f"Platform: {platform_info['system']} {platform_info['release']}")
                print(f"Python: {platform_info['python_version']}")
            print()
        
        # Load configuration
        try:
            config = load_config(parsed_args.config)
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            return 1
        
        # Merge command-line arguments
        config.merge_with_args(parsed_args)
        
        # Show configuration if requested
        if parsed_args.show_config:
            show_configuration(config)
            return 0
        
        # Create and run generator
        generator = ActivityGenerator(config)
        generator.generate()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        return 130
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if parsed_args.debug:
            logger.exception("Full traceback:")
        return 1


def run() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    run()