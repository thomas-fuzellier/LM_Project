import json
import os
import requests

CV_PARSED_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cv_parsed.json")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

PARAGRAPHE_EXPERIENCE_DEFAUT = (
    "Ingénieur diplômé en informatique et système, je dispose d'une première expérience en "
    "développement logiciel en C/C++, incluant le développement sur systèmes embarqués, "
    "l'intégration sur matériel ainsi que les phases de tests et de validation. J'évolue "
    "également dans des environnements Linux, ce qui me permet d'appréhender efficacement "
    "les problématiques d'intégration et de performance sur des systèmes complexes."
)

PARAGRAPHE_PROJETS_DEFAUT = (
    "Au cours de mes expériences, j'ai été amené à travailler sur des projets mêlant logiciel "
    "et matériel, avec des enjeux d'analyse, de diagnostic et de résolution de problèmes "
    "techniques. Cette approche globale du cycle de développement, de la conception à la "
    "validation, correspond pleinement aux missions proposées sur vos projets."
)


def charger_cv() -> dict:
    if not os.path.exists(CV_PARSED_PATH):
        raise FileNotFoundError("cv_parsed.json introuvable. Place-le à la racine du projet.")
    with open(CV_PARSED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generer_lettre_ia(offre_texte: str, entreprise: str, poste: str, api_key: str) -> dict:
    cv = charger_cv()

    system_prompt = f"""Tu es un assistant qui personnalise une lettre de motivation.
Tu reçois le CV structuré d'un candidat et une offre d'emploi.

Réponds UNIQUEMENT en JSON valide, sans texte autour, sans markdown, avec cette structure exacte :

{{
  "template": "lettre_template_defense.docx" ou "lettre_template.docx",
  "raison_template": "courte explication du choix",
  "accroche": "paragraphe d'accroche de 3-4 phrases (utilisé seulement si template civil)",
  "experience_principale": "paragraphe de 4-5 phrases sur l'expérience pertinente (utilisé seulement si template civil)",
  "competences_cles": "une phrase listant les compétences clés (utilisé seulement si template civil)",
  "conclusion": "paragraphe de clôture (utilisé seulement si template civil)",
  "paragraphe_experience": "paragraphe technique pour le template défense",
  "paragraphe_projets": "paragraphe sur les projets pour le template défense"
}}

RÈGLES POUR LE CHOIX DU TEMPLATE :
- "lettre_template_defense.docx" UNIQUEMENT si l'entreprise opère dans la défense, l'armement, le militaire, ou si l'offre mentionne habilitation/secret défense/DGA
- "lettre_template.docx" pour tout le reste

RÈGLES SPÉCIFIQUES AU TEMPLATE DÉFENSE :
Le template défense a une structure et un ton FIXES (mentions de la souveraineté, de la sécurité,
et de la réserve opérationnelle ne doivent jamais être modifiées). Seuls deux paragraphes sont adaptables :

Voici les paragraphes PAR DÉFAUT, déjà bien écrits et alignés avec le ton de la lettre :

paragraphe_experience (défaut) :
"{PARAGRAPHE_EXPERIENCE_DEFAUT}"

paragraphe_projets (défaut) :
"{PARAGRAPHE_PROJETS_DEFAUT}"

→ Si l'offre ne donne pas de raison claire de dévier (poste similaire : embarqué, C/C++, systèmes),
GARDE CES PARAGRAPHES QUASIMENT TELS QUELS (tu peux ajuster légèrement le vocabulaire pour coller à l'offre).
→ Si l'offre cible un domaine clairement différent visible dans le CV (ex: IA/data au lieu d'embarqué),
ADAPTE ces deux paragraphes en piochant dans les expériences du CV pertinentes pour CE poste précis,
tout en gardant le même ton sobre et professionnel que l'original.
→ Ne jamais inventer d'informations absentes du CV.

RÈGLES GÉNÉRALES :
- Le candidat est un homme : utilise systématiquement des formulations masculines
  ("motivé", "diplômé", "ingénieur" — jamais "motivé(e)", "diplômé(e)", "ingénieur(e)")
- Sélectionne l'expérience la plus pertinente selon les tags qui matchent l'offre
- Écris à la première personne
- Ton professionnel, sobre, jamais familier

STYLE D'ÉCRITURE (pour sonner humain, pas généré par IA) :
- Évite les formulations creuses et génériques type "passionné par les nouvelles technologies",
  "fort de mon expérience", "je suis convaincu que mon profil correspond parfaitement"
- Varie la longueur des phrases : alterne phrases courtes et plus longues, évite que chaque
  phrase suive la même structure (sujet-verbe-complément répété)
- Préfère des détails concrets et factuels (technologies, résultats, contexte précis) plutôt
  que des qualificatifs vagues ("rigoureux", "dynamique", "polyvalent")
- N'utilise pas de tournures ronflantes ou trop ambitieuses ("révolutionner", "exceller",
  "impact significatif") — reste factuel et mesuré
- Évite de commencer systématiquement les phrases par "Je" — varie les amorces
- N'utilise jamais de tirets cadratins (—) ni de formulations trop "marketing"
"""

    user_prompt = f"""CV du candidat :
{json.dumps(cv, ensure_ascii=False, indent=2)}

Entreprise : {entreprise}
Poste : {poste}

Offre d'emploi :
{offre_texte}
"""

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(
        f"{GEMINI_URL}?key={api_key}",
        json=payload,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    texte_reponse = data["candidates"][0]["content"]["parts"][0]["text"]

    resultat = json.loads(texte_reponse)

    # Filet de sécurité : si l'IA oublie un champ défense, on retombe sur le défaut
    resultat.setdefault("paragraphe_experience", PARAGRAPHE_EXPERIENCE_DEFAUT)
    resultat.setdefault("paragraphe_projets", PARAGRAPHE_PROJETS_DEFAUT)

    return resultat