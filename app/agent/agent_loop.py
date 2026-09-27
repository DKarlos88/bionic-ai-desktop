"""Agent loop for autonomous AI execution with tool support."""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from app.agent.permission_manager import PermissionLevel, PermissionManager
from app.agent.tool_registry import ToolRegistry
from app.ollama_client import OllamaClient
from app.storage.database import Database

logger = logging.getLogger(__name__)


class AgentLoop:
    """Main agent loop for handling tool requests and user interactions."""

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
        self.session_approvals = set()

    def get_tools_description(self) -> str:
        """Get formatted description of available tools for the AI."""
        tools = self.registry.list_tools()
        description = "Available tools:\n\n"

        for tool in tools:
            params_str = ", ".join(tool.parameters.keys()) if tool.parameters else "none"
            description += f"- {tool.name}({params_str}): {tool.description}\n"

        description += (
            "\nCRITICAL INSTRUCTIONS:\n"
            "1. If the user asks for a file or system action, decide if a tool is needed.\n"
            "2. If a tool is needed, return EXACTLY one tool call in this format:\n"
            "   [TOOL]create_folder {\"folder_path\": \"C:\\\\Users\\\\test\\\\MyFolder\"}\n"
            "3. Do not add markdown, explanations, or extra words before or after the tool call.\n"
            "4. If no tool is needed, reply normally in natural language.\n"
            "5. Only use one tool at a time."
        )
        return description

    def build_system_prompt(self, user_prompt: str) -> str:
        """Build a stronger system prompt for tool-driven actions."""
        return (
            "You are Bionic AI Desktop, a desktop assistant that uses tools when needed.\n\n"
            "Use tools only when the user asks for a filesystem, system, or command action.\n"
            "When a tool is needed, respond with exactly this format and nothing else:\n"
            "[TOOL]tool_name {\"param_name\": \"value\"}\n\n"
            "Examples:\n"
            "[TOOL]create_folder {\"folder_path\": \"C:\\\\Users\\\\test\\\\Proyecto\"}\n"
            "[TOOL]read_file {\"file_path\": \"C:\\\\Users\\\\test\\\\notes.txt\"}\n"
            "[TOOL]list_files {\"directory\": \"C:\\\\Users\\\\test\\\\Desktop\"}\n"
            "\n"
            "Never use markdown, never explain the tool call, and never add extra text around it.\n"
            "If the user request does not require a tool, answer normally.\n\n"
            f"User request: {user_prompt}\n\n"
            f"{self.get_tools_description()}"
        )

    def _resolve_directory(self, text: str) -> str:
        """Resolve standard desktop folders from a natural-language sentence."""
        lower = text.lower()
        if "document" in lower or "documents" in lower:
            return str(Path.home() / "Documents")
        if "download" in lower:
            return str(Path.home() / "Downloads")
        if "picture" in lower or "images" in lower:
            return str(Path.home() / "Pictures")
        # Handle both English and Spanish for Desktop
        if "desktop" in lower or "escritorio" in lower:
            return str(Path.home() / "Desktop")
        return str(Path.home() / "Desktop")

    def _extract_folder_name(self, prompt: str) -> str:
        """Extract a folder name from a natural-language prompt."""
        patterns = [
            r"(?:carpeta|folder|directorio)\s+(?:llamada|called|named)?\s*['\"]?([A-Za-z0-9_ .-]+)['\"]?",
            r"(?:crear|create)\s+(?:la\s+)?(?:carpeta|folder)\s+(?:llamada|called|named)?\s*['\"]?([A-Za-z0-9_ .-]+)['\"]?",
            r"(?:llamada|called|named)\s*['\"]?([A-Za-z0-9_ .-]+)['\"]?",
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Proyecto"

    def _extract_file_path(self, prompt: str) -> str:
        """Extract a file path from a natural-language prompt if mentioned."""
        patterns = [
            r"['\"]([^'\"]+\.[A-Za-z0-9]+)['\"]",
            r"([A-Za-z]:\\[^\s]+|~?/[^\s]+\.[A-Za-z0-9]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                value = match.group(1) if match.group(1) else match.group(2)
                if value:
                    return value
        return str(Path.home() / "Desktop" / "nota.txt")

    def infer_tool_request(self, prompt: str) -> Optional[tuple[str, dict]]:
        """Infer a tool call when the user gives a natural-language action."""
        p = prompt.lower()

        if any(k in p for k in [
            "crear carpeta", "create folder", "create a folder",
            "carpeta llamada", "folder called", "folder named",
            "crear una carpeta", "make a folder"
        ]):
            folder_name = self._extract_folder_name(prompt)
            return "create_folder", {"folder_path": str(Path(self._resolve_directory(prompt)) / folder_name)}

        if any(k in p for k in [
            "listar archivos", "list files", "lista de archivos",
            "ver archivos", "show files", "muestra los archivos"
        ]):
            return "list_files", {"directory": self._resolve_directory(prompt)}

        if any(k in p for k in [
            "leer archivo", "read file", "abre el archivo", "open file",
            "muestra el contenido"
        ]):
            return "read_file", {"file_path": self._extract_file_path(prompt)}

        if any(k in p for k in [
            "escribir archivo", "write file", "guardar archivo",
            "save file", "crear archivo"
        ]):
            base_dir = self._resolve_directory(prompt)
            file_name = "nuevo_archivo.txt"
            match = re.search(r"([A-Za-z0-9_ .-]+\.[A-Za-z0-9]+)", prompt)
            if match:
                file_name = match.group(1)
            return "write_file", {"file_path": str(Path(base_dir) / file_name), "content": ""}

        return None

    def parse_tool_request(self, response: str) -> Optional[tuple[str, dict]]:
        """Parse a tool request from an AI response."""
        text = response.strip()

        pattern = r"\[TOOL\]\s*([a-zA-Z_]+)\s*(\{.*?\})\s*$"
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            fallback = re.search(r"\[TOOL\]\s*([a-zA-Z_]+)\s*(\{.*?\})", text, re.DOTALL)
            if not fallback:
                return None
            match = fallback

        tool_name = match.group(1)
        try:
            params = json.loads(match.group(2))
            if not isinstance(params, dict):
                return None
            return tool_name, params
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool parameters: {e}")
            return None

    def process_response(self, response: str) -> Optional[tuple[str, dict]]:
        """Check if response contains a tool request."""
        tool_request = self.parse_tool_request(response)
        if tool_request:
            return tool_request
        return self.infer_tool_request(response)

    def should_request_approval(
        self, tool_name: str, permission_level: PermissionLevel
    ) -> bool:
        """Check if tool needs approval for this request."""
        if tool_name in self.session_approvals:
            return False
        if permission_level == PermissionLevel.HIGH:
            return True
        return True

    def execute_tool(self, tool_name: str, parameters: dict) -> tuple[bool, str]:
        """Execute a tool with safety checks."""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return False, f"Tool not found: {tool_name}"

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
        """Generate response with tool support."""
        system_prompt = self.build_system_prompt(prompt)

        try:
            response = self.client.generate(model, system_prompt)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error: {str(e)}"

        tool_request = self.process_response(response)
        if not tool_request:
            return response

        tool_name, parameters = tool_request
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return f"{response}\n\n(Tool {tool_name} not found)"

        if not self.should_request_approval(tool_name, tool.permission_level):
            success, result = self.execute_tool(tool_name, parameters)
            if success:
                follow_up_prompt = (
                    f"The tool {tool_name} was executed successfully. "
                    f"Result: {result}\n\nPlease provide a helpful response to the user."
                )
                return self.client.generate(model, follow_up_prompt)
            return result

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
                    return self.client.generate(model, follow_up_prompt)
                return result

            return f"{response}\n\n(Tool execution was denied by user)"

        return f"{response}\n\n(Tool execution requires approval: {tool_name})"
