# Contributing to GitHub Activity Generator

First off, thank you for considering contributing to GitHub Activity Generator! It's people like you that make this tool better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Process](#development-process)
- [Style Guidelines](#style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please be respectful and considerate in all interactions.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Git and GitHub
- Familiarity with Python development

### Setting Up Your Development Environment

1. **Fork the Repository**
   ```bash
   # Click the 'Fork' button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/github-activity-generator.git
   cd github-activity-generator
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/originalowner/github-activity-generator.git
   ```

4. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install Development Dependencies**
   ```bash
   make install-dev
   # or
   pip install -e ".[dev]"
   ```

6. **Install Pre-commit Hooks**
   ```bash
   make pre-commit
   # or
   pre-commit install
   ```

7. **Run Tests to Verify Setup**
   ```bash
   make test
   ```

## 💡 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear Title**: Summarize the issue
- **Description**: What you expected vs. what happened
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Environment**: Python version, OS, Git version
- **Error Messages**: Complete error messages and stack traces
- **Screenshots**: If applicable

**Example Bug Report:**
```markdown
Title: ValueError when using --start_date with invalid format

Description:
When providing an incorrectly formatted date to --start_date, the program crashes with an unhelpful error message.

Steps to Reproduce:
1. Run `python contribute.py --start_date 01-01-2024`
2. See error

Expected: Clear error message about date format
Actual: ValueError with stack trace

Environment:
- Python 3.9.7
- macOS 12.1
- Git 2.33.0
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Use Case**: Why is this enhancement needed?
- **Current Behavior**: What happens now?
- **Desired Behavior**: What should happen?
- **Possible Implementation**: If you have ideas

### Your First Code Contribution

Unsure where to begin? Look for these labels:

- `good first issue` - Simple issues perfect for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Documentation improvements

### Pull Requests

1. **Find or Create an Issue**: Discuss your change first
2. **Fork and Branch**: Create a feature branch
3. **Write Code**: Follow our style guidelines
4. **Write Tests**: Ensure your change is tested
5. **Document**: Update documentation if needed
6. **Submit PR**: Create a pull request

## 🔄 Development Process

### Branching Strategy

- `main` - Stable release branch
- `develop` - Development branch (if applicable)
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Urgent fixes

### Workflow

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run tests
   make test
   
   # Run linters
   make lint
   
   # Run type checking
   make type-check
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Test changes
   - `chore:` Build process or auxiliary tool changes

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use the PR template
   - Link related issues
   - Request reviews

## 🎨 Style Guidelines

### Python Style

We follow PEP 8 with these tools enforcing our style:

- **Black** - Code formatting (line length: 88)
- **Ruff** - Fast Python linter
- **MyPy** - Static type checking

### Code Style Examples

```python
# Good
from datetime import datetime
from typing import List, Optional

def generate_commits(
    start_date: datetime,
    end_date: datetime,
    max_commits: int = 10
) -> List[str]:
    """Generate commit messages for date range.
    
    Args:
        start_date: Start of date range
        end_date: End of date range
        max_commits: Maximum commits per day
        
    Returns:
        List of commit messages
    """
    commits = []
    # Implementation here
    return commits


# Bad
def generate_commits(start_date,end_date,max_commits=10):
    commits=[]
    # No docstring, poor formatting
    return commits
```

### Documentation Style

- Use Google-style docstrings
- Include type hints
- Write clear, concise comments
- Update README for user-facing changes

### Commit Message Guidelines

```bash
# Good
feat: add support for custom commit messages
fix: handle leap years correctly in date calculation
docs: update README with new configuration options
test: add edge cases for weekend detection

# Bad
added stuff
fix
update
WIP
```

## 🧪 Testing Guidelines

### Test Structure

```python
class TestFeatureName:
    """Test suite for feature name."""
    
    def test_normal_case(self):
        """Test normal expected behavior."""
        # Arrange
        input_data = create_test_data()
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_result
    
    def test_edge_case(self):
        """Test edge cases and boundaries."""
        pass
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            function_under_test(invalid_input)
```

### Testing Checklist

- [ ] Unit tests for new functions
- [ ] Integration tests for workflows
- [ ] Edge case testing
- [ ] Error handling tests
- [ ] Documentation tests (doctest)
- [ ] Performance tests for critical paths

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto
```

## 🚢 Pull Request Process

### Before Submitting

1. **Update Documentation**
   - README.md for user-facing changes
   - Docstrings for API changes
   - CHANGELOG.md for notable changes

2. **Run Quality Checks**
   ```bash
   make check  # Runs all checks
   ```

3. **Update Tests**
   - Add tests for new features
   - Update existing tests if needed
   - Ensure 90%+ coverage

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one maintainer approval
3. **Testing**: Reviewers may test locally
4. **Merge**: Maintainers will merge when ready

### After Your PR is Merged

1. Delete your feature branch
2. Pull the latest main
3. Thank you for contributing! 🎉

## 🌟 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project documentation

## 🤝 Community

### Getting Help

- **Discord**: [Join our server](https://discord.gg/example)
- **Discussions**: Use GitHub Discussions for Q&A
- **Issues**: For bug reports and features

### Resources

- [Development Setup Guide](docs/development.md)
- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)

## 📚 Additional Resources

### Learning Materials

- [Git Basics](https://git-scm.com/book)
- [Python Best Practices](https://docs.python-guide.org/)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)

### Tools We Use

- **pytest**: Testing framework
- **black**: Code formatter
- **ruff**: Linter
- **mypy**: Type checker
- **pre-commit**: Git hooks
- **tox**: Test automation
- **sphinx**: Documentation

## ❓ Questions?

Feel free to:
- Open an issue with the `question` label
- Start a discussion
- Reach out on Discord

Thank you for contributing to GitHub Activity Generator! 🚀