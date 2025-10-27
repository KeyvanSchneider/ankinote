# storage.py — gestion des fichiers et dossiers du Notebook

import os

# --- Définition du dossier de base ---
# Par défaut : dans le dossier de l'utilisateur, sous /Documents/AnkiNotebook
DEFAULT_BASE = os.path.join(os.path.expanduser("~"), "Documents", "AnkiNotebook")


def ensure_base_path():
    """Crée le dossier de base s'il n'existe pas et le renvoie."""
    os.makedirs(DEFAULT_BASE, exist_ok=True)
    return DEFAULT_BASE


def list_folders():
    """Liste les dossiers présents dans le dossier principal."""
    ensure_base_path()
    return sorted([
        f for f in os.listdir(DEFAULT_BASE)
        if os.path.isdir(os.path.join(DEFAULT_BASE, f))
    ])


def list_notes(folder):
    """Liste les fichiers .md dans un dossier donné."""
    path = os.path.join(DEFAULT_BASE, folder)
    os.makedirs(path, exist_ok=True)
    return sorted([
        f for f in os.listdir(path)
        if f.endswith(".md") and os.path.isfile(os.path.join(path, f))
    ])


def create_folder(name):
    """Crée un dossier dans le répertoire principal."""
    path = os.path.join(DEFAULT_BASE, name)
    os.makedirs(path, exist_ok=True)
    return path


def create_note(folder, name):
    """Crée un fichier .md vide dans le dossier spécifié."""
    folder_path = os.path.join(DEFAULT_BASE, folder)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, name + ".md")
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
    return file_path


def load_markdown(file_path):
    """Charge le contenu texte d'un fichier Markdown."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""


def save_markdown(file_path, content):
    """Sauvegarde le texte brut dans un fichier Markdown."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"[Notebook] Erreur de sauvegarde : {e}")

