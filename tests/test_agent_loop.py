"""Tests for the current agent tool-call parser."""

from app.agent.agent_loop import AgentLoop
from app.agent.tool_registry import ToolRegistry


def _make_agent():
    return AgentLoop(client=None, registry=ToolRegistry(), db=None)


def test_parse_tool_request_json_format():
    agent = _make_agent()

    assert agent.parse_tool_request(
        '[TOOL]read_file {"file_path": "notes.txt"}'
    ) == ("read_file", {"file_path": "notes.txt"})


def test_parse_tool_request_rejects_malformed_json():
    agent = _make_agent()

    assert agent.parse_tool_request('[TOOL]read_file {"file_path": }') is None


def test_parse_tool_request_empty_response():
    agent = _make_agent()

    assert agent.parse_tool_request("") is None
