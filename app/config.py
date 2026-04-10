import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Excel directory resolution order:
# 1) EXCEL_DIR env var (absolute or relative to BASE_DIR)
# 2) Default to project parent folder to preserve local behavior
excel_dir_raw = (os.getenv("EXCEL_DIR") or "").strip()
if excel_dir_raw:
    excel_path = Path(excel_dir_raw).expanduser()
    EXCEL_DIR = (BASE_DIR / excel_path).resolve() if not excel_path.is_absolute() else excel_path.resolve()
else:
    EXCEL_DIR = BASE_DIR.parent.resolve()

CACHE_DIR = BASE_DIR / "cache"
HISTORY_DIR = CACHE_DIR / "history"
UPLOADS_DIR = BASE_DIR / "uploads"

# Create directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
HISTORY_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Excel file configurations
EXCEL_FILES = {
    "fiche_consommation": {
        "file_name": "Fiche_Complète_Contrôle_Approvisionnement_Interne.xlsx",
        "sheet_name": "FICHE CONSOMATION JOURNALIERE",
        "cache_file": "fiche_consommation.json"
    },
    "calcul_viande": {
        "file_name": "Calculateur_Ing_Viande 07,03,2026.xlsx",
        "sheet_name": "📊 Conso Journalière",
        "cache_file": "calcul_viande.json"
    },
    "emballage_synthese": {
        "file_name": "Calculateur_Emballage_V3.xlsx",
        "sheet_name": "Synthèse Totaux",
        "cache_file": "emballage_synthese.json"
    }
}

# API Configuration
API_TITLE = "Données Approvisionnement"
API_VERSION = "1.0.0"
REFRESH_INTERVAL = 3600  # 1 hour in seconds

# Authentication configuration (no DB)
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
# Preferred secure option: provide AUTH_PASSWORD_HASH.
# Optional fallback for quick setup: AUTH_PASSWORD (plain text), but less secure.
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-session-secret-please")
SESSION_COOKIE_NAME = "appro_session"
