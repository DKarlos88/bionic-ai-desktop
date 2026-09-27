"""Approval dialog for tool execution requests"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from app.agent.permission_manager import PermissionLevel


class ApprovalDialog(QDialog):
    """Dialog to request user approval for tool execution"""

    def __init__(
        self,
        tool_name: str,
        description: str,
        permission_level: PermissionLevel,
        parameters: dict,
        parent=None,
    ):
        super().__init__(parent)
        self.tool_name = tool_name
        self.description = description
        self.permission_level = permission_level
        self.parameters = parameters
        self.approved = False
        self.approved_for_session = False

        self.setWindowTitle("Solicitud de Permiso")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Risk indicator
        risk_layout = QHBoxLayout()
        risk_label = QLabel("Nivel de Riesgo:")
        risk_value = QLabel(self.permission_level.value.upper())

        if self.permission_level == PermissionLevel.LOW:
            risk_value.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
            risk_text = "🟢 BAJO - Operación segura"
        elif self.permission_level == PermissionLevel.MEDIUM:
            risk_value.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
            risk_text = "🟡 MEDIO - Requiere confirmación"
        else:  # HIGH
            risk_value.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12px;")
            risk_text = "🔴 ALTO - Requiere confirmación especial"

        risk_layout.addWidget(risk_label)
        risk_layout.addWidget(QLabel(risk_text))
        risk_layout.addStretch()
        layout.addLayout(risk_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)

        # Tool name and description
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        tool_label = QLabel(f"Herramienta: {self.tool_name}")
        tool_label.setFont(title_font)
        layout.addWidget(tool_label)

        desc_label = QLabel(f"Descripción: {self.description}")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Parameters
        if self.parameters:
            params_label = QLabel("Parámetros:")
            params_label.setFont(title_font)
            layout.addWidget(params_label)

            params_text = QTextEdit()
            params_text.setReadOnly(True)
            params_text.setMaximumHeight(120)

            params_str = ""
            for key, value in self.parameters.items():
                if isinstance(value, str) and len(value) > 100:
                    params_str += f"• {key}:\n  {value[:100]}...\n\n"
                else:
                    params_str += f"• {key}: {value}\n"
            params_text.setText(params_str)
            layout.addWidget(params_text)
        else:
            params_label = QLabel("Parámetros: Ninguno")
            layout.addWidget(params_label)

        # Warning message for HIGH risk
        if self.permission_level == PermissionLevel.HIGH:
            warning_label = QLabel(
                "⚠️ ADVERTENCIA: Esta operación tiene un alto nivel de riesgo. "
                "Asegúrate de que sea exactamente lo que deseas antes de aprobar."
            )
            warning_label.setWordWrap(True)
            warning_label.setStyleSheet(
                "background-color: #FFF3E0; padding: 10px; "
                "border-left: 4px solid #F44336; border-radius: 3px;"
            )
            layout.addWidget(warning_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        deny_button = QPushButton("Denegar")
        deny_button.clicked.connect(self.deny)
        deny_button.setStyleSheet(
            "QPushButton { background-color: #F44336; color: white; padding: 8px 20px; "
            "border-radius: 4px; font-weight: bold; } "
            "QPushButton:hover { background-color: #D32F2F; }"
        )
        button_layout.addWidget(deny_button)

        if self.permission_level != PermissionLevel.HIGH:
            session_button = QPushButton("Permitir esta sesión")
            session_button.clicked.connect(self.approve_session)
            session_button.setStyleSheet(
                "QPushButton { background-color: #FF9800; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-weight: bold; } "
                "QPushButton:hover { background-color: #F57C00; }"
            )
            button_layout.addWidget(session_button)

        approve_button = QPushButton("Permitir")
        approve_button.clicked.connect(self.approve)
        approve_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 8px 20px; "
            "border-radius: 4px; font-weight: bold; } "
            "QPushButton:hover { background-color: #388E3C; }"
        )
        button_layout.addWidget(approve_button)

        layout.addLayout(button_layout)

    def approve(self):
        """Approve the tool execution"""
        self.approved = True
        self.accept()

    def approve_session(self):
        """Approve for this session"""
        self.approved = True
        self.approved_for_session = True
        self.accept()

    def deny(self):
        """Deny the tool execution"""
        self.approved = False
        self.reject()
