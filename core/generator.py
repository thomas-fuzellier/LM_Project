from docx import Document
from datetime import datetime


def remplacer_placeholder(doc, mapping):
    for p in doc.paragraphs:
        for k, v in mapping.items():
            if k in p.text:
                p.text = p.text.replace(k, v)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for k, v in mapping.items():
                    if k in cell.text:
                        cell.text = cell.text.replace(k, v)


def generer_lettre(template_path, output_path, entreprise, poste):
    doc = Document(template_path)

    mapping = {
        "{entreprise}": entreprise,
        "{poste}": poste,
        "{date}": datetime.now().strftime("%d/%m/%Y")
    }

    remplacer_placeholder(doc, mapping)
    doc.save(output_path)