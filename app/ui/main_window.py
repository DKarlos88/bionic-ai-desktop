"""Main application window"""

import sys
import logging
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QMessageBox,
    QTabWidget,
)
from PySide6.QtCore import QThread, QObject, Signal, Slot

from app.config import WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME
from app.ollama_client import OllamaClient
from app.ui.chat_widget import ChatWidget
from app.ui.audit_widget import AuditWidget
from app.storage.database import Database

logger = logging.getLogger(__name__)


class GenerateWorker(QObject):
    """Worker thread for AI generation"""

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, client: OllamaClient, model: str, prompt: str):
        super().__init__()
        self.client = client
        self.model = model
        self.prompt = prompt

    def run(self):
        try:
            response = self.client.generate(self.model, self.prompt)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.client = OllamaClient()
        self.db = Database()
        self.current_conversation = None

        self.setWindowTitle(APP_NAME)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.setup_ui()
        self.check_ollama_connection()

    def setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Top panel with model selector
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Modelo:"))
        self.model_combo = QComboBox()
        top_layout.addWidget(self.model_combo)
        self.refresh_button = QPushButton("Actualizar modelos")
        self.refresh_button.clicked.connect(self.load_models)
        top_layout.addWidget(self.refresh_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Tabs for chat and audit
        self.tabs = QTabWidget()
        self.chat_widget = ChatWidget()
        self.audit_widget = AuditWidget(self.db)
        self.tabs.addTab(self.chat_widget, "Chat")
        self.tabs.addTab(self.audit_widget, "Auditoría")
        main_layout.addWidget(self.tabs)

        # Connect signals
        self.chat_widget.send_button.clicked.connect(self.send_message)
        self.chat_widget.input_box.returnPressed.connect(self.send_message)
        self.chat_widget.clear_button.clicked.connect(self.clear_chat)

        # Create new conversation
        self.current_conversation = self.db.create_conversation("Nueva conversación")

    def check_ollama_connection(self):
        """Check if Ollama is running"""
        if not self.client.is_running():
            QMessageBox.warning(
                self,
                "Ollama no disponible",
                "No se puede conectar a Ollama en localhost:11434.\n"
                "Asegúrate de que Ollama está instalado y ejecutándose.",
            )
            return False
        self.load_models()
        return True

    def load_models(self):
        """Load available models"""
        models = self.client.list_models()
        self.model_combo.clear()
        if not models:
            self.model_combo.addItem("No hay modelos disponibles")
            QMessageBox.information(
                self,
                "Sin modelos",
                "No hay modelos disponibles.\n" "Descarga uno usando: ollama pull llama3.1",
            )
            return

        for model in models:
            self.model_combo.addItem(model)

    def send_message(self):
        """Send message to AI"""
        text = self.chat_widget.input_box.text().strip()
        if not text:
            return

        current_model = self.model_combo.currentText()
        if current_model == "No hay modelos disponibles":
            QMessageBox.warning(self, "Error", "No hay modelos disponibles")
            return

        # Save user message
        self.chat_widget.append_user_message(text)
        self.db.add_message(self.current_conversation, "user", text)
        self.chat_widget.clear_input()

        # Generate response in thread
        worker = GenerateWorker(self.client, current_model, text)
        thread = QThread(self)
        worker.moveToThread(thread)

        worker.finished.connect(self.on_response_received)
        worker.error.connect(self.on_error)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)
        thread.start()

    def on_response_received(self, text: str):
        """Handle AI response"""
        self.chat_widget.append_assistant_message(text)
        self.db.add_message(self.current_conversation, "assistant", text)

    def on_error(self, error: str):
        """Handle error"""
        QMessageBox.critical(self, "Error", f"Error: {error}")
        logger.error(f"Generation error: {error}")

    def clear_chat(self):
        """Clear chat and start new conversation"""
        self.chat_widget.clear_chat()
        self.current_conversation = self.db.create_conversation("Nueva conversación")
