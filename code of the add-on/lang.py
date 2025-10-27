# lang.py — multilingue (Français / English)

import json, os
CONFIG_LANG_PATH = os.path.join(os.path.expanduser("~"), ".anki_notebook_lang.json")
LANG = "fr"

def load_language():
    global LANG
    if os.path.exists(CONFIG_LANG_PATH):
        try:
            with open(CONFIG_LANG_PATH, "r", encoding="utf-8") as f:
                LANG = json.load(f).get("lang", "fr")
        except Exception:
            LANG = "fr"

def save_language():
    try:
        with open(CONFIG_LANG_PATH, "w", encoding="utf-8") as f:
            json.dump({"lang": LANG}, f)
    except Exception:
        pass

translations = {
    "fr": {
        "dock_title": "Notebook",
        "menu_open": "🧠 Ouvrir / Fermer le Notebook",
        "new": "➕ Nouveau",
        "new_folder": "📁 Nouveau dossier",
        "new_subfolder": "📁 Nouveau sous-dossier",
        "new_note": "📝 Nouvelle note",
        "new_note_here": "📝 Nouvelle note ici",
        "folder_name": "Nom du dossier :",
        "note_name": "Nom (sans .md) :",
        "rename": "✏️ Renommer",
        "delete": "🗑️ Supprimer",
        "confirm_delete": "Supprimer « {name} » ?",
        "delete_error": "Impossible de supprimer le fichier",
        "updated_folder": "Dossier mis à jour",
        "choose_folder": "Choisir un dossier",
        "new_folder_set": "Nouveau dossier sélectionné",
        "search": "Rechercher",
        "search_placeholder": "Tapez un mot-clé...",
        "search_label": "Rechercher dans toutes les notes :",
        "save": "💾 Sauvegarder",
        "placeholder_note": "Écris tes notes ici...",
        "new_name": "Nouveau nom :",
        "error": "Erreur",
        "change_dir": "📁 Changer le dossier"
    },
    "en": {
        "dock_title": "Notebook",
        "menu_open": "🧠 Open / Close Notebook",
        "new": "➕ New",
        "new_folder": "📁 New Folder",
        "new_subfolder": "📁 New Subfolder",
        "new_note": "📝 New Note",
        "new_note_here": "📝 New Note Here",
        "folder_name": "Folder name:",
        "note_name": "Name (without .md):",
        "rename": "✏️ Rename",
        "delete": "🗑️ Delete",
        "confirm_delete": "Delete “{name}”?",
        "delete_error": "Failed to delete file",
        "updated_folder": "Folder updated",
        "choose_folder": "Choose Folder",
        "new_folder_set": "New folder selected",
        "search": "Search",
        "search_placeholder": "Type a keyword...",
        "search_label": "Search across all notes:",
        "save": "💾 Save",
        "placeholder_note": "Write your notes here...",
        "new_name": "New name:",
        "error": "Error",
        "change_dir": "📁 Change Folder"
    },
}

def t(key, **kwargs):
    value = translations.get(LANG, {}).get(key, key)
    return value.format(**kwargs)

def get_language_label():
    return "🌐 Langue : Français" if LANG == "fr" else "🌐 Language : English"

def toggle_language(action=None):
    global LANG
    LANG = "en" if LANG == "fr" else "fr"
    save_language()
    if action:
        action.setText(get_language_label())
    print(f"[Notebook] Langue changée : {LANG}")

load_language()

