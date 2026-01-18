from core.database import DatabaseManager
from datetime import datetime

db = DatabaseManager()

# 1. On nettoie les tests
with db.get_connection() as conn:
    conn.execute("DELETE FROM milestone_events")
    conn.execute("DELETE FROM article_history")

# 2. On insère les vrais événements marquants
# Remplace 'ARTICLE_ID_BOTNET' par le vrai ID de ton article sur le botnet
article_id = 2783785 # (Vérifie l'ID avec list_articles.py)

# Le changement de titre du 13
db.log_milestone(article_id, 'title_change', "Optimisation : Why Streamlit... is a Billing Trap")
# On triche un peu sur la date pour coller à tes logs du 13 vers 07h00
with db.get_connection() as conn:
    conn.execute("UPDATE milestone_events SET occurred_at = '2026-01-13 07:00:00' WHERE event_type = 'title_change'")

# Le Like de Jess Lee le 17
db.log_milestone(article_id, 'staff_curated', "Reaction de Jess Lee (Staff)")
with db.get_connection() as conn:
    conn.execute("UPDATE milestone_events SET occurred_at = '2026-01-17 01:00:00' WHERE event_type = 'staff_curated'")

print("✅ Vrais jalons injectés. Relance advanced_analytics.py !")