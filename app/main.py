"""Main application entry point"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.config import LOG_FILE
from app.ui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Start application"""
    logger.info("Starting Bionic AI Desktop")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
