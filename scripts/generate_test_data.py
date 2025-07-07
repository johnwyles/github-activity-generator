#!/usr/bin/env python3
"""Generate test data for GitHub Activity Generator testing."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import yaml


def generate_date_ranges() -> List[Dict[str, str]]:
    """Generate various test date ranges."""
    ranges = []
    today = datetime.now()
    
    # Standard ranges
    ranges.extend([
        {
            "name": "last_year",
            "start": (today - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
        },
        {
            "name": "last_month",
            "start": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
        },
        {
            "name": "last_week",
            "start": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
        },
        {
            "name": "single_day",
            "start": today.strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
        },
    ])
    
    # Edge cases
    ranges.extend([
        {
            "name": "leap_year",
            "start": "2024-02-28",
            "end": "2024-03-01",
        },
        {
            "name": "year_boundary",
            "start": "2023-12-30",
            "end": "2024-01-02",
        },
        {
            "name": "long_range",
            "start": "2020-01-01",
            "end": "2023-12-31",
        },
    ])
    
    return ranges


def generate_test_configs() -> List[Dict]:
    """Generate various test configurations."""
    configs = []
    
    # Basic configurations
    base_configs = [
        {
            "name": "default",
            "config": {
                "date_range": {
                    "start_date": "30_days_ago",
                    "end_date": "today",
                },
                "commit_behavior": {
                    "max_commits_per_day": 10,
                    "frequency_percentage": 80,
                },
            },
        },
        {
            "name": "high_activity",
            "config": {
                "date_range": {
                    "start_date": "90_days_ago",
                    "end_date": "today",
                },
                "commit_behavior": {
                    "max_commits_per_day": 20,
                    "frequency_percentage": 95,
                    "skip_weekends": False,
                    "skip_holidays": False,
                },
            },
        },
        {
            "name": "work_pattern",
            "config": {
                "date_range": {
                    "start_date": "180_days_ago",
                    "end_date": "today",
                },
                "commit_behavior": {
                    "max_commits_per_day": 12,
                    "frequency_percentage": 85,
                    "skip_weekends": True,
                    "skip_holidays": True,
                    "holiday_country": "US",
                },
            },
        },
        {
            "name": "minimal",
            "config": {
                "date_range": {
                    "start_date": "7_days_ago",
                    "end_date": "today",
                },
                "commit_behavior": {
                    "max_commits_per_day": 1,
                    "frequency_percentage": 100,
                },
            },
        },
    ]
    
    # Add edge case configurations
    edge_configs = [
        {
            "name": "zero_frequency",
            "config": {
                "commit_behavior": {
                    "frequency_percentage": 0,
                },
            },
        },
        {
            "name": "max_values",
            "config": {
                "commit_behavior": {
                    "max_commits_per_day": 20,
                    "frequency_percentage": 100,
                },
            },
        },
        {
            "name": "different_countries",
            "configs": [
                {
                    "name": f"holidays_{country}",
                    "config": {
                        "commit_behavior": {
                            "skip_holidays": True,
                            "holiday_country": country,
                        },
                    },
                }
                for country in ["US", "UK", "CA", "AU", "DE", "FR", "JP"]
            ],
        },
    ]
    
    configs.extend(base_configs)
    
    # Flatten nested configs
    for item in edge_configs:
        if "configs" in item:
            configs.extend(item["configs"])
        else:
            configs.append(item)
    
    return configs


def generate_test_repositories() -> List[Dict[str, str]]:
    """Generate test repository URLs."""
    return [
        {
            "name": "github_ssh",
            "url": "git@github.com:testuser/test-repo.git",
            "expected_name": "test-repo",
        },
        {
            "name": "github_https",
            "url": "https://github.com/testuser/test-repo.git",
            "expected_name": "test-repo",
        },
        {
            "name": "gitlab_ssh",
            "url": "git@gitlab.com:testgroup/test-project.git",
            "expected_name": "test-project",
        },
        {
            "name": "bitbucket_https",
            "url": "https://bitbucket.org/testteam/test-repo.git",
            "expected_name": "test-repo",
        },
        {
            "name": "nested_path",
            "url": "git@github.com:org/team/project/repo.git",
            "expected_name": "repo",
        },
    ]


def generate_cli_test_cases() -> List[Dict]:
    """Generate CLI argument test cases."""
    return [
        {
            "name": "basic",
            "args": ["--start_date", "2024-01-01", "--end_date", "2024-01-31"],
            "expected": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        },
        {
            "name": "all_options",
            "args": [
                "--start_date", "2024-01-01",
                "--end_date", "2024-12-31",
                "--max_commits", "15",
                "--frequency", "90",
                "--no_weekends",
                "--no_holidays",
                "--country_holidays", "UK",
                "--repository", "git@github.com:test/repo.git",
                "--user_name", "Test User",
                "--user_email", "test@example.com",
            ],
            "expected": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "max_commits": 15,
                "frequency": 90,
                "no_weekends": True,
                "no_holidays": True,
                "country_holidays": "UK",
                "repository": "git@github.com:test/repo.git",
                "user_name": "Test User",
                "user_email": "test@example.com",
            },
        },
        {
            "name": "short_options",
            "args": [
                "-sd", "2024-01-01",
                "-ed", "2024-01-31",
                "-mc", "5",
                "-fr", "50",
                "-nw",
                "-nh",
                "-ch", "CA",
            ],
            "expected": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "max_commits": 5,
                "frequency": 50,
                "no_weekends": True,
                "no_holidays": True,
                "country_holidays": "CA",
            },
        },
    ]


def generate_expected_outputs() -> Dict:
    """Generate expected outputs for various scenarios."""
    return {
        "commit_patterns": [
            "Contribution: 2024-01-01 10:00",
            "Contribution: 2024-01-01 10:01",
            "Contribution: 2024-01-01 10:02",
        ],
        "skip_reasons": [
            "Skipping 2024-01-06 - Weekend",
            "Skipping 2024-01-01 - Holiday",
            "Skipping 2024-01-15 - Frequency filter",
        ],
        "success_messages": [
            "✅ Repository generation completed successfully!",
            "✅ Successfully generated 100 commits across 30 days!",
        ],
        "error_messages": {
            "invalid_date": "🔴 Date format is incorrect. Please use YYYY-MM-DD format.",
            "start_after_end": "🔴 Start date cannot be greater than end date.",
            "unsupported_country": "🔴 Country is not supported.",
            "invalid_frequency": "🔴 Frequency must be between 0 and 100.",
            "invalid_max_commits": "🔴 Max commits must be between 1 and 20.",
        },
    }


def save_test_data(output_dir: Path) -> None:
    """Save all test data to files.
    
    Args:
        output_dir: Directory to save test data
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save date ranges
    date_ranges = generate_date_ranges()
    with open(output_dir / "date_ranges.json", "w") as f:
        json.dump(date_ranges, f, indent=2)
    
    # Save configurations
    configs = generate_test_configs()
    with open(output_dir / "test_configs.yaml", "w") as f:
        yaml.dump({"test_configurations": configs}, f, default_flow_style=False)
    
    # Save repository URLs
    repos = generate_test_repositories()
    with open(output_dir / "test_repositories.json", "w") as f:
        json.dump(repos, f, indent=2)
    
    # Save CLI test cases
    cli_cases = generate_cli_test_cases()
    with open(output_dir / "cli_test_cases.json", "w") as f:
        json.dump(cli_cases, f, indent=2)
    
    # Save expected outputs
    outputs = generate_expected_outputs()
    with open(output_dir / "expected_outputs.json", "w") as f:
        json.dump(outputs, f, indent=2)
    
    # Generate sample commits data
    sample_commits = []
    base_date = datetime(2024, 1, 1)
    for day in range(30):
        date = base_date + timedelta(days=day)
        if date.weekday() < 5:  # Weekday
            num_commits = random.randint(1, 10)
            for i in range(num_commits):
                commit_time = date + timedelta(minutes=i)
                sample_commits.append({
                    "date": commit_time.isoformat(),
                    "message": f"Contribution: {commit_time.strftime('%Y-%m-%d %H:%M')}",
                    "day_of_week": commit_time.strftime("%A"),
                })
    
    with open(output_dir / "sample_commits.json", "w") as f:
        json.dump(sample_commits, f, indent=2)
    
    print(f"✅ Test data generated in {output_dir}")
    print(f"  - {len(date_ranges)} date ranges")
    print(f"  - {len(configs)} configurations")
    print(f"  - {len(repos)} repository URLs")
    print(f"  - {len(cli_cases)} CLI test cases")
    print(f"  - {len(sample_commits)} sample commits")


def main():
    """Generate test data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    test_data_dir = project_root / "tests" / "fixtures" / "data"
    
    save_test_data(test_data_dir)


if __name__ == "__main__":
    main()