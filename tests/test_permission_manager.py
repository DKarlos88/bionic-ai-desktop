"""Tests for the current permission manager behavior."""

from pathlib import Path

from app.agent.permission_manager import PermissionManager


def test_file_access_is_limited_to_configured_directories(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    manager = PermissionManager()
    manager.allowed_paths = [allowed.resolve()]

    assert manager.check_file_access(allowed / "note.txt")
    assert not manager.check_file_access(tmp_path / "outside.txt")


def test_path_prefix_sibling_is_not_allowed(tmp_path):
    allowed = tmp_path / "safe"
    sibling = tmp_path / "safe-other"
    allowed.mkdir()
    sibling.mkdir()
    manager = PermissionManager()
    manager.allowed_paths = [allowed.resolve()]

    assert not manager.check_file_access(sibling / "file.txt")


def test_dangerous_command_substrings_are_blocked():
    manager = PermissionManager()

    assert not manager.check_command_safety("shutdown /s")
    assert not manager.check_command_safety("echo hello && format C:")
    assert manager.check_command_safety("echo hello")
