# 🎯 GitHub Activity Generator

> 🤖 A **modern, production-ready** tool to generate realistic GitHub activity! Create believable contribution graphs for testing, demos, or populating new profiles.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linter-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/johnwyles/github-activity-generator/workflows/CI/badge.svg)](https://github.com/johnwyles/github-activity-generator/actions)

## ✨ Features

### 🚀 Core Features
- **Generate realistic GitHub activity** - Create authentic-looking contribution patterns
- **Smart scheduling** - Skip weekends, holidays, or create custom patterns
- **Timezone aware** - All commits properly timestamped with timezone support
- **Dry run mode** - Preview your activity before committing
- **Auto-push to GitHub** - Direct integration with remote repositories
- **Progress tracking** - Beautiful progress bars and statistics

### 🎨 New in v2.0 (Complete Rewrite!)
- **Zero linter errors** - Clean, maintainable code (0 ruff errors, was 178!)
- **Modern Python** - Full type hints, Python 3.8+ only
- **Professional structure** - Proper package layout with `src/` directory
- **Comprehensive testing** - Full test suite with pytest
- **Rich CLI** - Beautiful terminal output with colors and progress bars
- **YAML configuration** - Save and reuse your favorite patterns
- **Extensible design** - Easy to add new features

## 🚀 Quick Start

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/johnwyles/github-activity-generator.git
cd github-activity-generator

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### 🎮 Basic Usage

```bash
# See what it does first (always start with --dry-run!)
generate.py --dry-run

# Generate activity for the last 30 days
generate.py --start-date 30_days_ago

# Create realistic work patterns (skip weekends & holidays)
generate.py --no-weekends --no-holidays --frequency 90

# Auto-push to GitHub
generate.py --repository git@github.com:username/repo.git
```

## 📖 Documentation

### Command Line Options

```
generate.py [OPTIONS]

Date Control:
  --start-date DATE       Start date (YYYY-MM-DD or special values)
                         Special values: today, yesterday, N_days_ago
  --end-date DATE        End date (default: today)

Activity Patterns:
  --max-commits N        Max commits per day (1-20, default: 10)
  --frequency N          Percentage of days with commits (0-100, default: 80)
  --no-weekends          Skip Saturdays and Sundays
  --no-holidays          Skip holidays (use with --country-holidays)
  --country-holidays CC  Country code for holidays (US, UK, CA, etc.)

Git Configuration:
  --repository URL       Remote repository URL to push to
  --user-name NAME       Override Git user name
  --user-email EMAIL     Override Git user email

Output Options:
  --dry-run             Preview what would be generated
  --verbose             Show detailed output
  --no-progress         Disable progress bar
  --config FILE         Load settings from YAML file
```

### 🎨 Example Patterns

#### The Consistent Contributor
```bash
generate.py --frequency 100 --max-commits 5
```

#### The Weekend Warrior
```bash
generate.py --no-weekdays --max-commits 15
```

#### The 9-to-5 Developer
```bash
generate.py --no-weekends --no-holidays --country-holidays US \
            --frequency 95 --max-commits 12
```

#### The Burst Contributor
```bash
generate.py --frequency 40 --max-commits 20
```

### 📝 Configuration Files

Save your favorite patterns in YAML:

```yaml
# work-pattern.yaml
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
```

Then use it:
```bash
generate.py --config work-pattern.yaml
```

## 🏗️ Architecture

This is a complete rewrite with modern Python practices:

```
github-activity-generator/
├── src/
│   └── github_activity_generator/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── core.py              # Core generation logic
│       ├── config_loader.py     # YAML configuration
│       ├── git_ops.py           # Git operations
│       ├── dry_run.py           # Dry-run simulation
│       ├── progress.py          # Progress tracking
│       └── validators.py        # Input validation
├── tests/                       # Comprehensive test suite
├── generate.py                  # Main entry point
└── pyproject.toml              # Modern Python packaging
```

## 🧪 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src tests

# Linting (0 errors!)
ruff check src tests

# Type checking
mypy src
```

## 🙏 Credits

### Original Inspiration
This project is a complete rewrite inspired by the original [github-activity-generator](https://github.com/Shpota/github-activity-generator) by **Serhii Shpota**. Thank you for the brilliant idea!

### Complete Rewrite
This modern v2.0 rewrite was done with extensive assistance from **[Claude Code](https://claude.ai/code)** by Anthropic. The AI assistant helped:
- Restructure the entire codebase with modern Python practices
- Fix all 178 linter errors to achieve 0 errors
- Add comprehensive type hints and error handling
- Create a full test suite
- Implement timezone awareness
- Design the new CLI with rich output
- And much more!

### Contributors
- **John Wyles** - Current maintainer and v2.0 rewrite
- **You?** - Contributions welcome!

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool generates Git commits with backdated timestamps. Use responsibly:
- ✅ Great for testing and demos
- ✅ Perfect for populating test repositories
- ✅ Useful for visualization examples
- ❌ Don't misrepresent your actual work history
- ❌ Don't use for misleading employers or clients

---

<p align="center">
  Made with ❤️ and lots of ☕ by <a href="https://github.com/johnwyles">John Wyles</a><br>
  Powered by 🤖 <a href="https://claude.ai/code">Claude Code</a>
</p>