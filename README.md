# Talend Doc Gen

Génère automatiquement un site de documentation (Markdown + HTML) pour tes
flux d'intégration de données Talend, en combinant :

- le **parsing des exports Talend Studio** (fichiers `.item` / `.properties`,
  ou une archive `.zip` d'export) pour extraire composants, connexions et
  métadonnées ;
- des **métadonnées manuelles** (YAML) pour les jobs dont tu n'as pas
  l'export, ou pour enrichir un job déjà parsé (description métier,
  systèmes source/cible, planification, notes...) ;
- tes **captures d'écran** du canevas Talend, associées automatiquement par
  nom de job ;
- un **schéma généré automatiquement** (diagramme Mermaid, coloré par
  catégorie de composant) à partir des composants/connexions, en complément
  (ou à défaut) de la capture d'écran ;
- un **fichier Word (.docx) par flux**, mise en page soignée, prêt à être
  déposé dans une bibliothèque SharePoint.

## Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Les fichiers Word sont toujours générés (dépendance `python-docx`, installée
par défaut). Le schéma qui y est intégré utilise la capture d'écran quand
elle existe ; sinon, un rendu du diagramme Mermaid en image est tenté via le
paquet optionnel `playwright` (`pip install playwright && playwright install
chromium`) — sans lui, le fichier Word est quand même généré, avec un simple
message à la place de l'image.

## Structure du projet

```
items/          Exports Talend : dépose ici les .item/.properties, ou un .zip
                (non suivi par git par défaut, voir .gitignore — peut
                contenir des secrets dans les paramètres de contexte)
jobs/           Métadonnées manuelles YAML (un fichier par job)
screenshots/    Captures d'écran du canevas Talend (nommées comme le job)
docs/           Site généré (Markdown + HTML + Word) — ne pas éditer à la main
  jobs/           Pages Markdown + HTML, une par flux
  word/           Documents Word (.docx), un par flux — à déposer sur SharePoint
  assets/         CSS, captures d'écran copiées
talend_doc_gen/ Code de l'outil
tests/          Tests unitaires (pytest)
```

## Utilisation

### 1. Récupérer l'export d'un job Talend

Dans Talend Studio : clic droit sur le job → **Export items** → export en
`.zip`, ou récupère directement les fichiers `NomDuJob_0.1.item` et
`NomDuJob_0.1.properties` du workspace. Dépose-les dans `items/`.

### 2. Ajouter une capture d'écran du flux

Fais une capture du canevas du job dans Talend Studio et enregistre-la dans
`screenshots/` sous le nom **exact du job** (insensible à la casse, espaces
et tirets ignorés) : `NomDuJob.png` (formats acceptés : png, jpg, jpeg, gif,
webp).

### 3. (Optionnel) Documenter un flux sans export Talend

Si tu n'as pas le fichier `.item` (accès Studio non disponible, job légataire,
etc.), crée un fichier YAML dans `jobs/` — voir l'exemple
[`jobs/CRM_Export_Prospects.yaml`](jobs/CRM_Export_Prospects.yaml). Il peut
aussi servir à **enrichir** un job déjà parsé depuis un `.item` : mets le même
`name`, seuls les champs renseignés dans le YAML écrasent ceux du `.item`
(les composants/connexions du `.item` restent la source de vérité si le YAML
n'en définit pas).

### 4. Générer la documentation

```bash
python3 -m talend_doc_gen.cli generate \
  --items-dir items \
  --manual-dir jobs \
  --screenshots-dir screenshots \
  --out-dir docs
```

Cela génère, pour chaque job :

- `docs/jobs/<slug>.md` et `docs/jobs/<slug>.html` : description, systèmes
  source/cible, capture d'écran, schéma Mermaid, tableau des composants et
  des connexions, paramètres de contexte, notes ;
- `docs/word/<slug>.docx` : le même contenu, mis en page pour Word/SharePoint
  (fiche d'identité, tableaux colorés par catégorie de composant, schéma en
  image) ;
- `docs/index.md` / `docs/index.html` : index de tous les flux.

Par défaut, les **valeurs** des paramètres de contexte (hôtes, identifiants,
mots de passe chiffrés Talend...) sont masquées dans tous les formats — seuls
les noms de paramètres apparaissent. Utilise `--show-context-values`
uniquement dans un dépôt privé/de confiance pour les afficher en clair.

Pour consulter le site HTML, ouvre simplement `docs/index.html` dans un
navigateur (le diagramme Mermaid est rendu côté client via un CDN — une
connexion internet est nécessaire pour l'affichage graphique du schéma
généré ; le code Mermoid brut reste lisible sinon). Deux jobs d'exemple sont
déjà fournis (un avec export `.item`, un avec métadonnées manuelles) pour
que `docs/` soit navigable dès la première génération.

Relance la commande `generate` à chaque nouvel export ou capture d'écran
ajoutée : la documentation reste ainsi toujours synchronisée avec les flux
réels.

## Lancer les tests

```bash
pytest
```
