#!/usr/bin/env python3
"""Test script to demonstrate different behavior patterns."""

import subprocess
import sys

behaviors = {
    "consistent": "Regular random pattern (original behavior)",
    "regular": "9-to-5 developer with vacations and sick days",
    "intense": "Startup mode - intense bursts with recovery",
    "hobbyist": "Weekend and evening commits, more in winter",
    "opensource": "Steady contributor, more active in October",
    "irregular": "Freelancer with project-based gaps"
}

def test_behavior(behavior, days=30):
    """Test a behavior pattern."""
    print(f"\n{'='*60}")
    print(f"Testing {behavior.upper()} behavior")
    print(f"{behaviors[behavior]}")
    print(f"{'='*60}")
    
    cmd = [
        "./generate.py",
        "--behavior", behavior,
        "--dry-run",
        "--start-date", "2024-01-01",
        "--end-date", "2024-01-30",
        "--max-commits", "20"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract key statistics from output
    for line in result.stdout.split('\n'):
        if "Total Commits" in line or "Days with Commits" in line:
            print(line.strip())
            
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")

if __name__ == "__main__":
    print("GitHub Activity Generator - Behavior Pattern Demo")
    print("This shows how different behaviors create different commit patterns\n")
    
    for behavior in behaviors:
        test_behavior(behavior)
    
    print("\n" + "="*60)
    print("Summary:")
    print("- CONSISTENT: Random distribution based on frequency")
    print("- REGULAR: Weekdays only with vacation/sick days")  
    print("- INTENSE: High activity bursts (startup mode)")
    print("- HOBBYIST: Mostly weekends and evenings")
    print("- OPENSOURCE: Moderate steady, spike in October")
    print("- IRREGULAR: Project-based with gaps")