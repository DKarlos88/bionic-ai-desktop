"""File system tools"""

import logging
from pathlib import Path
import shutil
from app.agent.permission_manager import PermissionManager

logger = logging.getLogger(__name__)
permission_manager = PermissionManager()


def read_file(file_path: str) -> str:
    """Read file contents"""
    path = Path(file_path)
    if not permission_manager.check_file_access(path):
        return f"Error: Access denied to {file_path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return f"Error: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Write content to file"""
    path = Path(file_path)
    if not permission_manager.check_file_access(path):
        return f"Error: Access denied to {file_path}"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written successfully: {file_path}"
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return f"Error: {str(e)}"


def list_files(directory: str) -> list[str]:
    """List files in directory"""
    path = Path(directory)
    if not permission_manager.check_file_access(path):
        return [f"Error: Access denied to {directory}"]

    try:
        return [str(p) for p in path.iterdir()]
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return [f"Error: {str(e)}"]


def delete_file(file_path: str) -> str:
    """Delete a file"""
    path = Path(file_path)
    if not permission_manager.check_file_access(path):
        return f"Error: Access denied to {file_path}"

    try:
        if path.is_file():
            path.unlink()
            return f"File deleted: {file_path}"
        else:
            return f"Error: Not a file: {file_path}"
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return f"Error: {str(e)}"


def create_folder(folder_path: str) -> str:
    """Create a folder"""
    path = Path(folder_path)
    if not permission_manager.check_file_access(path):
        return f"Error: Access denied to {folder_path}"

    try:
        path.mkdir(parents=True, exist_ok=True)
        return f"Folder created: {folder_path}"
    except Exception as e:
        logger.error(f"Failed to create folder: {e}")
        return f"Error: {str(e)}"


def copy_file(source: str, destination: str) -> str:
    """Copy file"""
    src_path = Path(source)
    dst_path = Path(destination)

    if not permission_manager.check_file_access(src_path):
        return f"Error: Access denied to source {source}"
    if not permission_manager.check_file_access(dst_path):
        return f"Error: Access denied to destination {destination}"

    try:
        shutil.copy2(src_path, dst_path)
        return f"File copied: {source} -> {destination}"
    except Exception as e:
        logger.error(f"Failed to copy file: {e}")
        return f"Error: {str(e)}"
