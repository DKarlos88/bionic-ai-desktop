"""Configuration for Bionic AI Desktop"""

import ctypes
import os
from pathlib import Path

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.1")

# App Configuration
APP_NAME = "Bionic AI Desktop"
APP_VERSION = "0.1.0"

# Database Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATA_DIR / "app.db"

# Logging Configuration
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bionic.log"

# UI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Permission Levels
PERMISSION_LEVELS = {
    "low": "Bajo riesgo - Aprobación agrupada",
    "medium": "Riesgo medio - Confirmación individual",
    "high": "Alto riesgo - Confirmación reforzada",
}


def get_desktop_path() -> Path:
    """Return the user's actual Windows Desktop path, including localized names."""
    if os.name == "nt":
        try:
            buffer = ctypes.create_unicode_buffer(260)
            # CSIDL_DESKTOPDIRECTORY returns the real Desktop folder, e.g. Escritorio.
            result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buffer)
            if result == 0 and buffer.value:
                return Path(buffer.value)
        except (AttributeError, OSError):
            pass

    candidates = [Path.home() / "Desktop", Path.home() / "Escritorio"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


# Allowed paths for file operations. Resolve the localized Desktop once and reuse it.
ALLOWED_PATHS = [
    get_desktop_path(),
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Pictures",
]

# Denied commands (basic blacklist)
DENIED_COMMANDS = [
    "format",
    "del /s /q",
    "rd /s /q",
    "diskpart",
    "shutdown /s",
    "shutdown /h",
    "net user",
    "net localgroup",
]
