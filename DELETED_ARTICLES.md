# Gestion des Articles Supprimés

## 🗑️ Le Problème

Quand tu supprimes un article sur DEV.to, il disparaît de l'API mais **reste dans ta base de données locale** avec tout son historique. Cela peut créer de la confusion dans les statistiques.

## ✅ La Solution

Nous avons créé un système de **détection et marquage** des articles supprimés :
- Les articles supprimés sont **marqués** (pas effacés)
- Leur historique est **préservé** pour analyse
- Ils sont **filtrés** par défaut des rapports
- Tu peux les **restaurer** en cas d'erreur
- Tu peux les **purger définitivement** si besoin

---

## 📋 Workflow Recommandé

### 1️⃣ Configuration Initiale (une seule fois)

```bash
# Ajouter les colonnes de tracking
python3 cleanup_articles.py --api-key YOUR_KEY --init
```

### 2️⃣ Détection des Articles Supprimés (régulièrement)

```bash
# Détecter les articles supprimés (sans les marquer)
python3 cleanup_articles.py --api-key YOUR_KEY --detect

# Détecter ET marquer comme supprimés
python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted
```

**Recommandation :** Lance cette commande hebdomadairement ou après avoir supprimé des articles.

### 3️⃣ Voir les Articles Supprimés

```bash
# Lister les articles marqués comme supprimés
python3 cleanup_articles.py --list-deleted

# Voir les statistiques
python3 cleanup_articles.py --stats

# Inclure les articles supprimés dans list_articles
python3 list_articles.py --include-deleted
```

### 4️⃣ Restaurer un Article (si erreur)

```bash
# Si un article a été marqué par erreur
python3 cleanup_articles.py --restore 3144468
```

### 5️⃣ Purge Définitive (optionnel)

```bash
# Supprimer DÉFINITIVEMENT les articles supprimés de la DB
python3 cleanup_articles.py --api-key YOUR_KEY --purge-deleted --confirm
```

⚠️ **ATTENTION** : Cette action est **irréversible** et supprime :
- Toutes les métriques historiques
- Les analytics quotidiennes
- Les commentaires
- Les referrers/traffic sources

---

## 🔍 Commandes Détaillées

### `cleanup_articles.py`

#### Initialisation
```bash
python3 cleanup_articles.py --api-key YOUR_KEY --init
```
Ajoute les colonnes `is_deleted` et `deleted_at` à la table `article_metrics`.

#### Détection
```bash
# Détecter seulement (liste les articles)
python3 cleanup_articles.py --api-key YOUR_KEY --detect

# Détecter et marquer
python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted
```
Compare la base de données avec l'API DEV.to pour trouver les articles supprimés.

#### Consultation
```bash
# Lister les articles supprimés
python3 cleanup_articles.py --list-deleted

# Voir les statistiques (actifs vs supprimés)
python3 cleanup_articles.py --stats
```

#### Restauration
```bash
# Restaurer un article marqué par erreur
python3 cleanup_articles.py --restore ARTICLE_ID
```

#### Purge
```bash
# Supprimer définitivement
python3 cleanup_articles.py --api-key YOUR_KEY --purge-deleted --confirm
```

---

## 📊 Impact sur les Autres Scripts

### Scripts Mis à Jour

#### `list_articles.py`
- Par défaut : **exclut** les articles supprimés
- Option `--include-deleted` : les affiche avec 🗑️

```bash
# Articles actifs uniquement (défaut)
python3 list_articles.py

# Inclure les articles supprimés
python3 list_articles.py --include-deleted
```

### Scripts À Mettre À Jour (si besoin)

Les autres scripts (`dashboard.py`, `quality_analytics.py`, etc.) peuvent aussi être mis à jour pour filtrer les articles supprimés. Pour l'instant, ils montrent tous les articles.

**Pour les filtrer manuellement**, ajoute cette clause WHERE dans les requêtes SQL :
```sql
WHERE (is_deleted IS NULL OR is_deleted = 0)
```

---

## 🎯 Cas d'Usage

### Cas 1 : Article Supprimé par Erreur
```bash
# 1. Tu supprimes un article sur DEV.to
# 2. Tu lances la détection
python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted

# 3. Tu réalises ton erreur
# 4. Tu restaures dans la DB
python3 cleanup_articles.py --restore 3144468

# 5. Tu republies l'article sur DEV.to
# 6. À la prochaine collecte, il réapparaîtra normalement
```

### Cas 2 : Nettoyage de Printemps
```bash
# 1. Tu supprimes plusieurs vieux articles sur DEV.to
# 2. Tu marques les articles supprimés
python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted

# 3. Tu consultes les stats
python3 cleanup_articles.py --stats

# 4. Après quelques mois, tu purges définitivement
python3 cleanup_articles.py --purge-deleted --confirm
```

### Cas 3 : Audit Régulier
```bash
# Routine hebdomadaire
python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted
python3 cleanup_articles.py --stats
```

---

## 🛡️ Sécurité des Données

### Ce qui est Préservé
✅ Marquage des articles supprimés **préserve** :
- Toutes les métriques historiques
- Les analytics quotidiennes
- Les commentaires
- Les referrers
- Les snapshots temporels

### Ce qui est Supprimé
❌ Purge définitive **supprime** :
- Toutes les données de l'article
- Impossible à récupérer
- **Utiliser avec précaution !**

---

## 💡 Conseils

1. **Lance `--init` une seule fois** au début pour ajouter les colonnes

2. **Détecte régulièrement** les articles supprimés :
   ```bash
   # Ajoute à ta routine de collecte
   python3 devto_tracker.py --api-key YOUR_KEY --collect
   python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted
   ```

3. **Ne purge PAS immédiatement** - garde l'historique quelques mois pour analyse

4. **Vérifie avant de purger** :
   ```bash
   python3 cleanup_articles.py --list-deleted
   # Vérifie que tu veux vraiment supprimer ces articles
   python3 cleanup_articles.py --purge-deleted --confirm
   ```

5. **Utilise `--include-deleted`** pour auditer ce qui a été supprimé :
   ```bash
   python3 list_articles.py --include-deleted --sort views
   ```

---

## 🔄 Routine de Maintenance Recommandée

### Quotidienne
```bash
python3 devto_tracker.py --api-key YOUR_KEY --collect
```

### Hebdomadaire
```bash
python3 cleanup_articles.py --api-key YOUR_KEY --detect --mark-deleted
python3 cleanup_articles.py --stats
```

### Mensuelle
```bash
python3 cleanup_articles.py --list-deleted
# Décider si purge nécessaire
```

### Semestrielle
```bash
# Si beaucoup d'articles supprimés depuis longtemps
python3 cleanup_articles.py --purge-deleted --confirm
```

---

## ❓ FAQ

### Que se passe-t-il si je republie un article supprimé ?
À la prochaine collecte, il sera automatiquement récupéré de l'API et apparaîtra comme un "nouvel" article avec ses nouvelles métriques.

### Puis-je récupérer un article après purge ?
Non, la purge est définitive. C'est pourquoi on recommande de **marquer** plutôt que purger.

### Les statistiques incluent-elles les articles supprimés ?
Après marquage, `list_articles.py` les exclut par défaut. Les autres scripts peuvent encore les inclure - à toi de décider si tu veux les filtrer.

### Comment savoir si un article est supprimé ?
```bash
python3 list_articles.py --include-deleted
# Les articles supprimés ont 🗑️ à côté du titre
```

---

**En résumé** : Le système de marquage te donne la flexibilité de gérer tes articles supprimés tout en préservant l'historique précieux pour tes analyses ! 📊