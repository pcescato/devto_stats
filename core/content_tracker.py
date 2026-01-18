#!/usr/bin/env python3
from datetime import datetime
from core.database import DatabaseManager

class ContentTracker:
    def __init__(self, db_path="devto_metrics.db"):
        self.db = DatabaseManager(db_path)

    def track_changes(self, article_id, current_title, current_tags, edited_at_api, conn=None):
        """
        Compare la date edited_at de l'API avec notre dernier historique.
        """
        # On récupère le dernier titre et la dernière date de modif connue
        query = """
            SELECT title, edited_at_api 
            FROM article_history 
            WHERE article_id = ? 
            ORDER BY changed_at DESC LIMIT 1
        """
        should_close = conn is None
        if conn is None:
            conn = self.db.get_connection()
        
        last_version = conn.execute(query, (article_id,)).fetchone()
        
        if should_close:
            conn.close()
            conn = None

        # Si c'est la première fois ou si edited_at a changé
        if not last_version or (edited_at_api and edited_at_api != last_version['edited_at_api']):
            
            # On vérifie si c'est une modif de titre (majeur) ou juste du texte (mineur)
            event_desc = "Content update"
            is_major = False
            
            if last_version and current_title != last_version['title']:
                event_desc = f"Title change: '{last_version['title']}' -> '{current_title}'"
                is_major = True
                print(f"📢 [MAJOR] {event_desc}")

            # On sauvegarde la nouvelle version
            self._save_version(article_id, current_title, current_tags, edited_at_api, conn)
            
            # On loggue l'événement Milestone pour le Sismographe
            if is_major:
                self.db.log_milestone(article_id, 'title_change', event_desc, conn)

    def _save_version(self, article_id, title, tags, edited_at_api, conn=None):
        query = """
            INSERT INTO article_history (article_id, title, tags, edited_at_api, changed_at) 
            VALUES (?, ?, ?, ?, ?)
        """
        should_close = conn is None
        if conn is None:
            conn = self.db.get_connection()
        
        conn.execute(query, (article_id, title, tags, edited_at_api, datetime.now()))
        
        if should_close:
            conn.commit()
            conn.close()