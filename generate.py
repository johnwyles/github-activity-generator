#!/usr/bin/env python3
"""🎮 GitHub Activity Generator - Let's make some commits!

This is the main entry point for generating GitHub activity.
Run with --help to see all options, or just run it to generate a year of commits!
"""

import sys

# Import the magic ✨
from src.github_activity_generator.cli import main

if __name__ == "__main__":
    # Let's go! 🚀
    sys.exit(main())