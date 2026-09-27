"""System information and process management tools"""

import logging
import psutil

logger = logging.getLogger(__name__)


def get_system_info() -> dict:
    """Get system information"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "cpu_count": psutil.cpu_count(),
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {"error": str(e)}


def list_processes() -> list[dict]:
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "status", "memory_percent"]
        ):
            processes.append(
                {
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "status": proc.info["status"],
                    "memory": proc.info["memory_percent"],
                }
            )
        return processes
    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        return [{"error": str(e)}]


def kill_process(pid: int) -> str:
    """Kill a process by PID"""
    try:
        proc = psutil.Process(pid)
        proc.kill()
        return f"Process killed: {proc.name()}"
    except Exception as e:
        logger.error(f"Failed to kill process: {e}")
        return f"Error: {str(e)}"
