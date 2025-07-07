#!/usr/bin/env python3
"""Compatibility wrapper for the old contribute.py interface.

This module provides backward compatibility for tests and scripts
that expect the old contribute.py interface.
"""

import sys
from datetime import datetime, timedelta
from subprocess import Popen

# Map old functions to maintain compatibility
def main(def_args=sys.argv[1:]):
    """Main function for backward compatibility."""
    # Import and use the new CLI
    from src.github_activity_generator.cli import main as new_main
    return new_main(def_args)


def arguments(argsval):
    """Parse arguments in old format."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-ch", "--country_holidays", default="US")
    parser.add_argument("-nh", "--no_holidays", action="store_true", default=False)
    parser.add_argument("-nw", "--no_weekends", action="store_true", default=False)
    parser.add_argument("-mc", "--max_commits", type=int, default=10)
    parser.add_argument("-fr", "--frequency", type=int, default=80)
    parser.add_argument("-r", "--repository", type=str, required=False)
    parser.add_argument("-un", "--user_name", type=str, required=False)
    parser.add_argument("-ue", "--user_email", type=str, required=False)
    parser.add_argument("-sd", "--start_date", type=str,
                       default=(datetime.now() - timedelta(365)).strftime("%Y-%m-%d"))
    parser.add_argument("-ed", "--end_date", type=str,
                       default=datetime.now().strftime("%Y-%m-%d"))
    
    return parser.parse_args(argsval)


def run(commands):
    """Run command for backward compatibility."""
    print("⚪ Running: " + " ".join(commands))
    Popen(commands).wait()


def message(date):
    """Generate commit message."""
    return date.strftime("Contribution: %Y-%m-%d %H:%M")


def contributions_per_day(args):
    """Get random contributions per day."""
    import random
    max_c = args.max_commits
    max_c = max(min(max_c, 20), 1)
    return random.randint(1, max_c)


def not_weekend(args, date):
    """Check if date is not a weekend."""
    return not args.no_weekends or date.weekday() < 5


def not_holiday(args, date, country='US'):
    """Check if date is not a holiday."""
    if not args.no_holidays:
        return True
    
    import holidays
    country_holidays = holidays.__dict__.get(country, holidays.US)()
    return date not in country_holidays


def make_daily_commits(args, date):
    """Make commits for a day."""
    # This is a stub for compatibility
    pass


def contribute(date):
    """Make a single commit."""
    # This is a stub for compatibility
    import os
    with open("README.md", "a") as f:
        f.write(message(date) + "\n\n")
    run(["git", "add", "."])
    run(["git", "commit", "-m", f'"{message(date)}"', "--date", date.strftime('"%Y-%m-%d %H:%M:%S"')])


# For backward compatibility with imports
randint = __import__('random').randint


if __name__ == "__main__":
    main()