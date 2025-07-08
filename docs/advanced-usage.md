# Advanced Usage Guide

This guide covers advanced usage patterns and techniques for GitHub Activity Generator.

## Table of Contents

- [Complex Scheduling Patterns](#complex-scheduling-patterns)
- [Automation and Scripting](#automation-and-scripting)
- [Integration with CI/CD](#integration-with-cicd)
- [Custom Commit Patterns](#custom-commit-patterns)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)

## Complex Scheduling Patterns

### Realistic Work Patterns

Simulate realistic work patterns with varying activity levels:

```bash
#!/bin/bash
# realistic-work-pattern.sh

# Monday-Tuesday: High activity
python contribute.py \
  --start_date 2023-01-02 \
  --end_date 2023-01-03 \
  --frequency 95 \
  --max_commits 15

# Wednesday-Thursday: Medium activity  
python contribute.py \
  --start_date 2023-01-04 \
  --end_date 2023-01-05 \
  --frequency 80 \
  --max_commits 10

# Friday: Low activity
python contribute.py \
  --start_date 2023-01-06 \
  --end_date 2023-01-06 \
  --frequency 60 \
  --max_commits 5
```

### Seasonal Variations

Different activity levels for different seasons:

```yaml
# config-summer.yaml
commit_behavior:
  frequency_percentage: 50  # Lower activity in summer
  skip_weekends: true
  
# config-winter.yaml  
commit_behavior:
  frequency_percentage: 90  # Higher activity in winter
  skip_weekends: true
```

### Project-Based Patterns

Simulate project lifecycles:

```python
#!/usr/bin/env python3
# project-lifecycle.py

import subprocess
from datetime import datetime, timedelta

def generate_project_activity(start_date, project_name, duration_days):
    """Generate activity pattern for a project lifecycle."""
    
    phases = [
        ("planning", 0.1, 5, 50),      # 10% of time, 5 commits/day, 50% frequency
        ("development", 0.6, 15, 90),   # 60% of time, 15 commits/day, 90% frequency
        ("testing", 0.2, 10, 80),       # 20% of time, 10 commits/day, 80% frequency
        ("maintenance", 0.1, 3, 30),    # 10% of time, 3 commits/day, 30% frequency
    ]
    
    current_date = start_date
    
    for phase_name, phase_duration, max_commits, frequency in phases:
        phase_days = int(duration_days * phase_duration)
        end_date = current_date + timedelta(days=phase_days)
        
        print(f"Generating {phase_name} phase: {current_date} to {end_date}")
        
        subprocess.run([
            "python", "contribute.py",
            "--start_date", current_date.strftime("%Y-%m-%d"),
            "--end_date", end_date.strftime("%Y-%m-%d"),
            "--max_commits", str(max_commits),
            "--frequency", str(frequency),
            "--repository", f"git@github.com:user/{project_name}.git"
        ])
        
        current_date = end_date + timedelta(days=1)

# Generate activity for a 90-day project
generate_project_activity(
    datetime(2023, 1, 1),
    "awesome-project",
    90
)
```

## Automation and Scripting

### Batch Repository Generation

Generate activity for multiple repositories:

```bash
#!/bin/bash
# batch-generate.sh

REPOS=(
    "project-alpha"
    "project-beta"
    "project-gamma"
)

BASE_DIR="/path/to/repos"
CONFIG_FILE="config.yaml"

for repo in "${REPOS[@]}"; do
    echo "Generating activity for $repo..."
    
    cd "$BASE_DIR/$repo" || exit 1
    
    python contribute.py \
        --config "$CONFIG_FILE" \
        --repository "git@github.com:username/$repo.git"
    
    cd ..
done
```

### Parallel Generation

Generate activity for multiple repositories in parallel:

```bash
#!/bin/bash
# parallel-generate.sh

generate_repo() {
    repo=$1
    echo "Starting generation for $repo..."
    
    python contribute.py \
        --config "configs/$repo.yaml" \
        --repository "git@github.com:username/$repo.git" \
        > "logs/$repo.log" 2>&1
    
    echo "Completed $repo"
}

export -f generate_repo

# Run in parallel (max 4 at a time)
cat repo-list.txt | xargs -P 4 -I {} bash -c 'generate_repo "$@"' _ {}
```

### Scheduled Generation

Use cron for automated generation:

```bash
# Add to crontab -e
# Generate activity every Sunday at 2 AM
0 2 * * 0 cd /path/to/generator && python contribute.py --config weekly.yaml

# Generate monthly summary on the 1st
0 3 1 * * cd /path/to/generator && python contribute.py --config monthly.yaml
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
# .github/workflows/generate-activity.yml
name: Generate Activity

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:      # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install github-activity-generator
      
      - name: Generate activity
        env:
          GIT_USER_NAME: ${{ secrets.GIT_USER_NAME }}
          GIT_USER_EMAIL: ${{ secrets.GIT_USER_EMAIL }}
        run: |
          python contribute.py \
            --config config.yaml \
            --user_name "$GIT_USER_NAME" \
            --user_email "$GIT_USER_EMAIL"
      
      - name: Push changes
        run: |
          git push origin main
```

### GitLab CI Integration

```yaml
# .gitlab-ci.yml
generate-activity:
  stage: generate
  image: python:3.11
  only:
    - schedules
  script:
    - pip install github-activity-generator
    - python contribute.py --config config.yaml
    - git push origin main
  variables:
    GIT_STRATEGY: clone
```

## Custom Commit Patterns

### Time-Based Patterns

```python
#!/usr/bin/env python3
# time-based-pattern.py

import subprocess
from datetime import datetime, time

def generate_workday_commits(date_str):
    """Generate commits only during work hours."""
    
    work_hours = [
        (9, 11, 5),    # 9-11 AM: 5 commits
        (14, 17, 10),  # 2-5 PM: 10 commits
    ]
    
    for start_hour, end_hour, max_commits in work_hours:
        subprocess.run([
            "python", "contribute.py",
            "--start_date", date_str,
            "--end_date", date_str,
            "--max_commits", str(max_commits),
            "--time_range", f"{start_hour}:00-{end_hour}:00"
        ])
```

### Repository-Specific Patterns

```yaml
# Frontend repository - more commits during business hours
# config-frontend.yaml
commit_behavior:
  max_commits_per_day: 20
  frequency_percentage: 85
  peak_hours: "09:00-17:00"

# Backend repository - fewer but consistent commits
# config-backend.yaml  
commit_behavior:
  max_commits_per_day: 8
  frequency_percentage: 95
  
# Documentation repository - sporadic updates
# config-docs.yaml
commit_behavior:
  max_commits_per_day: 3
  frequency_percentage: 30
```

## Performance Optimization

### Large Date Ranges

For very large date ranges, process in chunks:

```python
#!/usr/bin/env python3
# chunk-processing.py

from datetime import datetime, timedelta
import subprocess

def generate_in_chunks(start_date, end_date, chunk_days=30):
    """Process large date ranges in chunks."""
    
    current = start_date
    
    while current < end_date:
        chunk_end = min(current + timedelta(days=chunk_days), end_date)
        
        print(f"Processing chunk: {current} to {chunk_end}")
        
        subprocess.run([
            "python", "contribute.py",
            "--start_date", current.strftime("%Y-%m-%d"),
            "--end_date", chunk_end.strftime("%Y-%m-%d"),
            "--no_progress"  # Disable progress for chunks
        ])
        
        current = chunk_end + timedelta(days=1)

# Process 5 years in 30-day chunks
generate_in_chunks(
    datetime(2019, 1, 1),
    datetime(2024, 1, 1),
    30
)
```

### Memory-Efficient Processing

```bash
# Process with minimal memory usage
python contribute.py \
  --start_date 2020-01-01 \
  --end_date 2023-12-31 \
  --no_progress \
  --batch_size 100  # Process 100 days at a time
```

## Security Best Practices

### Credential Management

Never hardcode credentials. Use environment variables:

```bash
# Set environment variables
export GIT_USER_NAME="Your Name"
export GIT_USER_EMAIL="your.email@example.com"
export GITHUB_TOKEN="your-token"

# Use in script
python contribute.py \
  --user_name "$GIT_USER_NAME" \
  --user_email "$GIT_USER_EMAIL"
```

### SSH Key Management

```bash
# Generate deployment key for automation
ssh-keygen -t ed25519 -C "activity-generator@example.com" -f ~/.ssh/activity_generator

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/activity_generator

# Use specific key
GIT_SSH_COMMAND="ssh -i ~/.ssh/activity_generator" python contribute.py ...
```

### Secure Configuration

```yaml
# config-secure.yaml
git_settings:
  # Use environment variables
  user_name: ${GIT_USER_NAME}
  user_email: ${GIT_USER_EMAIL}
  
# Don't commit sensitive data
# .gitignore
config-prod.yaml
*.key
*.pem
```

## Advanced Patterns

### Multi-Account Support

```bash
#!/bin/bash
# multi-account.sh

ACCOUNTS=(
    "work:work@company.com:~/.ssh/work_key"
    "personal:personal@email.com:~/.ssh/personal_key"
    "opensource:oss@email.com:~/.ssh/oss_key"
)

for account in "${ACCOUNTS[@]}"; do
    IFS=':' read -r name email key <<< "$account"
    
    echo "Generating for $name account..."
    
    GIT_SSH_COMMAND="ssh -i $key" python contribute.py \
        --user_name "$name" \
        --user_email "$email" \
        --config "config-$name.yaml"
done
```

### Contribution Graph Art

Create patterns in your contribution graph:

```python
#!/usr/bin/env python3
# graph-art.py

def create_heart_pattern():
    """Create a heart shape in the contribution graph."""
    
    heart_pattern = [
        "  ❤❤  ❤❤  ",
        "❤❤❤❤❤❤❤❤❤",
        "❤❤❤❤❤❤❤❤❤",
        "  ❤❤❤❤❤❤  ",
        "    ❤❤❤    ",
        "      ❤      "
    ]
    
    # Map pattern to dates and commit counts
    # Implementation details...
```

## Troubleshooting Performance

### Profiling

```bash
# Profile execution
python -m cProfile -o profile.stats contribute.py --config config.yaml

# Analyze results
python -m pstats profile.stats
```

### Debug Mode

```bash
# Enable debug logging
export GITHUB_ACTIVITY_DEBUG=1
python contribute.py --verbose --config config.yaml
```

### Resource Monitoring

```bash
# Monitor resource usage
/usr/bin/time -v python contribute.py --config config.yaml
```