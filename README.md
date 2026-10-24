# Data Pipeline App : analyse des avis Trustpilot sur BoursoBank

Application Python qui collecte les avis clients publiés sur Trustpilot à propos de
BoursoBank, les stocke dans une base SQLite, les analyse avec pandas et des techniques
de NLP, puis les présente dans un dashboard interactif.

Projet Fil Rouge du cours *Introduction à Python*, Master MSID, EMLV (2026-2027).

## Avancement

- [x] **Étape 1 : Collecte** : scraping des avis Trustpilot avec Playwright, export CSV
- [x] **Étape 2 : Stockage** : base SQLite, insertion incrémentale sans doublons, requêtes SQL
- [x] **Analyse exploratoire** : notebook pandas (notes, évolution, types d'avis, mots fréquents)
- [ ] **Analyse de sentiment** : approche naïve et librairie NLP
- [ ] **Dashboard** : application Streamlit avec filtres et graphiques Plotly
- [ ] **Extension**

## Architecture du pipeline

```
Trustpilot ──► collect.py ──► data/raw/*.csv ──► storage.py ──► data/reviews.db ──► analyse / dashboard
 (Playwright)                 (données brutes)                  (SQLite)
```

## Structure du projet

```
Data_Pipeline_App/
├── data/
│   ├── raw/                 # CSV bruts issus de la collecte
│   └── reviews.db           # base SQLite (générée, non versionnée)
├── notebooks/
│   └── 01_analyse_exploratoire.ipynb
├── src/
│   ├── collect.py           # collecte des avis (Playwright + extraction JSON)
│   ├── storage.py           # création de la base et insertion des avis
│   ├── queries.py           # requêtes SQL de base
│   ├── explore.py           # script d'exploration initiale du site
│   └── inspect_json.py      # inspection de la structure des données
├── requirements.txt
└── README.md
```

## Installation

Prérequis : Python 3.10 ou plus récent, Git, et un environnement Linux ou WSL.

```bash
git clone https://github.com/hocineb18/Data_Pipeline_App.git
cd Data_Pipeline_App
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
```

La dernière commande installe le navigateur Chromium utilisé pour la collecte.

## Utilisation

Toutes les commandes se lancent depuis la racine du projet, avec l'environnement
virtuel activé.

**1. Collecter les avis** (une fenêtre Chromium s'ouvre pendant quelques minutes) :

```bash
python src/collect.py
```

**2. Les insérer dans la base SQLite :**

```bash
python src/storage.py
```

La base `data/reviews.db` est créée au premier lancement. Les lancements suivants
n'ajoutent que les avis nouveaux. Pour une mise à jour complète :

```bash
python src/collect.py && python src/storage.py
```

**3. Afficher les statistiques de base :**

```bash
python src/queries.py
```

**4. Ouvrir l'analyse exploratoire :**

```bash
jupyter notebook --no-browser
```

puis ouvrir `notebooks/01_analyse_exploratoire.ipynb` et exécuter toutes les cellules.

## Choix techniques

- **Playwright plutôt que requests** : Trustpilot bloque les requêtes HTTP classiques
  (erreur 403). Playwright pilote un vrai navigateur, qui passe la vérification anti-robot.
- **Extraction depuis le JSON intégré** : les avis sont lus dans le bloc `__NEXT_DATA__`
  de la page plutôt que dans les balises HTML, dont les noms de classes changent
  régulièrement. Le JSON est plus stable et plus complet.
- **Collecte respectueuse** : pause aléatoire de 2 à 5 secondes entre les pages.
- **Mise à jour incrémentale** : `review_id` est la clé primaire de la table `reviews`,
  et l'insertion utilise `INSERT OR IGNORE` : un avis déjà présent n'est jamais dupliqué.
- **Requêtes paramétrées** : protection contre les injections SQL.
- **Minimisation des données personnelles** : seul le pseudo de l'auteur est conservé.

## Schéma de la base

| Table | Contenu |
|---|---|
| `sources` | Entreprises collectées : nom, plateforme, URL |
| `reviews` | Avis : identifiant, titre, texte, note (1-5), date, auteur, pays, langue, type d'avis (sollicité ou spontané), réponse de l'entreprise, likes, date de collecte |

## Premiers résultats

- Note moyenne de **4,43/5**, avec une distribution très polarisée (78 % de 5 étoiles, 11 % de 1 étoile).
- Les avis **sollicités** par l'entreprise ont une moyenne de **4,74**, contre **1,95** pour les avis **spontanés**.
- Principaux sujets de mécontentement : carte bancaire, accessibilité du service client, recours aux chatbots.

## Limites connues

- Trustpilot n'affiche que 10 pages (200 avis) aux visiteurs non connectés. Vu le volume
  d'avis reçus par BoursoBank, une collecte couvre seulement quelques jours. Des collectes
  régulières permettent d'accumuler un historique dans la base.

## Auteur

Hocine Baleh
