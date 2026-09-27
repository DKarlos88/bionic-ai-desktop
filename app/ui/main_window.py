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
from PySide6.QtCore import QThread, QObject, Signal, QMetaObject, Qt

from app.config import WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME
from app.ollama_client import OllamaClient
from app.storage.database import Database
from app.agent.tools_loader import load_tools
from app.agent.agent_loop import AgentLoop
from app.ui.chat_widget import ChatWidget
from app.ui.audit_widget import AuditWidget
from app.ui.approval_dialog import ApprovalDialog

logger = logging.getLogger(__name__)


class GenerateWorker(QObject):
    """Worker thread for AI generation"""

    finished = Signal(str)
    error = Signal(str)
    approval_requested = Signal(str, str, str, dict)  # tool_name, description, level, params

    def __init__(self, agent: AgentLoop, model: str, prompt: str):
        super().__init__()
        self.agent = agent
        self.model = model
        self.prompt = prompt
        self.approval_result = None

    def run(self):
        try:
            response = self.agent.generate_with_tools(
                self.model,
                self.prompt,
                approval_callback=self.request_approval,
            )
            self.finished.emit(response)
        except Exception as e:
            logger.exception(f"Generation error: {e}")
            self.error.emit(str(e))

    def request_approval(self, tool_name, description, permission_level, parameters):
        """Request approval - emit signal to main thread"""
        # Store approval result temporarily
        self.approval_requested.emit(tool_name, description, permission_level.value, str(parameters))
        
        # Wait for result from main thread
        # This is a simplified approach - the main thread will set this
        return getattr(self, '_approval_result', (False, False))

    def set_approval_result(self, approved: bool, approved_for_session: bool):
        """Set the approval result from main thread"""
        self._approval_result = (approved, approved_for_session)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.client = OllamaClient()
        self.db = Database()
        self.registry = load_tools()
        self.agent = AgentLoop(self.client, self.registry, self.db)
        self.current_conversation = None
        self.current_worker = None

        self.setWindowTitle(APP_NAME)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.setup_ui()
        self.check_ollama_connection()

    def setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Modelo:"))
        self.model_combo = QComboBox()
        top_layout.addWidget(self.model_combo)
        self.refresh_button = QPushButton("Actualizar modelos")
        self.refresh_button.clicked.connect(self.load_models)
        top_layout.addWidget(self.refresh_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        self.chat_widget = ChatWidget()
        self.audit_widget = AuditWidget(self.db)
        self.tabs.addTab(self.chat_widget, "Chat")
        self.tabs.addTab(self.audit_widget, "Auditoría")
        main_layout.addWidget(self.tabs)

        self.chat_widget.send_button.clicked.connect(self.send_message)
        self.chat_widget.input_box.returnPressed.connect(self.send_message)
        self.chat_widget.clear_button.clicked.connect(self.clear_chat)

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
                "No hay modelos disponibles.\nDescarga uno usando: ollama pull llama3.1",
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

        self.chat_widget.append_user_message(text)
        self.db.add_message(self.current_conversation, "user", text)
        self.chat_widget.clear_input()

        self.current_worker = GenerateWorker(self.agent, current_model, text)
        thread = QThread(self)
        self.current_worker.moveToThread(thread)

        # Connect signals
        self.current_worker.finished.connect(self.on_response_received)
        self.current_worker.error.connect(self.on_error)
        self.current_worker.approval_requested.connect(self.on_approval_requested)
        thread.started.connect(self.current_worker.run)
        self.current_worker.finished.connect(thread.quit)
        self.current_worker.error.connect(thread.quit)
        self.current_worker.finished.connect(self.current_worker.deleteLater)
        self.current_worker.error.connect(self.current_worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        thread.start()

    def on_approval_requested(self, tool_name: str, description: str, permission_level: str, parameters: str):
        """Handle approval request from worker thread"""
        dialog = ApprovalDialog(
            tool_name, 
            description, 
            self._parse_permission_level(permission_level),
            self._parse_parameters(parameters)
        )
        result = dialog.exec_()
        approved = result == 1
        approved_for_session = dialog.approved_for_session if approved else False
        
        if self.current_worker:
            self.current_worker.set_approval_result(approved, approved_for_session)

    def _parse_permission_level(self, level_str: str):
        """Parse permission level string back to enum"""
        from app.agent.permission_manager import PermissionLevel
        return PermissionLevel[level_str.upper()]

    def _parse_parameters(self, params_str: str) -> dict:
        """Parse parameters string to dict"""
        import ast
        try:
            return ast.literal_eval(params_str)
        except:
            return {}

    def on_response_received(self, text: str):
        """Handle AI response"""
        self.chat_widget.append_assistant_message(text)
        self.db.add_message(self.current_conversation, "assistant", text)
        self.audit_widget.load_logs()

    def on_error(self, error: str):
        """Handle error"""
        QMessageBox.critical(self, "Error", f"Error: {error}")
        logger.error(f"Generation error: {error}")

    def clear_chat(self):
        """Clear chat and start new conversation"""
        self.chat_widget.clear_chat()
        self.current_conversation = self.db.create_conversation("Nueva conversación")
