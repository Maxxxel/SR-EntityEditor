# drs_editor/gui/log_widget.py
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QDateTime


class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFontFamily("Consolas")  # Or another monospaced font

    def log_message(self, message: str):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.append(f"[{timestamp}] {message}")
