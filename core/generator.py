from docx import Document
from datetime import datetime


def remplacer_dans_paragraphe(paragraph, mapping):
    """Remplace les placeholders même s'ils sont splitté sur plusieurs runs."""
    # Reconstitue le texte complet
    texte_complet = "".join(run.text for run in paragraph.runs)
    
    # Vérifie si un placeholder est présent
    if not any(k in texte_complet for k in mapping):
        return

    # Applique les remplacements
    for k, v in mapping.items():
        texte_complet = texte_complet.replace(k, v)

    # Réécrit tout dans le premier run, vide les autres
    if paragraph.runs:
        paragraph.runs[0].text = texte_complet
        for run in paragraph.runs[1:]:
            run.text = ""


def remplacer_placeholder(doc, mapping):
    # Paragraphes du corps
    for p in doc.paragraphs:
        remplacer_dans_paragraphe(p, mapping)

    # Tableaux
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    remplacer_dans_paragraphe(p, mapping)

    # En-têtes et pieds de page
    for section in doc.sections:
        for p in section.header.paragraphs:
            remplacer_dans_paragraphe(p, mapping)
        for p in section.footer.paragraphs:
            remplacer_dans_paragraphe(p, mapping)


def generer_lettre(template_path, output_path, entreprise, poste):
    doc = Document(template_path)
    mapping = {
        "{entreprise}": entreprise,
        "{poste}": poste,
        "{date}": datetime.now().strftime("%d/%m/%Y"),
    }
    remplacer_placeholder(doc, mapping)
    doc.save(output_path)