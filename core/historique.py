import json
import os
from datetime import datetime

HISTORIQUE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "historique.json")


def charger_historique() -> list:
    if not os.path.exists(HISTORIQUE_PATH):
        return []
    with open(HISTORIQUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ajouter_entree(entreprise: str, poste: str, template: str, pdf_path: str):
    historique = charger_historique()
    historique.insert(0, {  # ← plus récent en premier
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "entreprise": entreprise,
        "poste": poste,
        "template": os.path.basename(template),
        "pdf_path": pdf_path
    })
    with open(HISTORIQUE_PATH, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=2, ensure_ascii=False)