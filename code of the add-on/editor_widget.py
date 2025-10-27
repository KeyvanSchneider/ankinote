# editor_widget.py — éditeur Markdown moderne, multilingue et autosave

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette, QColor
from .storage import save_markdown, load_markdown
from .lang import t


class NotebookEditor(QWidget):
    """Éditeur Markdown minimaliste (style Notion) avec autosave et traduction."""

    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path

        # --- Zone de texte ---
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setPlaceholderText(t("placeholder_note"))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        # --- Bouton sauvegarde ---
        self.btn_save = QPushButton(t("save"))
        self.btn_save.clicked.connect(self.save_file)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()

        # --- Layout global ---
        layout = QVBoxLayout()
        layout.addLayout(btn_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # --- Style clair et doux ---
        self.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #ebebeb; }
            QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                background-color: #ffffff;
                font-family: "Inter","Helvetica Neue",sans-serif;
                font-size: 14px;
                padding: 10px;
            }
        """)

        # --- Thème clair/sombre ---
        self.apply_system_theme()

        # --- Autosave (toutes les 2 secondes) ---
        self.autosave_timer = QTimer()
        self.autosave_timer.setInterval(2000)
        self.autosave_timer.timeout.connect(self.save_file)
        self.autosave_timer.start()

        # --- Charger le fichier si fourni ---
        if self.file_path:
            self.load_file(self.file_path)

    # ------------------------- Re-traduction dynamique -------------------------

    def retranslate_ui(self):
        """Met à jour les textes si la langue change."""
        self.btn_save.setText(t("save"))
        self.text_edit.setPlaceholderText(t("placeholder_note"))

    # ----------------------------- Apparence ----------------------------------

    def apply_system_theme(self):
        """Adapte les couleurs selon le thème clair/sombre du système."""
        palette = self.text_edit.palette()
        app_palette = self.palette()
        bg = app_palette.color(QPalette.ColorRole.Base)
        mode = "dark" if bg.lightnessF() < 0.5 else "light"

        if mode == "dark":
            bg_color = QColor("#1E1E1E")
            text_color = QColor("#EAEAEA")
        else:
            bg_color = QColor("#FFFFFF")
            text_color = QColor("#000000")

        palette.setColor(QPalette.ColorRole.Base, bg_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        self.text_edit.setPalette(palette)

    # ----------------------------- Fichiers -----------------------------------

    def load_file(self, file_path):
        """Charge le contenu d'une note Markdown existante."""
        self.file_path = file_path
        content = load_markdown(file_path)
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(content)
        self.text_edit.blockSignals(False)

    def save_file(self):
        """Sauvegarde le contenu courant dans le fichier associé."""
        if not self.file_path:
            return
        content = self.text_edit.toPlainText()
        save_markdown(self.file_path, content)

