import json
import os

PROFIL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "profil.json")

PROFIL_DEFAUT = {
    "nom": "FUZELLIER",
    "prenom": "Thomas",
    "email": "thomas.fuzellier@outlook.fr",
    "telephone": "+33 (0) 6 10 48 41 37"
}


def charger_profil() -> dict:
    if not os.path.exists(PROFIL_PATH):
        sauvegarder_profil(PROFIL_DEFAUT)
        return PROFIL_DEFAUT.copy()
    with open(PROFIL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_profil(profil: dict):
    with open(PROFIL_PATH, "w", encoding="utf-8") as f:
        json.dump(profil, f, indent=2, ensure_ascii=False)