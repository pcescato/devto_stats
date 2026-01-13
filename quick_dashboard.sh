#!/bin/bash
# 
# Quick Dashboard - Script wrapper simple
# Usage: ./quick_dashboard.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/devto_metrics.db"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Génération de votre dashboard...${NC}\n"

# Check si la DB existe
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Base de données introuvable: $DB_PATH"
    echo "Assurez-vous d'avoir collecté des données avec devto_tracker.py"
    exit 1
fi

# Lancer le dashboard
python3 "$SCRIPT_DIR/dashboard.py" --db "$DB_PATH"

echo -e "\n${GREEN}✅ Dashboard généré avec succès !${NC}"
echo ""
echo "💡 Conseils :"
echo "  • Lancez ce script après chaque nouvelle publication"
echo "  • Comparez les métriques entre vos articles"
echo "  • Identifiez vos lecteurs fidèles dans la section commentateurs"
echo ""
echo "📅 Prochain article ? Validez la cohérence titre/tags/contenu !"