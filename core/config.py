import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

TEMPLATE_DEFAULT = os.path.join(TEMPLATE_DIR, "lettre_template.docx")
TEMPLATE_DEFENSE = os.path.join(TEMPLATE_DIR, "lettre_template_defense.docx")

OUTPUT_DOCX = os.path.join(OUTPUT_DIR, "lettre_generee.docx")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "lettre_generee.pdf")