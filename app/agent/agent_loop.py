"""Agent loop for autonomous AI execution with tool support."""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from app.agent.permission_manager import PermissionLevel, PermissionManager
from app.agent.tool_registry import ToolRegistry
from app.config import get_desktop_path
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

    def grant_session_approval(self, tool_name: str) -> None:
        """Persist a tool approval for the current session."""
        self.session_approvals.add(tool_name)
        logger.info("Session approval granted for tool: %s", tool_name)

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
            "2. If a tool is needed, return EXACTLY one tool call in this format.\n"
            "3. Never copy example paths such as C:\\\\Users\\\\test. Use the user's real path.\n"
            "4. Do not add markdown, explanations, or extra words around the tool call.\n"
            "5. If no tool is needed, reply normally in natural language.\n"
            "6. Only use one tool at a time.\n"
            "7. Use only this format: [TOOL]tool_name {\"param_name\": \"value\"}\n"
            "8. Do not add a second sentence, explanation text, or JSON outside the tool block.\n"
        )
        return description

    def build_system_prompt(self, user_prompt: str) -> str:
        """Build a system prompt for tool-driven actions."""
        desktop = str(get_desktop_path())
        return (
            "You are Bionic AI Desktop, a desktop assistant that uses tools when needed.\n\n"
            "Use tools only when the user asks for a filesystem, system, or command action.\n"
            "Never use placeholder paths such as C:\\\\Users\\\\test.\n"
            f"The user's real Desktop path is: {desktop}\n"
            "When a tool is needed, respond with EXACTLY this format and nothing else:\n"
            "[TOOL]tool_name {\"param_name\": \"value\"}\n\n"
            "CRITICAL: Do not add markdown, do not explain, do not add extra text.\n"
            "If the user request does not require a tool, answer normally.\n\n"
            f"User request: {user_prompt}\n\n"
            f"{self.get_tools_description()}"
        )

    def _resolve_directory(self, text: str) -> str:
        """Resolve a standard user directory, including localized Windows Desktop."""
        lower = text.lower()
        if "document" in lower:
            return str(Path.home() / "Documents")
        if "download" in lower:
            return str(Path.home() / "Downloads")
        if "picture" in lower or "image" in lower or "imagen" in lower:
            return str(Path.home() / "Pictures")
        return str(get_desktop_path())

    def _extract_folder_name(self, prompt: str) -> str:
        """Extract only the requested folder name, not trailing location words."""
        quoted = re.search(
            r"(?:carpeta|folder|directorio)\s+(?:llamada|llamado|called|named)?\s*['\"]([^'\"]+)['\"]",
            prompt,
            flags=re.IGNORECASE,
        )
        if quoted:
            return quoted.group(1).strip()

        named = re.search(
            r"(?:carpeta|folder|directorio)\s+(?:llamada|llamado|called|named)\s+([A-Za-z0-9_.-]+)",
            prompt,
            flags=re.IGNORECASE,
        )
        if named:
            return named.group(1).strip()

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
                return match.group(1)
        return str(get_desktop_path() / "nota.txt")

    def infer_tool_request(self, prompt: str) -> Optional[tuple[str, dict]]:
        """Infer a tool call from a natural-language user request."""
        p = prompt.lower()

        if any(k in p for k in (
            "crear carpeta", "crear una carpeta", "create folder",
            "create a folder", "carpeta llamada", "folder called",
            "folder named", "make a folder",
        )):
            folder_name = self._extract_folder_name(prompt)
            return "create_folder", {
                "folder_path": str(Path(self._resolve_directory(prompt)) / folder_name)
            }

        if any(k in p for k in (
            "listar archivos", "lista de archivos", "list files",
            "ver archivos", "show files", "muestra los archivos",
        )):
            return "list_files", {"directory": self._resolve_directory(prompt)}

        if any(k in p for k in (
            "leer archivo", "read file", "abre el archivo", "open file",
            "muestra el contenido",
        )):
            return "read_file", {"file_path": self._extract_file_path(prompt)}

        if any(k in p for k in (
            "escribir archivo", "write file", "guardar archivo",
            "save file", "crear archivo",
        )):
            base_dir = self._resolve_directory(prompt)
            match = re.search(r"([A-Za-z0-9_.-]+\.[A-Za-z0-9]+)", prompt)
            file_name = match.group(1) if match else "nuevo_archivo.txt"
            return "write_file", {
                "file_path": str(Path(base_dir) / file_name),
                "content": "",
            }

        return None

    def _parse_tool_arguments(self, tool_name: str, raw_args: str) -> Optional[dict]:
        """Parse the arguments from a raw tool call string."""
        if not raw_args:
            return {}

        raw_args = raw_args.strip()
        if raw_args.startswith("{") and raw_args.endswith("}"):
            try:
                params = json.loads(raw_args)
                return params if isinstance(params, dict) else {}
            except json.JSONDecodeError:
                logger.warning("JSON parse failed for %s: %s", tool_name, raw_args)
                return None

        # Handle function-call style: tool_name("a", "b")
        values = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', raw_args)
        if values:
            if tool_name == "create_folder":
                return {"folder_path": values[0]}
            if tool_name == "list_files":
                return {"directory": values[0]}
            if tool_name == "read_file":
                return {"file_path": values[0]}
            if tool_name == "write_file":
                return {"file_path": values[0], "content": values[1] if len(values) > 1 else ""}
            if tool_name == "execute_command":
                return {"command": values[0], "timeout": int(values[1]) if len(values) > 1 else 30}
            if tool_name == "execute_powershell":
                return {"command": values[0], "timeout": int(values[1]) if len(values) > 1 else 30}

        # Handle compact key:value forms like: tool_name key="value"
        kv_pairs = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\"([^\"]*)\"", raw_args)
        if kv_pairs:
            return {key: value for key, value in kv_pairs}

        return None

    def parse_tool_request(self, response: str) -> Optional[tuple[str, dict]]:
        """Parse a model tool call in multiple supported formats."""
        if not response:
            return None

        text = response.strip()
        text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = text.replace("\r", " ").replace("\n", " ")

        # Case 1: [TOOL]tool_name {"param": "value"}
        match = re.search(
            r"(?:\[TOOL\]|\bTOOL\b\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*(\{.*\})",
            text,
            re.DOTALL,
        )
        if match:
            tool_name = match.group(1)
            params = self._parse_tool_arguments(tool_name, match.group(2))
            if params is not None:
                return tool_name, params

        # Case 2: tool_name("arg", "arg2") or tool_name('arg')
        match = re.search(
            r"(?:\[TOOL\]|\bTOOL\b\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)",
            text,
            re.DOTALL,
        )
        if match:
            tool_name = match.group(1)
            params = self._parse_tool_arguments(tool_name, match.group(2))
            if params is not None:
                return tool_name, params

        # Case 3: tool_name {"param": "value"} without [TOOL]
        match = re.search(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*(\{.*\})",
            text,
            re.DOTALL,
        )
        if match:
            tool_name = match.group(1)
            params = self._parse_tool_arguments(tool_name, match.group(2))
            if params is not None:
                return tool_name, params

        return None

    def process_response(self, response: str) -> Optional[tuple[str, dict]]:
        """Parse a model tool request, with natural-language fallback."""
        return self.parse_tool_request(response) or self.infer_tool_request(response)

    def should_request_approval(
        self, tool_name: str, permission_level: PermissionLevel
    ) -> bool:
        """Check if a tool needs approval for this request."""
        if tool_name in self.session_approvals:
            logger.info("Tool %s already approved for this session", tool_name)
            return False
        return True

    def execute_tool(self, tool_name: str, parameters: dict) -> tuple[bool, str]:
        """Execute a tool and record the result."""
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
        except Exception as exc:
            error_msg = str(exc)
            self.db.log_action(
                action="tool_failed",
                tool_name=tool_name,
                command=str(parameters),
                approved=True,
                result=f"Error: {error_msg}",
            )
            logger.exception("Tool execution failed")
            return False, f"Error executing {tool_name}: {error_msg}"

    def generate_with_tools(
        self, model: str, prompt: str, approval_callback=None
    ) -> str:
        """Generate a response and execute at most one approved tool."""
        tool_request = self.infer_tool_request(prompt)

        try:
            response = self.client.generate(model, self.build_system_prompt(prompt))
        except Exception as exc:
            logger.error("Generation failed: %s", exc)
            return f"Error: {exc}"

        if not tool_request:
            tool_request = self.parse_tool_request(response)
        if not tool_request:
            return response

        tool_name, parameters = tool_request
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return f"{response}\n\n(Tool {tool_name} not found)"

        if self.should_request_approval(tool_name, tool.permission_level):
            if not approval_callback:
                return f"{response}\n\n(Tool execution requires approval: {tool_name})"
            approved, approved_for_session = approval_callback(
                tool_name, tool.description, tool.permission_level, parameters
            )
            if not approved:
                logger.info("User denied approval for tool: %s", tool_name)
                return f"(Tool execution was denied by user)"
            if approved_for_session:
                self.grant_session_approval(tool_name)

        success, result = self.execute_tool(tool_name, parameters)
        if not success:
            return result

        follow_up_prompt = (
            f"The tool {tool_name} was executed successfully. Result: {result}\n\n"
            "Reply briefly and naturally in the user's language. Confirm the real path."
        )
        try:
            return self.client.generate(model, follow_up_prompt)
        except Exception as exc:
            logger.error("Follow-up generation failed: %s", exc)
            return f"Acción completada: {result}"
