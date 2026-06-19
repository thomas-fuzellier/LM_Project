import tkinter as tk
from tkinter import ttk, messagebox
import os

from core.generator import generer_lettre
from core.profil import charger_profil, sauvegarder_profil
from export.pdf_exporter import docx_to_pdf
from core.config import OUTPUT_DOCX, OUTPUT_PDF, TEMPLATE_DEFAULT, TEMPLATE_DEFENSE


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de lettres")
        self.root.geometry("460x400")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Onglets ---
        self.frame_generer = ttk.Frame(notebook)
        self.frame_profil = ttk.Frame(notebook)
        notebook.add(self.frame_generer, text="✉ Générer")
        notebook.add(self.frame_profil, text="👤 Mon profil")

        self._build_generer(self.frame_generer)
        self._build_profil(self.frame_profil)

    # ------------------------------------------------------------------ #
    #  ONGLET GÉNÉRER
    # ------------------------------------------------------------------ #

    def _build_generer(self, frame):
        self.type_job = "autre"

        tk.Label(frame, text="Nom de l'entreprise").pack(pady=(15, 2))
        self.entry_entreprise = tk.Entry(frame, width=40)
        self.entry_entreprise.pack()

        tk.Label(frame, text="Nom du poste").pack(pady=(10, 2))
        self.entry_poste = tk.Entry(frame, width=40)
        self.entry_poste.pack()

        self.btn_type = tk.Button(frame, text="Secteur : autre", command=self.toggle_type, width=22)
        self.btn_type.pack(pady=12)

        self.btn_generer = tk.Button(frame, text="Générer PDF", command=self.generer, width=22)
        self.btn_generer.pack()

        self.label_status = tk.Label(frame, text="")
        self.label_status.pack(pady=8)

    # ------------------------------------------------------------------ #
    #  ONGLET PROFIL
    # ------------------------------------------------------------------ #

    def _build_profil(self, frame):
        profil = charger_profil()

        champs = [
            ("Prénom",    "prenom"),
            ("Nom",       "nom"),
            ("Email",     "email"),
            ("Téléphone", "telephone"),
        ]

        self.profil_entries = {}

        for label, cle in champs:
            tk.Label(frame, text=label).pack(pady=(10, 2))
            entry = tk.Entry(frame, width=40)
            entry.insert(0, profil.get(cle, ""))
            entry.pack()
            self.profil_entries[cle] = entry

        tk.Button(frame, text="💾 Sauvegarder le profil", command=self.sauvegarder, width=26).pack(pady=15)
        self.label_profil_status = tk.Label(frame, text="")
        self.label_profil_status.pack()

    # ------------------------------------------------------------------ #
    #  LOGIQUE
    # ------------------------------------------------------------------ #

    def toggle_type(self):
        if self.type_job == "defense":
            self.type_job = "autre"
            self.btn_type.config(text="Secteur : autre")
        else:
            self.type_job = "defense"
            self.btn_type.config(text="Secteur : défense")

    def sauvegarder(self):
        profil = {cle: entry.get().strip() for cle, entry in self.profil_entries.items()}
        sauvegarder_profil(profil)
        self.label_profil_status.config(text="Profil sauvegardé ✔", fg="green")

    def generer(self):
        entreprise = self.entry_entreprise.get().strip()
        poste = self.entry_poste.get().strip()

        if not entreprise or not poste:
            self.label_status.config(text="⚠ Remplis tous les champs.", fg="orange")
            return

        template = TEMPLATE_DEFENSE if self.type_job == "defense" else TEMPLATE_DEFAULT
        generer_lettre(template, OUTPUT_DOCX, entreprise, poste)

        self.btn_generer.config(state=tk.DISABLED)
        self.label_status.config(text="Conversion en cours…", fg="gray")

        docx_to_pdf(OUTPUT_DOCX, OUTPUT_PDF, callback=self._on_pdf_done)

    def _on_pdf_done(self):
        if os.path.exists(OUTPUT_DOCX):
            os.remove(OUTPUT_DOCX)
        self.root.after(0, self._update_ui_done)

    def _update_ui_done(self):
        self.btn_generer.config(state=tk.NORMAL)
        self.label_status.config(text="PDF généré ✔", fg="green")