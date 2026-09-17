# DWH_Load_Clients

Synchronise quotidiennement les clients du CRM vers l'entrepôt de données (DWH).

| Champ | Valeur |
|---|---|
| Propriétaire | corentin.poirier |
| Version | 0.1 |
| Planification | _Non renseigné_ |
| Source du parsing | item |

## Objectif métier

Alimenter le référentiel clients pour le reporting BI.

## Systèmes source

_Non renseigné_

## Systèmes cible

_Non renseigné_

## Schéma du flux

_Aucune capture d'écran associée à ce job (dépose une image nommée `DWH_Load_Clients.png` dans le dossier `screenshots/`)._

```mermaid
flowchart LR
    tFileInputDelimited_1["tFileInputDelimited_1<br/><i>tFileInputDelimited</i>"]
    tMap_1["tMap_1<br/><i>tMap</i>"]
    tDBOutput_1["tDBOutput_1<br/><i>tDBOutput</i>"]
    tLogRow_1["tLogRow_1<br/><i>tLogRow</i>"]
    tFileInputDelimited_1 -->|row1| tMap_1
    tMap_1 -->|row2| tDBOutput_1
    tMap_1 -.->|rejet| tLogRow_1
    classDef source fill:#DBEAFE,stroke:#2563EB,stroke-width:1px,color:#1e293b;
    class tFileInputDelimited_1 source;
    classDef transform fill:#FEF3C7,stroke:#D97706,stroke-width:1px,color:#1e293b;
    class tMap_1 transform;
    classDef target fill:#DCFCE7,stroke:#16A34A,stroke-width:1px,color:#1e293b;
    class tDBOutput_1 target;
    classDef other fill:#F1F5F9,stroke:#64748B,stroke-width:1px,color:#1e293b;
    class tLogRow_1 other;
```

## Composants

| Nom | Type | Description |
|---|---|---|
| tFileInputDelimited_1 | tFileInputDelimited | Lit le fichier CSV des clients exporté par le CRM |
| tMap_1 | tMap | Nettoyage et mapping des colonnes clients |
| tDBOutput_1 | tDBOutput | Insertion dans la table clients de l'entrepôt de données |
| tLogRow_1 | tLogRow | _Non renseigné_ |

## Connexions

| De | Vers | Type | Nature |
|---|---|---|---|
| tFileInputDelimited_1 | tMap_1 | row1 | Flux principal |
| tMap_1 | tDBOutput_1 | row2 | Flux principal |
| tMap_1 | tLogRow_1 | rejet | Rejet |
