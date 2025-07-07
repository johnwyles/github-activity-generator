# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with 90%+ coverage
- Modern Python packaging with `pyproject.toml`
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline
- Type hints throughout the codebase
- Progress bar for long operations
- Dry-run mode to preview changes
- Configuration file support (YAML)
- Professional documentation
- Makefile for common development tasks
- Support for Python 3.8 through 3.12

### Changed
- Migrated from setup.py to pyproject.toml
- Improved error handling and user feedback
- Enhanced code organization and structure
- Updated dependencies to latest versions

### Fixed
- Better handling of edge cases
- Improved date validation
- More robust git operations

## [2.0.0] - 2024-01-XX

### Added
- Complete project restructuring
- Professional Python project standards
- Comprehensive testing framework
- CI/CD automation
- Documentation improvements

### Changed
- Major refactoring for better maintainability
- Improved command-line interface
- Better error messages

### Removed
- Legacy code patterns
- Outdated dependencies

## [1.2.0] - 2023-XX-XX

### Added
- `--start_date` and `--end_date` options for custom date ranges
- Support for different country holiday calendars
- `--dry_run` mode for testing

### Changed
- Improved date handling logic
- Better weekend detection

### Fixed
- Leap year handling
- Holiday detection accuracy

## [1.1.0] - 2023-XX-XX

### Added
- `--no_weekends` flag to skip weekends
- `--no_holidays` flag to skip holidays
- `--country_holidays` option for different countries
- Frequency control with `--frequency` parameter

### Changed
- Refactored commit generation logic
- Improved command-line argument parsing

### Fixed
- Git command execution on Windows
- Unicode handling in commit messages

## [1.0.0] - 2023-XX-XX

### Added
- Initial release
- Basic commit generation
- Random commits per day (1-20)
- Repository creation and initialization
- Push to remote repository
- Custom user configuration
- Date range support

[Unreleased]: https://github.com/yourusername/github-activity-generator/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/yourusername/github-activity-generator/compare/v1.2.0...v2.0.0
[1.2.0]: https://github.com/yourusername/github-activity-generator/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/yourusername/github-activity-generator/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourusername/github-activity-generator/releases/tag/v1.0.0