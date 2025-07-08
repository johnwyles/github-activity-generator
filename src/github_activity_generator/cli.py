"""Command-line interface for GitHub Activity Generator."""

import argparse
import sys
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
  # Preview what would be generated (always start with dry-run!)
  %(prog)s --dry-run --start-date 30_days_ago

  # Generate realistic work activity (weekdays only, respecting holidays)
  %(prog)s --no-weekends --no-holidays --country-holidays US \\
           --start-date 2024-01-01 --end-date 2024-12-31 \\
           --frequency 85 --max-commits 12

  # Simulate different contributor patterns
  %(prog)s --frequency 100 --max-commits 5   # Consistent daily contributor
  %(prog)s --frequency 40 --max-commits 20   # Burst contributor
  %(prog)s --frequency 80 --max-commits 1    # Minimal daily activity

  # Auto-push to GitHub repository
  %(prog)s --repository git@github.com:username/project.git \\
           --user-name "Your Name" --user-email "you@example.com" \\
           --start-date 180_days_ago --no-weekends

  # Different time periods
  %(prog)s --start-date yesterday --end-date today           # Just today
  %(prog)s --start-date 7_days_ago                          # Last week
  %(prog)s --start-date 2024-01-01 --end-date 2024-03-31   # Q1 2024
  %(prog)s --start-date 2023-01-01 --end-date 2023-12-31   # Full year

  # Configuration file for complex patterns
  cat > github-work.yaml << 'EOF'
  date_range:
    start_date: "2024-01-01"
    end_date: "2024-12-31"
  commit_behavior:
    max_commits_per_day: 15
    frequency_percentage: 90
    skip_weekends: true
    skip_holidays: true
    holiday_country: "US"
  git_settings:
    user_name: "Your Name"
    user_email: "your.email@company.com"
    repository_url: "git@github.com:company/project.git"
  EOF

  %(prog)s --config github-work.yaml
""",
    )

    # Version
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {APP_VERSION}"
    )

    # Configuration file
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="FILE",
        help="Configuration file (YAML format)",
    )

    # Date range arguments
    date_group = parser.add_argument_group("Date Range")
    date_group.add_argument(
        "-sd",
        "--start-date",
        type=str,
        metavar="DATE",
        help="Start date (YYYY-MM-DD or special values like 'today', '365_days_ago')",
    )
    date_group.add_argument(
        "-ed",
        "--end-date",
        type=str,
        metavar="DATE",
        help="End date (YYYY-MM-DD or special values like 'today', '365_days_ago')",
    )

    # Commit behavior arguments
    commit_group = parser.add_argument_group("Commit Behavior")
    commit_group.add_argument(
        "-mc",
        "--max-commits",
        type=int,
        metavar="N",
        help="Maximum commits per day (1-20, default: 10)",
    )
    commit_group.add_argument(
        "-fr",
        "--frequency",
        type=int,
        metavar="N",
        help="Percentage of days to commit (0-100, default: 80)",
    )
    commit_group.add_argument(
        "-nw", "--no-weekends", action="store_true", help="Skip weekends"
    )
    commit_group.add_argument(
        "-nh", "--no-holidays", action="store_true", help="Skip holidays"
    )
    commit_group.add_argument(
        "-ch",
        "--country-holidays",
        type=str,
        metavar="CODE",
        help="Country code for holidays (e.g., US, UK, DE)",
    )

    # Git settings arguments
    git_group = parser.add_argument_group("Git Settings")
    git_group.add_argument(
        "-r",
        "--repository",
        type=str,
        metavar="URL",
        help="Remote repository URL (SSH or HTTPS format)",
    )
    git_group.add_argument(
        "-un",
        "--user-name",
        type=str,
        metavar="NAME",
        help="Git user name (overrides global config)",
    )
    git_group.add_argument(
        "-ue",
        "--user-email",
        type=str,
        metavar="EMAIL",
        help="Git user email (overrides global config)",
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    output_group.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    output_group.add_argument(
        "--no-progress", action="store_true", help="Disable progress bar"
    )
    output_group.add_argument(
        "--log-file", type=str, metavar="FILE", help="Write logs to file"
    )

    # Debug options
    debug_group = parser.add_argument_group("Debug Options")
    debug_group.add_argument("--debug", action="store_true", help="Enable debug mode")
    debug_group.add_argument(
        "--show-config", action="store_true", help="Show configuration and exit"
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


def show_usage_and_exit() -> None:  # noqa: PLR0915
    """Show comprehensive usage information and exit."""
    print(f"{Colors.BOLD}{Colors.CYAN}{APP_NAME} v{APP_VERSION}{Colors.RESET}")
    print()
    print("Generate realistic GitHub activity to populate your contribution graph.")
    print("This tool creates Git commits with backdated timestamps.")
    print()
    print(f"{Colors.BOLD}USAGE:{Colors.RESET} generate.py [OPTIONS]")
    print()
    print(f"{Colors.BOLD}COMMON EXAMPLES:{Colors.RESET}")
    print("  generate.py --dry-run")
    print("      # Preview without creating commits")
    print("  generate.py --start-date 30_days_ago")
    print("      # Generate last 30 days of activity")
    print("  generate.py --start-date 2024-01-01 --end-date 2024-12-31")
    print("      # Specific date range")
    print("  generate.py --no-weekends --frequency 90")
    print("      # Skip weekends, 90% commit frequency")
    print("  generate.py --repository git@github.com:user/repo.git")
    print("      # Auto-push to GitHub")
    print()
    print(f"{Colors.BOLD}KEY OPTIONS:{Colors.RESET}")
    print()
    print(f"{Colors.CYAN}Date Control:{Colors.RESET}")
    print("  --start-date DATE    Start date for commits (default: 365_days_ago)")
    print("                       Examples: 2024-01-01, today, yesterday, 30_days_ago")
    print("  --end-date DATE      End date for commits (default: today)")
    print("                       Examples: 2024-12-31, today, yesterday")
    print()
    print(f"{Colors.CYAN}Commit Patterns:{Colors.RESET}")
    print("  --max-commits N      Max commits per day, 1-20 (default: 10)")
    print("  --frequency N        Percentage of days with commits,")
    print("                       0-100 (default: 80)")
    print("  --no-weekends        Skip Saturdays and Sundays")
    print("  --no-holidays        Skip holidays (use with --country-holidays)")
    print("  --country-holidays   Country code for holidays (US, UK, CA, etc.)")
    print()
    print(f"{Colors.CYAN}Git Configuration:{Colors.RESET}")
    print("  --repository URL     Remote repository URL to push to")
    print("                       Example: git@github.com:username/repo.git")
    print("  --user-name NAME     Override Git user name")
    print("  --user-email EMAIL   Override Git user email")
    print()
    print(f"{Colors.CYAN}Output Control:{Colors.RESET}")
    print("  --dry-run           Preview what would be generated")
    print("                      without creating commits")
    print("  --verbose           Show detailed output during generation")
    print("  --no-progress       Disable progress bar")
    print()
    print(f"{Colors.BOLD}MORE EXAMPLES:{Colors.RESET}")
    print()
    print("# Generate a realistic work pattern (weekdays only, with holidays):")
    print("generate.py --no-weekends --no-holidays --country-holidays US \\")
    print("            --start-date 2024-01-01 --end-date 2024-12-31 \\")
    print("            --frequency 85 --max-commits 12")
    print()
    print("# Simulate an open source contributor (evenings and weekends):")
    print("generate.py --start-date 90_days_ago --max-commits 8 \\")
    print('            --user-name "Jane Developer" \\')
    print('            --user-email "jane@example.com"')
    print()
    print("# Create activity for a private work repo with auto-push:")
    print("generate.py --repository git@github.com:company/internal-tool.git \\")
    print("            --no-weekends --frequency 95 --max-commits 20 \\")
    print("            --start-date 2024-01-01 --end-date 2024-06-30")
    print()
    print("# Generate sparse activity for an archived project:")
    print("generate.py --start-date 2023-01-01 --end-date 2023-03-31 \\")
    print("            --frequency 30 --max-commits 3")
    print()
    print("# Test different patterns with dry-run:")
    print("generate.py --dry-run --start-date 30_days_ago --frequency 50  # Sparse")
    print("generate.py --dry-run --start-date 30_days_ago --frequency 100 # Daily")
    print("generate.py --dry-run --no-weekends --no-holidays --country-holidays UK")
    print()
    print("# Use configuration file for complex setups:")
    print("cat > work-pattern.yaml << EOF")
    print("date_range:")
    print('  start_date: "2024-01-01"')
    print('  end_date: "2024-12-31"')
    print("commit_behavior:")
    print("  max_commits_per_day: 15")
    print("  frequency_percentage: 90")
    print("  skip_weekends: true")
    print("  skip_holidays: true")
    print('  holiday_country: "US"')
    print("git_settings:")
    print('  user_name: "Your Name"')
    print('  user_email: "your.email@company.com"')
    print('  repository_url: "git@github.com:company/project.git"')
    print("EOF")
    print("generate.py --config work-pattern.yaml")
    print()
    print("Run 'generate.py --help' for complete option list.")
    sys.exit(0)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for CLI.

    Args:
        args: Command-line arguments (for testing)

    Returns:
        Exit code
    """
    # Check if no arguments provided (not counting the script name)
    if args is None and len(sys.argv) == 1:
        show_usage_and_exit()

    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Set up logging
    log_level = (
        "DEBUG"
        if parsed_args.debug
        else ("INFO" if not parsed_args.verbose else "DEBUG")
    )
    setup_logging(
        level=log_level,
        log_file=parsed_args.log_file,
        verbose=parsed_args.verbose or parsed_args.debug,
        use_rich=not parsed_args.no_progress,
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
