import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="devto_metrics.db"):
        self.db_path = db_path
        # On s'assure que la base est saine dès l'initialisation
        self._run_migrations()

    def get_connection(self):
        """Retourne une connexion prête à l'emploi avec row_factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _run_migrations(self):
        """Vérifie et met à jour le schéma automatiquement."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Vérification de 'is_deleted' dans article_metrics
        # (C'est ce qui a fait planter list_articles.py tout à l'heure)
        try:
            cursor.execute("SELECT is_deleted FROM article_metrics LIMIT 1")
        except sqlite3.OperationalError:
            print("🔧 Migration : Ajout de la colonne 'is_deleted'...")
            cursor.execute("ALTER TABLE article_metrics ADD COLUMN is_deleted INTEGER DEFAULT 0")

        # 2. Création de la table d'historique (pour les changements de titres/contenus)
        # On y ajoute un 'content_hash' pour détecter les changements sans stocker des gigas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                title TEXT,
                slug TEXT,
                tags TEXT,
                content_hash TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Création de la table des événements marquants (Jess Lee, pics de vélocité)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS milestone_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                event_type TEXT, 
                description TEXT,
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # --- MÉTHODES UTILITAIRES POUR TES SCRIPTS ---

    def get_latest_article_snapshot(self, article_id):
        """Récupère les dernières métriques connues d'un article."""
        query = "SELECT * FROM article_metrics WHERE article_id = ? ORDER BY collected_at DESC LIMIT 1"
        with self.get_connection() as conn:
            return conn.execute(query, (article_id,)).fetchone()

    def mark_as_deleted(self, article_id):
        """Soft delete d'un article."""
        with self.get_connection() as conn:
            conn.execute("UPDATE article_metrics SET is_deleted = 1 WHERE article_id = ?", (article_id,))
            
    def get_all_active_articles(self):
        """Centralise la liste des articles pour list_articles.py et sismograph.py."""
        query = """
            SELECT article_id, title, slug, MAX(views) as total_views, MAX(published_at) as published_at
            FROM article_metrics 
            WHERE is_deleted = 0 
            GROUP BY article_id 
            ORDER BY published_at DESC
        """
        with self.get_connection() as conn:
            return conn.execute(query).fetchall()