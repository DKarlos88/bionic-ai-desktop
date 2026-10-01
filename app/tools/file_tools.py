"""File system tools"""

import logging
from pathlib import Path
import shutil
from app.agent.permission_manager import PermissionManager

logger = logging.getLogger(__name__)
permission_manager = PermissionManager()


def _normalize_path(file_path: str | Path) -> Path:
    """Normalize a file path by removing extra spaces and resolving it."""
    if isinstance(file_path, Path):
        return file_path.resolve()
    
    # Convert to string, strip extra whitespace, then resolve
    normalized = str(file_path).strip()
    return Path(normalized).resolve()


def read_file(file_path: str) -> str:
    """Read file contents"""
    path = _normalize_path(file_path)
    logger.debug(f"read_file normalized path: {path}")
    
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
    path = _normalize_path(file_path)
    logger.debug(f"write_file normalized path: {path}")
    
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
    path = _normalize_path(directory)
    logger.debug(f"list_files normalized path: {path}")
    
    if not permission_manager.check_file_access(path):
        return [f"Error: Access denied to {directory}"]

    try:
        return [str(p) for p in path.iterdir()]
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return [f"Error: {str(e)}"]


def delete_file(file_path: str) -> str:
    """Delete a file"""
    path = _normalize_path(file_path)
    logger.debug(f"delete_file normalized path: {path}")
    
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
    path = _normalize_path(folder_path)
    logger.debug(f"create_folder normalized path: {path}")
    
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
    src_path = _normalize_path(source)
    dst_path = _normalize_path(destination)
    
    logger.debug(f"copy_file normalized source: {src_path}")
    logger.debug(f"copy_file normalized destination: {dst_path}")

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
