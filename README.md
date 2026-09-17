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
- un **schéma généré automatiquement** (diagramme Mermaid) à partir des
  composants/connexions, en complément (ou à défaut) de la capture d'écran.

## Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Structure du projet

```
items/          Exports Talend : dépose ici les .item/.properties, ou un .zip
jobs/           Métadonnées manuelles YAML (un fichier par job)
screenshots/    Captures d'écran du canevas Talend (nommées comme le job)
docs/           Site généré (Markdown + HTML) — ne pas éditer à la main
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
- `docs/index.md` / `docs/index.html` : index de tous les flux.

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
