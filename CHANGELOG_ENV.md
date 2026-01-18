# Mise à jour - Variables d'environnement

## 🎯 Résumé des changements

Les clés API sont maintenant chargées automatiquement depuis un fichier `.env` au lieu d'être passées via la ligne de commande. Cela améliore la sécurité en évitant d'exposer les clés dans l'historique de commandes.

## ✅ Modifications apportées

### 1. Nouveau fichier `.env`
- Créé `.env` pour stocker les clés API
- Créé `.env.example` comme template
- Déjà protégé par `.gitignore`

### 2. Scripts modifiés

Tous les scripts utilisant l'API DEV.to ont été mis à jour :

- ✅ `devto_tracker.py` - Charge DEVTO_API_KEY depuis .env
- ✅ `cleanup_articles.py` - Charge DEVTO_API_KEY depuis .env  
- ✅ `content_collector.py` - Charge DEVTO_API_KEY depuis .env

**Changements:**
- Ajout de `import os` et `from dotenv import load_dotenv`
- Argument `--api-key` maintenant optionnel (fallback vers variable d'environnement)
- Messages d'erreur clairs si la clé n'est pas trouvée

### 3. Documentation mise à jour

- ✅ `README.md` - Instructions de configuration avec `.env`
- ✅ `list_methods.md` - Toutes les commandes mises à jour
- ✅ Workflows quotidiens simplifiés

### 4. Corrections

- ✅ Corrigé l'erreur `sqlite3.OperationalError: no such column: is_deleted` dans `list_articles.py`
  - Le script vérifie maintenant si la colonne existe avant de l'utiliser
  - Compatible avec les bases de données existantes

### 5. Dépendances

- ✅ Installé `python-dotenv` pour charger les variables d'environnement

## 📝 Utilisation

### Avant :
```bash
python3 devto_tracker.py --api-key YOUR_KEY --init
python3 devto_tracker.py --api-key YOUR_KEY --collect
```

### Maintenant :
```bash
# Configuration unique
echo "DEVTO_API_KEY=your_actual_key" > .env

# Utilisation simplifiée
python3 devto_tracker.py --init
python3 devto_tracker.py --collect
```

## 🔐 Sécurité

✅ Les clés ne sont plus exposées dans :
- L'historique du terminal
- Les logs de commandes
- Les captures d'écran

✅ Le fichier `.env` est protégé par `.gitignore` et ne sera pas commité

## 🚀 Prochaines étapes

1. **Configurer votre `.env`** :
   ```bash
   # Éditer le fichier .env
   DEVTO_API_KEY=votre_clé_ici
   ```

2. **Tester la collecte** :
   ```bash
   python3 devto_tracker.py --collect
   ```

3. **Utiliser tous les scripts sans --api-key** !

## ℹ️ Rétrocompatibilité

Les scripts continuent de fonctionner avec `--api-key` si vous préférez (par exemple pour des tests ou plusieurs comptes).

Priorité :
1. Argument `--api-key` si fourni
2. Variable d'environnement `DEVTO_API_KEY` sinon
3. Message d'erreur clair si aucune des deux n'est trouvée
