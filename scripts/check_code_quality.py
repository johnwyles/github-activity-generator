#!/usr/bin/env python3
"""Run all code quality checks for GitHub Activity Generator."""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output.
    
    Args:
        cmd: Command to run
        description: Description of what's being checked
        
    Returns:
        Tuple of (success, output)
    """
    print(f"\n{BLUE}▶ {description}{RESET}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"{GREEN}✓ {description} passed{RESET}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{RED}✗ {description} failed{RESET}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False, e.stdout + e.stderr


def main():
    """Run all code quality checks."""
    print(f"{BOLD}Running Code Quality Checks{RESET}")
    print("=" * 50)
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Change to project root
    import os
    os.chdir(project_root)
    
    # Track overall success
    all_passed = True
    
    # Define checks to run
    checks = [
        # Formatting
        (["black", "--check", "src", "tests"], "Black formatting"),
        (["isort", "--check-only", "src", "tests"], "Import sorting"),
        
        # Linting
        (["ruff", "check", "src", "tests"], "Ruff linting"),
        (["flake8", "src", "tests"], "Flake8 linting"),
        
        # Type checking
        (["mypy", "src", "tests"], "Type checking"),
        
        # Security
        (["bandit", "-r", "src", "-f", "json", "-o", "/dev/null"], "Security scan"),
        
        # Tests
        (["pytest", "tests", "--tb=short"], "Unit tests"),
        (["pytest", "--cov=src", "--cov-report=term-missing:skip-covered", "--cov-fail-under=90"], "Test coverage"),
    ]
    
    # Optional checks (don't fail if tool not installed)
    optional_checks = [
        (["pylint", "src"], "Pylint analysis"),
        (["safety", "check", "--json"], "Dependency vulnerabilities"),
    ]
    
    # Run required checks
    for cmd, description in checks:
        success, output = run_command(cmd, description)
        if not success:
            all_passed = False
    
    # Run optional checks
    print(f"\n{YELLOW}Optional Checks:{RESET}")
    for cmd, description in optional_checks:
        try:
            success, output = run_command(cmd, description)
        except FileNotFoundError:
            print(f"{YELLOW}⚠ {description} skipped (tool not installed){RESET}")
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print(f"{GREEN}{BOLD}✓ All required checks passed!{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some checks failed!{RESET}")
        print(f"\n{YELLOW}Fix the issues and run again:{RESET}")
        print(f"  python {__file__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())