import tkinter as tk
from tkinter import ttk, messagebox
import os

from core.generator import generer_lettre
from core.profil import charger_profil, sauvegarder_profil
from core.historique import charger_historique, ajouter_entree
from core.ia_generator import generer_lettre_ia
from export.pdf_exporter import docx_to_pdf
from core.config import OUTPUT_DOCX, TEMPLATE_DEFAULT, TEMPLATE_DEFENSE, get_output_pdf, TEMPLATE_DIR


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de lettres")
        self.root.geometry("560x560")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_generer = ttk.Frame(notebook)
        self.frame_ia = ttk.Frame(notebook)
        self.frame_profil = ttk.Frame(notebook)
        self.frame_historique = ttk.Frame(notebook)

        notebook.add(self.frame_generer, text="✉ Générer")
        notebook.add(self.frame_ia, text="🤖 Lettre IA")
        notebook.add(self.frame_profil, text="👤 Mon profil")
        notebook.add(self.frame_historique, text="📋 Historique")

        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._build_generer(self.frame_generer)
        self._build_ia(self.frame_ia)
        self._build_profil(self.frame_profil)
        self._build_historique(self.frame_historique)

    # ------------------------------------------------------------------ #
    #  ONGLET GÉNÉRER (manuel, sans IA)
    # ------------------------------------------------------------------ #

    def _build_generer(self, frame):
        self.type_job = "autre"
        self.output_pdf_courant = None

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
    #  ONGLET LETTRE IA
    # ------------------------------------------------------------------ #

    def _build_ia(self, frame):
        tk.Label(frame, text="Nom de l'entreprise").pack(pady=(15, 2))
        self.entry_ia_entreprise = tk.Entry(frame, width=45)
        self.entry_ia_entreprise.pack()

        tk.Label(frame, text="Intitulé du poste").pack(pady=(10, 2))
        self.entry_ia_poste = tk.Entry(frame, width=45)
        self.entry_ia_poste.pack()

        tk.Label(frame, text="Colle le texte de l'offre d'emploi").pack(pady=(10, 2))

        text_container = tk.Frame(frame)
        text_container.pack(fill="both", expand=True, padx=15)

        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side="right", fill="y")

        self.text_offre = tk.Text(text_container, height=10, width=55, wrap="word",
                                   yscrollcommand=scrollbar.set)
        self.text_offre.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_offre.yview)

        self.btn_generer_ia = tk.Button(frame, text="🤖 Générer la lettre avec l'IA",
                                         command=self.generer_avec_ia, width=28)
        self.btn_generer_ia.pack(pady=12)

        self.label_status_ia = tk.Label(frame, text="", wraplength=480, justify="left")
        self.label_status_ia.pack(pady=4, padx=15)

    # ------------------------------------------------------------------ #
    #  ONGLET PROFIL
    # ------------------------------------------------------------------ #

    def _build_profil(self, frame):
        profil = charger_profil()

        champs = [
            ("Prénom", "prenom"),
            ("Nom", "nom"),
            ("Email", "email"),
            ("Téléphone", "telephone"),
        ]

        self.profil_entries = {}
        for label, cle in champs:
            tk.Label(frame, text=label).pack(pady=(10, 2))
            entry = tk.Entry(frame, width=40)
            entry.insert(0, profil.get(cle, ""))
            entry.pack()
            self.profil_entries[cle] = entry

        tk.Label(frame, text="Clé API Gemini").pack(pady=(15, 2))
        entry_api = tk.Entry(frame, width=40, show="•")
        entry_api.insert(0, profil.get("api_key", ""))
        entry_api.pack()
        self.profil_entries["api_key"] = entry_api

        tk.Button(frame, text="💾 Sauvegarder le profil", command=self.sauvegarder, width=26).pack(pady=15)
        self.label_profil_status = tk.Label(frame, text="")
        self.label_profil_status.pack()

    # ------------------------------------------------------------------ #
    #  ONGLET HISTORIQUE
    # ------------------------------------------------------------------ #

    def _build_historique(self, frame):
        tk.Label(frame, text="Lettres générées", font=("Segoe UI", 11, "bold")).pack(pady=(12, 6))

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", padx=10)
        tk.Button(btn_frame, text="🔄 Rafraîchir", command=self._rafraichir_historique).pack(side="left")

        container = tk.Frame(frame)
        container.pack(fill="both", expand=True, padx=10, pady=6)

        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        self.canvas_historique = tk.Canvas(container, yscrollcommand=scrollbar.set, bg="#f9f9f9")
        self.canvas_historique.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas_historique.yview)

        self.frame_liste = tk.Frame(self.canvas_historique, bg="#f9f9f9")
        self.canvas_window = self.canvas_historique.create_window((0, 0), window=self.frame_liste, anchor="nw")

        self.frame_liste.bind("<Configure>", lambda e: self.canvas_historique.configure(
            scrollregion=self.canvas_historique.bbox("all")
        ))

        self._rafraichir_historique()

    def _rafraichir_historique(self):
        for widget in self.frame_liste.winfo_children():
            widget.destroy()

        historique = charger_historique()

        if not historique:
            tk.Label(self.frame_liste, text="Aucune lettre générée pour l'instant.",
                     bg="#f9f9f9", fg="gray").pack(pady=20)
            return

        for entree in historique:
            self._build_entree_historique(entree)

    def _build_entree_historique(self, entree):
        pdf_existe = os.path.exists(entree["pdf_path"])

        card = tk.Frame(self.frame_liste, bg="white", relief="solid", bd=1)
        card.pack(fill="x", padx=6, pady=4, ipadx=8, ipady=6)

        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(side="left", fill="x", expand=True)

        tk.Label(info_frame, text=f"🏢 {entree['entreprise']}  —  {entree['poste']}",
                 font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"📅 {entree['date']}   📄 {entree['template']}",
                 font=("Segoe UI", 8), fg="gray", bg="white").pack(anchor="w")

        if pdf_existe:
            tk.Button(card, text="📂 Ouvrir", width=9,
                      command=lambda p=entree["pdf_path"]: os.startfile(p)
                      ).pack(side="right", padx=6)
        else:
            tk.Label(card, text="PDF introuvable", fg="red", bg="white",
                     font=("Segoe UI", 8)).pack(side="right", padx=6)

    # ------------------------------------------------------------------ #
    #  LOGIQUE — ONGLET GÉNÉRER (manuel)
    # ------------------------------------------------------------------ #

    def _on_tab_changed(self, event):
        tab = event.widget.tab("current", "text")
        if "Historique" in tab:
            self._rafraichir_historique()

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

        self.output_pdf_courant = get_output_pdf(entreprise, poste)
        self._template_courant = TEMPLATE_DEFENSE if self.type_job == "defense" else TEMPLATE_DEFAULT
        self._entreprise_courante = entreprise
        self._poste_courant = poste
        self._contenu_ia_courant = None

        generer_lettre(self._template_courant, OUTPUT_DOCX, entreprise, poste)

        self.btn_generer.config(state=tk.DISABLED)
        self.label_status.config(text="Conversion en cours…", fg="gray")

        docx_to_pdf(OUTPUT_DOCX, self.output_pdf_courant, callback=lambda: self._on_pdf_done(source="generer"))

    # ------------------------------------------------------------------ #
    #  LOGIQUE — ONGLET LETTRE IA
    # ------------------------------------------------------------------ #

    def generer_avec_ia(self):
        entreprise = self.entry_ia_entreprise.get().strip()
        poste = self.entry_ia_poste.get().strip()
        offre_texte = self.text_offre.get("1.0", "end").strip()

        if not entreprise or not poste or not offre_texte:
            self.label_status_ia.config(text="⚠ Remplis l'entreprise, le poste et colle l'offre.", fg="orange")
            return

        profil = charger_profil()
        api_key = profil.get("api_key", "").strip()

        if not api_key:
            self.label_status_ia.config(
                text="⚠ Aucune clé API renseignée. Va dans l'onglet 'Mon profil'.", fg="red")
            return

        self.btn_generer_ia.config(state=tk.DISABLED)
        self.label_status_ia.config(text="🤖 Analyse de l'offre et génération en cours…", fg="gray")
        self.root.update_idletasks()

        try:
            resultat_ia = generer_lettre_ia(offre_texte, entreprise, poste, api_key)
        except Exception as e:
            self.btn_generer_ia.config(state=tk.NORMAL)
            self.label_status_ia.config(text=f"❌ Erreur IA : {e}", fg="red")
            return

        template_nom = resultat_ia.get("template", "lettre_template.docx")
        template_path = os.path.join(TEMPLATE_DIR, template_nom)

        if not os.path.exists(template_path):
            template_path = TEMPLATE_DEFAULT

        self.output_pdf_courant = get_output_pdf(entreprise, poste)
        self._template_courant = template_path
        self._entreprise_courante = entreprise
        self._poste_courant = poste
        self._contenu_ia_courant = resultat_ia

        generer_lettre(template_path, OUTPUT_DOCX, entreprise, poste, contenu_ia=resultat_ia)

        raison = resultat_ia.get("raison_template", "")
        self.label_status_ia.config(
            text=f"📄 Template choisi : {template_nom}\n💡 {raison}\n\nConversion PDF en cours…",
            fg="gray")

        docx_to_pdf(OUTPUT_DOCX, self.output_pdf_courant, callback=lambda: self._on_pdf_done(source="ia"))

    # ------------------------------------------------------------------ #
    #  LOGIQUE COMMUNE
    # ------------------------------------------------------------------ #

    def _on_pdf_done(self, source):
        if os.path.exists(OUTPUT_DOCX):
            os.remove(OUTPUT_DOCX)

        ajouter_entree(
            entreprise=self._entreprise_courante,
            poste=self._poste_courant,
            template=self._template_courant,
            pdf_path=self.output_pdf_courant
        )

        self.root.after(0, lambda: self._update_ui_done(source))

    def _update_ui_done(self, source):
        if source == "generer":
            self.btn_generer.config(state=tk.NORMAL)
            self.label_status.config(text="PDF généré ✔", fg="green")
        else:
            self.btn_generer_ia.config(state=tk.NORMAL)
            raison = self._contenu_ia_courant.get("raison_template", "")
            template_nom = os.path.basename(self._template_courant)
            self.label_status_ia.config(
                text=f"✔ PDF généré avec succès\n📄 Template : {template_nom}\n💡 {raison}",
                fg="green")

        os.startfile(self.output_pdf_courant)