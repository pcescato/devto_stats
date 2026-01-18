# Milestone Timeline - Documentation

## 📅 Nouvelle fonctionnalité : Timeline des événements

### Description
Affiche une timeline complète des événements marquants (milestones) pour :
- Les changements de titre
- Les sélections par la curation staff
- Les articles en tendance
- Les jalons du compte (100k vues, etc.)

### Structure de la table

```sql
CREATE TABLE milestone_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER,           -- NULL = événement global
    event_type TEXT,              -- Catégorie de l'événement
    description TEXT,             -- Détails de l'événement
    occurred_at TIMESTAMP         -- Quand l'événement a eu lieu
)
```

### Utilisation

#### 1. Voir tous les événements
```bash
python3 sismograph.py --milestones
```

**Sortie :**
```
📅 MILESTONE TIMELINE
====================================================================================================

Date                 Type            Article ID   Description
----------------------------------------------------------------------------------------------------
2026-01-18 13:18:38  title_change    3144468      Titre change...
2026-01-18 13:18:38  staff_curated   3144468      Article selectionne...

📊 STATISTIQUES
Type d'événement               Nombre
----------------------------------------
title_change                   1
staff_curated                  1

📌 Total d'événements : 2
📄 Articles affectés : 1
🔥 Événements cette semaine : 2
```

#### 2. Voir les événements d'un article spécifique
```bash
python3 sismograph.py --milestone-article 3144468
```

Affiche uniquement les événements liés à l'article 3144468.

### Ajouter des événements (from Python)

```python
from core.database import DatabaseManager

db = DatabaseManager()

# Enregistrer un changement de titre
db.log_milestone(
    article_id=3144468,
    event_type='title_change',
    description='Titre changé de Old Title à New Title'
)

# Enregistrer une sélection staff
db.log_milestone(
    article_id=3144468,
    event_type='staff_curated',
    description='Article sélectionné par la curation staff'
)

# Enregistrer un événement global (article_id=None)
db.log_milestone(
    article_id=None,
    event_type='milestone_100k',
    description='Total de 100k vues atteint'
)
```

### Types d'événements recommandés

| Type | Description | Exemple |
|------|-------------|---------|
| `title_change` | Changement de titre | "Titre changé de 'X' à 'Y'" |
| `staff_curated` | Sélectionné par staff | "Article sélectionné par la curation" |
| `trending` | Devenu tendance | "Article en tendance" |
| `milestone_*` | Jalon atteint | "100k vues atteint" |
| `published` | Publication | "Article publié" |
| `featured` | En avant | "Article en avant" |
| `comment_surge` | Pic de commentaires | "+50 commentaires en 1h" |
| `deleted` | Supprimé | "Article supprimé par l'auteur" |

### Affichage des statistiques

La fonction affiche automatiquement :
- **Timeline complète** - Tous les événements triés par date
- **Comptage par type** - Distribution des types d'événements
- **Total d'événements** - Nombre total enregistré
- **Articles affectés** - Nombre d'articles avec des événements
- **Événements récents** - Comptage des 7 derniers jours

### Intégration dans les scripts

#### Dans `devto_tracker.py` ou scripts de collecte :
```python
from core.database import DatabaseManager

db = DatabaseManager('devto_metrics.db')

# Après avoir détecté un changement
if article_title_changed:
    db.log_milestone(
        article_id=article_id,
        event_type='title_change',
        description=f'Titre changé de "{old_title}" à "{new_title}"'
    )
```

#### Dans `cleanup_articles.py` :
```python
# Quand un article est supprimé
db.log_milestone(
    article_id=article_id,
    event_type='deleted',
    description='Article supprimé (n\'existe plus sur DEV.to)'
)
```

### Cas d'usage

1. **Tracer l'évolution des articles**
   ```bash
   python3 sismograph.py --milestone-article 3144468
   ```
   Voir tout l'historique d'un article

2. **Analyser les performances après curation**
   ```bash
   # Combiner avec --evolution
   python3 sismograph.py --evolution 3144468
   # Puis voir les milestones pour voir quand il a été curé
   ```

3. **Identifier les pics d'engagement**
   ```bash
   # Correler milestones avec engagement_evolution
   python3 sismograph.py --milestones
   # Chercher les événements comme "staff_curated" ou "trending"
   ```

4. **Suivre la maintenance des articles**
   Voir quand les titres ont été optimisés, quand les articles ont été révisés, etc.

### Notes

- Chaque événement est **automatiquement timestampé** avec `occurred_at`
- Les événements peuvent être **globaux** (article_id = NULL) ou **spécifiques** à un article
- La timeline est **triée par date décroissante** (plus récent d'abord)
- Les statistiques incluent un **compte des 7 derniers jours**
- Compatible avec l'architecture `DatabaseManager` refactorisée

### Exemple complet d'intégration

```python
from core.database import DatabaseManager
from datetime import datetime

db = DatabaseManager()

# Simulation d'une collection avec événements
def collect_and_track():
    # Collecte classique
    # ...
    
    # Enregistrer les milestones découverts
    db.log_milestone(3144468, 'staff_curated', 'Nouvel article Staff Picks')
    db.log_milestone(3100000, 'trending', 'En tendance sur DEV.to')
    
# Puis afficher la timeline
# python3 sismograph.py --milestones
```
