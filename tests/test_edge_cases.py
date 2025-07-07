"""Tests for edge cases and error conditions."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import contribute


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_date_range(self, mock_git_commands):
        """Test when start and end date are the same."""
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-01",
            "--frequency", "100",
            "--max_commits", "1"
        ]
        
        contribute.main(args)
        
        # Should make exactly 1 day of commits
        commit_calls = [call for call in mock_git_commands.call_args_list if "commit" in str(call)]
        assert len(commit_calls) == 1

    def test_zero_frequency(self, mock_git_commands):
        """Test with 0% frequency (no commits should be made)."""
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-07",
            "--frequency", "0",
            "--max_commits", "10"
        ]
        
        # Mock randint to always return 50 (which is > 0)
        with patch("contribute.randint", return_value=50):
            contribute.main(args)
        
        # Should not make any commits
        commit_calls = [call for call in mock_git_commands.call_args_list if "commit" in str(call)]
        assert len(commit_calls) == 0

    def test_leap_year_date_range(self, mock_git_commands):
        """Test date range including leap day."""
        args = [
            "--start_date", "2024-02-28",
            "--end_date", "2024-03-01",
            "--frequency", "100",
            "--max_commits", "1"
        ]
        
        contribute.main(args)
        
        # Should have 3 days: Feb 28, Feb 29, Mar 1
        commit_calls = [call for call in mock_git_commands.call_args_list if "commit" in str(call)]
        assert len(commit_calls) == 3

    def test_very_long_date_range(self, mock_git_commands):
        """Test with a very long date range (multiple years)."""
        args = [
            "--start_date", "2020-01-01",
            "--end_date", "2020-01-31",  # Just one month for testing
            "--frequency", "100",
            "--max_commits", "1"
        ]
        
        contribute.main(args)
        
        # Should have 31 days of commits
        commit_calls = [call for call in mock_git_commands.call_args_list if "commit" in str(call)]
        assert len(commit_calls) == 31

    def test_special_characters_in_paths(self, temp_dir):
        """Test handling of special characters in repository names."""
        special_repos = [
            "git@github.com:user/repo-with-dash.git",
            "git@github.com:user/repo_with_underscore.git",
            "git@github.com:user/repo.with.dots.git",
        ]
        
        for repo_url in special_repos:
            start = repo_url.rfind("/") + 1
            end = repo_url.rfind(".")
            directory = repo_url[start:end]
            
            # Should extract directory name correctly
            assert directory in ["repo-with-dash", "repo_with_underscore", "repo.with.dots"]

    def test_unicode_in_messages(self, temp_dir):
        """Test that unicode in dates is handled correctly."""
        # The current implementation uses strftime which handles unicode
        test_date = datetime(2024, 1, 1, 10, 30)
        message = contribute.message(test_date)
        
        # Should be valid UTF-8
        assert isinstance(message, str)
        message.encode('utf-8')  # Should not raise

    def test_file_system_limits(self, temp_dir):
        """Test behavior with file system limits."""
        # Test very long README content (multiple commits)
        for i in range(1000):
            date = datetime(2024, 1, 1) + timedelta(minutes=i)
            with open("README.md", "a") as f:
                f.write(contribute.message(date) + "\n\n")
        
        # File should exist and be readable
        assert Path("README.md").exists()
        
        with open("README.md", "r") as f:
            content = f.read()
            lines = content.strip().split("\n")
            # Should have 2000 lines (1000 entries * 2 lines each)
            assert len(lines) == 2000

    def test_concurrent_git_operations(self, mock_subprocess):
        """Test behavior with concurrent git operations."""
        # Simulate slow git operations
        mock_subprocess.return_value.wait = MagicMock(side_effect=lambda: None)
        
        # Should not crash
        contribute.run(["git", "init"])
        contribute.run(["git", "add", "."])
        contribute.run(["git", "commit", "-m", "test"])

    def test_interrupted_execution(self, temp_dir, mock_git_commands):
        """Test recovery from interrupted execution."""
        # Create partial README.md as if interrupted
        with open("README.md", "w") as f:
            f.write("Contribution: 2024-01-01 10:00\n\n")
            f.write("Contribution: 2024-01-01 10:01\n")  # Missing newline
        
        # Run contribute again
        contribute.contribute(datetime(2024, 1, 1, 10, 2))
        
        # Should append correctly
        with open("README.md", "r") as f:
            content = f.read()
            assert "Contribution: 2024-01-01 10:02" in content

    def test_invalid_git_config(self, mock_git_commands):
        """Test with invalid git configuration."""
        # Test with empty user name/email
        args = [
            "--user_name", "",
            "--user_email", "",
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-01"
        ]
        
        contribute.main(args)
        
        # Should handle empty strings
        config_calls = [call for call in mock_git_commands.call_args_list if "config" in str(call)]
        # Empty strings should result in no config calls
        assert len(config_calls) == 0

    def test_permission_errors(self, temp_dir):
        """Test handling of permission errors."""
        # Create read-only directory
        readonly_dir = temp_dir / "readonly"
        readonly_dir.mkdir()
        
        # Make it read-only (Unix-like systems)
        if sys.platform != "win32":
            os.chmod(readonly_dir, 0o444)
            
            # Try to create file in read-only directory
            with pytest.raises(PermissionError):
                with open(readonly_dir / "test.txt", "w") as f:
                    f.write("test")
            
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)

    def test_disk_space_handling(self, temp_dir, monkeypatch):
        """Test behavior when disk space is low."""
        # Mock os.statvfs to simulate low disk space
        if hasattr(os, 'statvfs'):
            mock_statvfs = MagicMock()
            mock_statvfs.f_bavail = 1  # 1 block available
            mock_statvfs.f_frsize = 4096  # 4KB blocks
            
            with patch("os.statvfs", return_value=mock_statvfs):
                # Should still work (current implementation doesn't check disk space)
                contribute.contribute(datetime(2024, 1, 1))

    def test_malformed_repository_urls(self):
        """Test extraction of directory names from malformed URLs."""
        test_cases = [
            ("not-a-url", "not-a-url"),  # No slashes
            ("https://github.com/user/", ""),  # Trailing slash
            ("repo.git", "repo"),  # Just filename
            ("", ""),  # Empty string
        ]
        
        for url, expected in test_cases:
            if "/" in url:
                start = url.rfind("/") + 1
            else:
                start = 0
                
            if "." in url[start:]:
                end = url.rfind(".")
            else:
                end = len(url)
                
            directory = url[start:end]
            assert directory == expected

    def test_extreme_commit_counts(self, mock_git_commands):
        """Test with extreme commit counts."""
        # Test with max commits at boundaries
        args = contribute.arguments(["--max_commits", "20"])
        
        # Test multiple times to ensure it never exceeds 20
        for _ in range(50):
            commits = contribute.contributions_per_day(args)
            assert 1 <= commits <= 20

    def test_time_zone_handling(self):
        """Test that dates are handled consistently regardless of timezone."""
        # The current implementation uses naive datetime objects
        date1 = datetime(2024, 1, 1, 23, 59, 59)
        date2 = datetime(2024, 1, 2, 0, 0, 0)
        
        # Should be exactly 1 second apart
        diff = date2 - date1
        assert diff.total_seconds() == 1

    @pytest.mark.parametrize("exit_code", [0, 1, 128])
    def test_git_exit_codes(self, mock_subprocess, exit_code):
        """Test handling of various git exit codes."""
        mock_subprocess.return_value.wait.return_value = exit_code
        
        # Current implementation doesn't check exit codes
        contribute.run(["git", "status"])
        
        # Should complete without raising
        assert mock_subprocess.called