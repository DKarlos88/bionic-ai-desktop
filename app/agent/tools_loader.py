"""Tools loader - Registers all available tools for the agent"""

import logging
from app.agent.tool_registry import ToolRegistry
from app.agent.permission_manager import PermissionLevel
from app.tools import file_tools, shell_tools, system_tools

logger = logging.getLogger(__name__)


def load_tools() -> ToolRegistry:
    """Load and register all available tools"""
    registry = ToolRegistry()

    # FILE TOOLS (LOW/MEDIUM RISK)
    registry.register(
        name="read_file",
        description="Lee el contenido de un archivo de texto",
        func=file_tools.read_file,
        permission_level=PermissionLevel.LOW,
        parameters={"file_path": "Ruta del archivo a leer"},
    )

    registry.register(
        name="write_file",
        description="Escribe contenido en un archivo (lo crea si no existe)",
        func=file_tools.write_file,
        permission_level=PermissionLevel.MEDIUM,
        parameters={
            "file_path": "Ruta del archivo a crear/escribir",
            "content": "Contenido a escribir",
        },
    )

    registry.register(
        name="list_files",
        description="Lista todos los archivos en una carpeta",
        func=file_tools.list_files,
        permission_level=PermissionLevel.LOW,
        parameters={"directory": "Ruta de la carpeta"},
    )

    registry.register(
        name="create_folder",
        description="Crea una carpeta en la ruta especificada",
        func=file_tools.create_folder,
        permission_level=PermissionLevel.MEDIUM,
        parameters={"folder_path": "Ruta de la carpeta a crear"},
    )

    registry.register(
        name="copy_file",
        description="Copia un archivo a otro destino",
        func=file_tools.copy_file,
        permission_level=PermissionLevel.MEDIUM,
        parameters={
            "source": "Ruta del archivo origen",
            "destination": "Ruta del archivo destino",
        },
    )

    registry.register(
        name="delete_file",
        description="Elimina un archivo (¡requiere confirmación especial!)",
        func=file_tools.delete_file,
        permission_level=PermissionLevel.HIGH,
        parameters={"file_path": "Ruta del archivo a eliminar"},
    )

    # SHELL TOOLS (MEDIUM/HIGH RISK)
    registry.register(
        name="execute_command",
        description="Ejecuta un comando en la terminal (CMD de Windows)",
        func=shell_tools.execute_command,
        permission_level=PermissionLevel.HIGH,
        parameters={"command": "Comando a ejecutar", "timeout": "Timeout en segundos"},
    )

    registry.register(
        name="execute_powershell",
        description="Ejecuta un comando en PowerShell",
        func=shell_tools.execute_powershell,
        permission_level=PermissionLevel.HIGH,
        parameters={"command": "Comando PowerShell a ejecutar", "timeout": "Timeout en segundos"},
    )

    # SYSTEM TOOLS (LOW/MEDIUM RISK)
    registry.register(
        name="get_system_info",
        description="Obtiene información del sistema (CPU, RAM, Disco)",
        func=system_tools.get_system_info,
        permission_level=PermissionLevel.LOW,
        parameters={},
    )

    registry.register(
        name="list_processes",
        description="Lista todos los procesos activos del sistema",
        func=system_tools.list_processes,
        permission_level=PermissionLevel.LOW,
        parameters={},
    )

    registry.register(
        name="kill_process",
        description="Detiene un proceso por su ID",
        func=system_tools.kill_process,
        permission_level=PermissionLevel.HIGH,
        parameters={"pid": "ID del proceso a detener"},
    )

    logger.info(f"Loaded {len(registry.list_tools())} tools")
    return registry
