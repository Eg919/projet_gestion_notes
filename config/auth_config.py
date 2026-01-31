"""
Chargement des identifiants de connexion.

Ordre de priorité :
1. Variables d'environnement : GESTION_NOTES_USER, GESTION_NOTES_PASSWORD
2. Fichier protégé : config/credentials.json 
3. Valeurs par défaut (développement uniquement) : Admin / 1234

Pour la production : définir les variables d'environnement ou créer
config/credentials.json à partir de config/credentials.example.json.
"""
import json
import os

# Racine du projet (dossier parent de config/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CREDENTIALS_FILE = os.path.join(_PROJECT_ROOT, "config", "credentials.json")

# Noms des variables d'environnement
ENV_USER = "GESTION_NOTES_USER"
ENV_PASSWORD = "GESTION_NOTES_PASSWORD"

# Valeurs par défaut (développement uniquement)
DEFAULT_USER = "Admin"
DEFAULT_PASSWORD = "1234"


def load_credentials():
    """
    Charge les identifiants (username, password).

    Retourne un tuple (username: str, password: str).
    Utilise les variables d'environnement en priorité, puis le fichier
    config/credentials.json, puis les valeurs par défaut.
    """
    # 1. Variables d'environnement
    user = os.environ.get(ENV_USER, "").strip()
    password = os.environ.get(ENV_PASSWORD, "").strip()
    if user and password:
        return user, password

    # 2. Fichier protégé config/credentials.json
    if os.path.isfile(_CREDENTIALS_FILE):
        try:
            with open(_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                u = (data.get("username") or data.get("user") or "").strip()
                p = (data.get("password") or "").strip()
                if u and p:
                    return u, p
        except (OSError, json.JSONDecodeError):
            pass

    # 3. Valeurs par défaut (développement)
    return DEFAULT_USER, DEFAULT_PASSWORD
