"""Tests for permission manager and agent parsing."""

from pathlib import Path

from app.agent.agent_loop import AgentLoop
from app.agent.permission_manager import PermissionManager
from app.storage.database import Database
from app.agent.tool_registry import ToolRegistry


def _make_agent() -> AgentLoop:
    registry = ToolRegistry()
    registry.register(
        "read_file",
        "Read file",
        lambda file_path: str(file_path),
        None,
        {"file_path": "path"},
    )
    registry.register(
        "create_folder",
        "Create folder",
        lambda folder_path: str(folder_path),
        None,
        {"folder_path": "path"},
    )
    return AgentLoop(client=None, registry=registry, db=Database(Path("/tmp/test-bionic.db")))


def test_permission_manager_allows_desktop_paths():
    manager = PermissionManager()
    desktop_path = Path.home() / "Desktop"
    desktop_path.mkdir(exist_ok=True)
    assert manager.check_file_access(desktop_path / "demo.txt") is True


def test_permission_manager_rejects_outside_paths():
    manager = PermissionManager()
    assert manager.check_file_access(Path("/etc/passwd")) is False


def test_permission_manager_rejects_dangerous_command():
    manager = PermissionManager()
    assert manager.check_command_safety("ping 127.0.0.1 && del /s /q C:/temp") is False
    assert manager.check_command_safety("echo hello") is True


def test_agent_parse_tool_request():
    agent = _make_agent()
    parsed = agent.parse_tool_request('[TOOL]read_file {"file_path": "/tmp/demo.txt"}')
    assert parsed is not None
    assert parsed[0] == "read_file"
    assert parsed[1]["file_path"] == "/tmp/demo.txt"


def test_agent_validate_tool_request_rejects_forbidden_path():
    agent = _make_agent()
    valid, message = agent.validate_tool_request("read_file", {"file_path": "/etc/passwd"})
    assert valid is False
    assert "Access denied" in message


"""Tests for permission manager and agent parsing."""

from pathlib import Path

from app.agent.agent_loop import AgentLoop
from app.agent.permission_manager import PermissionManager
from app.storage.database import Database
from app.agent.tool_registry import ToolRegistry


def _make_agent() -> AgentLoop:
    registry = ToolRegistry()
    registry.register(
        "read_file",
        "Read file",
        lambda file_path: str(file_path),
        None,
        {"file_path": "path"},
    )
    registry.register(
        "create_folder",
        "Create folder",
        lambda folder_path: str(folder_path),
        None,
        {"folder_path": "path"},
    )
    return AgentLoop(client=None, registry=registry, db=Database(Path("/tmp/test-bionic.db")))


def test_permission_manager_allows_desktop_paths():
    manager = PermissionManager()
    desktop_path = Path.home() / "Desktop"
    desktop_path.mkdir(exist_ok=True)
    assert manager.check_file_access(desktop_path / "demo.txt") is True


def test_permission_manager_rejects_outside_paths():
    manager = PermissionManager()
    assert manager.check_file_access(Path("/etc/passwd")) is False


def test_permission_manager_rejects_dangerous_command():
    manager = PermissionManager()
    assert manager.check_command_safety("ping 127.0.0.1 && del /s /q C:/temp") is False
    assert manager.check_command_safety("echo hello") is True


def test_agent_parse_tool_request():
    agent = _make_agent()
    parsed = agent.parse_tool_request('[TOOL]read_file {"file_path": "/tmp/demo.txt"}')
    assert parsed is not None
    assert parsed[0] == "read_file"
    assert parsed[1]["file_path"] == "/tmp/demo.txt"


def test_agent_validate_tool_request_rejects_forbidden_path():
    agent = _make_agent()
    valid, message = agent.validate_tool_request("read_file", {"file_path": "/etc/passwd"})
    assert valid is False
    assert "Access denied" in message

