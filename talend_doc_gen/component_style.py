"""Classification heuristique des composants Talend par catégorie
fonctionnelle.

Un job Talend n'a pas de notion native de « catégorie » de composant : ce
module en déduit une à partir du nom technique du composant (ex:
``tFileInputDelimited`` -> source), uniquement pour colorer les schémas et
tableaux générés et en faciliter la lecture visuelle. C'est un simple
indice, pas une classification garantie exacte pour des composants
personnalisés/inhabituels.
"""

from __future__ import annotations

_ORCHESTRATION_HINTS = (
    "prejob",
    "postjob",
    "runjob",
    "ref_global",
    "connection",
    "close",
    "commit",
    "setglobalvar",
)
_SOURCE_HINTS = ("input", "filelist", "get")
_TARGET_HINTS = ("output", "put", "delete")
_TRANSFORM_HINTS = ("map", "filtercolumns", "java", "fixedflowinput")

# Couleurs (fond clair + bordure) réutilisées pour le diagramme Mermaid, les
# tableaux HTML/Word et leur légende.
CATEGORY_STYLE = {
    "orchestration": {"fill": "#EDE9FE", "stroke": "#7C3AED", "label_fr": "Orchestration"},
    "source": {"fill": "#DBEAFE", "stroke": "#2563EB", "label_fr": "Source"},
    "target": {"fill": "#DCFCE7", "stroke": "#16A34A", "label_fr": "Cible"},
    "transform": {"fill": "#FEF3C7", "stroke": "#D97706", "label_fr": "Transformation"},
    "other": {"fill": "#F1F5F9", "stroke": "#64748B", "label_fr": "Autre"},
}


def component_category(component_type: str) -> str:
    """Retourne 'orchestration' | 'source' | 'target' | 'transform' | 'other'."""
    t = (component_type or "").lower()
    if any(hint in t for hint in _ORCHESTRATION_HINTS):
        return "orchestration"
    if any(hint in t for hint in _SOURCE_HINTS):
        return "source"
    if any(hint in t for hint in _TARGET_HINTS):
        return "target"
    if any(hint in t for hint in _TRANSFORM_HINTS):
        return "transform"
    return "other"
