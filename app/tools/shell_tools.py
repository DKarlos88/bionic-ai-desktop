"""Shell command execution tools"""

import logging
import subprocess
from app.agent.permission_manager import PermissionManager

logger = logging.getLogger(__name__)
permission_manager = PermissionManager()


def execute_command(command: str, timeout: int = 30) -> str:
    """Execute a shell command"""
    if not permission_manager.check_command_safety(command):
        return f"Error: Command blocked for safety reasons: {command}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout or result.stderr or "Command executed successfully"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return f"Error: {str(e)}"


def execute_powershell(command: str, timeout: int = 30) -> str:
    """Execute a PowerShell command"""
    if not permission_manager.check_command_safety(command):
        return f"Error: Command blocked for safety reasons: {command}"

    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout or result.stderr or "Command executed successfully"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        logger.error(f"PowerShell execution failed: {e}")
        return f"Error: {str(e)}"
