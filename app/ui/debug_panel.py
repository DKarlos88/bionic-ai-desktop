"""Debug panel for showing detailed execution information"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt
from app.storage.database import Database


class DebugPanel(QWidget):
    """Panel for displaying debug information about tool execution"""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Setup debug panel interface"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🔍 Debug Panel - Información Detallada de Ejecución")
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Buttons layout
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("🔄 Actualizar")
        refresh_button.clicked.connect(self.load_debug_info)
        button_layout.addWidget(refresh_button)

        clear_button = QPushButton("🗑️ Limpiar")
        clear_button.clicked.connect(self.clear_debug_info)
        button_layout.addWidget(clear_button)

        export_button = QPushButton("💾 Exportar")
        export_button.clicked.connect(self.export_debug_info)
        button_layout.addWidget(export_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Debug text area
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        self.debug_text.setStyleSheet(
            "QTextEdit { font-family: 'Courier New'; font-size: 10px; "
            "background-color: #1e1e1e; color: #00ff00; }"
        )
        layout.addWidget(self.debug_text)

        # Load initial info
        self.load_debug_info()

    def load_debug_info(self):
        """Load and display debug information"""
        logs = self.db.get_audit_log(limit=50)
        
        debug_output = "═" * 100 + "\n"
        debug_output += "INFORMACIÓN DE AUDITORÍA Y EJECUCIÓN DE HERRAMIENTAS\n"
        debug_output += "═" * 100 + "\n\n"

        if not logs:
            debug_output += "📭 No hay registros de ejecución.\n"
            self.debug_text.setText(debug_output)
            return

        for i, log in enumerate(logs, 1):
            debug_output += f"\n{'─' * 100}\n"
            debug_output += f"[{i}] ID: {log['id']}\n"
            debug_output += f"    Timestamp: {log['timestamp']}\n"
            debug_output += f"    Acción: {log['action']}\n"
            debug_output += f"    Herramienta: {log['tool_name']}\n"
            debug_output += f"    Comando/Parámetros:\n"
            
            # Pretty print the command
            cmd_str = log['command']
            if cmd_str.startswith("{"):
                try:
                    import json
                    cmd_dict = json.loads(cmd_str)
                    for key, value in cmd_dict.items():
                        debug_output += f"        • {key}: {value}\n"
                except:
                    debug_output += f"        {cmd_str}\n"
            else:
                debug_output += f"        {cmd_str}\n"
            
            debug_output += f"    Aprobado: {'✅ Sí' if log['approved'] else '❌ No'}\n"
            debug_output += f"    Resultado:\n"
            
            result_str = log['result']
            if len(result_str) > 200:
                debug_output += f"        {result_str[:200]}...\n"
            else:
                debug_output += f"        {result_str}\n"

        debug_output += f"\n{'═' * 100}\n"
        debug_output += f"Total de registros mostrados: {len(logs)}\n"
        
        self.debug_text.setText(debug_output)

    def clear_debug_info(self):
        """Clear debug panel"""
        self.debug_text.clear()
        self.debug_text.setText(
            "🗑️ Panel de debug limpiado.\n"
            "Los registros en la base de datos se mantienen.\n"
            "Usa el botón 'Actualizar' para volver a cargar la información."
        )

    def export_debug_info(self):
        """Export debug information to file"""
        try:
            logs = self.db.get_audit_log(limit=1000)
            
            export_text = "═" * 100 + "\n"
            export_text += "EXPORTACIÓN DE AUDITORÍA - BIONIC AI DESKTOP\n"
            export_text += "═" * 100 + "\n\n"

            for log in logs:
                export_text += f"[{log['timestamp']}] {log['action']} - {log['tool_name']}\n"
                export_text += f"  Comando: {log['command']}\n"
                export_text += f"  Aprobado: {log['approved']}\n"
                export_text += f"  Resultado: {log['result']}\n\n"

            # Save to file
            from pathlib import Path
            from app.config import LOG_DIR
            
            export_path = LOG_DIR / "audit_export.txt"
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(export_text)

            self.debug_text.setText(
                f"✅ Exportación completada.\n"
                f"Archivo guardado en: {export_path}\n\n"
                f"Total de registros exportados: {len(logs)}"
            )
        except Exception as e:
            self.debug_text.setText(f"❌ Error al exportar: {str(e)}")
