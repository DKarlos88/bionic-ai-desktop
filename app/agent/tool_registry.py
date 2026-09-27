"""Tool registry and management"""

import logging
from typing import Callable, Any
from dataclasses import dataclass
from app.agent.permission_manager import PermissionLevel

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """Tool definition"""

    name: str
    description: str
    func: Callable
    permission_level: PermissionLevel
    parameters: dict[str, str]


class ToolRegistry:
    """Registry of available tools"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        func: Callable,
        permission_level: PermissionLevel,
        parameters: dict[str, str] = None,
    ):
        """Register a new tool"""
        if parameters is None:
            parameters = {}
        self.tools[name] = Tool(
            name=name,
            description=description,
            func=func,
            permission_level=permission_level,
            parameters=parameters,
        )
        logger.info(f"Tool registered: {name}")

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all available tools"""
        return list(self.tools.values())

    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return tool.func(**kwargs)
