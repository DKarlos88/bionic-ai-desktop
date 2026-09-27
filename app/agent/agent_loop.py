"""Agent loop for autonomous AI execution with tool support"""

import logging
import json
import re
from typing import Optional
from app.agent.tool_registry import ToolRegistry
from app.agent.permission_manager import PermissionManager, PermissionLevel
from app.ollama_client import OllamaClient
from app.storage.database import Database

logger = logging.getLogger(__name__)


class AgentLoop:
    """Main agent loop for handling tool requests and user interactions"""

    def __init__(
        self,
        client: OllamaClient,
        registry: ToolRegistry,
        db: Database,
        permission_manager: Optional[PermissionManager] = None,
    ):
        self.client = client
        self.registry = registry
        self.db = db
        self.permission_manager = permission_manager or PermissionManager()
        self.session_approvals = set()  # Tools approved for this session

    def get_tools_description(self) -> str:
        """Get formatted description of available tools for the AI"""
        tools = self.registry.list_tools()
        description = "Available tools:\n\n"

        for tool in tools:
            params_str = ", ".join(tool.parameters.keys()) if tool.parameters else "none"
            description += f"- {tool.name}({params_str}): {tool.description}\n"

        description += (
            "\nTo use a tool, include [TOOL] in your response followed by "
            "the tool name and parameters in JSON format. Example: "
            '[TOOL]create_folder {"folder_path": "C:\\\\Users\\\\test\\\\MyFolder"}'
        )
        return description

    def parse_tool_request(self, response: str) -> Optional[tuple[str, dict]]:
        """Parse tool request from AI response"""
        # Look for [TOOL] pattern
        pattern = r"\[TOOL\]([a-zA-Z_]+)\s*({.*?})"
        match = re.search(pattern, response, re.DOTALL)

        if not match:
            return None

        tool_name = match.group(1)
        try:
            params = json.loads(match.group(2))
            return tool_name, params
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool parameters: {e}")
            return None

    def process_response(self, response: str) -> Optional[tuple[str, dict]]:
        """Check if response contains a tool request"""
        return self.parse_tool_request(response)

    def should_request_approval(
        self, tool_name: str, permission_level: PermissionLevel
    ) -> bool:
        """Check if tool needs approval for this request"""
        # Always approve if in session approvals
        if tool_name in self.session_approvals:
            return False

        # Always request approval for HIGH risk
        if permission_level == PermissionLevel.HIGH:
            return True

        # Request approval for MEDIUM and LOW (can be approved for session)
        return True

    def execute_tool(
        self, tool_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """Execute a tool with safety checks"""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return False, f"Tool not found: {tool_name}"

        # Validate parameters
        try:
            result = tool.func(**parameters)
            self.db.log_action(
                action="tool_executed",
                tool_name=tool_name,
                command=str(parameters),
                approved=True,
                result=str(result)[:500],
            )
            return True, str(result)
        except Exception as e:
            error_msg = str(e)
            self.db.log_action(
                action="tool_failed",
                tool_name=tool_name,
                command=str(parameters),
                approved=True,
                result=f"Error: {error_msg}",
            )
            logger.error(f"Tool execution failed: {e}")
            return False, f"Error executing {tool_name}: {error_msg}"

    def generate_with_tools(
        self, model: str, prompt: str, approval_callback=None
    ) -> str:
        """Generate response with tool support"""
        # Add tools description to system context
        system_prompt = f"{prompt}\n\n{self.get_tools_description()}"

        # Get initial response
        try:
            response = self.client.generate(model, system_prompt)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error: {str(e)}"

        # Check if response contains a tool request
        tool_request = self.process_response(response)
        if not tool_request:
            return response

        tool_name, parameters = tool_request
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return f"{response}\n\n(Tool {tool_name} not found)"

        # Check if approval is needed
        if not self.should_request_approval(tool_name, tool.permission_level):
            # Auto-execute if already approved for session
            success, result = self.execute_tool(tool_name, parameters)
            if success:
                # Get follow-up response from AI
                follow_up_prompt = (
                    f"The tool {tool_name} was executed successfully. "
                    f"Result: {result}\n\nPlease provide a helpful response to the user."
                )
                follow_up_response = self.client.generate(model, follow_up_prompt)
                return follow_up_response
            else:
                return result
        else:
            # Request approval
            if approval_callback:
                approved, approved_for_session = approval_callback(
                    tool_name, tool.description, tool.permission_level, parameters
                )

                if approved:
                    if approved_for_session:
                        self.session_approvals.add(tool_name)

                    success, result = self.execute_tool(tool_name, parameters)
                    if success:
                        follow_up_prompt = (
                            f"The tool {tool_name} was executed successfully. "
                            f"Result: {result}\n\nPlease provide a helpful response to the user."
                        )
                        follow_up_response = self.client.generate(
                            model, follow_up_prompt
                        )
                        return follow_up_response
                    else:
                        return result
                else:
                    return f"{response}\n\n(Tool execution was denied by user)"
            else:
                return f"{response}\n\n(Tool execution requires approval: {tool_name})"

        return response
