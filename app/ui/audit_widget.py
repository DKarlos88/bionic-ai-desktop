"""Audit log widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from app.storage.database import Database


class AuditWidget(QWidget):
    """Widget for displaying audit logs"""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Setup audit interface"""
        layout = QVBoxLayout(self)

        # Audit table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Acción", "Herramienta", "Comando", "Aprobado", "Resultado", "Tiempo"]
        )
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Actualizar")
        refresh_button.clicked.connect(self.load_logs)
        clear_button = QPushButton("Limpiar historial")
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Load initial logs
        self.load_logs()

    def load_logs(self):
        """Load audit logs into table"""
        logs = self.db.get_audit_log()
        self.table.setRowCount(len(logs))

        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(str(log["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(log["action"]))
            self.table.setItem(row, 2, QTableWidgetItem(log["tool_name"]))
            self.table.setItem(row, 3, QTableWidgetItem(log["command"]))
            approved_text = "Sí" if log["approved"] else "No"
            self.table.setItem(row, 4, QTableWidgetItem(approved_text))
            self.table.setItem(row, 5, QTableWidgetItem(log["result"][:50]))
            self.table.setItem(row, 6, QTableWidgetItem(log["timestamp"][:19]))
