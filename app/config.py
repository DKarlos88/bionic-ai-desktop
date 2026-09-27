"""Configuration for Bionic AI Desktop"""

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

# Allowed paths for file operations
ALLOWED_PATHS = [
    Path.home() / "Desktop",
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
