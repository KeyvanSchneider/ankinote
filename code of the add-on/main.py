# main.py — version finale (Anki 25+, PyQt6)
# Nom : Notebook
# Raccourci : ⇧ + N
# Langue : dynamique FR/EN

from aqt import mw
from aqt.qt import QAction, QDockWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from aqt import gui_hooks
from .ui_main import NotebookMain
from .lang import toggle_language, get_language_label, t

notebook_dock = None  # référence globale


# ---------------------------------------------------------------------------
# Réappliquer la langue au dock
# ---------------------------------------------------------------------------
def _apply_language_to_dock():
    global notebook_dock
    if notebook_dock:
        notebook_dock.setWindowTitle(t("dock_title"))
        widget = notebook_dock.widget()
        if hasattr(widget, "retranslate_ui"):
            widget.retranslate_ui()


# ---------------------------------------------------------------------------
# Afficher / masquer le panneau Notebook
# ---------------------------------------------------------------------------
def toggle_notebook():
    global notebook_dock

    # Masquer si déjà visible
    if notebook_dock and notebook_dock.isVisible():
        notebook_dock.hide()
        return

    # Créer le dock si besoin
    if not notebook_dock:
        notebook_dock = QDockWidget(t("dock_title"), mw)
        notebook_dock.setObjectName("NotebookDock")
        notebook_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        notebook_widget = NotebookMain()
        notebook_dock.setWidget(notebook_widget)
        notebook_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, notebook_dock)

    notebook_dock.show()
    notebook_dock.raise_()


# ---------------------------------------------------------------------------
# Changement de langue (FR <-> EN)
# ---------------------------------------------------------------------------
def _on_change_language(action_lang):
    toggle_language(action_lang)
    _apply_language_to_dock()


# ---------------------------------------------------------------------------
# Création du menu dans Anki
# ---------------------------------------------------------------------------
def setup_menu():
    # Ouvrir / fermer le Notebook
    action_notebook = QAction(t("menu_open"), mw)
    action_notebook.setShortcut(QKeySequence("Shift+N"))
    action_notebook.triggered.connect(toggle_notebook)
    mw.form.menuTools.addAction(action_notebook)

    # Bouton changement de langue
    action_lang = QAction(get_language_label(), mw)
    action_lang.triggered.connect(lambda: _on_change_language(action_lang))
    mw.form.menuTools.addAction(action_lang)


# ---------------------------------------------------------------------------
# Hook principal
# ---------------------------------------------------------------------------
def on_main_window_init():
    """Initialise le menu quand la fenêtre principale est prête."""
    if not hasattr(mw, "_notebook_menu_setup_done"):
        setup_menu()
        mw._notebook_menu_setup_done = True


gui_hooks.main_window_did_init.append(on_main_window_init)

