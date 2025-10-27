# ui_main.py — version finale (Anki 25+, PyQt6)
# - Multilingue FR/EN
# - Suppression fiable (macOS / Windows / Linux)
# - Interface modernisée et légère

import os, json, shutil, time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QSplitter, QTreeWidget,
    QTreeWidgetItem, QMenu, QInputDialog, QMessageBox, QFileDialog,
    QDialog, QLineEdit, QLabel, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt
from .storage import ensure_base_path
from .editor_widget import NotebookEditor
from .lang import t

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".anki_notebook_config.json")


# ----------------------------- Config du dossier racine -----------------------------

def load_notebook_path():
    """Lit le chemin racine depuis la config, sinon fallback vers ensure_base_path()."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                path = json.load(f).get("notebook_path")
                if path and os.path.exists(path):
                    return path
        except Exception:
            pass
    return ensure_base_path()


def save_notebook_path(path):
    """Sauvegarde le chemin racine dans la config utilisateur."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"notebook_path": path}, f)
    except Exception as e:
        QMessageBox.warning(None, t("error"), f"{e}")


# -------------------------------- Boîte de recherche --------------------------------

class SearchDialog(QDialog):
    """Fenêtre modale de recherche globale dans toutes les notes (.md)."""

    def __init__(self, parent, root_path, open_note_callback):
        super().__init__(parent)
        self.root_path = root_path
        self.open_note_callback = open_note_callback
        self._build()

    def _build(self):
        self.setWindowTitle("🔍 " + t("search"))
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.input = QLineEdit()
        self.input.setPlaceholderText(t("search_placeholder"))
        self.input.textChanged.connect(self.on_search_changed)

        self.results = QTreeWidget()
        self.results.setHeaderHidden(True)
        self.results.itemDoubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(QLabel(t("search_label")))
        layout.addWidget(self.input)
        layout.addWidget(self.results)

    def on_search_changed(self, text):
        text = text.strip().lower()
        self.results.clear()
        if not text:
            return

        matches = []
        for root, _, files in os.walk(self.root_path):
            for f in files:
                if f.startswith(".") or not f.endswith(".md"):
                    continue
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read().lower()
                        if text in f.lower() or text in content:
                            matches.append((f, full_path))
                except Exception:
                    pass

        for title, path in matches[:500]:
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, path)
            self.results.addTopLevelItem(item)

    def on_item_double_clicked(self, item, col):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            self.open_note_callback(path)
            self.accept()


# -------------------------------- Classe principale --------------------------------

class NotebookMain(QWidget):
    """Explorateur de fichiers + éditeur Markdown + recherche globale."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_path = load_notebook_path()
        os.makedirs(self.root_path, exist_ok=True)

        # --- Arborescence ---
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        # --- Boutons (haut) ---
        self.btn_new = QPushButton(t("new"))
        self.btn_change_dir = QPushButton(t("change_dir"))
        self.btn_search = QPushButton(t("search"))

        self.btn_new.clicked.connect(self.new_root_item)
        self.btn_change_dir.clicked.connect(self.change_root_folder)
        self.btn_search.clicked.connect(self.open_search_dialog)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_change_dir)
        btn_layout.addWidget(self.btn_search)

        # --- Éditeur ---
        self.editor = NotebookEditor()

        # --- Split principal ---
        split = QSplitter()
        split.addWidget(self.tree)
        split.addWidget(self.editor)
        split.setSizes([260, 600])

        layout = QVBoxLayout(self)
        layout.addLayout(btn_layout)
        layout.addWidget(split)
        self.setLayout(layout)

        # --- Style global ---
        self.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #ebebeb; }
            QTreeWidget {
                background-color: #fafafa;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                font-size: 13px;
            }
            QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                background-color: #ffffff;
                font-family: 'Inter','Helvetica Neue',sans-serif;
                font-size: 14px;
                padding: 10px;
            }
        """)

        self.refresh_tree()

    # ----------------------------- Re-traduction -----------------------------

    def retranslate_ui(self):
        self.btn_new.setText(t("new"))
        self.btn_change_dir.setText(t("change_dir"))
        self.btn_search.setText(t("search"))
        if hasattr(self.editor, "retranslate_ui"):
            self.editor.retranslate_ui()

    # ----------------------------- Helpers anti-fantômes -----------------------------

    def _detach_editor_if_affected(self, target_path: str):
        """Détache l’éditeur si le fichier/dossier supprimé est ouvert ou contient le fichier ouvert."""
        cur = getattr(self.editor, "file_path", None)
        if not cur:
            return
        if os.path.isdir(target_path):
            if cur.startswith(os.path.join(target_path, "")):
                self.editor.text_edit.clear()
                self.editor.file_path = None
        else:
            if os.path.normpath(cur) == os.path.normpath(target_path):
                self.editor.text_edit.clear()
                self.editor.file_path = None

    # ----------------------------- Actions haut ------------------------------

    def open_search_dialog(self):
        dlg = SearchDialog(self, self.root_path, self.editor.load_file)
        dlg.exec()

    def change_root_folder(self):
        new_path = QFileDialog.getExistingDirectory(self, t("choose_folder"), self.root_path)
        if new_path:
            cur = getattr(self.editor, "file_path", None)
            if cur and not cur.startswith(os.path.join(new_path, "")):
                self.editor.text_edit.clear()
                self.editor.file_path = None
            self.root_path = new_path
            save_notebook_path(new_path)
            os.makedirs(new_path, exist_ok=True)
            self.refresh_tree()
            QMessageBox.information(self, t("updated_folder"), f"{t('new_folder_set')}:\n{new_path}")

    # ----------------------------- Arborescence ------------------------------

    def refresh_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        self._add_children(self.tree.invisibleRootItem(), self.root_path)
        self.tree.expandAll()
        self.tree.blockSignals(False)
        # Si la note ouverte a disparu, on détache
        cur = getattr(self.editor, "file_path", None)
        if cur and not os.path.exists(cur):
            self.editor.text_edit.clear()
            self.editor.file_path = None

    def _add_children(self, parent_item, path):
        if not os.path.exists(path):
            return
        try:
            entries = sorted(os.listdir(path))
        except FileNotFoundError:
            return
        for e in entries:
            if e.startswith(".") or e.lower() in {"thumbs.db", "desktop.ini"}:
                continue
            full = os.path.join(path, e)
            item = QTreeWidgetItem([e])
            item.setData(0, Qt.ItemDataRole.UserRole, full)
            parent_item.addChild(item)
            if os.path.isdir(full):
                self._add_children(item, full)

    # ------------------ Création / suppression / renommage -------------------

    def new_root_item(self):
        menu = QMenu()
        f_act = menu.addAction(t("new_folder"))
        n_act = menu.addAction(t("new_note"))
        act = menu.exec(self.btn_new.mapToGlobal(self.btn_new.rect().bottomLeft()))
        if not act:
            return

        if act == f_act:
            name, ok = QInputDialog.getText(self, t("new_folder"), t("folder_name"))
            if ok and name.strip():
                os.makedirs(os.path.join(self.root_path, name.strip()), exist_ok=True)
        elif act == n_act:
            name, ok = QInputDialog.getText(self, t("new_note"), t("note_name"))
            if ok and name.strip():
                with open(os.path.join(self.root_path, name.strip() + ".md"), "w", encoding="utf-8") as f:
                    f.write("")

        self.tree.clearSelection()
        self.refresh_tree()

    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not os.path.exists(path):
            self.refresh_tree()
            return

        is_dir = os.path.isdir(path)
        menu = QMenu()
        if is_dir:
            menu.addAction(t("new_subfolder"))
            menu.addAction(t("new_note_here"))
        menu.addSeparator()
        menu.addAction(t("rename"))
        menu.addAction(t("delete"))

        act = menu.exec(self.tree.viewport().mapToGlobal(pos))
        if not act:
            return
        text = act.text()

        if text == t("new_subfolder"):
            name, ok = QInputDialog.getText(self, t("new_subfolder"), t("folder_name"))
            if ok and name.strip():
                os.makedirs(os.path.join(path, name.strip()), exist_ok=True)
                self.refresh_tree()

        elif text == t("new_note_here"):
            name, ok = QInputDialog.getText(self, t("new_note_here"), t("note_name"))
            if ok and name.strip():
                with open(os.path.join(path, name.strip() + ".md"), "w", encoding="utf-8") as f:
                    f.write("")
                self.refresh_tree()

        elif text == t("rename"):
            new_name, ok = QInputDialog.getText(self, t("rename"), t("new_name"), text=os.path.basename(path))
            if ok and new_name.strip():
                new_full = os.path.join(os.path.dirname(path), new_name.strip())
                self._detach_editor_if_affected(path)
                os.rename(path, new_full)
                self.refresh_tree()

        elif text == t("delete"):
            confirm = QMessageBox.question(self, t("delete"), t("confirm_delete", name=os.path.basename(path)))
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    self._detach_editor_if_affected(path)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    elif os.path.exists(path):
                        os.remove(path)
                    time.sleep(0.1)
                    QApplication.processEvents()
                    self.tree.clearSelection()
                    self.refresh_tree()
                except Exception as e:
                    QMessageBox.warning(self, t("error"), f"{t('delete_error')} : {e}")

    # --------------------------------- Ouvrir --------------------------------

    def on_item_double_clicked(self, item, col):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path) and path.endswith(".md"):
            self.editor.load_file(path)

