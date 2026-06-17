import tkinter as tk
import os

from core.generator import generer_lettre
from export.pdf_exporter import docx_to_pdf
from core.config import (
    OUTPUT_DOCX,
    OUTPUT_PDF,
    TEMPLATE_DEFAULT,
    TEMPLATE_DEFENSE
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de lettres")
        self.root.geometry("420x320")

        self.type_job = "autre"

        tk.Label(root, text="Nom de l'entreprise").pack()
        self.entry_entreprise = tk.Entry(root, width=40)
        self.entry_entreprise.pack()

        tk.Label(root, text="Nom du poste").pack()
        self.entry_poste = tk.Entry(root, width=40)
        self.entry_poste.pack()

        self.btn_type = tk.Button(
            root,
            text="Secteur : autre",
            command=self.toggle_type
        )
        self.btn_type.pack(pady=10)

        tk.Button(
            root,
            text="Générer PDF",
            command=self.generer
        ).pack(pady=10)

        self.label_status = tk.Label(root, text="")
        self.label_status.pack()

    def toggle_type(self):
        if self.type_job == "defense":
            self.type_job = "autre"
            self.btn_type.config(text="Secteur : autre")
        else:
            self.type_job = "defense"
            self.btn_type.config(text="Secteur : défense")

    def generer(self):
        entreprise = self.entry_entreprise.get().strip()
        poste = self.entry_poste.get().strip()

        template = TEMPLATE_DEFENSE if self.type_job == "defense" else TEMPLATE_DEFAULT

        generer_lettre(template, OUTPUT_DOCX, entreprise, poste)
        docx_to_pdf(OUTPUT_DOCX, OUTPUT_PDF)

        if os.path.exists(OUTPUT_DOCX):
            os.remove(OUTPUT_DOCX)

        self.label_status.config(text="PDF généré ✔")