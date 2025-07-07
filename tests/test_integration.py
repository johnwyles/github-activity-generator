"""Integration tests for the complete workflow."""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

import contribute


class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.integration
    def test_full_workflow_no_push(self, temp_dir, mock_git_commands):
        """Test complete workflow without pushing to remote."""
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-03",
            "--max_commits", "2",
            "--frequency", "100"
        ]
        
        # Run main function
        contribute.main(args)
        
        # Verify git init was called
        assert any("init" in str(call) for call in mock_git_commands.call_args_list)
        
        # Verify commits were made (add + commit for each)
        add_calls = [call for call in mock_git_commands.call_args_list if "add" in str(call)]
        commit_calls = [call for call in mock_git_commands.call_args_list if "commit" in str(call)]
        
        # Should have at least 3 days of commits
        assert len(add_calls) >= 3
        assert len(commit_calls) >= 3
        
        # Verify README.md was created
        assert Path("README.md").exists()

    @pytest.mark.integration
    def test_full_workflow_with_push(self, temp_dir, mock_git_commands):
        """Test complete workflow with pushing to remote."""
        repo_url = "git@github.com:test/repo.git"
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-02",
            "--max_commits", "1",
            "--frequency", "100",
            "--repository", repo_url
        ]
        
        # Run main function
        contribute.main(args)
        
        # Verify remote was added
        remote_calls = [call for call in mock_git_commands.call_args_list 
                       if "remote" in str(call) and "add" in str(call)]
        assert len(remote_calls) == 1
        assert repo_url in str(remote_calls[0])
        
        # Verify push was attempted
        push_calls = [call for call in mock_git_commands.call_args_list if "push" in str(call)]
        assert len(push_calls) == 1

    @pytest.mark.integration
    def test_weekend_holiday_filtering_integration(self, temp_dir, mock_git_commands, mock_holidays):
        """Test integration with weekend and holiday filtering."""
        args = [
            "--start_date", "2024-01-01",  # Monday (holiday)
            "--end_date", "2024-01-07",     # Sunday
            "--no_weekends",
            "--no_holidays",
            "--frequency", "100",
            "--max_commits", "1"
        ]
        
        contribute.main(args)
        
        # Count actual commits made
        commit_calls = [call for call in mock_git_commands.call_args_list if "commit" in str(call)]
        
        # Should skip: Jan 1 (holiday), Jan 6-7 (weekend)
        # Should commit: Jan 2-5 (Tue-Fri) = 4 days
        assert len(commit_calls) == 4

    @pytest.mark.integration
    @pytest.mark.requires_git
    def test_real_git_operations(self, temp_dir):
        """Test with real git operations (requires git installed)."""
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Git not available")
        
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-01",
            "--max_commits", "1",
            "--frequency", "100"
        ]
        
        # Run without mocking
        contribute.main(args)
        
        # Verify git repository was created
        assert Path(".git").exists()
        
        # Verify commits were made
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True
        )
        commit_count = int(result.stdout.strip())
        assert commit_count >= 1
        
        # Verify README.md content
        assert Path("README.md").exists()
        with open("README.md", "r") as f:
            content = f.read()
            assert "Contribution: 2024-01-01" in content

    @pytest.mark.integration
    def test_custom_user_config(self, temp_dir, mock_git_commands):
        """Test with custom user configuration."""
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-01",
            "--user_name", "Test User",
            "--user_email", "test@example.com",
            "--max_commits", "1"
        ]
        
        contribute.main(args)
        
        # Verify user config was set
        config_calls = [call for call in mock_git_commands.call_args_list if "config" in str(call)]
        
        user_name_set = any("user.name" in str(call) and "Test User" in str(call) 
                           for call in config_calls)
        user_email_set = any("user.email" in str(call) and "test@example.com" in str(call) 
                            for call in config_calls)
        
        assert user_name_set
        assert user_email_set

    @pytest.mark.integration
    def test_existing_repository_handling(self, temp_dir, mock_git_commands):
        """Test handling of existing repository directory."""
        # Create existing directory with some content
        repo_dir = "repository-test"
        os.mkdir(repo_dir)
        
        with open(os.path.join(repo_dir, "existing.txt"), "w") as f:
            f.write("existing content")
        
        args = [
            "--start_date", "2024-01-01",
            "--end_date", "2024-01-01",
            "--repository", f"git@github.com:test/{repo_dir}.git"
        ]
        
        # Change to parent directory
        os.chdir(temp_dir)
        
        # Run main - should handle existing directory
        contribute.main(args)
        
        # Verify it used the existing directory
        assert os.path.exists(os.path.join(repo_dir, "existing.txt"))
        assert os.path.exists(os.path.join(repo_dir, "README.md"))

    @pytest.mark.integration
    def test_date_validation_integration(self, temp_dir, capsys):
        """Test date validation in integration."""
        # Test invalid date format
        args = ["--start_date", "2024/01/01"]  # Wrong format
        
        with pytest.raises(SystemExit):
            contribute.main(args)
        
        captured = capsys.readouterr()
        assert "Date format is incorrect" in captured.out

    @pytest.mark.integration
    def test_start_after_end_date(self, temp_dir, capsys):
        """Test error when start date is after end date."""
        args = [
            "--start_date", "2024-01-10",
            "--end_date", "2024-01-01"
        ]
        
        with pytest.raises(SystemExit):
            contribute.main(args)
        
        captured = capsys.readouterr()
        assert "Start date cannot be greater than end date" in captured.out

    @pytest.mark.integration
    def test_future_date_warning(self, temp_dir, mock_input, capsys):
        """Test warning for future dates."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        args = [
            "--start_date", future_date,
            "--end_date", future_date
        ]
        
        # User confirms with 'y'
        mock_input.return_value = "y"
        
        # Should not raise SystemExit
        with patch("contribute.run"):  # Mock git operations
            contribute.main(args)
        
        captured = capsys.readouterr()
        assert "Start date is greater than current date" in captured.out
        assert "End date is greater than current date" in captured.out

    @pytest.mark.integration
    def test_unsupported_country(self, temp_dir, capsys):
        """Test error for unsupported country holidays."""
        args = ["--country_holidays", "XX"]  # Invalid country code
        
        with pytest.raises(SystemExit):
            contribute.main(args)
        
        captured = capsys.readouterr()
        assert "Country is not supported" in captured.out

    @pytest.mark.integration
    def test_frequency_out_of_bounds(self, temp_dir, capsys):
        """Test error for frequency out of bounds."""
        # Test frequency > 100
        args = ["--frequency", "150"]
        
        with pytest.raises(SystemExit):
            contribute.main(args)
        
        captured = capsys.readouterr()
        assert "Frequency must be between 0 and 100" in captured.out
        
        # Test frequency < 0
        args = ["--frequency", "-10"]
        
        with pytest.raises(SystemExit):
            contribute.main(args)

    @pytest.mark.integration
    def test_max_commits_out_of_bounds(self, temp_dir, capsys):
        """Test error for max_commits out of bounds."""
        # Test max_commits > 20
        args = ["--max_commits", "25"]
        
        with pytest.raises(SystemExit):
            contribute.main(args)
        
        captured = capsys.readouterr()
        assert "Max commits must be between 1 and 20" in captured.out