#!/usr/bin/env python

"""GIthub Activity Generator"""

import argparse
import os
import sys
from datetime import datetime
from datetime import timedelta
from random import randint
from subprocess import Popen

# Import US holidays module (install with "pip install holidays")
import holidays

# Emojis present: ✅ 🔴 🔵 ⚪
CEND = "\33[0m"
CBOLD = "\33[1m"
CITALIC = "\33[3m"
CURL = "\33[4m"
CBLINK = "\33[5m"
CBLINK2 = "\33[6m"
CSELECTED = "\33[7m"
CGREY = "\33[90m"
CRED = "\33[91m"
CGREEN = "\33[92m"
CYELLOW = "\33[93m"
CBLUE = "\33[94m"
CVIOLET = "\33[95m"
CBEIGE = "\33[96m"
CWHITE = "\33[97m"

def main(def_args=sys.argv[1:]):
    """Main function"""

    args = arguments(def_args)
    country_for_holidays = args.country_holidays
    curr_date = datetime.now()
    delta_days = timedelta(days=1)
    directory = "repository-" + curr_date.strftime("%Y-%m-%d-%H-%M-%S")
    frequency = args.frequency
    repository = args.repository
    user_email = args.user_email
    user_name = args.user_name

    # Check if the country is supported
    if country_for_holidays not in holidays.__dict__:
        sys.exit("""🔴 Country is not supported. Please refer to the documentation
                 which can be found at 
                 https://python-holidays.readthedocs.io/en/latest/#available-countries""")

    # Check if the date format is correct
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        sys.exit("🔴 Date format is incorrect. Please use YYYY-MM-DD format.")

    # Check if the start date is greater than the end date
    if start_date > end_date:
        sys.exit("🔴 Start date cannot be greater than end date.")

    # Check if the start date is greater than the current date
    if start_date > curr_date:
        print("🔵 Start date is greater than current date. Are you sure?")
        prompt = input("🔵 Continue? [y/N]: ")
        if prompt.lower() != "y":
            sys.exit("🔴 Aborting...")

    # Check if the end date is greater than the current date
    if end_date > curr_date:
        print("🔵 End date is greater than current date. Are you sure?")
        prompt = input("🔵 Continue? [y/N]: ")
        if prompt.lower() != "y":
            sys.exit("🔴 Aborting...")

    # Check if the frequency is between 0 and 100
    if frequency > 100 or frequency < 0:
        sys.exit("🔴 Frequency must be between 0 and 100.")

    # Check if the max commits is between 1 and 20
    if args.max_commits > 20 or args.max_commits < 1:
        sys.exit("🔴 Max commits must be between 1 and 20.")

    # Get the directory to the repository
    if repository is not None:
        start = repository.rfind("/") + 1
        end = repository.rfind(".")
        directory = repository[start:end]

    # We can skip creating the directory because this script actually works even
    # if the repository is already there.
    try:
        os.mkdir(directory)
    except FileExistsError:
        print(
            CBLUE
            + f"🔵 Skipping directory {directory} creation as it already "
            + "exists."
            + CEND
        )
    os.chdir(directory)

    # Setup the get repository
    run(["git", "init", "-b", "main"])
    if user_name is not None:
        run(["git", "config", "user.name", user_name])
    if user_email is not None:
        run(["git", "config", "user.email", user_email])

    #########$###########################################
    ### START: This is where ALL the business happens ###
    #####################################################
    # Loop through the dates and make commits
    while start_date <= end_date:
        # Check if the date is not a holiday or weekend and the frequency is above a randomized threshold
        if (not_weekend(args, start_date) or not_holiday(args, start_date, country_for_holidays)) and randint(0, 100) < frequency:
            # Make a commit for the day we are on
            make_daily_commits(args, start_date)
        
        # Increment the date
        start_date += delta_days
    ###########
    ### END ###
    ###########

    # Run some git operations to setup the repository
    if repository is not None:
        run(["git", "branch", "-m", "main"])
        run(["git", "remote", "add", "origin", repository])
        run(["git", "push", "-u", "origin", "main"])

    print("✅ Repository generation completed successfully!")


def not_holiday(args, start_date, country_for_holidays='US'):
    """Returns True if the date is not a holiday"""

    # Get the holidays for the country
    country_holidays = holidays.__dict__[country_for_holidays]()

    # Check if the date is a holiday
    return not args.no_holidays or start_date not in country_holidays


def not_weekend(args, start_date):
    """Returns True if the date is not a weekend"""

    # Check if the date is not on a weekend
    return not args.no_weekends or start_date.weekday() < 5


def make_daily_commits(args, start_date):  ##
    """Makes a commit for a given day"""

    # Loop through the number of commits for the day adding a minute to each
    # subsquent commit
    for commit_time in (
        start_date + timedelta(minutes=m) \
        for m in range(contributions_per_day(args))
    ):
        contribute(commit_time)


def contribute(date):
    """Makes a commit for a given time"""
    
    # Add an entry to the README.md for the repository for each date
    with open(os.path.join(os.getcwd(), "README.md"), "a", encoding="UTF-8") \
    as file:
        file.write(message(date) + "\n\n")
    
    print("⚪ Adding commit for " + date.strftime("%Y-%m-%d %H:%M" + "..."))
    run(["git", "add", "."])
    
    print("Commiting...")
    run(
        [
            "git",
            "commit",
            "-m",
            f'"{message(date)}"',
            "--date",
            date.strftime('"%Y-%m-%d %H:%M:%S"'),
        ]
    )


def run(commands):
    """Runs git command"""
    
    print("⚪ Running: " + " ".join(commands))
    Popen(commands).wait()


def message(date):
    """Returns a date formated commit message"""

    return date.strftime("Contribution: %Y-%m-%d %H:%M")


def contributions_per_day(args):
    """Returns a random number of commits per day"""

    max_c = args.max_commits
    max_c = max(min(max_c, 20), 1)
    return randint(1, max_c)


def arguments(argsval):
    """Parses arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-ch",
        "--country_holidays",
        required=False,
        default="US",
        help="""Specify the country for holidays. The default is US. For example
                US, UK, etc. For a full list of supported countries, please
                refer to https://python-holidays.readthedocs.io/en/latest/#available-countries"""
    )
    parser.add_argument(
        "-nh",
        "--no_holidays",
        required=False,
        action="store_true",
        default=False,
        help="""Do not commit on holidays.""",
    )
    parser.add_argument(
        "-nw",
        "--no_weekends",
        required=False,
        action="store_true",
        default=False,
        help="""Do not commit on the weekend.""",
    )
    parser.add_argument(
        "-mc",
        "--max_commits",
        type=int,
        default=10,
        required=False,
        help="""Defines the maximum amount of commits a day the script can make.
                Accepts a number from 1 to 20. If N is specified the script
                commits from 1 to N times a day. The exact number of commits is
                defined randomly for each day. The default value is 10.""",
    )
    parser.add_argument(
        "-fr",
        "--frequency",
        type=int,
        default=80,
        required=False,
        help="""Percentage of days when the script performs commits. If N is
                specified, the script will commit N%% of days in a year.
                The default value is 80.""",
    )
    parser.add_argument(
        "-r",
        "--repository",
        type=str,
        required=False,
        help="""A link on an empty non-initialized remote git repository. If
                specified, the script pushes the changes to the repository. The
                link is accepted in SSH or HTTPS format. For example: 
                git@github.com:user/repo.git or https://github.com/user/repo.git
                """,
    )
    parser.add_argument(
        "-un",
        "--user_name",
        type=str,
        required=False,
        help="""Overrides user.name git config. If not specified, the global
                config is used.""",
    )
    parser.add_argument(
        "-ue",
        "--user_email",
        type=str,
        required=False,
        help="""Overrides user.email git config. If not specified, the global
                config is used.""",
    )
    parser.add_argument(
        "-sd",
        "--start_date",
        type=str,
        default=(datetime.now() - timedelta(365)).strftime("%Y-%m-%d"),
        required=False,
        help="""Specifies the date to startadding commits. The format should be
                YYYY-MM-DD. This value can be in future too. For example
                2019-12-05. The value defaults to todays date. NOTE: This option
                will get ignored if used with days_before""",
    )
    parser.add_argument(
        "-ed",
        "--end_date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        required=False,
        help="""Specifies the last date to adding commits. The format should be
                YYYY-MM-DD. This value can be in future too. For example
                2019-12-05. NOTE: This option will get ignored if used with
                days_after""",
    )

    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
