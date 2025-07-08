# 🎯 GitHub Activity Generator

> 🤖 A tool to generate a full year of GitHub activity in seconds! Create realistic-looking contribution graphs for demo projects, testing, or just for fun.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/johnwyles/github-activity-generator/graphs/commit-activity)

[![GitHub Stars](https://img.shields.io/github/stars/johnwyles/github-activity-generator.svg?style=social&label=Star)](https://github.com/johnwyles/github-activity-generator)
[![GitHub Forks](https://img.shields.io/github/forks/johnwyles/github-activity-generator.svg?style=social&label=Fork)](https://github.com/johnwyles/github-activity-generator/fork)
[![GitHub Issues](https://img.shields.io/github/issues/johnwyles/github-activity-generator.svg)](https://github.com/johnwyles/github-activity-generator/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/johnwyles/github-activity-generator.svg)](https://github.com/johnwyles/github-activity-generator/commits/main)
[![Contributions](https://img.shields.io/badge/contributions-welcome-orange.svg)](https://github.com/johnwyles/github-activity-generator/blob/main/CONTRIBUTING.md)

## ✨ What is this?

Ever wanted to populate your GitHub contribution graph? This tool creates a Git repository filled with commits in the past, which will show up as a beautiful pattern of green squares on your GitHub profile!

<details>
<summary>📸 <b>See it in action!</b></summary>

```
🟩🟩⬜🟩🟩⬜⬜   Your GitHub profile
🟩🟩🟩🟩🟩⬜⬜   can look like this!
🟩🟩🟩🟩⬜⬜🟩   
⬜🟩🟩🟩🟩🟩🟩   (But with actual commits)
```
</details>

## 🚀 Quick Start

### 📦 Installation

```bash
# Clone this repo
git clone https://github.com/johnwyles/github-activity-generator.git
cd github-activity-generator

# Set up Python environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install it!
pip install -e .
```

### 🎮 Generate Your First Activity!

Just three commands to a full contribution graph:

```bash
# 1. Generate a year of activity
python generate.py

# 2. Create a GitHub repo (on github.com)
# 3. Push it!
cd repository-[timestamp]
git remote add origin YOUR_REPO_URL
git push -u origin main
```

💡 **That's it!** Check your GitHub profile and watch the green squares appear!

## 🎨 Features

### 🗓️ Flexible Date Ranges
Generate activity for any time period:
- Last 7 days: `--start-date 7_days_ago`
- Last month: `--start-date 30_days_ago`  
- Specific dates: `--start-date 2023-01-01 --end-date 2023-12-31`
- Special values: `today`, `yesterday`, `N_days_ago`

### 🎲 Realistic Patterns
- **Random commits**: 1-20 commits per day (customizable)
- **Frequency control**: Set what percentage of days get commits
- **Smart scheduling**: Skip weekends and holidays
- **Natural variation**: Mimics real coding patterns

### 🏖️ Respect Your Weekends
```bash
# Skip weekends - because even fake you needs work-life balance!
python generate.py --no-weekends

# Skip holidays too - support for 100+ countries
python generate.py --no-weekends --no-holidays --country-holidays US
```

### 🔍 Preview Mode (Dry Run)
See what will happen before creating any commits:
```bash
python generate.py --dry-run
```

Shows you:
- 📊 Total commits to be created
- 📅 Date range and skip patterns  
- 📈 Distribution across weekdays
- ✅ Everything you need to know!

## 🛠️ Command Reference

### Basic Commands

| Command | Description | Example |
|---------|-------------|---------|
| No args | Generate 1 year of activity | `python generate.py` |
| Custom dates | Set specific date range | `python generate.py --start-date 2024-01-01 --end-date 2024-06-30` |
| Dry run | Preview without creating | `python generate.py --dry-run` |
| Push to GitHub | Auto-push to remote | `python generate.py --repository git@github.com:user/repo.git` |

### 🎛️ All Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--start-date` | `-sd` | 365_days_ago | Start date (YYYY-MM-DD or special value) |
| `--end-date` | `-ed` | today | End date (YYYY-MM-DD or special value) |
| `--max-commits` | `-mc` | 10 | Max commits per day (1-20) |
| `--frequency` | `-fr` | 80 | % of days with commits (0-100) |
| `--no-weekends` | `-nw` | | Skip Saturdays & Sundays |
| `--no-holidays` | `-nh` | | Skip holidays |
| `--country-holidays` | `-ch` | US | Country for holidays (US, UK, CA, etc.) |
| `--repository` | `-r` | | Remote repo URL (auto-push) |
| `--user-name` | `-un` | | Override Git user name |
| `--user-email` | `-ue` | | Override Git user email |
| `--dry-run` | | | Preview mode - no commits |
| `--no-progress` | | | Hide progress bar |
| `--verbose` | `-v` | | Show detailed output |
| `--config` | `-c` | | Use YAML config file |

## 🎯 Examples

### 🌟 The Overachiever
Maximum activity every single day:
```bash
python generate.py \
  --max-commits 20 \
  --frequency 100 \
  --start-date 365_days_ago
```

### 💼 The 9-to-5 Developer
Weekdays only, moderate activity:
```bash
python generate.py \
  --no-weekends \
  --no-holidays \
  --max-commits 10 \
  --frequency 85 \
  --country-holidays US
```

### 🎨 The Weekend Warrior
Only commits on weekends:
```bash
# Use config file for complex patterns
cat > weekend-warrior.yaml << EOF
date_range:
  start_date: "2024-01-01"
  end_date: "2024-12-31"
  
commit_behavior:
  max_commits_per_day: 15
  frequency_percentage: 95
  skip_weekends: false  # Don't skip them
  skip_holidays: false
  
# Then manually edit to remove weekday commits
EOF

python generate.py --config weekend-warrior.yaml
```

### 🧪 The Tester
Just see what would happen:
```bash
python generate.py \
  --dry-run \
  --start-date 30_days_ago \
  --max-commits 5 \
  --frequency 50
```

## 📝 Configuration Files

For complex setups, use a YAML config file:

```yaml
# my-config.yaml
date_range:
  start_date: "2024-01-01"
  end_date: "2024-12-31"

commit_behavior:
  max_commits_per_day: 12
  frequency_percentage: 90
  skip_weekends: true
  skip_holidays: true
  holiday_country: "US"

git_settings:
  user_name: "Your Name"
  user_email: "your.email@example.com"
  repository_url: "git@github.com:username/my-activity.git"

output:
  show_progress: true
  verbose: false
  dry_run: false
```

Then just:
```bash
python generate.py --config my-config.yaml
```

## 🏗️ How It Works

1. **📁 Creates a new Git repository** in a timestamped directory
2. **📝 Generates commits** by adding entries to README.md
3. **🕐 Backdates each commit** using Git's `--date` option
4. **📤 Optionally pushes** to your GitHub repository

Each commit adds a simple line to README.md:
```
Contribution: 2024-01-15 14:23:00
```

When pushed to GitHub, these commits appear on your contribution graph! 🎉

## 🔧 Advanced Usage

### 🤖 Custom Git Identity
Override your Git configuration:
```bash
python generate.py \
  --user-name "Bot McBotface" \
  --user-email "bot@example.com"
```

### 🌍 Holiday Support
Skip holidays for any country:
```bash
# US holidays
python generate.py --no-holidays --country-holidays US

# UK holidays  
python generate.py --no-holidays --country-holidays UK

# Japanese holidays
python generate.py --no-holidays --country-holidays JP
```

[Full list of supported countries →](https://python-holidays.readthedocs.io/en/latest/#available-countries)

### 📊 Verbose Output
See everything that's happening:
```bash
python generate.py --verbose
```

### 🚫 No Progress Bar
For scripts and automation:
```bash
python generate.py --no-progress
```

## 🐛 Troubleshooting

<details>
<summary><b>🔴 Git not found</b></summary>

```
Error: Git is not installed or not in PATH
```
**Solution**: Install Git from https://git-scm.com/
</details>

<details>
<summary><b>🔴 Permission denied when pushing</b></summary>

```
Error: Permission denied (publickey)
```
**Solution**: 
- Set up SSH keys: https://docs.github.com/en/authentication
- Or use HTTPS with token: `https://github.com/user/repo.git`
</details>

<details>
<summary><b>🔴 Module not found</b></summary>

```
Error: No module named 'holidays'
```
**Solution**: 
```bash
pip install holidays pyyaml tqdm click rich
# or
pip install -e .
```
</details>

<details>
<summary><b>🔴 No commits appearing</b></summary>

Make sure to:
1. Push to the default branch (usually `main`)
2. Check that dates are not in the future
3. Verify the repository is public (or you're logged in)
</details>

## 🏗️ Project Structure

```
github-activity-generator/
├── 🎮 generate.py                 # Main script - run this!
├── 📦 src/                       # The brains
│   └── github_activity_generator/
│       ├── cli.py                # Command-line interface
│       ├── core.py               # Core generation logic
│       ├── git_ops.py            # Git operations
│       └── ...                   # Other magical modules
├── 🧪 tests/                     # Test suite
├── 📜 contribute.py.legacy       # Original script (still works!)
├── 📖 README.md                  # You are here!
└── ⚖️  LICENSE                   # Apache 2.0
```

## 🧑‍💻 Development

Want to contribute? Awesome! 

```bash
# Get dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests

# Check types
mypy src
```

## ⚠️ Disclaimer

This tool creates artificial commit history. Please:

- 🤝 **Be honest** if asked about your contributions
- 💼 **Don't misrepresent** your coding activity professionally  
- 🎓 **Use responsibly** for learning, testing, or fun
- 🎮 **Have fun** but be ethical!

## 📜 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ by developers who love green squares

⭐ Star this repo if it made you smile!

</div>