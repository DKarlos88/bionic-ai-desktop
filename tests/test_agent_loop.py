# test_agent_loop.py

from pathlib import Path

from app.agent.agent_loop import AgentLoop
from app.agent.tool_registry import ToolRegistry
from app.storage.database import Database


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


def test_parse_tool_request_handles_bracket_format():
    agent = _make_agent()
    parsed = agent.parse_tool_request('[TOOL]read_file {"file_path": "/tmp/demo.txt"}')
    assert parsed == ("read_file", {"file_path": "/tmp/demo.txt"})


def test_validate_tool_request_rejects_unknown_tool():
    agent = _make_agent()
    valid, message = agent.validate_tool_request("unknown_tool", {})
    assert valid is False
    assert "Tool not found" in message

