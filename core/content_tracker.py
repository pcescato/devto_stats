import sqlite3
import json
from datetime import datetime

class ContentTracker:
    def __init__(self, db_manager):
        """
        Initialise le tracker avec une instance de DatabaseManager.
        """
        self.db = db_manager

    def check_content_updates(self, article_id, current_title, current_tags):
        """
        Compare le titre et les tags actuels avec la dernière version connue.
        Si un changement est détecté, enregistre un Milestone.
        """
        conn = self.db.get_connection()
        
        # 1. Récupérer la dernière version connue
        last_version = conn.execute("""
            SELECT title, tags FROM article_metrics 
            WHERE article_id = ? 
            ORDER BY collected_at DESC LIMIT 1 OFFSET 1
        """, (article_id,)).fetchone()

        if not last_version:
            return # Premier enregistrement, rien à comparer

        old_title = last_version['title']
        old_tags = last_version['tags']

        # 2. Détection de changement de Titre
        if old_title and old_title != current_title:
            print(f"📝 Title change detected for article {article_id}")
            self.db.log_milestone(
                article_id, 
                "TITLE_CHANGE", 
                f"From: '{old_title}' To: '{current_title}'"
            )

        # 3. Détection de changement de Tags
        if old_tags and old_tags != current_tags:
            print(f"🏷️ Tags change detected for article {article_id}")
            self.db.log_milestone(
                article_id, 
                "TAGS_CHANGE", 
                f"From: {old_tags} To: {current_tags}"
            )