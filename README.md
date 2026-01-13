# DEV.to Metrics Tracker 📊

**Collecte automatique et analyse historique de vos métriques DEV.to**

> "Sans données historiques, on ne voit que des snapshots. Avec des données historiques, on voit des tendances."

## 🎯 Objectifs

1. **Collecter automatiquement** toutes vos métriques DEV.to
2. **Historiser** les données pour analyse temporelle
3. **Analyser en profondeur** l'engagement (commentaires, followers, etc.)
4. **Ne jamais perdre de données** (la clé du projet !)

## 📦 Fichiers

```
devto-metrics-tracker/
├── devto_tracker.py          # Script principal de collecte
├── comment_analyzer.py       # Analyse approfondie des commentaires
├── setup_automation.sh       # Configuration automatique
├── dev.py                    # Votre script analytics original
└── devto_metrics.db          # Base de données SQLite (générée)
```

## 🚀 Installation rapide

### 1. Prérequis

```bash
pip install requests
```

### 2. Initialisation

```bash
# Initialiser la base de données
python3 devto_tracker.py --api-key YOUR_API_KEY --init

# Premier snapshot
python3 devto_tracker.py --api-key YOUR_API_KEY --collect
```

### 3. Automatisation (recommandé)

```bash
# Setup automatique avec cron
export DEVTO_API_KEY='your-api-key'
chmod +x setup_automation.sh
./setup_automation.sh
```

Cela va :
- ✅ Initialiser la base de données
- ✅ Faire une collecte test
- ✅ Créer un wrapper pour cron
- ✅ Vous proposer différentes fréquences de collecte

## 📊 Structure de la base de données

### Table: `snapshots`
Vue d'ensemble quotidienne de toutes vos métriques.

| Colonne | Description |
|---------|-------------|
| `collected_at` | Timestamp de la collecte |
| `total_articles` | Nombre total d'articles |
| `total_views` | Vues cumulées |
| `total_reactions` | Réactions cumulées |
| `total_comments` | Commentaires cumulés |
| `follower_count` | Nombre de followers |

### Table: `article_metrics`
Métriques détaillées par article à chaque collecte.

| Colonne | Description |
|---------|-------------|
| `collected_at` | Timestamp de la collecte |
| `article_id` | ID unique de l'article |
| `title` | Titre de l'article |
| `views` | Nombre de vues |
| `reactions` | Nombre de réactions |
| `comments` | Nombre de commentaires |
| `tags` | Tags (JSON array) |

### Table: `follower_events`
Évolution du nombre de followers.

| Colonne | Description |
|---------|-------------|
| `collected_at` | Timestamp |
| `follower_count` | Nombre total |
| `new_followers_since_last` | Gain depuis dernière collecte |

### Table: `comments`
Commentaires individuels pour analyse qualitative.

| Colonne | Description |
|---------|-------------|
| `comment_id` | ID unique du commentaire |
| `article_id` | Article concerné |
| `created_at` | Date du commentaire |
| `author_username` | Auteur |
| `body_html` | Contenu HTML |
| `body_length` | Longueur en caractères |

## 🔍 Utilisation

### Collecte manuelle

```bash
# Collecter un snapshot
python3 devto_tracker.py --api-key YOUR_KEY --collect

# Voir la croissance des 30 derniers jours
python3 devto_tracker.py --api-key YOUR_KEY --analyze-growth 30

# Analyser la vélocité d'un article spécifique
python3 devto_tracker.py --api-key YOUR_KEY --analyze-article 123456
```

### Analyse des commentaires

```bash
# Analyser les commentaires d'un article
python3 comment_analyzer.py --article 123456

# Comparer l'engagement entre articles
python3 comment_analyzer.py --compare

# Trouver vos lecteurs les plus engagés
python3 comment_analyzer.py --engaged-readers

# Analyser le timing des commentaires
python3 comment_analyzer.py --timing

# Rapport complet
python3 comment_analyzer.py --full-report
```

## 📈 Exemples de questions répondues

Avec les données historisées, vous pouvez répondre à :

### Growth Analysis
- Combien de vues ai-je gagné par jour cette semaine ?
- Quel article a la meilleure vélocité (vues/jour) ?
- Quand ai-je eu le plus de nouveaux followers ?

### Comment Deep-Dive
- Qui sont mes lecteurs les plus fidèles ?
- Combien de temps après publication arrivent les commentaires ?
- Quels articles génèrent le plus de discussion ?
- Quelle est la longueur moyenne des commentaires (engagement profond) ?

### Correlation Analysis
- Quel article m'a apporté le plus de followers ?
- Y a-t-il un lien entre nombre de commentaires et followers gagnés ?
- Les articles longs (>10min) génèrent-ils plus d'engagement ?

## ⏰ Fréquences de collecte recommandées

### Début (0-1000 followers)
**2x par jour** (matin et soir)
- Suffisant pour voir les tendances
- Pas trop de requêtes API
```cron
0 8,20 * * * /path/to/collect_metrics.sh
```

### Croissance (1000-5000 followers)
**4x par jour** (toutes les 6h)
- Capture les variations journalières
```cron
0 */6 * * * /path/to/collect_metrics.sh
```

### Établi (5000+ followers)
**6x par jour** ou plus
- Pour articles viraux
- Capturer les pics précisément
```cron
0 */4 * * * /path/to/collect_metrics.sh
```

## 💡 Cas d'usage réels

### Cas 1 : Article viral
> "Beyond the Linear CV" - 1114 vues en 2,5 jours

Avec tracking historique, vous pouvez :
- Voir la courbe de croissance heure par heure
- Identifier le pic (probablement H+6 à H+24)
- Corréler avec les commentaires de Ben Halpern et Art Light
- Mesurer la "longue traîne" après le pic

### Cas 2 : Followers growth
> +210 followers en 2,5 jours

Questions répondues :
- Combien le jour 1 ? Jour 2 ? Jour 3 ?
- Corrélation avec les vues ?
- Quand s'est stabilisé ?

### Cas 3 : Engagement commentaires
> 15 commentaires dont un très détaillé d'Art Light

Analyses possibles :
- Qui a commenté en premier ?
- Longueur moyenne des commentaires (>200 chars = engagement profond)
- Combien de jours après publication ?
- Combien de commentateurs uniques ?

## 🔧 Maintenance

### Backup de la base
```bash
# Backup simple
cp devto_metrics.db devto_metrics_backup_$(date +%Y%m%d).db

# Backup compressé
sqlite3 devto_metrics.db .dump | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Vérifier la taille
```bash
du -h devto_metrics.db
```

### Nettoyer les vieilles données (si nécessaire)
```sql
-- Garder seulement les 90 derniers jours
DELETE FROM article_metrics 
WHERE collected_at < datetime('now', '-90 days');

-- Vacuum pour récupérer l'espace
VACUUM;
```

## 📊 Requêtes SQL utiles

### Croissance par article (derniers 7 jours)
```sql
SELECT 
    article_id,
    title,
    MAX(views) - MIN(views) as views_gained,
    MAX(reactions) - MIN(reactions) as reactions_gained,
    MAX(comments) - MIN(comments) as comments_gained
FROM article_metrics
WHERE collected_at >= datetime('now', '-7 days')
GROUP BY article_id
ORDER BY views_gained DESC
LIMIT 10;
```

### Meilleurs jours de la semaine
```sql
SELECT 
    strftime('%w', collected_at) as day_of_week,
    CASE strftime('%w', collected_at)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END as day_name,
    COUNT(*) as publications,
    AVG(views) as avg_views
FROM article_metrics
GROUP BY day_of_week
ORDER BY avg_views DESC;
```

### Vitesse de commentaires par article
```sql
SELECT 
    article_id,
    article_title,
    COUNT(*) as total_comments,
    ROUND(
        (julianday(MAX(created_at)) - julianday(MIN(created_at))) * 24, 
        1
    ) as duration_hours,
    ROUND(
        COUNT(*) / ((julianday(MAX(created_at)) - julianday(MIN(created_at))) * 24 + 1),
        2
    ) as comments_per_hour
FROM comments
GROUP BY article_id
HAVING total_comments > 5
ORDER BY comments_per_hour DESC;
```

## 🚨 Troubleshooting

### Erreur: "Database is locked"
```bash
# Vérifier les processus utilisant la DB
lsof devto_metrics.db

# Si bloqué, attendre ou tuer le processus
```

### Erreur: "API rate limit"
```bash
# Réduire la fréquence de collecte
# Dev.to limite généralement à ~10 req/sec
```

### Données manquantes
```bash
# Vérifier les logs
tail -f logs/collection.log

# Tester manuellement
python3 devto_tracker.py --api-key YOUR_KEY --collect
```

## 🎯 Roadmap / Idées futures

- [ ] Dashboard web interactif (Flask/Streamlit)
- [ ] Export vers CSV pour analyse dans Excel/Sheets
- [ ] Alertes (email si article dépasse X vues)
- [ ] Intégration avec d'autres APIs (Twitter, GitHub)
- [ ] Analyse de sentiment des commentaires
- [ ] Prédiction de performance d'article

## 📝 Notes importantes

1. **L'API DEV.to ne conserve pas l'historique**
   - Vos données d'aujourd'hui = snapshot actuel
   - Pas d'historique avant votre première collecte
   - D'où l'importance de commencer MAINTENANT

2. **Respect de l'API**
   - Ne pas collecter trop fréquemment
   - 2-6x par jour est raisonnable
   - Éviter les pics de requêtes

3. **Confidentialité**
   - La DB contient votre API key indirectement
   - Ne pas commit dans Git
   - Ajouter `*.db` dans .gitignore

## 🤝 Contributing

Idées ? Bugs ? Améliorations ?
1. Fork le repo
2. Créer une branche feature
3. Commit vos changements
4. Push et créer une Pull Request

## 📄 License

MIT License - Utilisez comme vous voulez !

## 🙏 Remerciements

Inspiré par le besoin de ne pas perdre les données de croissance de
"Beyond the Linear CV" (+210 followers en 2,5 jours).

---

**Made with ❤️ and efficient laziness**
