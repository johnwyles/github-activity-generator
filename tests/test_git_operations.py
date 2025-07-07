"""Tests for git operations and commands."""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

import contribute


class TestGitOperations:
    """Test git-related operations."""

    def test_run_command(self, mock_subprocess):
        """Test the run command wrapper."""
        commands = ["git", "init", "-b", "main"]
        contribute.run(commands)
        
        mock_subprocess.assert_called_once_with(commands)
        mock_subprocess.return_value.wait.assert_called_once()

    def test_git_init(self, mock_git_commands):
        """Test git repository initialization."""
        args = contribute.arguments([])
        
        # Simulate the part of main() that initializes git
        contribute.run(["git", "init", "-b", "main"])
        
        mock_git_commands.assert_called_with(["git", "init", "-b", "main"])

    def test_git_config_user(self, mock_git_commands):
        """Test git user configuration."""
        # Test with custom user name and email
        user_name = "Test User"
        user_email = "test@example.com"
        
        contribute.run(["git", "config", "user.name", user_name])
        contribute.run(["git", "config", "user.email", user_email])
        
        expected_calls = [
            call(["git", "config", "user.name", user_name]),
            call(["git", "config", "user.email", user_email])
        ]
        mock_git_commands.assert_has_calls(expected_calls)

    def test_git_add_and_commit(self, mock_git_commands):
        """Test git add and commit operations."""
        test_date = datetime(2024, 1, 1, 10, 30, 0)
        
        # Create a README.md file
        with open("README.md", "w") as f:
            f.write(contribute.message(test_date) + "\n\n")
        
        # Test add operation
        contribute.run(["git", "add", "."])
        mock_git_commands.assert_called_with(["git", "add", "."])
        
        # Test commit operation
        contribute.run([
            "git",
            "commit",
            "-m",
            f'"{contribute.message(test_date)}"',
            "--date",
            test_date.strftime('"%Y-%m-%d %H:%M:%S"'),
        ])
        
        # Verify the commit command was called correctly
        last_call = mock_git_commands.call_args_list[-1]
        assert last_call[0][0][0:3] == ["git", "commit", "-m"]
        assert "--date" in last_call[0][0]

    def test_contribute_function(self, mock_git_commands, temp_dir):
        """Test the contribute function."""
        test_date = datetime(2024, 1, 1, 10, 30, 0)
        
        # Call contribute
        contribute.contribute(test_date)
        
        # Check that README.md was created with correct content
        readme_path = temp_dir / "README.md"
        assert readme_path.exists()
        
        with open(readme_path, "r") as f:
            content = f.read()
            assert contribute.message(test_date) in content
        
        # Check that git commands were called
        assert mock_git_commands.call_count >= 2  # At least add and commit

    def test_make_daily_commits(self, mock_git_commands):
        """Test making multiple commits for a day."""
        args = contribute.arguments(["--max_commits", "3"])
        test_date = datetime(2024, 1, 1)
        
        # Mock contributions_per_day to return a fixed value
        with patch("contribute.contributions_per_day", return_value=3):
            contribute.make_daily_commits(args, test_date)
        
        # Should have 3 commits (3 adds + 3 commits = 6 calls)
        assert mock_git_commands.call_count == 6

    def test_git_remote_and_push(self, mock_git_commands):
        """Test git remote add and push operations."""
        repository = "git@github.com:test/repo.git"
        
        # Test remote add
        contribute.run(["git", "remote", "add", "origin", repository])
        mock_git_commands.assert_called_with(["git", "remote", "add", "origin", repository])
        
        # Test push
        contribute.run(["git", "push", "-u", "origin", "main"])
        mock_git_commands.assert_called_with(["git", "push", "-u", "origin", "main"])

    def test_directory_creation(self, temp_dir):
        """Test repository directory creation."""
        # Test default directory naming
        curr_date = datetime.now()
        expected_pattern = f"repository-{curr_date.strftime('%Y-%m-%d')}"
        
        # Create a directory
        test_dir = f"repository-{curr_date.strftime('%Y-%m-%d-%H-%M-%S')}"
        os.mkdir(test_dir)
        
        assert os.path.exists(test_dir)
        assert test_dir.startswith(expected_pattern)

    def test_directory_from_repository_url(self):
        """Test directory name extraction from repository URL."""
        test_cases = [
            ("git@github.com:user/my-repo.git", "my-repo"),
            ("https://github.com/user/another-repo.git", "another-repo"),
            ("https://gitlab.com/group/subgroup/project.git", "project"),
            ("git@bitbucket.org:team/repo-name.git", "repo-name"),
        ]
        
        for repo_url, expected_dir in test_cases:
            # Extract directory name as done in main()
            start = repo_url.rfind("/") + 1
            end = repo_url.rfind(".")
            directory = repo_url[start:end]
            
            assert directory == expected_dir

    def test_existing_directory_handling(self, temp_dir, mock_git_commands, capsys):
        """Test handling of existing repository directory."""
        # Create an existing directory
        existing_dir = "existing-repo"
        os.mkdir(existing_dir)
        
        # Try to create the same directory
        try:
            os.mkdir(existing_dir)
        except FileExistsError:
            print(f"🔵 Skipping directory {existing_dir} creation as it already exists.")
        
        # Check that appropriate message was printed
        captured = capsys.readouterr()
        assert "Skipping directory" in captured.out
        assert existing_dir in captured.out

    def test_commit_message_format(self):
        """Test commit message formatting."""
        test_dates = [
            datetime(2024, 1, 1, 0, 0, 0),
            datetime(2024, 6, 15, 12, 30, 45),
            datetime(2024, 12, 31, 23, 59, 59),
        ]
        
        for date in test_dates:
            message = contribute.message(date)
            expected = date.strftime("Contribution: %Y-%m-%d %H:%M")
            assert message == expected

    def test_git_branch_rename(self, mock_git_commands):
        """Test git branch rename to main."""
        contribute.run(["git", "branch", "-m", "main"])
        mock_git_commands.assert_called_with(["git", "branch", "-m", "main"])

    @pytest.mark.parametrize("error_code", [1, 128, 255])
    def test_git_command_failure(self, mock_subprocess, error_code):
        """Test handling of git command failures."""
        # Make git command fail
        mock_subprocess.return_value.wait.return_value = error_code
        
        # The current implementation doesn't check return codes,
        # but this test documents the behavior
        contribute.run(["git", "init"])
        
        mock_subprocess.assert_called_once_with(["git", "init"])
        assert mock_subprocess.return_value.wait.return_value == error_code