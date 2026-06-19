import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

TEMPLATE_DEFAULT = os.path.join(TEMPLATE_DIR, "lettre_template.docx")
TEMPLATE_DEFENSE = os.path.join(TEMPLATE_DIR, "lettre_template_defense.docx")

OUTPUT_DOCX = os.path.join(OUTPUT_DIR, "_temp_lettre.docx")  # fichier temporaire fixe


def get_output_pdf(entreprise: str, poste: str) -> str:
    """Génère un nom de fichier PDF unique basé sur l'entreprise, le poste et la date."""
    date = datetime.now().strftime("%Y-%m-%d")

    # Nettoie les caractères invalides pour un nom de fichier
    def nettoyer(s):
        return "".join(c for c in s if c.isalnum() or c in " -_").strip().replace(" ", "_")

    nom = f"cover_letter_{nettoyer(entreprise)}_{nettoyer(poste)}_{date}.pdf"
    return os.path.join(OUTPUT_DIR, nom)