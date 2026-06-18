import tkinter as tk
import os

from core.generator import generer_lettre
from export.pdf_exporter import docx_to_pdf
from core.config import OUTPUT_DOCX, OUTPUT_PDF, TEMPLATE_DEFAULT, TEMPLATE_DEFENSE


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

        self.btn_type = tk.Button(root, text="Secteur : autre", command=self.toggle_type)
        self.btn_type.pack(pady=10)

        self.btn_generer = tk.Button(root, text="Générer PDF", command=self.generer)
        self.btn_generer.pack(pady=10)

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

        if not entreprise or not poste:
            self.label_status.config(text="⚠ Remplis tous les champs.")
            return

        template = TEMPLATE_DEFENSE if self.type_job == "defense" else TEMPLATE_DEFAULT

        # Génération du .docx (instantané)
        generer_lettre(template, OUTPUT_DOCX, entreprise, poste)

        # Désactiver le bouton pendant la conversion
        self.btn_generer.config(state=tk.DISABLED)
        self.label_status.config(text="Conversion en cours…")

        # Conversion PDF en arrière-plan
        docx_to_pdf(OUTPUT_DOCX, OUTPUT_PDF, callback=self._on_pdf_done)

    def _on_pdf_done(self):
        """Appelé depuis le thread de conversion une fois le PDF prêt."""
        if os.path.exists(OUTPUT_DOCX):
            os.remove(OUTPUT_DOCX)

        # Màj UI depuis le thread principal via `after`
        self.root.after(0, self._update_ui_done)

    def _update_ui_done(self):
        self.btn_generer.config(state=tk.NORMAL)
        self.label_status.config(text="PDF généré ✔")