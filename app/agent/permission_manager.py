"""Permission management system"""

import logging
from enum import Enum
from pathlib import Path
from app.config import ALLOWED_PATHS, DENIED_COMMANDS

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission risk levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PermissionManager:
    """Manages permissions for tool execution"""

    def __init__(self):
        # Normalize allowed paths once at initialization
        self.allowed_paths = [Path(p).resolve() for p in ALLOWED_PATHS]
        self.denied_commands = DENIED_COMMANDS
        logger.info(f"Allowed paths: {self.allowed_paths}")

    def check_file_access(self, file_path: str | Path) -> bool:
        """Check if file path is allowed"""
        try:
            # Normalize the file path
            file_path = Path(file_path).resolve()
            
            # Debug logging
            logger.debug(f"Checking access for: {file_path}")
            
            # Check if the file is under any allowed directory
            for allowed in self.allowed_paths:
                try:
                    # This will succeed if file_path is under allowed
                    file_path.relative_to(allowed)
                    logger.debug(f"Access granted (under {allowed}): {file_path}")
                    return True
                except ValueError:
                    # Not under this allowed path, continue to next
                    continue
            
            # Not under any allowed path
            logger.warning(f"Access denied to: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error checking file access for {file_path}: {e}")
            return False

    def check_command_safety(self, command: str) -> bool:
        """Check if command is safe to execute"""
        command_lower = command.lower()
        for denied in self.denied_commands:
            if denied.lower() in command_lower:
                logger.warning(f"Dangerous command blocked: {command}")
                return False
        return True

    def get_permission_level(self, tool_name: str, action: str) -> PermissionLevel:
        """Determine permission level for an action"""
        low_risk_actions = ["read", "list", "search", "get_info", "analyze"]
        high_risk_actions = ["delete", "format", "install", "shutdown", "upload"]

        if any(action.lower().startswith(a) for a in high_risk_actions):
            return PermissionLevel.HIGH
        elif any(action.lower().startswith(a) for a in low_risk_actions):
            return PermissionLevel.LOW
        else:
            return PermissionLevel.MEDIUM
