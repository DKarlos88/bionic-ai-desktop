"""Chat widget for conversations"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ChatWidget(QWidget):
    """Widget for chat interface"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup chat interface"""
        layout = QVBoxLayout(self)

        # Chat display
        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setPlaceholderText("Conversación...")
        font = QFont()
        font.setPointSize(10)
        self.chat_output.setFont(font)
        layout.addWidget(self.chat_output)

        # Input area
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Escribe tu mensaje...")
        self.send_button = QPushButton("Enviar")
        self.clear_button = QPushButton("Limpiar")
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)
        layout.addLayout(input_layout)

    def append_user_message(self, text: str):
        """Append user message to chat"""
        self.chat_output.append(f"<b style='color: #2196F3'>Yo:</b> {text}")

    def append_assistant_message(self, text: str):
        """Append assistant message to chat"""
        self.chat_output.append(f"<b style='color: #4CAF50'>IA:</b> {text}")

    def clear_input(self):
        """Clear input field"""
        self.input_box.clear()
        self.input_box.setFocus()

    def clear_chat(self):
        """Clear entire chat"""
        self.chat_output.clear()
